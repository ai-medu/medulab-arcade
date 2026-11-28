import json
from xml.etree import ElementTree

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from courses import coding_missions as content
from courses.models import Chapter, Item, LearningProgram, UserProgress

STEPS = {0: (0, -1), 90: (1, 0), 180: (0, 1), 270: (-1, 0)}


def walk(data):
    """지도 미션의 모범 풀이를 파이썬으로 따라가 본다. (도착했는가, 남은 보석 수)"""
    rows = data['spec']['map']
    cells = {(c, r): ch for r, row in enumerate(rows) for c, ch in enumerate(row) if ch not in '# '}
    pos = next(k for k, ch in cells.items() if ch == 'S')
    goal = next((k for k, ch in cells.items() if ch == 'G'), None)
    gems = {k for k, ch in cells.items() if ch == '*'}
    heading = [{'N': 0, 'E': 90, 'S': 180, 'W': 270}[data['spec'].get('dir', 'E')]]
    here = [pos]

    def ahead(turn=0):
        dc, dr = STEPS[(heading[0] + turn) % 360]
        return here[0][0] + dc, here[0][1] + dr

    def test(kind):
        if kind == 'gem':
            return here[0] in gems
        return ahead({'ahead': 0, 'left': -90, 'right': 90}[kind]) in cells

    def run(steps):
        for step in steps:
            if step == 'F':
                assert ahead() in cells, (data['title'], here[0], '벽에 부딪힘')
                here[0] = ahead()
            elif step in ('L', 'R'):
                heading[0] = (heading[0] + (-90 if step == 'L' else 90)) % 360
            elif step == 'C':
                assert here[0] in gems, (data['title'], here[0], '보석 없음')
                gems.remove(here[0])
            elif step[0] == 'repeat':
                for _ in range(step[1]):
                    run(step[2])
            elif step[0] == 'until':
                for _ in range(200):
                    if here[0] == goal:
                        break
                    run(step[1])
            elif step[0] == 'if':
                if test(step[1]):
                    run(step[2])
            elif step[0] == 'ifelse':
                run(step[2] if test(step[1]) else step[3])

    if data['spec']['type'] == 'keys':
        return None
    run(data['solution'])
    return goal is None or here[0] == goal, len(gems)


class MissionContentTests(TestCase):
    def test_every_map_solution_reaches_the_goal_with_all_gems(self):
        for chapter in content.CHAPTERS:
            for data in chapter['missions']:
                if data['spec']['type'] == 'maze':
                    self.assertEqual(walk(data), (True, 0), data['title'])

    def test_maps_fit_the_stage_and_solutions_are_valid_blocks(self):
        for number, chapter in enumerate(content.CHAPTERS, 1):
            for index, data in enumerate(chapter['missions'], 1):
                spec = data['spec']
                for row in spec.get('map', []):
                    self.assertLessEqual(len(row), 10, data['title'])
                self.assertLessEqual(len(spec.get('map', [])), 5, data['title'])
                xml, count = content.solution_xml(data)
                root = ElementTree.fromstring(xml)
                used = {el.get('type') for el in root.iter() if el.tag.endswith('block')}
                offered = {t.split(':')[0] for cat in spec['blocks'] for t in cat['types']}
                offered |= {'medu_when_flag_clicked'}
                if 'controls_if_else' in offered:
                    offered.add('controls_if')
                self.assertLessEqual(used, offered, f"{data['title']}: 도구상자에 없는 블록")
                self.assertLessEqual(set(spec.get('require', [])), used, data['title'])
                self.assertGreater(count, 0)
                if spec['type'] != 'keys':
                    self.assertEqual(content.mission_data(number, index)['spec']['par'], count)


class MissionPageTests(TestCase):
    def setUp(self):
        self.program = LearningProgram.objects.create(name='코딩기초')
        chapter = Chapter.objects.create(program=self.program, number=1, title='예전')
        self.old = Item.objects.create(chapter=chapter, number=1, key='codingbasics_01_01', title='예전 미로',
                                       item_type='block_coding', example_input='{"grid": []}')
        self.kid = User.objects.create_user('kid', password='x')
        profile = self.kid.profile
        profile.user_type, profile.is_approved, profile.onboarding_complete = 'medulab_member', True, True
        profile.save()
        UserProgress.objects.create(user=self.kid, item=self.old, code='3', completed=True)
        call_command('seed_coding_missions', verbosity=0)
        self.client.force_login(self.kid)

    def save(self, item, **body):
        return self.client.post(reverse('mission_save', args=[item.id]), json.dumps(body), content_type='application/json')

    def test_seed_keeps_old_items_and_records_and_can_run_twice(self):
        call_command('seed_coding_missions', verbosity=0)
        items = Item.objects.filter(chapter__program=self.program)
        self.assertEqual((items.count(), self.program.chapters.count()), (18, 6))
        item = items.get(key='codingbasics_01_01')
        self.assertEqual((item.id, item.title), (self.old.id, '첫걸음! 깃발까지 가기'))
        self.assertTrue(UserProgress.objects.get(user=self.kid, item=item).completed)

    def test_page_shows_mission_without_the_answer(self):
        res = self.client.get(reverse('item_page', args=[self.old.id]))
        self.assertTemplateUsed(res, 'learning_program/item_page_mission.html')
        self.assertContains(res, '/meducode/?mission=1')
        self.assertContains(res, '첫걸음! 깃발까지 가기')
        self.assertNotIn('solution', res.content.decode())
        self.assertEqual(res.context['page_data']['xml'], '')

    def test_best_stars_and_successful_blocks_are_kept(self):
        item = Item.objects.get(key='codingbasics_03_01')
        self.assertEqual(self.save(item, success=False, stars=0, xml='<a/>').status_code, 200)
        progress = UserProgress.objects.get(user=self.kid, item=item)
        self.assertFalse(progress.completed)
        self.assertEqual(self.client.get(reverse('item_page', args=[item.id])).context['page_data']['xml'], '<a/>')
        self.save(item, success=True, stars=3, xml='<good/>')
        self.save(item, success=True, stars=1, xml='<long/>')
        self.save(item, success=False, stars=0, xml='<broken/>')
        res = self.client.get(reverse('item_page', args=[item.id]))
        self.assertEqual((res.context['stars'], res.context['completed'], res.context['page_data']['xml']), (3, True, '<long/>'))
        cards = self.client.get(reverse('chapter_detail', args=[item.chapter_id]))
        self.assertContains(cards, '받은 별 3개')
        self.assertContains(cards, '받은 별 0개')

    def test_bad_requests_are_rejected(self):
        item = Item.objects.get(key='codingbasics_01_01')
        for body in ({'success': True, 'stars': 9, 'xml': ''}, {'success': 'yes', 'stars': 1}, {'success': True, 'stars': 1, 'xml': 'x' * 50000}):
            self.assertEqual(self.save(item, **body).status_code, 400, body.get('stars'))
        self.assertEqual(self.client.get(reverse('mission_save', args=[item.id])).status_code, 405)
        other = Item.objects.create(chapter=item.chapter, number=99, key='plain', title='보통')
        self.assertEqual(self.save(other, success=True, stars=3, xml='').status_code, 404)

    def test_guests_cannot_save(self):
        self.client.logout()
        res = self.save(Item.objects.get(key='codingbasics_01_02'), success=True, stars=3, xml='')
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(UserProgress.objects.filter(user=self.kid).count(), 1)
