from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


def make(username, user_type, complete=True):
    user = User.objects.create_user(username, password='x')
    profile = user.profile
    profile.user_type, profile.onboarding_complete = user_type, complete
    profile.save()
    return user


class MemberFilterTests(TestCase):
    def setUp(self):
        self.client.force_login(make('boss', 'medulab_staff'))
        User.objects.filter(username='boss').update(is_staff=True)
        make('kim1', 'medulab_member')
        make('kim2', 'medulab_member')
        make('lee1', 'medulab_member')
        make('kim_mom', 'medulab_parent')
        make('site_kid', 'student')
        make('site_any', 'general')
        make('ghost', 'general', complete=False)

    def _get(self, query=''):
        res = self.client.get(reverse('member_list') + query)
        groups = {g['key']: g for g in res.context['member_groups']}
        counts = {f['code']: f['count'] for g in groups.values() for f in g['filters']}
        return res, groups, counts

    def _names(self, res):
        return {u.username for u in res.context['users']}

    def test_only_groups_show_until_one_is_chosen(self):
        res, groups, _ = self._get()
        self.assertEqual((res.context['all_count'], groups['medulab']['count'], groups['site']['count']), (7, 5, 2))
        self.assertContains(res, '?group=medulab')
        self.assertContains(res, '?group=site')
        self.assertNotContains(res, '?type=')

    def test_medulab_group_lists_its_types_in_order(self):
        res, _, _ = self._get('?group=medulab')
        self.assertEqual(self._names(res), {'boss', 'kim1', 'kim2', 'lee1', 'kim_mom'})
        html = res.content.decode()
        codes = ['medulab_member', 'medulab_parent', 'medulab_teacher', 'medulab_inactive', 'medulab_staff']
        spots = [html.index(f'?type={code}') for code in codes]
        self.assertEqual(spots, sorted(spots))
        self.assertNotIn('?type=student', html)

    def test_site_group_lists_its_types(self):
        res, _, _ = self._get('?group=site')
        self.assertEqual(self._names(res), {'site_kid', 'site_any'})
        html = res.content.decode()
        spots = [html.index(f'?type={code}"') for code in ('student', 'parent', 'general', 'teacher')]
        self.assertEqual(spots, sorted(spots))
        self.assertNotIn('?type=medulab_member', html)

    def test_choosing_a_type_keeps_its_group_open_and_numbers_match(self):
        res, groups, counts = self._get('?type=medulab_parent')
        self.assertTrue(groups['medulab']['active'])
        self.assertEqual(self._names(res), {'kim_mom'})
        for code, n in counts.items():
            self.assertEqual(len(self.client.get(reverse('member_list') + f'?type={code}').context['users']), n, code)

    def test_search_counts_only_matches_and_unknown_group_is_ignored(self):
        res, groups, counts = self._get('?q=kim')
        self.assertEqual((res.context['all_count'], counts['medulab_member'], groups['medulab']['count']), (3, 2, 3))
        res, groups, _ = self._get('?group=nope')
        self.assertEqual(res.context['current_group'], '')
        self.assertEqual(len(res.context['users']), 7)
