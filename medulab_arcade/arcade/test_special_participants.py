import datetime

from unittest import mock

from django.test import TestCase
from django.urls import reverse

from arcade.models import SpecialLectureReservation
from arcade.special_lecture import parse_birth_date
from arcade.test_special_lecture import apply_extras, make_lecture, make_member


class BirthDateParsingTests(TestCase):
    def test_formats(self):
        for raw in ('2016.03.15', '2016-03-15', '20160315', '2016/03/15', ' 2016.03.15 '):
            self.assertEqual(parse_birth_date(raw), datetime.date(2016, 3, 15))

    def test_invalid_values(self):
        for raw in ('', '2016.13.01', '2999.01.01', '1800.01.01', 'abc', '2016.02.31'):
            self.assertIsNone(parse_birth_date(raw))


class ParticipantFieldsTests(TestCase):
    def setUp(self):
        patcher = mock.patch('arcade.special_lecture._spawn')   # 알림 스레드가 테스트 DB를 건드리지 않게
        patcher.start()
        self.addCleanup(patcher.stop)
        self.lecture = make_lecture()
        self.url = reverse('special_lecture_apply', args=[self.lecture.pk])
        self.base = {'applicant_name': '김보호', 'phone': '01012345678', 'p_name': '김학생', 'p_school': '한빛초',
                     'p_grade': '4학년', 'p_birth': '2016.03.15', **apply_extras()}

    def test_detail_shows_four_input_fields(self):
        res = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        for name in ('p_name', 'p_school', 'p_grade', 'p_birth'):
            self.assertContains(res, f'name="{name}"')
        for label in ('이름', '학교', '학년', '생년월일'):
            self.assertContains(res, f'<span>{label}</span>')

    def test_saves_all_four_fields(self):
        self.client.post(self.url, self.base)
        person = SpecialLectureReservation.objects.get().participants.get()
        self.assertEqual((person.name, person.school, person.grade, person.birth_date),
                         ('김학생', '한빛초', '4학년', datetime.date(2016, 3, 15)))

    def test_each_missing_field_is_rejected_with_its_name(self):
        for key, label in (('p_name', '이름'), ('p_school', '학교'), ('p_grade', '학년'), ('p_birth', '생년월일')):
            res = self.client.post(self.url, dict(self.base, **{key: ''}), follow=True)
            self.assertFalse(SpecialLectureReservation.objects.exists(), key)
            self.assertContains(res, label)

    def test_bad_birth_date_rejected(self):
        res = self.client.post(self.url, dict(self.base, p_birth='2016.99.99'), follow=True)
        self.assertFalse(SpecialLectureReservation.objects.exists())
        self.assertContains(res, '생년월일 형식이 올바르지 않아요')

    def test_form_values_are_kept_after_error(self):
        res = self.client.post(self.url, dict(self.base, p_birth='x'), follow=True)
        self.assertContains(res, 'value="한빛초"')
        self.assertContains(res, 'value="4학년"')

    def test_friend_rows_need_all_four_fields_but_empty_rows_are_ignored(self):
        self.client.post(self.url, dict(self.base, f_name=['친구', ''], f_school=['한빛초', ''], f_grade=['', ''], f_birth=['2016.05.05', '']))
        self.assertFalse(SpecialLectureReservation.objects.exists())   # 친구 학년 누락
        self.client.post(self.url, dict(self.base, f_name=['친구', ''], f_school=['한빛초', ''], f_grade=['4학년', ''], f_birth=['2016.05.05', '']))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual(reservation.participants.count(), 2)
        self.assertEqual(reservation.amount, 20000)

    def test_medulab_parent_children_keep_known_info(self):
        parent = make_member('mp70', 'medulab_parent')
        parent.profile.children_info = [{'name': '정해준', 'birth_date': '20130903', 'school': '해솔초', 'grade': '5학년'}]
        parent.profile.save()
        self.client.force_login(parent)
        page = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        self.assertContains(page, '해솔초 5학년')
        self.client.post(self.url, {'applicant_name': '학부모', 'phone': '01099998888', 'child': ['i0'], **apply_extras()})
        person = SpecialLectureReservation.objects.get().participants.get()
        self.assertEqual((person.school, person.grade, person.birth_date), ('해솔초', '5학년', datetime.date(2013, 9, 3)))

    def test_admin_list_and_reservation_page_show_details(self):
        self.client.post(self.url, self.base)
        reservation = SpecialLectureReservation.objects.get()
        page = self.client.get(reverse('special_reservation', args=[reservation.token]))
        self.assertContains(page, '2016.03.15')
        self.assertContains(page, '한빛초 4학년')
        admin = make_member('adm70')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        res = self.client.get(f"{reverse('special_admin_list')}?lecture={self.lecture.pk}")
        self.assertContains(res, '한빛초 4학년 · 2016.03.15')
        self.assertContains(res, reverse('special_lecture_list'))
        self.assertContains(res, '특강 목록 화면 보기')
