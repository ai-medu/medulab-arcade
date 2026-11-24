from django.test import TestCase
from django.urls import reverse

from arcade.models import NavItem


class AiceInfoTests(TestCase):
    def test_page_shows_roadmap_and_every_certificate(self):
        res = self.client.get(reverse('aice_info'))
        self.assertEqual(res.status_code, 200)
        for text in ('FUTURE 3급', 'FUTURE 2급', 'FUTURE 1급', 'JUNIOR', 'BASIC', 'GENERATIVE 2급', 'ASSOCIATE', 'PROFESSIONAL',
                     '출제범위', '₩ 30,000원', '₩ 120,000원', 'https://aice.study/info/aice/asso', '민간자격'):
            self.assertContains(res, text)

    def test_menu_has_curriculum_roadmap_first_and_aice_second(self):
        # 마이그레이션이 만든 클래스 메뉴 순서
        names = list(NavItem.objects.filter(section='learning').order_by('order', 'id').values_list('name', flat=True))
        self.assertEqual(names[:2], ['커리큘럼 로드맵', 'AICE 과정 안내'])
        self.assertEqual(NavItem.objects.get(name='AICE 과정 안내').url_name, 'aice_info')


class WorksGalleryMenuTests(TestCase):
    def test_gallery_moved_from_class_menu_to_bottom_of_play_menu(self):
        self.assertFalse(NavItem.objects.filter(url_name='works_gallery').exists())
        html = self.client.get(reverse('aice_info')).content.decode()
        play = html[html.index('🎮 플레이'):html.index('🏫 클래스')]
        self.assertIn('🎨 플레이존', play)
        self.assertLess(play.index('🧩 메듀코드'), play.index('🎨 플레이존'))
        self.assertNotIn('학생 작품 갤러리', html[html.index('🏫 클래스'):html.index('🏫 클래스') + 1500])


class FinderMenuTests(TestCase):
    def test_finder_renamed_and_third(self):
        names = list(NavItem.objects.filter(section='learning').order_by('order', 'id').values_list('name', flat=True))
        self.assertEqual(names[:3], ['커리큘럼 로드맵', 'AICE 과정 안내', '내게 맞는 수업'])


class PlayPageBackLinkTests(TestCase):
    def test_back_button_goes_to_playzone_list(self):
        from django.contrib.auth.models import User
        from arcade.models import Project
        author = User.objects.create_user('maker', password='x')
        Project.objects.create(title='테스트게임', author=author, author_display_name='학생', description='d',
                               status='approved', external_url='https://example.com/game')
        res = self.client.get(reverse('play', args=['테스트게임']))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f'<a href="{reverse("works_gallery")}" class="back-btn">')
