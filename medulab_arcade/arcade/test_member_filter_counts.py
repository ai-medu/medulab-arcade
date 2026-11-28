from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


def make(username, user_type, complete=True):
    user = User.objects.create_user(username, password='x')
    profile = user.profile
    profile.user_type, profile.onboarding_complete = user_type, complete
    profile.save()
    return user


class MemberFilterCountTests(TestCase):
    def setUp(self):
        self.client.force_login(make('boss', 'medulab_staff'))
        User.objects.filter(username='boss').update(is_staff=True)
        make('kim1', 'medulab_member')
        make('kim2', 'medulab_member')
        make('lee1', 'medulab_member')
        make('kim_mom', 'medulab_parent')
        make('ghost', 'general', complete=False)

    def _counts(self, query=''):
        res = self.client.get(reverse('member_list') + query)
        counts = {f['code']: f['count'] for f in res.context['type_filters']}
        return res, counts

    def test_numbers_match_the_list_each_button_opens(self):
        res, counts = self._counts()
        self.assertEqual((counts['medulab_member'], counts['medulab_parent'], counts['medulab_staff'], counts['general']), (3, 1, 1, 0))
        self.assertEqual(res.context['all_count'], len(res.context['users']))
        self.assertContains(res, '메듀랩 학생 <span class="n">(3)</span>')
        for code, n in counts.items():
            self.assertEqual(len(self.client.get(reverse('member_list') + f'?type={code}').context['users']), n, code)

    def test_choosing_a_type_keeps_all_numbers(self):
        res, counts = self._counts('?type=medulab_parent')
        self.assertEqual((res.context['all_count'], counts['medulab_member']), (5, 3))

    def test_search_counts_only_matches(self):
        res, counts = self._counts('?q=kim')
        self.assertEqual((res.context['all_count'], counts['medulab_member'], counts['medulab_parent']), (3, 2, 1))
