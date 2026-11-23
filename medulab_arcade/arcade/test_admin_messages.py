from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from arcade.models import AdminMessage


class AdminMessageTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def test_default_signup_guide_is_seeded_with_link(self):
        item = AdminMessage.objects.get(title__startswith='가입 안내')
        self.assertIn('https://medulab.kr/signup/?type=medulab_parent', item.body)
        page = self.client.get(reverse('admin_message_list'))
        self.assertContains(page, '가입 안내')
        self.assertContains(page, '📋 복사')
        self.assertContains(page, 'medulab_parent')

    def test_staff_only(self):
        self.client.force_login(User.objects.create_user('kid', password='x'))
        self.assertNotEqual(self.client.get(reverse('admin_message_list')).status_code, 200)
        self.assertNotEqual(self.client.post(reverse('admin_message_save'), {'title': 'a', 'body': 'b'}).status_code, 200)
        self.assertFalse(AdminMessage.objects.filter(title='a').exists())

    def test_create_update_delete(self):
        self.client.post(reverse('admin_message_save'), {'title': '수납 안내', 'body': '원비 안내\r\n두 번째 줄'})
        item = AdminMessage.objects.get(title='수납 안내')
        self.assertEqual(item.body, '원비 안내\n두 번째 줄')
        self.assertGreater(item.display_order, 0)   # 순서를 비우면 맨 아래
        self.client.post(reverse('admin_message_update', args=[item.pk]), {'title': '수납 안내 v2', 'body': '수정', 'display_order': '0'})
        item.refresh_from_db()
        self.assertEqual((item.title, item.body), ('수납 안내 v2', '수정'))
        self.client.post(reverse('admin_message_delete', args=[item.pk]))
        self.assertFalse(AdminMessage.objects.filter(pk=item.pk).exists())

    def test_empty_fields_are_rejected(self):
        before = AdminMessage.objects.count()
        res = self.client.post(reverse('admin_message_save'), {'title': ' ', 'body': 'x'}, follow=True)
        self.assertContains(res, '제목과 내용을 모두 입력')
        self.assertEqual(AdminMessage.objects.count(), before)

    def test_menu_link_is_above_member_management(self):
        html = self.client.get(reverse('admin_message_list')).content.decode()
        self.assertLess(html.index('안내 메시지</a>'), html.index('⚙️ 회원 관리'))
