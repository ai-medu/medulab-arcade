from unittest import mock

from django.test import TestCase, override_settings

from arcade.admin_notify import notify_admins
from arcade.telegram_notify import send_telegram


class TelegramTests(TestCase):
    @override_settings(TELEGRAM_BOT_TOKEN='', TELEGRAM_CHAT_IDS='')
    def test_does_nothing_when_not_configured(self):
        with mock.patch('arcade.telegram_notify.threading.Thread') as t:
            send_telegram('안녕')
        t.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN='tok', TELEGRAM_CHAT_IDS='111, 222')
    def test_sends_to_every_chat_with_link(self):
        with mock.patch('arcade.telegram_notify.urllib.request.urlopen') as op, \
                mock.patch('arcade.telegram_notify.threading.Thread') as t:
            t.side_effect = lambda target, args, daemon: mock.Mock(start=lambda: target(*args))
            send_telegram('새 상담 문의', '/consult/admin/')
        self.assertEqual(op.call_count, 2)
        body = op.call_args.args[0].data.decode()
        self.assertIn('https://medulab.kr/consult/admin/', body)

    @override_settings(TELEGRAM_BOT_TOKEN='tok', TELEGRAM_CHAT_IDS='111')
    def test_notify_admins_also_sends_telegram_and_survives_failure(self):
        with mock.patch('arcade.telegram_notify.send_telegram', side_effect=RuntimeError('boom')):
            notify_admins('info', '제목', '내용')   # 예외가 나도 알림 저장은 끝까지 간다
        from arcade.models import AdminNotification
        self.assertEqual(AdminNotification.objects.count(), 1)
        with mock.patch('arcade.telegram_notify.send_telegram') as sent:
            notify_admins('info', '제목2', '내용2', '/x/')
        sent.assert_called_once_with('제목2\n내용2', '/x/')
