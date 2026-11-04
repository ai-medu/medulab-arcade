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
