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
