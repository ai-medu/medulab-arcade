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
