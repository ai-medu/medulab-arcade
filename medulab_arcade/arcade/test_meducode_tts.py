import base64
import json
import tempfile
from datetime import timedelta
from unittest import mock

import requests
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from .models import MeduCodeSetting, MeduCodeTtsUsage

URL = '/meducode/api/tts/'
WAV = b'RIFF....WAVEfake-audio'


def google_ok(*args, **kwargs):
    res = mock.Mock(status_code=200)
    res.json.return_value = {'audioContent': base64.b64encode(WAV).decode()}
    return res


class MeduCodeTtsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('student', password='pw-for-test')
        self.client.force_login(self.user)
        self.settings_override = override_settings(
            GOOGLE_TTS_API_KEY='test-key', MEDUCODE_TTS_CACHE=tempfile.mkdtemp(),
            MEDUCODE_TTS_VOICE='ko-KR-Standard-A',
            MEDUCODE_TTS_USER_DAILY_CHARS=20, MEDUCODE_TTS_MONTHLY_CHARS=30,
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def say(self, text, client=None):
        return (client or self.client).post(URL, json.dumps({'text': text}), content_type='application/json')

    def used(self):
        return sum(MeduCodeTtsUsage.objects.values_list('chars', flat=True))

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_makes_audio_and_keeps_key_out_of_url(self, post):
        res = self.say('안녕하세요')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(base64.b64decode(res.json()['audio']), WAV)
        url, kwargs = post.call_args.args[0], post.call_args.kwargs
        self.assertNotIn('test-key', url)
        self.assertEqual(kwargs['headers']['X-Goog-Api-Key'], 'test-key')
        self.assertEqual(kwargs['json']['audioConfig'], {'audioEncoding': 'LINEAR16', 'sampleRateHertz': 16000,
                                                         'speakingRate': 1.0, 'pitch': 0.0, 'volumeGainDb': 0.0})
        self.assertEqual(kwargs['json']['voice'], {'languageCode': 'ko-KR', 'name': 'ko-KR-Standard-A'})
        self.assertEqual(self.used(), 5)

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_same_sentence_is_made_once(self, post):
        self.say('안녕하세요')
        self.assertEqual(self.say('  안녕하세요 ').status_code, 200)
        self.assertEqual(post.call_count, 1)
        self.assertEqual(self.used(), 5)

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_speed_pitch_volume(self, post):
        def say(**style):
            return self.client.post(URL, json.dumps({'text': '안녕', **style}), content_type='application/json')
        self.assertEqual(say(speed='slow', pitch='high', volume='low').status_code, 200)
        sent = post.call_args.kwargs['json']['audioConfig']
        self.assertEqual((sent['speakingRate'], sent['pitch'], sent['volumeGainDb']), (0.8, 4.0, -6.0))
        self.assertEqual(say(speed='fast').status_code, 200)
        self.assertEqual(post.call_count, 2)   # 설정이 다르면 따로 만든다
        for style in ({'speed': 'turbo'}, {'pitch': 5}, {'volume': ['high']}):
            self.assertEqual(say(**style).status_code, 400, style)

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_each_voice_is_made_separately(self, post):
        def say(voice):
            return self.client.post(URL, json.dumps({'text': '안녕', 'voice': voice}), content_type='application/json')
        for voice in ('ko-KR-Standard-A', 'ko-KR-Standard-C', 'ko-KR-Standard-C'):
            self.assertEqual(say(voice).status_code, 200)
        self.assertEqual([c.kwargs['json']['voice']['name'] for c in post.call_args_list], ['ko-KR-Standard-A', 'ko-KR-Standard-C'])
        for voice in ('ko-KR-Chirp3-HD-X', 'en-US-Standard-A', 5, ['x']):
            self.assertEqual(say(voice).status_code, 400, repr(voice))

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_login_is_required(self, post):
        self.client.logout()
        self.assertEqual(self.say('안녕').status_code, 401)
        post.assert_not_called()

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_csrf_is_checked(self, post):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.user)
        self.assertEqual(self.say('안녕', strict).status_code, 403)
        post.assert_not_called()

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_bad_requests(self, post):
        for text in ('', '   ', '가' * 101, 3, None):
            self.assertEqual(self.say(text).status_code, 400, repr(text))
        self.assertEqual(self.client.post(URL, 'nope', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post(URL, '[1]', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.delete(URL).status_code, 405)
        post.assert_not_called()

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_daily_and_monthly_limits(self, post):
        self.assertEqual(self.say('가' * 20).status_code, 200)
        self.assertEqual(self.say('나').status_code, 429)          # 회원 하루 한도
        other = Client()
        other.force_login(User.objects.create_user('other', password='pw-for-test'))
        self.assertEqual(self.say('다' * 10, other).status_code, 200)
        self.assertEqual(self.say('라', other).status_code, 429)   # 전체 월 한도
        self.assertEqual(post.call_count, 2)
        self.assertEqual(self.used(), 30)

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_my_usage(self, post):
        self.assertEqual(self.client.get(URL).json(), {'ok': True, 'used_today': 0, 'user_daily_chars': 20})
        self.say('안녕하세요')
        self.assertEqual(self.client.get(URL).json()['used_today'], 5)
        self.assertEqual(Client().get(URL).status_code, 401)

    def test_google_failure_is_refunded(self):
        failures = [mock.Mock(status_code=403, text='denied'), requests.Timeout()]
        for failure in failures:
            kwargs = {'side_effect': failure} if isinstance(failure, Exception) else {'return_value': failure}
            with mock.patch('arcade.meducode_tts.requests.post', **kwargs), self.assertLogs('arcade.meducode_tts', 'ERROR'):
                self.assertEqual(self.say('안녕').status_code, 502)
        self.assertEqual(self.used(), 0)

    @mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok)
    def test_without_key(self, post):
        with override_settings(GOOGLE_TTS_API_KEY=''):
            self.assertEqual(self.say('안녕').status_code, 503)
        post.assert_not_called()


SETTINGS_URL = '/meducode/api/settings/'
ADMIN_KEY = 'AIzaAdminKey_1234567890-abcd'


@override_settings(GOOGLE_TTS_API_KEY='', MEDUCODE_TTS_VOICE='ko-KR-Standard-A',
                   MEDUCODE_TTS_USER_DAILY_CHARS=2000, MEDUCODE_TTS_MONTHLY_CHARS=1000000)
class MeduCodeSettingsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('boss', password='pw-for-test', is_staff=True)
        self.client.force_login(self.admin)
        cache = override_settings(MEDUCODE_TTS_CACHE=tempfile.mkdtemp())
        cache.enable()
        self.addCleanup(cache.disable)

    def save(self, client=None, **body):
        return (client or self.client).post(SETTINGS_URL, json.dumps(body), content_type='application/json')

    def test_only_admin(self):
        student = Client()
        student.force_login(User.objects.create_user('kid', password='pw-for-test'))
        for client, status in ((Client(), 401), (student, 403)):
            self.assertEqual(client.get(SETTINGS_URL).status_code, status)
            self.assertEqual(self.save(client, api_key=ADMIN_KEY).status_code, status)
        self.assertFalse(MeduCodeSetting.objects.exists())

    def test_project_list_tells_who_is_admin(self):
        self.assertTrue(self.client.get('/meducode/api/projects/').json()['is_admin'])

    def test_key_is_encrypted_and_never_returned(self):
        res = self.save(api_key=f'  {ADMIN_KEY} ')
        self.assertEqual(res.status_code, 200)
        for body in (res.content, self.client.get(SETTINGS_URL).content):
            self.assertNotIn(ADMIN_KEY.encode(), body)
        data = res.json()
        self.assertEqual((data['has_key'], data['key_source'], data['key_hint']), (True, 'admin', 'abcd'))
        stored = MeduCodeSetting.objects.get(pk=1).tts_key_encrypted
        self.assertNotIn(ADMIN_KEY, stored)

    def test_empty_key_keeps_and_remove_deletes(self):
        self.save(api_key=ADMIN_KEY)
        self.assertTrue(self.save(api_key='', monthly_chars=500).json()['has_key'])
        self.assertFalse(self.save(remove_key=True).json()['has_key'])

    def test_saved_values_are_used_for_speech(self):
        self.save(api_key=ADMIN_KEY, user_daily_chars=3, monthly_chars=100)
        with mock.patch('arcade.meducode_tts.requests.post', side_effect=google_ok) as post:
            say = lambda text: self.client.post(URL, json.dumps({'text': text, 'voice': 'ko-KR-Standard-D'}), content_type='application/json')
            self.assertEqual(say('안녕').status_code, 200)
            self.assertEqual(say('반가워').status_code, 429)
        self.assertEqual(post.call_args.kwargs['headers']['X-Goog-Api-Key'], ADMIN_KEY)
        self.assertEqual(post.call_args.kwargs['json']['voice']['name'], 'ko-KR-Standard-D')

    def test_env_key_is_used_until_admin_sets_one(self):
        with override_settings(GOOGLE_TTS_API_KEY='env-key-wxyz'):
            self.assertEqual(self.client.get(SETTINGS_URL).json()['key_source'], 'env')
            self.assertEqual(self.save(api_key=ADMIN_KEY).json()['key_source'], 'admin')

    def test_changed_secret_key_means_enter_again(self):
        self.save(api_key=ADMIN_KEY)
        with override_settings(SECRET_KEY='another-secret-key-for-test'):
            self.client.force_login(self.admin)
            self.assertFalse(self.client.get(SETTINGS_URL).json()['has_key'])

    def test_usage_by_member(self):
        today = timezone.localdate()
        kid = User.objects.create_user('kid2', password='pw-for-test', first_name='하늘', last_name='김')
        MeduCodeTtsUsage.objects.create(user=kid, date=today, chars=30)
        MeduCodeTtsUsage.objects.create(user=self.admin, date=today, chars=7)
        if today.day > 1:
            MeduCodeTtsUsage.objects.create(user=kid, date=today.replace(day=1), chars=100)
        MeduCodeTtsUsage.objects.create(user=kid, date=today.replace(day=1) - timedelta(days=1), chars=999)   # 지난달
        data = self.client.get(SETTINGS_URL).json()
        month = 130 if today.day > 1 else 30
        self.assertEqual(data['used_today'], 37)
        self.assertEqual(data['used_this_month'], month + 7)
        self.assertEqual(data['usage'], [{'user': 'kid2', 'name': '김하늘', 'today': 30, 'month': month},
                                         {'user': 'boss', 'name': '', 'today': 7, 'month': 7}])

    def test_bad_values(self):
        for body in ({'api_key': 'short'}, {'api_key': 'a' * 30 + ' b'}, {'api_key': 5},
                     {'user_daily_chars': -1}, {'monthly_chars': '10'}, {'monthly_chars': True}):
            self.assertEqual(self.save(**body).status_code, 400, body)
        self.assertEqual(self.client.post(SETTINGS_URL, '[]', content_type='application/json').status_code, 400)

    def test_csrf_is_checked(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.admin)
        self.assertEqual(self.save(strict, api_key=ADMIN_KEY).status_code, 403)
