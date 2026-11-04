import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Attendance, ClassAttendance, ClassEnrollment, ScheduleEvent, SchoolClass, TuitionInvoice
from .views import compute_invoice_amounts, _presence_for_dates


class _KwonwooOctober:
    """김권우의 10월: 토요일 수업, 10/3 개천절, 10/10 결석(기록 없음), 10/17 보강, 10/24·10/31 출석"""

    def setUp(self):
        self.kid = User.objects.create_user('kid', password='x')
        self.klass = SchoolClass.objects.create(name='집중성장 토-오후반', tuition_fee=200000, monthly_sessions=4, days_of_week='6')
        self.enrollment = ClassEnrollment.objects.create(school_class=self.klass, student=self.kid)
        tz = timezone.get_current_timezone()
        ScheduleEvent.objects.create(title='개천절', event_type=ScheduleEvent.EVENT_TYPE_HOLIDAY, is_active=True,
                                     start_date=datetime.datetime(2026, 10, 3, tzinfo=tz),
                                     end_date=datetime.datetime(2026, 10, 3, tzinfo=tz))
        for day, kind in ((17, Attendance.TYPE_MAKEUP), (24, Attendance.TYPE_PRESENT), (31, Attendance.TYPE_PRESENT)):
            Attendance.objects.create(user=self.kid, date=datetime.date(2026, 10, day), attendance_type=kind)

    def _calc(self):
        return compute_invoice_amounts(self.klass, self.enrollment, datetime.date(2026, 11, 30))


class InvoiceAttendanceTests(_KwonwooOctober, TestCase):

    def test_no_record_falls_back_to_real_checkins(self):
        calc = self._calc()
        # 수업일 10/10, 17, 24, 31 중 10/10 한 번만 결석 (개천절 10/3 은 수업이 없으니 제외)
        self.assertEqual(calc['absence_count'], 1)
        self.assertEqual(calc['absence_deduction'], 50000)
        self.assertEqual(calc['amount'], 150000)

    def test_saved_attendance_sheet_wins_over_checkins(self):
        ClassAttendance.objects.create(enrollment=self.enrollment, date=datetime.date(2026, 10, 10), is_present=True)
        ClassAttendance.objects.create(enrollment=self.enrollment, date=datetime.date(2026, 10, 17), is_present=False)
        calc = self._calc()
        self.assertEqual(calc['absence_count'], 1)  # 10/10 은 출석부에서 출석으로 고쳐졌고, 10/17 이 결석으로 바뀜
        dates = [datetime.date(2026, 10, 10), datetime.date(2026, 10, 17)]
        self.assertEqual(_presence_for_dates(self.enrollment, dates),
                         {datetime.date(2026, 10, 10): True, datetime.date(2026, 10, 17): False})

    def test_home_access_is_not_attendance(self):
        Attendance.objects.filter(date=datetime.date(2026, 10, 24)).update(attendance_type=Attendance.TYPE_ACCESS)
        self.assertEqual(self._calc()['absence_count'], 2)

    def test_holiday_is_not_counted_as_absence(self):
        Attendance.objects.create(user=self.kid, date=datetime.date(2026, 10, 10), attendance_type=Attendance.TYPE_PRESENT)
        self.assertEqual(self._calc()['absence_count'], 0)

    def test_attendance_modal_shows_absence(self):
        staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(staff)
        inv = TuitionInvoice.objects.create(student=self.kid, school_class=self.klass, amount=150000, base_amount=200000,
                                            due_date=datetime.date(2026, 11, 30), absence_count=1, absence_deduction=50000)
        res = self.client.get(reverse('tuition_invoice_attendance_detail', args=[inv.id]))
        cells = {c['date']: c['is_present'] for c in res.context['cells']}
        self.assertEqual(cells, {datetime.date(2026, 10, 10): False, datetime.date(2026, 10, 17): True,
                                 datetime.date(2026, 10, 24): True, datetime.date(2026, 10, 31): True})


