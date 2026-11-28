from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ParentChildLink


def member(username, user_type, name=''):
    user = User.objects.create_user(username, password='x')
    profile = user.profile
    profile.user_type, profile.is_approved, profile.real_name = user_type, True, name
    profile.save()
    return user


class ClassGalleryButtonTests(TestCase):
    def setUp(self):
        self.kid = member('kid', 'medulab_member', '김준한')
        self.parent = member('mom', 'medulab_parent', '학부모')
        ParentChildLink.objects.create(parent=self.parent, child=self.kid)

    def _gallery(self, res):
        url = urlsplit(res.context['gallery_url'])
        return url.netloc, url.path, parse_qs(url.query)

    def test_student_sees_own_gallery(self):
        self.client.force_login(self.kid)
        res = self.client.get(reverse('my_report'))
        self.assertContains(res, '수업갤러리', count=1)
        host, path, query = self._gallery(res)
        self.assertEqual((host, path), ('medu.ipdisk.co.kr:8000', '/%EA%B0%A4%EB%9F%AC%EB%A6%AC/gallery_index.html'))
        self.assertEqual(query, {'school': ['메듀랩'], 'student': ['김준한']})

    def test_parent_sees_child_gallery_before_payment_history(self):
        self.client.force_login(self.parent)
        res = self.client.get(reverse('child_report', args=[self.kid.id]))
        self.assertContains(res, '수업갤러리', count=1)
        self.assertEqual(self._gallery(res)[2]['student'], ['김준한'])
        html = res.content.decode()
        self.assertLess(html.index('수업갤러리'), html.index('📋 납부내역'))

    def test_hidden_without_name_and_for_other_viewers(self):
        nameless = member('anon', 'medulab_member')
        self.client.force_login(nameless)
        self.assertNotContains(self.client.get(reverse('my_report')), '수업갤러리')
        staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(staff)
        self.assertNotContains(self.client.get(reverse('admin_student_report', args=[self.kid.id])), '수업갤러리')
