import tempfile
from pathlib import Path

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