class RecalcInvoiceTests(_KwonwooOctober, TestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def _invoice(self, **kw):
        defaults = dict(student=self.kid, school_class=self.klass, amount=195000, base_amount=200000,
                        discount_reason='친구소개', discount_amount=5000, due_date=datetime.date(2026, 11, 30))
        defaults.update(kw)
        return TuitionInvoice.objects.create(**defaults)

    def _recalc(self, *invoices):
        return self.client.post(reverse('tuition_invoice_bulk_action'),
                                {'bulk_action': 'recalc', 'invoice_ids': [i.id for i in invoices]}, follow=True)

    def test_recalc_updates_absence_and_keeps_discount(self):
        inv = self._invoice()
        res = self._recalc(inv)
        inv.refresh_from_db()
        # 결석 1회 차감 = (수업비 200,000 - 기본할인 5,000) ÷ 4회 = 48,750원
        self.assertEqual((inv.absence_count, inv.absence_deduction, inv.amount), (1, 48750, 146250))
        self.assertEqual((inv.discount_reason, inv.discount_amount), ('친구소개', 5000))
        self.assertEqual(inv.attended_count, 3)  # 전월 출석 3/4
        self.assertIn('금액 변경 1건', ' '.join(str(m) for m in res.context['messages']))
        self._recalc(inv)  # 한 번 더 해도 그대로
        inv.refresh_from_db()
        self.assertEqual(inv.amount, 146250)

    def test_recalc_skips_manual_paid_and_canceled(self):
        manual = self._invoice(amount=1000)
        paid = self._invoice(status=TuitionInvoice.STATUS_PAID, due_date=datetime.date(2026, 11, 29))
        canceled = self._invoice(status=TuitionInvoice.STATUS_CANCELED, due_date=datetime.date(2026, 11, 28))
        res = self._recalc(manual, paid, canceled)
        for inv, amount in ((manual, 1000), (paid, 195000), (canceled, 195000)):
            inv.refresh_from_db()
            self.assertEqual((inv.amount, inv.absence_count), (amount, 0))
        text = ' '.join(str(m) for m in res.context['messages'])
        self.assertIn('금액 변경 0건', text)
        self.assertIn('직접 수정', text)

    def test_recalc_keeps_extra_discount(self):
        inv = self._invoice(amount=185000, extra_discount_reason='직접입력', extra_discount_amount=10000)
        self._recalc(inv)
        inv.refresh_from_db()
        self.assertEqual((inv.absence_deduction, inv.extra_discount_amount, inv.amount), (48750, 10000, 136250))

    def test_non_staff_cannot_recalc(self):
        inv = self._invoice()
        self.client.force_login(self.kid)
        self.client.post(reverse('tuition_invoice_bulk_action'), {'bulk_action': 'recalc', 'invoice_ids': [inv.id]})
        inv.refresh_from_db()
        self.assertEqual(inv.amount, 195000)


class DiscountedSessionFeeTests(TestCase):
    """결석 1회 차감 = (수업비 - 기본할인) ÷ 월 출석 횟수. 수업비 140,000원, 기본할인 5,000원이면 33,750원"""

    def setUp(self):
        self.kid = User.objects.create_user('kid', password='x')
        self.klass = SchoolClass.objects.create(name='맞춤성장 토요반', tuition_fee=140000, monthly_sessions=4, days_of_week='6')
        self.enrollment = ClassEnrollment.objects.create(school_class=self.klass, student=self.kid,
                                                         discount_reason='친구소개', discount_amount=5000)
        # 2026년 10월 토요일: 3(개천절 제외) 10 17 24 31 중 10/10 한 번만 결석
        tz = timezone.get_current_timezone()
        ScheduleEvent.objects.create(title='개천절', event_type=ScheduleEvent.EVENT_TYPE_HOLIDAY, is_active=True,
                                     start_date=datetime.datetime(2026, 10, 3, tzinfo=tz),
                                     end_date=datetime.datetime(2026, 10, 3, tzinfo=tz))
        for day in (17, 24, 31):
            Attendance.objects.create(user=self.kid, date=datetime.date(2026, 10, day), attendance_type=Attendance.TYPE_PRESENT)

    def test_one_absence_deducts_discounted_fee_quarter(self):
        calc = compute_invoice_amounts(self.klass, self.enrollment, datetime.date(2026, 11, 30))
        self.assertEqual(self.klass.per_session_fee_after(5000), 33750)
        self.assertEqual((calc['absence_count'], calc['absence_deduction'], calc['discount_amount']), (1, 33750, 5000))
        self.assertEqual(calc['amount'], 140000 - 5000 - 33750)  # 101,250원

    def test_no_discount_uses_full_fee(self):
        self.enrollment.discount_amount = 0
        self.enrollment.save()
        calc = compute_invoice_amounts(self.klass, self.enrollment, datetime.date(2026, 11, 30))
        self.assertEqual((calc['absence_deduction'], calc['amount']), (35000, 105000))

    def test_discount_override_changes_per_session_fee(self):
        calc = compute_invoice_amounts(self.klass, self.enrollment, datetime.date(2026, 11, 30),
                                       discount_override=('직접입력', 20000))
        self.assertEqual(calc['absence_deduction'], 30000)  # (140,000 - 20,000) ÷ 4
        self.assertEqual(calc['amount'], 140000 - 20000 - 30000)

    def test_deduction_never_exceeds_discounted_fee(self):
        Attendance.objects.filter(user=self.kid).delete()  # 4회 모두 결석
        calc = compute_invoice_amounts(self.klass, self.enrollment, datetime.date(2026, 11, 30))
        self.assertEqual((calc['absence_count'], calc['absence_deduction'], calc['amount']), (4, 135000, 0))
