from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ProfilePageTests(TestCase):
    """상단 메뉴의 이름은 프로필 페이지로 연결되고, 프로필 페이지에는 회원정보와 수정 폼만 나온다"""

    def setUp(self):
        self.user = User.objects.create_user('profuser', password='x', email='p@example.com')
        self.client.force_login(self.user)

    def test_profile_shows_only_member_info_and_form(self):
        res = self.client.get(reverse('profile'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '회원 정보 수정')
        self.assertContains(res, 'name="real_name"')
        for gone in ('배지 컬렉션', '받은 좋아요', '내 작품'):
            self.assertNotContains(res, gone)

    def test_top_menu_name_links_to_profile(self):
        res = self.client.get(reverse('profile'))
        self.assertContains(res, f'href="{reverse("profile")}" class="nav-link">👤')
        self.user.is_staff = True
        self.user.save()
        res = self.client.get(reverse('profile'))
        self.assertContains(res, f'href="{reverse("profile")}" class="nav-link accent-text">👤')

    def test_profile_edit_saves(self):
        res = self.client.post(reverse('profile'), {
            'real_name': '홍길동', 'nickname': '길동', 'birth_date': '', 'phone_number': '01012345678',
            'email': 'p@example.com', 'user_type': self.user.profile.user_type,
        })
        self.assertEqual(res.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.real_name, '홍길동')
