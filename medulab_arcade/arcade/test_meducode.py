import json
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class MeduCodeServingTests(TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'assets').mkdir()
        (self.root / 'index.html').write_text('<html><body>MeduCode App</body></html>', encoding='utf-8')
        (self.root / 'assets' / 'index-abc123.js').write_text('console.log(1)', encoding='utf-8')
        (self.root / 'blockly-media').mkdir()
        (self.root / 'blockly-media' / 'click.mp3').write_bytes(b'ID3')

    def test_index_served_with_no_cache(self):
        with override_settings(MEDUCODE_DIST=self.root):
            res = self.client.get('/meducode/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Cache-Control'], 'no-cache')
        self.assertIn(b'MeduCode App', b''.join(res.streaming_content))

    def test_hashed_assets_are_cached_long(self):
        with override_settings(MEDUCODE_DIST=self.root):
            res = self.client.get('/meducode/assets/index-abc123.js')
        self.assertEqual(res.status_code, 200)
        self.assertIn('immutable', res['Cache-Control'])
        self.assertIn('javascript', res['Content-Type'])

    def test_other_files_and_missing_files(self):
        with override_settings(MEDUCODE_DIST=self.root):
            self.assertEqual(self.client.get('/meducode/blockly-media/click.mp3').status_code, 200)
            self.assertEqual(self.client.get('/meducode/nope.js').status_code, 404)

    def test_path_traversal_is_blocked(self):
        secret = self.root.parent / 'secret.txt'
        secret.write_text('top secret', encoding='utf-8')
        with override_settings(MEDUCODE_DIST=self.root):
            for url in ('/meducode/../secret.txt', '/meducode/%2e%2e/secret.txt', '/meducode/assets/../../secret.txt'):
                res = self.client.get(url)
                self.assertIn(res.status_code, (400, 404), url)   # 폴더 밖 파일은 절대 내려 주지 않는다
                self.assertNotIn(b'top secret', res.content)

    def test_not_deployed_yet_returns_404(self):
        with override_settings(MEDUCODE_DIST=self.root / 'missing'):
            self.assertEqual(self.client.get('/meducode/').status_code, 404)

    def test_play_menu_links_to_meducode(self):
        res = self.client.get(reverse('home'))
        self.assertContains(res, 'href="/meducode/"')
        self.assertContains(res, '🧩 메듀코드')
        self.assertContains(res, '🎮 플레이')
        self.assertContains(res, '🏫 클래스')
        self.assertContains(res, '📝 숙제')
        self.assertNotContains(res, '러닝센터')
        self.assertNotContains(res, '홈플레이')


class MeduCodeProjectApiTests(TestCase):
    URL = '/meducode/api/projects/'

    def setUp(self):
        self.user = User.objects.create_user('coder', password='pw12345!')
        self.other = User.objects.create_user('other', password='pw12345!')

    def post(self, name='내 작품', data='{"scenes": []}'):
        return self.client.post(self.URL, json.dumps({'name': name, 'data': data}), content_type='application/json')

    def test_guest_sees_login_state_and_cannot_save(self):
        self.assertFalse(self.client.get(self.URL).json()['logged_in'])
        self.assertEqual(self.post().status_code, 401)

    def test_save_list_load_update_delete(self):
        self.client.force_login(self.user)
        res = self.post()
        self.assertEqual(res.status_code, 201)
        pk = res.json()['project']['id']
        listing = self.client.get(self.URL).json()
        self.assertTrue(listing['logged_in'])
        self.assertEqual([p['name'] for p in listing['projects']], ['내 작품'])
        self.assertNotIn('data', listing['projects'][0])
        detail = self.client.get(f'{self.URL}{pk}/').json()['project']
        self.assertEqual(detail['data'], '{"scenes": []}')
        res = self.client.put(f'{self.URL}{pk}/', json.dumps({'name': '바꾼 이름', 'data': '{"a": 1}'}),
                              content_type='application/json')
        self.assertEqual(res.json()['project']['name'], '바꾼 이름')
        self.assertEqual(self.user.meducode_projects.get().data, '{"a": 1}')
        self.assertEqual(self.client.delete(f'{self.URL}{pk}/').status_code, 200)
        self.assertEqual(self.user.meducode_projects.count(), 0)

    def test_cannot_touch_other_members_project(self):
        self.client.force_login(self.user)
        pk = self.post().json()['project']['id']
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'{self.URL}{pk}/').status_code, 404)
        self.assertEqual(self.client.delete(f'{self.URL}{pk}/').status_code, 404)
        self.assertEqual(self.client.get(self.URL).json()['projects'], [])

    def test_size_and_count_limits_and_bad_data(self):
        self.client.force_login(self.user)
        big = '{"x": "' + 'a' * (2 * 1024 * 1024) + '"}'
        self.assertEqual(self.post(data=big).status_code, 413)
        self.assertEqual(self.post(data='not json').status_code, 400)
        self.assertEqual(self.post(data='[1]').status_code, 400)
        for i in range(30):
            self.assertEqual(self.post(name=f'작품{i}').status_code, 201)
        res = self.post(name='31번째')
        self.assertEqual(res.status_code, 400)
        self.assertIn('30개', res.json()['error'])
