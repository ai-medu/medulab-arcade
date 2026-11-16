import datetime
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from arcade.models import SpecialLectureParticipant, SpecialLectureReservation
from arcade.special_lecture import grant_welcome_coupon
from arcade.test_special_lecture import make_lecture, make_member

SOLAPI = dict(SOLAPI_API_KEY='k', SOLAPI_API_SECRET='s', SOLAPI_PF_ID='pf', SOLAPI_SENDER='01000000000',
              SOLAPI_TEMPLATE_SPECIAL='KA01TP-special')


class NotificationTests(TestCase):
    def setUp(self):
        self.lecture = make_lecture(end_time=datetime.time(14, 30), location='메듀랩 5층')
        self.apply_url = reverse('special_lecture_apply', args=[self.lecture.pk])
        self.guest = {'p_name': '김학생', 'p_school': '한빛초', 'p_grade': '4학년', 'p_birth': '2016.03.15', 'applicant_name': '김보호', 'phone': '010-1234-5678'}

    def _inline(self):
        return mock.patch('arcade.special_lecture._spawn', side_effect=lambda fn, *a: fn(*a))

    def _coupon_user(self, name):
        user = make_member(name)
        grant_welcome_coupon(user)
        self.client.force_login(user)

    @override_settings(**SOLAPI)
    def test_free_reservation_sends_alimtalk(self):
        self._coupon_user('notifyuser')
        with self._inline(), mock.patch('arcade.special_lecture._post_alimtalk', return_value=(True, '')) as post:
            self.client.post(self.apply_url, dict(self.guest, use_coupon='1'))
        phone, template, variables = post.call_args[0][:3]
        self.assertEqual((phone, template), ('01012345678', 'KA01TP-special'))
        self.assertEqual(variables['#{특강명}'], 'AI 특강')
        self.assertTrue(variables['#{일시}'].endswith('~14:30'))
        self.assertEqual(variables['#{결제금액}'], '무료')
        self.assertIsNotNone(SpecialLectureReservation.objects.get().notified_at)

    def test_without_template_records_reason_and_booking_still_confirmed(self):
        self._coupon_user('notifyuser2')
        with self._inline():
            self.client.post(self.apply_url, dict(self.guest, use_coupon='1'))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual(reservation.status, 'confirmed')
        self.assertIsNone(reservation.notified_at)
        self.assertIn('미완료', reservation.notify_detail)

    @override_settings(PORTONE_API_SECRET='secret', **SOLAPI)
    def test_paid_reservation_sends_alimtalk_once(self):
        reservation = SpecialLectureReservation.objects.create(
            lecture=self.lecture, applicant_name='김보호', phone='01012345678', amount=20000)
        SpecialLectureParticipant.objects.create(reservation=reservation, name='김학생', price=20000)

        class Resp:
            status_code = 200

            def json(self_inner):
                return {'status': 'PAID', 'amount': {'total': 20000}, 'method': {'type': 'PaymentMethodCard'}}

        with self._inline(), mock.patch('requests.get', return_value=Resp()), \
                mock.patch('arcade.special_lecture._post_alimtalk', return_value=(True, '')) as post:
            self.client.post(reverse('special_verify', args=[reservation.token]))
            self.client.post(reverse('special_verify', args=[reservation.token]))
        self.assertEqual(post.call_count, 1)

    @override_settings(**SOLAPI)
    def test_failed_send_is_recorded_not_raised(self):
        self._coupon_user('notifyuser3')
        with self._inline(), mock.patch('arcade.special_lecture._post_alimtalk', return_value=(False, 'HTTP 400: bad')):
            self.client.post(self.apply_url, dict(self.guest, use_coupon='1'))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual(reservation.status, 'confirmed')
        self.assertIsNone(reservation.notified_at)
        self.assertEqual(reservation.notify_detail, 'HTTP 400: bad')


class AdminUITests(TestCase):
    def setUp(self):
        self.lecture = make_lecture(end_time=datetime.time(14, 30), location='메듀랩 5층')

    def _staff(self, name):
        admin = make_member(name)
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)

    def test_staff_sees_manage_buttons_on_public_pages_and_others_do_not(self):
        res = self.client.get(reverse('special_lecture_list'))
        self.assertNotContains(res, '+ 특강 추가')
        self.assertNotContains(res, reverse('special_admin_delete', args=[self.lecture.pk]))
        self._staff('adm41')
        res = self.client.get(reverse('special_lecture_list'))
        for text in ('+ 특강 추가', reverse('special_admin_edit', args=[self.lecture.pk]),
                     reverse('special_admin_delete', args=[self.lecture.pk])):
            self.assertContains(res, text)
        res = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        self.assertContains(res, '✏️ 수정')
        self.assertContains(res, '🗑 삭제')
        self.assertContains(res, '수업 내용이 비어 있어요')

    def test_delete_from_public_page_returns_to_list(self):
        self._staff('adm42')
        res = self.client.post(reverse('special_admin_delete', args=[self.lecture.pk]), {'next': 'public'})
        self.assertRedirects(res, reverse('special_lecture_list'), fetch_redirect_response=False)

    def test_content_section_and_three_column_grid(self):
        self.lecture.description = '이런 수업이에요'
        self.lecture.save()
        res = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        self.assertContains(res, '📖 수업 내용')
        self.assertContains(res, '이런 수업이에요')
        self.assertContains(self.client.get(reverse('special_lecture_list')), 'repeat(3, 1fr)')
        self.assertContains(self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk])), 'special_check_friend'.replace('special_check_friend', '/special/check-friend/'))
