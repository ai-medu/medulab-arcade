from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import TypingGameRecord


class GameRecordTests(TestCase):
    def setUp(self):
        self.url = reverse('typing_game_records')
        self.kid = User.objects.create_user('kid', password='x')
        self.friend = User.objects.create_user('friend', password='x')

    def _save(self, user, game, level, value, lang='ko'):
        self.client.force_login(user)
        return self.client.post(self.url, {'game': game, 'lang': lang, 'level': level, 'value': value},
                                content_type='application/json')

    def _get(self, lang='ko'):
        return self.client.get(self.url, {'lang': lang}).json()

    def test_page_has_levels_and_sets_csrf_cookie(self):
        res = self.client.get(reverse('typing_game'))
        self.assertContains(res, 'id="tgLevelBtn"')
        self.assertIn('csrftoken', res.cookies)

    def test_anonymous_can_see_but_not_save(self):
        data = self._get()
        self.assertEqual((data['logged_in'], data['games']['rain']), (False, {'mine': None, 'top': None, 'cleared': 0}))
        res = self.client.post(self.url, {'game': 'rain', 'lang': 'ko', 'level': 1, 'value': 100},
                               content_type='application/json')
        self.assertEqual(res.status_code, 401)

    def test_levels_open_in_order(self):
        self.assertEqual(self._save(self.kid, 'rain', 2, 100).status_code, 400)
        self.assertEqual(self._save(self.kid, 'rain', 1, 100).status_code, 200)
        self.assertEqual(self._save(self.kid, 'rain', 2, 90).status_code, 200)
        self.assertEqual(self._get()['games']['rain']['cleared'], 2)
        self.assertEqual(self._save(self.kid, 'chain', 4, 23).status_code, 200)   # 끝말잇기는 난이도를 바로 고른다

    def test_higher_level_ranks_first_then_score(self):
        self._save(self.kid, 'rain', 1, 300)
        self.assertTrue(self._save(self.friend, 'rain', 1, 100).json()['new_best'])
        self.assertEqual(self._get()['games']['rain']['top']['name'], 'kid')
        res = self._save(self.friend, 'rain', 2, 90).json()
        self.assertTrue(res['new_top'])
        self.assertEqual(res['games']['rain']['top'], {'level': 2, 'value': 90.0, 'name': 'friend'})
        self.assertEqual(res['games']['rain']['mine'], {'level': 2, 'value': 90.0})

    def test_only_better_record_replaces_and_time_games_prefer_shorter(self):
        self._save(self.kid, 'car', 1, 40)
        self.assertFalse(self._save(self.kid, 'car', 1, 50).json()['new_best'])
        self.assertTrue(self._save(self.kid, 'car', 1, 30.44).json()['new_best'])
        self.assertEqual(TypingGameRecord.objects.get().value, 30.4)
        self._save(self.friend, 'car', 1, 25)
        self.assertEqual(self._get()['games']['car']['top']['name'], 'friend')

    def test_language_and_staff_are_separate(self):
        teacher = User.objects.create_user('boss', password='x', is_staff=True)
        res = self._save(teacher, 'chain', 4, 99)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self._save(teacher, 'rain', 7, 10).status_code, 200)    # 선생님은 모든 레벨
        self.assertIsNone(self._get()['games']['chain']['top'])                   # 전체 최고에는 넣지 않는다
        self._save(self.kid, 'chain', 4, 5, lang='en')
        self.assertIsNone(self._get('ko')['games']['chain']['top'])
        self.assertEqual(self._get('en')['games']['chain']['top']['value'], 5)

    def test_bad_values_are_rejected(self):
        for game, level, value in (('nope', 1, 10), ('rain', 11, 10), ('chain', 5, 10), ('rain', 1, 0),
                                   ('rain', 1, 999999), ('car', 1, 0.5), ('rain', 1, 'nan'), ('rain', 'x', 10)):
            self.assertEqual(self._save(self.kid, game, level, value).status_code, 400, (game, level, value))
        self.assertFalse(TypingGameRecord.objects.exists())
