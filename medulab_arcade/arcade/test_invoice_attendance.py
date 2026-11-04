import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Attendance, ClassAttendance, ClassEnrollment, ScheduleEvent, SchoolClass, TuitionInvoice
from .views import compute_invoice_amounts, _presence_for_dates


class InvoiceAttendanceTests(TestCase):
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
