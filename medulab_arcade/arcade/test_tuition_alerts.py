import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from arcade.models import AdminNotification, SchoolClass, TuitionBatchPayment, TuitionInvoice


def _paid_response(amount):
    resp = mock.Mock(status_code=200)
    resp.json.return_value = {'status': 'PAID', 'amount': {'total': amount}}
    return resp


@override_settings(PORTONE_API_SECRET='test', PORTONE_WEBHOOK_SECRET='')
class TuitionAlertTests(TestCase):
    def setUp(self):
        self.klass = SchoolClass.objects.create(name='AICE반', days_of_week='1', start_time=datetime.time(16, 0))
        self.kid = User.objects.create_user('kid', password='x')
        self.kid.profile.real_name = '홍길동'
        self.kid.profile.save()
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)

    def _invoice(self, amount=150000, days=7, **kwargs):
        return TuitionInvoice.objects.create(
            student=self.kid, school_class=self.klass, amount=amount,
            due_date=timezone.localdate() + datetime.timedelta(days=days), **kwargs)

    def _webhook(self, payment_id):
        return self.client.post(reverse('tuition_webhook'), {'data': {'paymentId': payment_id}},
                                content_type='application/json')

    def test_payment_notifies_once_even_if_verified_twice(self):
        invoice = self._invoice()
        with mock.patch('requests.get', return_value=_paid_response(150000)):
            self.client.post(reverse('tuition_pay_public_verify', args=[invoice.ensure_pay_token()]))
            self._webhook(invoice.portone_payment_id)
        n = AdminNotification.objects.get()
        self.assertEqual(n.kind, 'tuition_paid')
        self.assertIn('홍길동 150,000원', n.title)
        self.assertIn('AICE반', n.body)
        self.assertIn(f'student_id={self.kid.pk}', n.url)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, TuitionInvoice.STATUS_PAID)

    def test_batch_payment_makes_one_notification(self):
        invoices = [self._invoice(100000, -30), self._invoice(50000)]
        batch = TuitionBatchPayment.objects.create(amount=150000)
        batch.invoices.set(invoices)
        with mock.patch('requests.get', return_value=_paid_response(150000)):
            self._webhook(batch.portone_payment_id)
            self._webhook(batch.portone_payment_id)
        n = AdminNotification.objects.get()
        self.assertIn('150,000원', n.title)
        self.assertIn('외 1건', n.body)
        self.assertEqual(TuitionInvoice.objects.filter(status=TuitionInvoice.STATUS_PAID).count(), 2)

    def test_cancel_notifies(self):
        invoice = self._invoice(status=TuitionInvoice.STATUS_PAID, paid_at=timezone.now())
        self.client.force_login(self.staff)
        res = self.client.post(reverse('tuition_invoice_cancel', args=[invoice.pk]),
                               {'confirm': 'yes', 'mode': 'status_only', 'reason': '중복 결제'})
        self.assertTrue(res.json()['ok'])
        n = AdminNotification.objects.get(kind='tuition_cancel')
        self.assertIn('환불 없음', n.title)
        self.assertIn('중복 결제', n.body)

    def test_due_summary_once_a_day(self):
        self._invoice(100000, -1)
        self._invoice(50000, 0)
        self._invoice(70000, 5)   # 아직 기한 전이라 세지 않음
        self.client.force_login(self.staff)
        self.client.get(reverse('admin_notification_list'))
        data = self.client.get(reverse('admin_notification_list')).json()
        self.assertEqual(data['unread'], 1)
        self.assertIn('기한 지난 미납 1건, 오늘 기한 1건', data['items'][0]['title'])
        self.assertIn('100,000원', data['items'][0]['body'])

    def test_due_summary_silent_without_unpaid(self):
        self._invoice(days=5)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('admin_notification_list')).json()['unread'], 0)
