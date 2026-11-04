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


class ProfileEditRulesTests(TestCase):
    """회원 유형은 관리자만 바꾼다 / 화면에 없는 칸은 저장 때 지워지지 않는다"""

    def _post(self, user, **extra):
        self.client.force_login(user)
        data = {'real_name': '홍길동', 'nickname': '', 'birth_date': '', 'phone_number': '01012345678',
                'email': user.email}
        data.update(extra)
        return self.client.post(reverse('profile'), data)

    def test_user_type_cannot_be_changed_by_member(self):
        user = User.objects.create_user('kid1', password='x', email='k@example.com')
        before = user.profile.user_type
        res = self._post(user, user_type='medulab_teacher')
        self.assertEqual(res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.user_type, before)

    def test_non_parent_save_keeps_address_and_notify(self):
        user = User.objects.create_user('plain', password='x', email='p2@example.com')
        user.profile.address = '서울시 어딘가'
        user.profile.notify_attendance = True
        user.profile.save()
        self._post(user)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.address, '서울시 어딘가')
        self.assertTrue(user.profile.notify_attendance)

    def test_medulab_parent_saves_address_and_notify(self):
        user = User.objects.create_user('mparent', password='x', email='mp@example.com')
        user.profile.user_type = 'medulab_parent'
        user.profile.save()
        res = self._post(user, address='서울 강남구 테헤란로 1 101호', children_info='[]', notify_attendance='on')
        self.assertEqual(res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.address, '서울 강남구 테헤란로 1 101호')
        self.assertTrue(user.profile.notify_attendance)
        self.assertFalse(user.profile.notify_news)
        self.assertEqual(user.profile.user_type, 'medulab_parent')

    def test_profile_shows_type_read_only_and_address_search(self):
        user = User.objects.create_user('mparent2', password='x', email='mp2@example.com')
        user.profile.user_type = 'medulab_parent'
        user.profile.save()
        self.client.force_login(user)
        res = self.client.get(reverse('profile'))
        self.assertContains(res, '회원 유형은 관리자만 변경할 수 있어요')
        self.assertNotContains(res, 'name="user_type"')
        self.assertContains(res, 'profileAddressBtn')
