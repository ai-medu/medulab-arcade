from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from arcade.models import ConsultInquiry


class ConsultPageTests(TestCase):
    def test_parent_comes_first_and_is_default(self):
        html = self.client.get(reverse('consult_inquiry')).content.decode()
        self.assertLess(html.index('👨‍👩‍👧 학부모'), html.index('🙋 본인'))
        self.assertIn('value="parent" checked', html)

    def test_extra_fields_are_offered(self):
        res = self.client.get(reverse('consult_inquiry'))
        for text in ('관심 있는 수업', '희망 수업 요일', '희망 시간대', '코딩·로봇 경험', '희망 상담 방식', '알게 된 경로', '주소 검색',
                     '파이썬 코딩', 'name="preferred_days"'):
            self.assertContains(res, text)

    def test_submit_saves_extra_info_and_ignores_junk_values(self):
        with mock.patch('arcade.kakao_notify.send_kakao_memo_to_me') as memo:
            res = self.client.post(reverse('consult_inquiry'), {
                'applicant_type': 'parent', 'child_name[]': ['하은'], 'child_age[]': ['초4'],
                'phone_number': '010-5794-6461', 'address': '광주 서구 화개중앙로 51',
                'interest_areas': ['로봇 코딩', 'AICE 자격증', '엉뚱한값'],
                'preferred_days': ['월', '수', '일요일아님'],
                'preferred_time': '저녁', 'experience': '처음이에요', 'consult_method': '방문 상담',
                'referral_source': '네이버 검색', 'message': '난이도, 수업내용',
            }, follow=True)
        self.assertContains(res, '상담 문의가 접수되었습니다')
        i = ConsultInquiry.objects.get()
        self.assertEqual(i.address, '광주 서구 화개중앙로 51')
        self.assertEqual(i.interest_areas, '로봇 코딩, AICE 자격증')
        self.assertEqual(i.preferred_days, '월, 수')
        self.assertEqual((i.preferred_time, i.experience, i.consult_method, i.referral_source),
                         ('저녁', '처음이에요', '방문 상담', '네이버 검색'))
        text = memo.call_args.args[0]
        self.assertIn('관심 수업: 로봇 코딩, AICE 자격증', text)
        self.assertIn('희망 시간: 월, 수요일 저녁', text)
        self.assertIn('주소: 광주 서구 화개중앙로 51', text)

    def test_extra_fields_are_optional_and_bad_choice_rejected(self):
        res = self.client.post(reverse('consult_inquiry'), {
            'applicant_type': 'self', 'name': '철수', 'phone_number': '01012345678'})
        self.assertEqual(res.status_code, 302)
        res = self.client.post(reverse('consult_inquiry'), {
            'applicant_type': 'self', 'name': '철수', 'phone_number': '01012345678', 'preferred_time': '새벽'})
        self.assertEqual(res.status_code, 200)   # 목록에 없는 값은 받지 않는다


class ConsultAdminTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)
        self.i = ConsultInquiry.objects.create(
            applicant_type='parent', name='손하은 학부모', phone_number='01057946461',
            children_info=[{'name': '손하은', 'age': '초4'}], message='난이도, 수업내용, 수업방식, 비용',
            address='광주 서구 화개중앙로 51', interest_areas='로봇 코딩', preferred_days='월, 수', preferred_time='저녁')

    def test_list_is_clean_and_has_detail_modal_data(self):
        page = self.client.get(reverse('consult_inquiry_admin_list'))
        self.assertContains(page, 'id="inqOverlay"')
        self.assertContains(page, f'openInquiry({self.i.pk})')
        self.assertContains(page, '🎯 로봇 코딩')
        self.assertContains(page, '📅 월, 수')
        data = page.context['inquiries_json'][0]
        self.assertEqual((data['address'], data['children'], data['days']), ('광주 서구 화개중앙로 51', '손하은(초4)', '월, 수'))

    def test_toggle_still_works(self):
        self.client.post(reverse('consult_inquiry_toggle_handled', args=[self.i.pk]))
        self.i.refresh_from_db()
        self.assertTrue(self.i.is_handled)
