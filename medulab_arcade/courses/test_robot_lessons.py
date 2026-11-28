import json
import os
import shutil
import tempfile
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Chapter, Item, LearningProgram, UserProgress
from .robot_lessons.ollo_lv1 import LESSONS
from .robot_lessons.ollo_lv1_kids import ART
from .robot_lessons.ollo_lv2 import ART as LV2_ART, LESSONS as LV2


class RobotLessonTests(TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)
        override = override_settings(ROBOT_LESSON_DIR=self.dir)
        override.enable()
        self.addCleanup(override.disable)

        self.program = LearningProgram.objects.create(name='로봇코딩과정 로보티즈 올로AI')
        self.chapter = Chapter.objects.create(program=self.program, number=1, title='제1장 Lv1')
        Chapter.objects.create(program=self.program, number=2, title='제2장 Lv2', content='선생님이 쓴 설명')
        for n, lesson in enumerate(LESSONS, 1):
            Item.objects.create(chapter=self.chapter, number=n, key=lesson['key'], title=lesson['topic'], item_type='project')
        call_command('seed_ollo_lv1', stdout=StringIO())
        self.item = Item.objects.get(key='lv1_01')
        folder = os.path.join(self.dir, 'lv1_01')
        os.makedirs(folder)
        for name in ('thumb.jpg', 'guide.jpg', 'code.svg', 'build-01.jpg', 'build-02.jpg', 'ext-01.jpg', 'word-01.jpg'):
            with open(os.path.join(folder, name), 'wb') as f:
                f.write(b'x')

        self.member = User.objects.create_user('member', password='x')
        profile = self.member.profile
        profile.user_type, profile.is_approved = 'medulab_member', True
        profile.save()
        self.outsider = User.objects.create_user('outsider', password='x')

    def _asset(self, name):
        return self.client.get(reverse('robot_asset', args=[self.item.id, name]))

    def _post(self, url_name, body):
        return self.client.post(reverse(url_name, args=[self.item.id]), json.dumps(body), content_type='application/json')

    def test_lesson_data_is_well_formed(self):
        self.assertEqual(len(LESSONS), 12)
        with open(os.path.join(os.path.dirname(__file__), 'templates', 'learning_program', '_robot_games.html'), encoding='utf-8') as f:
            games = f.read()
        for lesson in LESSONS:
            self.assertEqual(len(lesson['quiz']), 5, lesson['key'])
            for q in lesson['quiz']:
                self.assertEqual(len(q['choices']), 4, q['q'])
                self.assertIn(q['answer'], range(4), q['q'])
            self.assertEqual([m['id'] for m in lesson['missions']], ['m1', 'm2', 'm3'])
            number = int(lesson['key'][-2:])
            self.assertEqual(lesson['code']['start'], None if number == 1 else number)   # 활은 직접 만드는 과녁 코드
            code = os.path.join(os.path.dirname(__file__), 'robot_lessons', 'ollo_lv1_code', f'code{number:02d}.svg')
            self.assertTrue(os.path.isfile(code), code)
            self.assertTrue(lesson['easy'] and lesson['school'], lesson['key'])
            self.assertIn(f"{lesson['play']['id']}: function", games)
            for term, desc, pic in lesson['words']:
                kind = pic.split(':')[0]
                self.assertIn(kind, ('crop', 'svg', 'thumb'), term)
                if kind == 'svg':
                    self.assertIn(pic[4:], ART, term)

    def test_seed_fills_only_empty_chapter_text(self):
        res = self.client.get(reverse('course_home', args=[self.program.id]))
        self.assertContains(res, '트리케라톱스')          # 1장 설명 전체가 잘리지 않고 보인다
        self.assertContains(res, '선생님이 쓴 설명')
        call_command('seed_ollo_lv1', '--force', stdout=StringIO())
        self.assertNotContains(self.client.get(reverse('course_home', args=[self.program.id])), '선생님이 쓴 설명')

    def test_chapter_lists_robot_cards(self):
        res = self.client.get(reverse('chapter_detail', args=[self.chapter.id]))
        self.assertContains(res, '1. 활')
        self.assertContains(res, reverse('robot_asset', args=[self.item.id, 'thumb.jpg']))

    def test_only_thumbnail_is_public(self):
        self.assertEqual(self._asset('thumb.jpg').status_code, 200)
        self.assertEqual(self._asset('build-01.jpg').status_code, 302)
        self.client.force_login(self.outsider)
        self.assertEqual(self._asset('build-01.jpg').status_code, 302)
        self.client.force_login(self.member)
        res = self._asset('build-01.jpg')
        self.assertEqual((res.status_code, res['Content-Type']), (200, 'image/jpeg'))
        self.assertIn('private', res['Cache-Control'])
        self.assertEqual(self._asset('code.svg')['Content-Type'], 'image/svg+xml')
        for bad in ('build-99.jpg', '..', 'secret.txt'):
            self.assertEqual(self._asset(bad).status_code, 404, bad)

    def test_lesson_page_shows_four_steps_without_answers(self):
        self.assertEqual(self.client.get(reverse('item_page', args=[self.item.id])).status_code, 302)
        self.client.force_login(self.member)
        res = self.client.get(reverse('item_page', args=[self.item.id]))
        self.assertTemplateUsed(res, 'learning_program/item_page_robot.html')
        for text in ('로봇 제작', '로봇 코딩', '미션 퀘스트', 'data-src="/meducode/"', 'build-02.jpg', 'ext-01.jpg',
                     '교과 연계', 'data-game="bow"', 'word-01.jpg', 'word-06.jpg', '전체화면 보기', '② 움직이는 과녁 만들기'):
            self.assertContains(res, text)
        self.assertNotContains(res, '교재 원본')
        self.assertNotContains(res, '시작 버튼 None')
        self.assertEqual(len(res.context['build_pages']), 3)      # 활 2쪽 + 과녁 1쪽 (시험용)
        self.assertEqual(res.context['ext_pages'], [])
        self.assertNotContains(res, LESSONS[0]['quiz'][0]['explain'])
        self.assertNotIn('answer', res.context['quiz'][0])

    def test_level2_lessons_are_well_formed_and_seeded(self):
        with open(os.path.join(os.path.dirname(__file__), 'templates', 'learning_program', '_robot_games.html'), encoding='utf-8') as f:
            games = f.read()
        code_dir = os.path.join(os.path.dirname(__file__), 'robot_lessons', 'ollo_lv2_code')
        self.assertEqual([x['key'] for x in LV2], [f'lv2_{n:02d}' for n in range(1, 13)])
        for number, lesson in enumerate(LV2, 1):
            self.assertEqual(len(lesson['quiz']), 5, lesson['key'])
            for q in lesson['quiz']:
                self.assertEqual(len(set(q['choices'])), 4, q['q'])
                self.assertIn(q['answer'], range(4), q['q'])
            self.assertEqual([m['id'] for m in lesson['missions']], ['m1', 'm2', 'm3'])
            self.assertEqual(lesson['code']['start'], number)
            self.assertTrue(os.path.isfile(os.path.join(code_dir, f'code{number:02d}.svg')))
            self.assertTrue(lesson['easy'] and lesson['school'] and lesson['game']['rules'], lesson['key'])
            self.assertTrue(f"{lesson['play']['id']}: function" in games, lesson['play']['id'])
            for term, desc, pic in lesson['words']:
                self.assertIn(pic.split(':')[0], ('crop', 'svg', 'thumb'), term)
                if pic.startswith('svg:'):
                    self.assertIn(pic[4:], LV2_ART, term)
        self.assertTrue(os.path.isfile(os.path.join(code_dir, 'code-drive.svg')))

        second = self.program.chapters.get(number=2)
        second.content = ''
        second.save()
        for n, lesson in enumerate(LV2, 1):
            Item.objects.create(chapter=second, number=n, key=lesson['key'], title=lesson['topic'], item_type='project')
        call_command('seed_ollo_lv2', stdout=StringIO())
        second.refresh_from_db()
        self.assertIn('도미노 로봇', second.content)
        item = Item.objects.get(key='lv2_01')
        self.client.force_login(self.member)
        res = self.client.get(reverse('item_page', args=[item.id]))
        for text in ('data-game="motor"', '예제 → 올로AI 2단계 코딩', '로봇이동 함수 보기', '숫자 버튼 1번'):
            self.assertContains(res, text)
        self.assertNotContains(res, '시작 버튼 1번</b>')

    def test_changed_picture_gets_a_new_address(self):
        self.client.force_login(self.member)
        path = os.path.join(self.dir, 'lv1_01', 'code.svg')
        page = reverse('item_page', args=[self.item.id])
        os.utime(path, (1000, 1000))
        self.assertContains(self.client.get(page), 'code.svg?v=1000')
        os.utime(path, (2000, 2000))
        self.assertContains(self.client.get(page), 'code.svg?v=2000')

    def test_quiz_grading_completes_at_80(self):
        self.client.force_login(self.member)
        right = [q['answer'] for q in LESSONS[0]['quiz']]
        low = [right[0]] + [(a + 1) % 4 for a in right[1:]]
        res = self._post('robot_quiz', {'answers': low}).json()
        self.assertEqual((res['percent'], res['passed']), (20, False))
        self.assertFalse(UserProgress.objects.get(user=self.member, item=self.item).completed)
        res = self._post('robot_quiz', {'answers': right[:4] + [(right[4] + 1) % 4]}).json()
        self.assertEqual((res['percent'], res['passed']), (80, True))
        self._post('robot_quiz', {'answers': low})          # 다시 낮게 받아도 완료와 최고 점수는 남는다
        progress = UserProgress.objects.get(user=self.member, item=self.item)
        self.assertEqual((progress.completed, progress.score), (True, 80))
        for bad in ([0], None, ['0'] * 5):
            self.assertEqual(self._post('robot_quiz', {'answers': bad}).status_code, 400)

    def test_mission_check_is_saved_and_kept_with_quiz(self):
        self.client.force_login(self.member)
        self._post('robot_quiz', {'answers': [q['answer'] for q in LESSONS[0]['quiz']]})
        self.assertEqual(self._post('robot_mission', {'id': 'm2', 'done': True}).json()['missions'], ['m2'])
        state = json.loads(UserProgress.objects.get(user=self.member, item=self.item).code)
        self.assertEqual(state, {'quiz_best': 100, 'missions': ['m2']})
        self.assertEqual(self._post('robot_mission', {'id': 'm2', 'done': False}).json()['missions'], [])
        self.assertEqual(self._post('robot_mission', {'id': 'zz', 'done': True}).status_code, 400)

    def test_outsider_cannot_submit(self):
        self.client.force_login(self.outsider)
        self.assertEqual(self._post('robot_mission', {'id': 'm1', 'done': True}).status_code, 302)
        self.assertFalse(UserProgress.objects.exists())
