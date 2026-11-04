from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Attendance, NotificationLog, ParentChildLink, SchoolClass, TuitionInvoice
from . import parent_notify

SOLAPI = dict(
    SOLAPI_API_KEY='key', SOLAPI_API_SECRET='secret', SOLAPI_PF_ID='KA01PF1',
    SOLAPI_SENDER='01011112222', SOLAPI_TEMPLATE_ATTENDANCE='KA01TP-att',
    SOLAPI_TEMPLATE_INVOICE='KA01TP-inv', SITE_BASE_URL='https://example.test',
)


class ParentNotifyTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user('kid', password='x')
        self.student.profile.real_name = '김학생'
        self.student.profile.save()
        self.parent = User.objects.create_user('mom', password='x')
        self.parent.profile.phone_number = '010-1234-5678'
        self.parent.profile.save()
        ParentChildLink.objects.create(parent=self.parent, child=self.student)
        self.klass = SchoolClass.objects.create(name='AICE반', tuition_fee=200000)
        patcher = mock.patch.object(parent_notify, '_spawn', lambda fn, *a: fn(*a))
        patcher.start()
        self.addCleanup(patcher.stop)

    def _attendance(self, kind='present'):
        return Attendance.objects.create(user=self.student, attendance_type=kind)

    def test_no_config_only_logs_dry_run(self):
        with mock.patch('arcade.parent_notify.requests.post') as post:
            parent_notify.notify_attendance(self._attendance())
        post.assert_not_called()
        log = NotificationLog.objects.get()
        self.assertEqual(log.status, NotificationLog.STATUS_DRYRUN)
        self.assertEqual(log.phone, '01012345678')

    @override_settings(**SOLAPI)
    def test_attendance_sent_once_per_day(self):
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            att = self._attendance('makeup')
            parent_notify.notify_attendance(att)
            parent_notify.notify_attendance(att)
        self.assertEqual(post.call_count, 1)
        kwargs = post.call_args.kwargs
        msg = kwargs['json']['message']
        self.assertEqual(msg['to'], '01012345678')
        self.assertEqual(msg['kakaoOptions']['templateId'], 'KA01TP-att')
        self.assertEqual(msg['kakaoOptions']['variables']['#{학생이름}'], '김학생')
        self.assertEqual(msg['kakaoOptions']['variables']['#{구분}'], '보강 출석')
        self.assertTrue(kwargs['headers']['Authorization'].startswith('HMAC-SHA256 apiKey=key, date='))
        self.assertEqual(NotificationLog.objects.filter(status='sent').count(), 1)

    @override_settings(**SOLAPI)
    def test_home_access_does_not_notify(self):
        with mock.patch('arcade.parent_notify.requests.post') as post:
            parent_notify.notify_attendance(self._attendance('access'))
        post.assert_not_called()
        self.assertEqual(NotificationLog.objects.count(), 0)

    @override_settings(**SOLAPI)
    def test_no_parent_is_skipped(self):
        ParentChildLink.objects.all().delete()
        with mock.patch('arcade.parent_notify.requests.post') as post:
            parent_notify.notify_attendance(self._attendance())
        post.assert_not_called()
        self.assertEqual(NotificationLog.objects.get().status, NotificationLog.STATUS_SKIPPED)

    @override_settings(**SOLAPI)
    def test_api_failure_is_logged_not_raised(self):
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 400
            post.return_value.text = 'bad'
            parent_notify.notify_attendance(self._attendance())
        self.assertEqual(NotificationLog.objects.get().status, NotificationLog.STATUS_FAILED)

    def _invoice(self, **kw):
        defaults = dict(student=self.student, school_class=self.klass, amount=180000, base_amount=200000,
                        due_date=timezone.localdate() + timedelta(days=5))
        defaults.update(kw)
        return TuitionInvoice.objects.create(**defaults)

    @override_settings(**SOLAPI)
    def test_invoice_notice_has_pay_link_and_is_sent_once(self):
        inv = self._invoice()
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            self.assertEqual(parent_notify.send_invoice_notice(inv), 1)
            self.assertEqual(parent_notify.send_invoice_notice(inv), 0)
        opts = post.call_args.kwargs['json']['message']['kakaoOptions']
        inv.refresh_from_db()
        self.assertEqual(opts['variables']['#{결제코드}'], inv.pay_token)
        self.assertNotIn('buttons', opts)
        self.assertEqual(opts['variables']['#{금액}'], '180,000원')

    @override_settings(**SOLAPI)
    def test_paid_invoice_not_notified(self):
        inv = self._invoice(status=TuitionInvoice.STATUS_PAID)
        with mock.patch('arcade.parent_notify.requests.post') as post:
            self.assertEqual(parent_notify.send_invoice_notice(inv), 0)
        post.assert_not_called()

    @override_settings(**SOLAPI)
    def test_reminder_command_respects_interval(self):
        inv = self._invoice(due_date=timezone.localdate() - timedelta(days=2))
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            call_command('send_tuition_reminders')
            call_command('send_tuition_reminders')
        self.assertEqual(post.call_count, 1)
        self.assertIn('미납', post.call_args.kwargs['json']['message']['kakaoOptions']['variables']['#{납부상태}'])
        self.assertEqual(NotificationLog.objects.filter(invoice=inv, kind='reminder', status='sent').count(), 1)

    def test_public_pay_page(self):
        inv = self._invoice()
        token = inv.ensure_pay_token()
        res = self.client.get(reverse('tuition_pay_public', args=[token]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '180,000')
        self.assertEqual(self.client.get(reverse('tuition_pay_public', args=['nope'])).status_code, 404)

    def test_public_pay_canceled_is_404(self):
        inv = self._invoice(status=TuitionInvoice.STATUS_CANCELED)
        token = inv.ensure_pay_token()
        self.assertEqual(self.client.get(reverse('tuition_pay_public', args=[token])).status_code, 404)

    @override_settings(PORTONE_API_SECRET='')
    def test_public_verify_requires_valid_token_and_post(self):
        inv = self._invoice()
        token = inv.ensure_pay_token()
        url = reverse('tuition_pay_public_verify', args=[token])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 503)
        self.assertEqual(self.client.post(reverse('tuition_pay_public_verify', args=['bad'])).status_code, 404)

    def test_daily_checkin_view_triggers_notice(self):
        self.client.force_login(self.student)
        url = reverse('api_daily_checkin')
        res = self.client.post(url, '{"attendance_type": "present"}', content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(NotificationLog.objects.filter(kind='attendance').count(), 1)
        # 집 접속으로 바꾸거나 다른 구분은 새 알림을 만들지 않는다
        self.client.post(url, '{"attendance_type": "access"}', content_type='application/json')
        self.assertEqual(NotificationLog.objects.filter(kind='attendance').count(), 1)

    @override_settings(**SOLAPI)
    def test_notice_includes_previous_unpaid(self):
        today = timezone.localdate()
        old = self._invoice(amount=150000, due_date=today - timedelta(days=30))
        new = self._invoice(amount=180000, due_date=today + timedelta(days=5))
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            parent_notify.send_invoice_notice(new)
        v = post.call_args.kwargs['json']['message']['kakaoOptions']['variables']
        self.assertIn('1건 150,000원', v['#{이전미납}'])
        self.assertEqual(v['#{총미납액}'], '330,000원')
        res = self.client.get(reverse('tuition_pay_public', args=[new.pay_token]))
        self.assertContains(res, '이전 미납')
        old.refresh_from_db()
        self.assertContains(res, old.pay_token)

    @override_settings(**SOLAPI)
    def test_notice_without_previous(self):
        inv = self._invoice()
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            parent_notify.send_invoice_notice(inv)
        v = post.call_args.kwargs['json']['message']['kakaoOptions']['variables']
        self.assertEqual(v['#{이전미납}'], '없음')

    @override_settings(**SOLAPI)
    def test_parent_who_disabled_attendance_notice_is_skipped(self):
        self.parent.profile.notify_attendance = False
        self.parent.profile.save()
        with mock.patch('arcade.parent_notify.requests.post') as post:
            parent_notify.notify_attendance(self._attendance())
        post.assert_not_called()
        self.assertEqual(NotificationLog.objects.get().status, NotificationLog.STATUS_SKIPPED)
        # 학원비 안내는 수신 설정과 무관하게 발송
        inv = self._invoice()
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            self.assertEqual(parent_notify.send_invoice_notice(inv), 1)


@override_settings(**SOLAPI)
class BulkInvoiceNoticeTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.klass = SchoolClass.objects.create(name='AICE반', tuition_fee=200000)
        self.with_parent = self._student('kid1', '010-1234-5678')
        self.no_parent = self._student('kid2', None)
        self.client.force_login(self.staff)

    def _student(self, name, parent_phone):
        student = User.objects.create_user(name, password='x')
        if parent_phone:
            parent = User.objects.create_user(name + '_mom', password='x')
            parent.profile.phone_number = parent_phone
            parent.profile.save()
            ParentChildLink.objects.create(parent=parent, child=student)
        return student

    def _invoice(self, student, **kw):
        defaults = dict(student=student, school_class=self.klass, amount=180000, base_amount=200000,
                        due_date=timezone.localdate() + timedelta(days=5))
        defaults.update(kw)
        return TuitionInvoice.objects.create(**defaults)

    def _bulk(self, *invoices):
        return self.client.post(reverse('tuition_invoice_bulk_action'), {
            'bulk_action': 'notify', 'invoice_ids': [i.id for i in invoices],
        }, follow=True)

    def test_bulk_notify_sends_and_summarizes(self):
        ok = self._invoice(self.with_parent)
        paid = self._invoice(self.with_parent, status=TuitionInvoice.STATUS_PAID)
        nobody = self._invoice(self.no_parent)
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            res = self._bulk(ok, paid, nobody)
        self.assertEqual(post.call_count, 1)
        text = ' '.join(str(m) for m in res.context['messages'])
        self.assertIn('1건을 발송', text)
        self.assertIn('미납이 아닌 건 1건', text)
        self.assertIn('학부모 번호 없음 1건', text)

    def test_resend_allowed_after_guard_window_but_not_double_click(self):
        inv = self._invoice(self.with_parent)
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            self._bulk(inv)
            self._bulk(inv)  # 바로 다시 누르면 중복 클릭으로 막는다
            self.assertEqual(post.call_count, 1)
            NotificationLog.objects.filter(invoice=inv).update(created_at=timezone.now() - timedelta(minutes=10))
            self._bulk(inv)  # 시간이 지난 뒤에는 다시 보낼 수 있다
            self.assertEqual(post.call_count, 2)

    def test_overdue_invoice_logged_as_reminder(self):
        inv = self._invoice(self.with_parent, due_date=timezone.localdate() - timedelta(days=3))
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            self._bulk(inv)
        self.assertEqual(NotificationLog.objects.get(invoice=inv).kind, 'reminder')

    def test_failure_is_reported(self):
        inv = self._invoice(self.with_parent)
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 400
            post.return_value.text = 'bad'
            res = self._bulk(inv)
        self.assertIn('실패 1건', ' '.join(str(m) for m in res.context['messages']))

    def test_dashboard_has_notify_button_and_last_notice(self):
        inv = self._invoice(self.with_parent)
        today = timezone.localdate()
        url = reverse('tuition_admin_dashboard') + f'?year={inv.due_date.year}&month={inv.due_date.month}'
        res = self.client.get(url)
        self.assertContains(res, '학부모에게 청구 안내 발송')
        self.assertNotContains(res, '안내</div>')
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            self._bulk(inv)
        self.assertContains(self.client.get(url), '안내</div>')

    def test_non_staff_blocked(self):
        inv = self._invoice(self.with_parent)
        self.client.force_login(self.with_parent)
        with mock.patch('arcade.parent_notify.requests.post') as post:
            self.client.post(reverse('tuition_invoice_bulk_action'), {'bulk_action': 'notify', 'invoice_ids': [inv.id]})
            dash = self.client.get(reverse('tuition_admin_dashboard'))
        post.assert_not_called()
        self.assertNotEqual(dash.status_code, 200)


class SingleInvoiceModalTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.klass = SchoolClass.objects.create(name='AICE반', tuition_fee=200000, days_of_week='1,3')
        self.kid = User.objects.create_user('kid', password='x')
        self.kid.profile.real_name = '김학생'
        self.kid.profile.save()
        from .models import ClassEnrollment
        ClassEnrollment.objects.create(school_class=self.klass, student=self.kid)
        self.client.force_login(self.staff)
        self.url = reverse('tuition_admin_dashboard') + '?year=2026&month=10'
        self.save_url = reverse('class_modal_invoice_save', args=[self.klass.id])

    def _save(self, **extra):
        data = {'student_id': self.kid.id, 'amount': 200000, 'due_date': '2026-10-31', 'status': 'unpaid',
                'once_per_month': True}
        data.update(extra)
        return self.client.post(self.save_url, data, content_type='application/json')

    def test_month_page_has_button_and_modal_data(self):
        res = self.client.get(self.url)
        self.assertContains(res, '10월 청구서 개별 생성')
        self.assertContains(res, 'id="siOverlay"')
        self.assertEqual(res.context['si_students'][0]['name'], '김학생')
        self.assertEqual(res.context['si_due_default'], '2026-10-31')
        self.assertEqual(res.context['si_students'][0]['classes'][0]['id'], self.klass.id)

    def test_all_view_has_no_single_invoice_modal(self):
        res = self.client.get(reverse('tuition_admin_dashboard') + '?view=unpaid')
        self.assertNotContains(res, 'id="siOverlay"')

    def test_creates_only_that_student_invoice(self):
        other = User.objects.create_user('other', password='x')
        from .models import ClassEnrollment
        ClassEnrollment.objects.create(school_class=self.klass, student=other)
        res = self._save()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])
        invoices = TuitionInvoice.objects.all()
        self.assertEqual([(i.student_id, str(i.due_date)) for i in invoices], [(self.kid.id, '2026-10-31')])

    def test_duplicate_month_blocked_but_allowed_after_cancel(self):
        self.assertEqual(self._save().status_code, 200)
        dup = self._save()
        self.assertEqual(dup.status_code, 400)
        self.assertIn('이미 2026년 10월 청구서', dup.json()['error'])
        # 이미 있는 청구서는 모달에서 '이미 있음'으로 막히도록 목록에 실린다
        res = self.client.get(self.url)
        self.assertIn(f'{self.kid.id}:{self.klass.id}', res.context['si_existing'])
        TuitionInvoice.objects.update(status=TuitionInvoice.STATUS_CANCELED)
        self.assertEqual(self._save().status_code, 200)
        self.assertEqual(TuitionInvoice.objects.count(), 2)

    def test_non_staff_cannot_use_save_api(self):
        self.client.force_login(self.kid)
        res = self._save()
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(TuitionInvoice.objects.count(), 0)
