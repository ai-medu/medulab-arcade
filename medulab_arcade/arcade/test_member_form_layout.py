from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class MemberCreateFormLayoutTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staffer', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def test_member_type_comes_first_and_notify_is_parent_only(self):
        html = self.client.get(reverse('member_create')).content.decode()
        # 회원 유형 선택이 아이디 입력보다 먼저 나온다
        self.assertLess(html.index('id="id_user_type"'), html.index('id="id_username"'))
        self.assertLess(html.index('회원 유형 *'), html.index('아이디 *'))
        # 알림 수신은 메듀랩 학부모일 때만 켜지도록 하는 스크립트가 있다
        self.assertIn("typeSel.value === 'medulab_parent'", html)
        self.assertIn('notifyAttBox', html)
