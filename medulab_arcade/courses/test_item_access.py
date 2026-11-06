from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from courses.models import Chapter, Item, LearningProgram


class ItemPageAccessTests(TestCase):
    """문제 페이지는 승인된 메듀랩 정회원과 관리자만 열 수 있다"""

    def setUp(self):
        program = LearningProgram.objects.create(name='AICE Junior 대비')
        chapter = Chapter.objects.create(program=program, number=1, title='Lv1-샘플')
        self.item = Item.objects.create(chapter=chapter, number=1, title='샘플 문항')
        self.url = reverse('item_page', args=[self.item.id])

    def _user(self, name, user_type, approved=True, staff=False):
        user = User.objects.create_user(name, password='x', is_staff=staff)
        user.profile.user_type = user_type
        user.profile.is_approved = approved
        user.profile.save()
        return user

    def test_anonymous_goes_to_login(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/accounts/login/', res['Location'])
        self.assertEqual(res['X-Robots-Tag'], 'noindex, nofollow')

    def test_non_member_redirected_home(self):
        self.client.force_login(self._user('gen', 'general'))
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('home'), fetch_redirect_response=False)

    def test_unapproved_medulab_member_blocked(self):
        self.client.force_login(self._user('pend', 'medulab_member', approved=False))
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_medulab_member_and_staff_allowed(self):
        self.client.force_login(self._user('mem', 'medulab_member'))
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.client.force_login(self._user('adm2', 'general', staff=True))
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_teacher_member_allowed_but_unapproved_teacher_blocked(self):
        self.client.force_login(self._user('tch', 'teacher'))
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.client.force_login(self._user('tch2', 'teacher', approved=False))
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_course_home_still_public(self):
        res = self.client.get(reverse('course_home', args=[self.item.chapter.program.id]))
        self.assertEqual(res.status_code, 200)
