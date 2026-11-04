from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import normalize_children_info


class ChildrenInfoTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def _parent(self, children_info):
        user = User.objects.create_user('mom', password='x')
        profile = user.profile
        profile.user_type = 'parent'
        profile.children_info = children_info
        profile.save()
        return user

    def test_normalize(self):
        self.assertEqual(normalize_children_info('[]'), [])
        self.assertEqual(normalize_children_info('"[]"'), [])
        self.assertEqual(normalize_children_info(None), [])
        self.assertEqual(normalize_children_info('[{"name": "민수"}]'), [{'name': '민수'}])
        self.assertEqual(normalize_children_info([{'name': '민수'}, 'x']), [{'name': '민수'}])
        self.assertEqual(normalize_children_info('깨진값'), [])

    def test_member_edit_opens_with_string_children_info(self):
        user = self._parent('[]')  # 과거에 문자열로 저장된 값
        res = self.client.get(reverse('member_edit', args=[user.id]))
        self.assertEqual(res.status_code, 200)

    def test_member_edit_page_lists_string_encoded_children(self):
        user = self._parent('[{"name": "민수", "birth_date": "", "school": "", "grade": ""}]')
        res = self.client.get(reverse('member_edit', args=[user.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '민수')

    def test_profile_form_does_not_wrap_string_again(self):
        from .forms import UserProfileUpdateForm
        user = self._parent('[]')
        form = UserProfileUpdateForm(instance=user.profile)
        # 예전에는 '"[]"' 로 한 번 더 감싸져 저장 시 다시 문자열 '[]' 이 되었다
        self.assertEqual(form.fields['children_info'].initial, '[]')


class MemberEditFieldsTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def _post_data(self, user, **extra):
        data = {'username': user.username, 'email': 'a@example.com', 'is_active': 'on',
                'user_type': user.profile.user_type, 'is_approved': 'on',
                'real_name': '홍길동', 'birth_date': '1973.01.31', 'phone_number': '010-1234-5678',
                'nickname': '길동'}
        data.update(extra)
        return data

    def test_shows_and_saves_personal_info(self):
        user = User.objects.create_user('kid', password='x')
        user.profile.user_type = 'medulab_member'
        user.profile.real_name = '준비된'
        user.profile.save()
        res = self.client.get(reverse('member_edit', args=[user.id]))
        self.assertContains(res, 'name="real_name"')
        self.assertContains(res, 'name="phone_number"')
        self.assertNotContains(res, 'name="notify_attendance"')
        res = self.client.post(reverse('member_edit', args=[user.id]), self._post_data(user))
        self.assertEqual(res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEqual((user.profile.real_name, user.profile.phone_number, str(user.profile.birth_date)),
                         ('홍길동', '01012345678', '1973-01-31'))

    def test_parent_notify_flags_editable_and_not_reset_for_students(self):
        parent = User.objects.create_user('mom', password='x')
        parent.profile.user_type = 'parent'
        parent.profile.save()
        res = self.client.get(reverse('member_edit', args=[parent.id]))
        self.assertContains(res, 'name="notify_attendance"')
        self.client.post(reverse('member_edit', args=[parent.id]), self._post_data(parent, address='서울'))
        parent.profile.refresh_from_db()
        self.assertFalse(parent.profile.notify_attendance)  # 체크 해제로 저장
        self.assertEqual(parent.profile.address, '서울')

        kid = User.objects.create_user('kid', password='x')
        kid.profile.user_type = 'medulab_member'
        kid.profile.save()
        self.client.post(reverse('member_edit', args=[kid.id]), self._post_data(kid))
        kid.profile.refresh_from_db()
        self.assertTrue(kid.profile.notify_attendance)  # 학생은 칸이 없어 기본값 유지

    def test_invalid_phone_rejected(self):
        user = User.objects.create_user('kid', password='x')
        res = self.client.post(reverse('member_edit', args=[user.id]), self._post_data(user, phone_number='12'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '전화번호는 숫자 기준')


class MemberRejectTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def _pending(self, name='newbie', user_type='medulab_member'):
        user = User.objects.create_user(name, password='x')
        user.profile.user_type = user_type
        user.profile.is_approved = False
        user.profile.save()
        return user

    def test_list_has_reject_button(self):
        self._pending()
        res = self.client.get(reverse('member_list'))
        self.assertContains(res, 'id="approveModalReject"')
        self.assertContains(res, "'학생회원')")  # 전환될 유형이 모달에 전달된다

    def test_reject_converts_to_general_type_and_completes_signup(self):
        cases = {'medulab_member': 'student', 'medulab_parent': 'parent',
                 'medulab_teacher': 'teacher', 'medulab_staff': 'general'}
        for i, (src, dst) in enumerate(cases.items()):
            user = self._pending(f'u{i}', src)
            res = self.client.post(reverse('member_reject', args=[user.id]))
            self.assertEqual(res.status_code, 302)
            user.profile.refresh_from_db()
            self.assertEqual(user.profile.user_type, dst)
            self.assertTrue(user.profile.is_approved)
            self.assertFalse(user.profile.needs_approval)
            self.assertTrue(User.objects.filter(pk=user.pk).exists())  # 삭제하지 않는다

    def test_cannot_reject_approved_staff_or_self(self):
        approved = self._pending('ok')
        approved.profile.is_approved = True
        approved.profile.save()
        other_staff = self._pending('adm')
        other_staff.is_staff = True
        other_staff.save()
        for target in (approved, other_staff, self.staff):
            before = target.profile.user_type
            self.client.post(reverse('member_reject', args=[target.id]))
            target.profile.refresh_from_db()
            self.assertEqual(target.profile.user_type, before)

    def test_non_staff_cannot_reject(self):
        user = self._pending()
        self.client.force_login(User.objects.create_user('plain', password='x'))
        self.client.post(reverse('member_reject', args=[user.id]))
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.user_type, 'medulab_member')

    def test_get_not_allowed(self):
        user = self._pending()
        self.assertEqual(self.client.get(reverse('member_reject', args=[user.id])).status_code, 405)
