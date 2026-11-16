import csv
import datetime
import io
import time
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail, signing
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from arcade.models import (
    SpecialLecture, SpecialLectureCoupon, SpecialLectureParticipant, SpecialLectureReservation,
)
from arcade.special_lecture import _alimtalk_variables, _send_admin_mail, send_reminders
from arcade.test_special_lecture import apply_extras, make_lecture, make_member

SOLAPI = dict(SOLAPI_API_KEY='k', SOLAPI_API_SECRET='s', SOLAPI_PF_ID='pf', SOLAPI_SENDER='01000000000',
              SOLAPI_TEMPLATE_SPECIAL='T1', SOLAPI_TEMPLATE_SPECIAL_REMINDER='T2')


def student(**kw):
    data = {'p_name': '김학생', 'p_school': '한빛초', 'p_grade': '4학년', 'p_birth': '2016.03.15',
            'applicant_name': '김보호', 'phone': '010-1234-5678'}
    data.update(kw)
    return data


class Base(TestCase):
    def setUp(self):
        patcher = mock.patch('arcade.special_lecture._spawn')   # 알림 스레드가 테스트 DB를 건드리지 않게
        self.spawn = patcher.start()
        self.addCleanup(patcher.stop)
        self.lecture = make_lecture()
        self.url = reverse('special_lecture_apply', args=[self.lecture.pk])

    def post(self, **kw):
        return self.client.post(self.url, dict(student(), **apply_extras(), **kw))

    def staff(self, name='opsadmin'):
        admin = make_member(name)
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        return admin

    def reservation(self, lecture=None, status='confirmed', amount=20000, paid=True, **kw):
        res = SpecialLectureReservation.objects.create(
            lecture=lecture or self.lecture, applicant_name='김보호', phone='01012345678', amount=amount, status=status,
            paid_at=timezone.now() if paid else None, **kw)
        SpecialLectureParticipant.objects.create(reservation=res, name='김학생', school='한빛초', grade='4학년',
                                                 birth_date=datetime.date(2016, 3, 15), price=amount)
        return res


class PrivacyAndSpamTests(Base):
    def test_privacy_consent_required_and_recorded(self):
        data = dict(student(), **apply_extras())
        del data['privacy']
        res = self.client.post(self.url, data, follow=True)
        self.assertFalse(SpecialLectureReservation.objects.exists())
        self.assertContains(res, '개인정보 수집·이용에 동의해 주세요')
        self.post()
        self.assertIsNotNone(SpecialLectureReservation.objects.get().privacy_agreed_at)

    def test_detail_shows_consent_and_hidden_guards(self):
        res = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        for text in ('name="privacy"', '개인정보 수집·이용에 동의합니다', 'name="website"', 'name="form_token"', '법정대리인'):
            self.assertContains(res, text)

    def test_honeypot_blocks(self):
        self.post(website='http://spam.example')
        self.assertFalse(SpecialLectureReservation.objects.exists())

    def test_missing_or_fake_token_blocks(self):
        for token in ('', 'garbage'):
            self.client.post(self.url, dict(student(), **dict(apply_extras(), form_token=token)))
        self.assertFalse(SpecialLectureReservation.objects.exists())

    def test_too_fast_submission_blocks(self):
        fresh = signing.dumps(int(time.time()), salt='special-form')
        self.client.post(self.url, dict(student(), **dict(apply_extras(), form_token=fresh)))
        self.assertFalse(SpecialLectureReservation.objects.exists())

    def test_rate_limit_per_ip(self):
        for i in range(8):
            self.client.post(self.url, dict(student(p_name=f'학생{i}'), **apply_extras()))
        self.assertEqual(SpecialLectureReservation.objects.count(), 8)
        self.client.post(self.url, dict(student(p_name='아홉째'), **apply_extras()))
        self.assertEqual(SpecialLectureReservation.objects.count(), 8)


class DuplicateTests(Base):
    def test_same_student_cannot_apply_twice(self):
        self.post()
        res = self.client.post(self.url, dict(student(), **apply_extras()), follow=True)
        self.assertEqual(SpecialLectureReservation.objects.count(), 1)
        self.assertContains(res, '이미 신청된 학생이에요')

    def test_same_name_different_birth_is_allowed(self):
        self.post()
        self.client.post(self.url, dict(student(p_birth='2015.01.01'), **apply_extras()))
        self.assertEqual(SpecialLectureReservation.objects.count(), 2)

    def test_canceled_or_expired_pending_do_not_block(self):
        res = self.reservation(status='canceled')
        self.post()
        self.assertEqual(SpecialLectureReservation.objects.exclude(pk=res.pk).count(), 1)
        SpecialLectureReservation.objects.exclude(pk=res.pk).delete()
        old = self.reservation(status='pending', paid=False)
        SpecialLectureReservation.objects.filter(pk=old.pk).update(created_at=timezone.now() - datetime.timedelta(hours=1))
        self.post()
        self.assertEqual(SpecialLectureReservation.objects.filter(status='pending').count(), 2)


class WaitlistTests(Base):
    def setUp(self):
        super().setUp()
        self.lecture = make_lecture(title='소규모', capacity=1)
        self.url = reverse('special_lecture_apply', args=[self.lecture.pk])
        self.reservation(status='confirmed', amount=20000)

    def test_full_lecture_shows_waitlist_ui_and_badge(self):
        detail = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        self.assertContains(detail, '대기 신청하기')
        self.assertContains(detail, '정원이 모두 찼어요')
        self.assertContains(self.client.get(reverse('special_lecture_list')), '대기 신청 가능')

    def test_waitlist_application_does_not_take_a_seat(self):
        res = self.post(p_name='대기학생', p_birth='2015.05.05')
        waiting = SpecialLectureReservation.objects.get(status='waitlist')
        self.assertRedirects(res, reverse('special_reservation', args=[waiting.token]), fetch_redirect_response=False)
        self.assertEqual(self.lecture.seats_taken(), 1)
        self.assertContains(self.client.get(reverse('special_reservation', args=[waiting.token])), '대기 신청이 접수되었어요')
        self.assertTrue(any(c.args[0].__name__ == '_send_admin_mail' for c in self.spawn.call_args_list))

    def test_admin_promote_paid_waitlist_gives_pay_link_and_blocks_when_full(self):
        self.post(p_name='대기학생', p_birth='2015.05.05')
        waiting = SpecialLectureReservation.objects.get(status='waitlist')
        self.staff()
        res = self.client.post(reverse('special_admin_promote', args=[waiting.pk]), follow=True)
        waiting.refresh_from_db()
        self.assertEqual(waiting.status, 'waitlist')   # 자리가 없어서 승인 불가
        self.assertContains(res, '남은 자리가 0자리')
        SpecialLectureReservation.objects.filter(status='confirmed').update(status='canceled')
        res = self.client.post(reverse('special_admin_promote', args=[waiting.pk]), follow=True)
        waiting.refresh_from_db()
        self.assertEqual(waiting.status, 'pending')
        self.assertContains(res, f'/special/r/{waiting.token}/pay/')

    def test_admin_promote_free_waitlist_confirms(self):
        waiting = self.reservation(status='waitlist', amount=0, paid=False)
        SpecialLectureReservation.objects.filter(status='confirmed', amount=20000).update(status='canceled')
        self.staff()
        self.client.post(reverse('special_admin_promote', args=[waiting.pk]))
        waiting.refresh_from_db()
        self.assertEqual(waiting.status, 'confirmed')


@override_settings(PORTONE_API_SECRET='secret', PORTONE_STORE_ID='store')
class RefundAndCapacityTests(Base):
    def setUp(self):
        super().setUp()
        self.staff()

    def _cancel_api(self, status=200, text='{}'):
        class Resp:
            pass
        resp = Resp()
        resp.status_code, resp.text = status, text
        return mock.patch('requests.post', return_value=resp)

    def test_cancel_refunds_paid_reservation(self):
        res = self.reservation()
        with self._cancel_api() as post:
            self.client.post(reverse('special_admin_cancel', args=[res.pk]))
        res.refresh_from_db()
        self.assertEqual((res.status, bool(res.refunded_at)), ('canceled', True))
        self.assertIn(res.portone_payment_id, post.call_args[0][0])
        self.assertTrue(post.call_args[0][0].endswith('/cancel'))

    def test_refund_failure_keeps_reservation_active(self):
        res = self.reservation()
        with self._cancel_api(500, 'boom'):
            response = self.client.post(reverse('special_admin_cancel', args=[res.pk]), follow=True)
        res.refresh_from_db()
        self.assertEqual(res.status, 'confirmed')
        self.assertContains(response, '환불에 실패해서 취소하지 않았어요')

    def test_skip_refund_cancels_without_calling_gateway(self):
        res = self.reservation()
        with self._cancel_api() as post:
            self.client.post(reverse('special_admin_cancel', args=[res.pk]), {'skip_refund': '1'})
        post.assert_not_called()
        res.refresh_from_db()
        self.assertEqual(res.status, 'canceled')

    def test_free_reservation_cancel_needs_no_refund(self):
        res = self.reservation(amount=0)
        with self._cancel_api() as post:
            self.client.post(reverse('special_admin_cancel', args=[res.pk]))
        post.assert_not_called()

    def _paid(self, total):
        class Resp:
            status_code = 200

            def json(self_inner):
                return {'status': 'PAID', 'amount': {'total': total}, 'method': {'type': 'PaymentMethodCard'}}
        return mock.patch('requests.get', return_value=Resp())

    def test_payment_after_capacity_filled_is_auto_refunded(self):
        lecture = make_lecture(title='만석', capacity=1)
        self.reservation(lecture=lecture, status='confirmed')
        late = self.reservation(lecture=lecture, status='pending', paid=False)
        SpecialLectureParticipant.objects.filter(reservation=late).update(name='늦은학생')
        with self._paid(20000), self._cancel_api():
            res = self.client.post(reverse('special_verify', args=[late.token]))
        self.assertEqual(res.status_code, 409)
        self.assertIn('자동으로 취소', res.json()['error'])
        late.refresh_from_db()
        self.assertEqual(late.status, 'canceled')
        self.assertTrue(late.refunded_at)

    def test_auto_refund_failure_leaves_note_for_admin(self):
        lecture = make_lecture(title='만석2', capacity=1)
        self.reservation(lecture=lecture, status='confirmed')
        late = self.reservation(lecture=lecture, status='pending', paid=False)
        with self._paid(20000), self._cancel_api(500, 'boom'):
            res = self.client.post(reverse('special_verify', args=[late.token]))
        self.assertEqual(res.status_code, 409)
        late.refresh_from_db()
        self.assertEqual(late.status, 'pending')
        self.assertIn('환불 필요', late.memo)

    def test_payment_within_capacity_still_confirms(self):
        lecture = make_lecture(title='여유', capacity=3)
        res = self.reservation(lecture=lecture, status='pending', paid=False)
        with self._paid(20000):
            self.assertTrue(self.client.post(reverse('special_verify', args=[res.token])).json()['ok'])


class LookupTests(Base):
    def test_lookup_finds_by_name_and_phone_and_links_pending_to_checkout(self):
        pending = self.reservation(status='pending', paid=False)
        res = self.client.post(reverse('special_lookup'), {'applicant_name': '김보호', 'phone': '010-1234-5678'})
        self.assertContains(res, 'AI 특강')
        self.assertContains(res, reverse('special_checkout', args=[pending.token]))

    def test_wrong_details_find_nothing(self):
        self.reservation()
        res = self.client.post(reverse('special_lookup'), {'applicant_name': '다른사람', 'phone': '01012345678'})
        self.assertContains(res, '일치하는 예약을 찾지 못했어요')
        self.assertEqual(self.client.get(reverse('special_lookup')).status_code, 200)

    def test_lookup_is_throttled(self):
        for _ in range(15):
            self.client.post(reverse('special_lookup'), {'applicant_name': 'x', 'phone': '01012345678'})
        res = self.client.post(reverse('special_lookup'), {'applicant_name': '김보호', 'phone': '01012345678'})
        self.assertContains(res, '조회가 너무 많아요')


@override_settings(**SOLAPI)
class ReminderTests(Base):
    def test_reminders_sent_once_to_confirmed_only(self):
        confirmed = self.reservation()
        self.reservation(status='pending', paid=False)
        self.reservation(status='waitlist', paid=False)
        with mock.patch('arcade.special_lecture._post_alimtalk', return_value=(True, '')) as post:
            self.assertEqual(send_reminders(self.lecture), (1, 0, []))
            self.assertEqual(send_reminders(self.lecture), (0, 0, []))
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args[0][1], 'T2')
        self.assertNotIn('#{결제금액}', post.call_args[0][2])
        confirmed.refresh_from_db()
        self.assertIsNotNone(confirmed.reminder_sent_at)

    def test_failure_is_reported_and_retried_later(self):
        res = self.reservation()
        with mock.patch('arcade.special_lecture._post_alimtalk', return_value=(False, 'HTTP 400')):
            self.assertEqual(send_reminders(self.lecture), (0, 1, ['HTTP 400']))
        res.refresh_from_db()
        self.assertIsNone(res.reminder_sent_at)

    def test_admin_button_and_command_for_tomorrows_lecture(self):
        self.reservation()
        self.staff('opsadmin2')
        with mock.patch('arcade.special_lecture._post_alimtalk', return_value=(True, '')):
            res = self.client.post(reverse('special_admin_remind', args=[self.lecture.pk]), follow=True)
        self.assertContains(res, '1건 보냈어요')
        tomorrow = make_lecture(title='내일 특강', lecture_at=timezone.now() + datetime.timedelta(days=1))
        self.reservation(lecture=tomorrow)
        out = io.StringIO()
        with mock.patch('arcade.special_lecture._post_alimtalk', return_value=(True, '')) as post:
            call_command('send_special_reminders', stdout=out)
        self.assertEqual(post.call_count, 1)
        self.assertIn('내일 특강: 발송 1건', out.getvalue())

    @override_settings(SOLAPI_SPECIAL_INCLUDE_URL=True, SITE_BASE_URL='https://medulab.kr')
    def test_confirmation_link_variable_is_optional(self):
        res = self.reservation()
        self.assertEqual(_alimtalk_variables(res)['#{확인주소}'], f'https://medulab.kr/special/r/{res.token}/')
        with override_settings(SOLAPI_SPECIAL_INCLUDE_URL=False):
            self.assertNotIn('#{확인주소}', _alimtalk_variables(res))


class ExportRosterCouponAndMailTests(Base):
    def test_csv_export_has_bom_and_participant_rows(self):
        self.reservation(referral_friend='이메듀')
        self.staff()
        res = self.client.get(reverse('special_admin_export', args=[self.lecture.pk]))
        text = res.content.decode('utf-8')
        self.assertTrue(text.startswith('﻿'))
        rows = list(csv.reader(io.StringIO(text.lstrip('﻿'))))
        self.assertEqual(rows[0][:6], ['신청일시', '상태', '신청자', '연락처', '이메일', '참가자'])
        self.assertEqual((rows[1][5], rows[1][6], rows[1][8]), ('김학생', '한빛초', '2016-03-15'))
        self.assertIn('이메듀', rows[1])

    def test_roster_lists_only_confirmed_people(self):
        self.reservation()
        waiting = self.reservation(status='waitlist', paid=False)
        SpecialLectureParticipant.objects.filter(reservation=waiting).update(name='대기자')
        self.staff()
        page = self.client.get(reverse('special_admin_roster', args=[self.lecture.pk]))
        self.assertContains(page, '김학생')
        self.assertNotContains(page, '대기자')
        self.assertContains(page, '인쇄')

    def test_export_and_roster_need_staff(self):
        for name in ('special_admin_export', 'special_admin_roster'):
            self.assertEqual(self.client.get(reverse(name, args=[self.lecture.pk])).status_code, 302)

    def test_grant_coupons_to_existing_members_once(self):
        old = make_member('oldmember')
        got = make_member('gotcoupon')
        SpecialLectureCoupon.objects.create(user=got)
        ghost = make_member('ghostmember')
        ghost.profile.onboarding_complete = False
        ghost.profile.save()
        self.staff('opsadmin3')
        page = self.client.get(reverse('special_admin_list'))
        self.assertContains(page, '기존 회원에게 쿠폰 지급')
        self.client.post(reverse('special_admin_grant_coupons'))
        self.assertTrue(SpecialLectureCoupon.objects.filter(user=old).exists())
        self.assertFalse(SpecialLectureCoupon.objects.filter(user=ghost).exists())   # 가입 미완료 계정 제외
        before = SpecialLectureCoupon.objects.count()
        self.client.post(reverse('special_admin_grant_coupons'))
        self.assertEqual(SpecialLectureCoupon.objects.count(), before)   # 두 번째는 추가 지급 없음
        self.assertEqual(SpecialLectureCoupon.objects.filter(user=old).count(), 1)

    def test_grant_requires_staff_and_post(self):
        make_member('plainx')
        self.client.post(reverse('special_admin_grant_coupons'))
        self.assertFalse(SpecialLectureCoupon.objects.exists())

    @override_settings(SPECIAL_NOTIFY_EMAILS=['ops@example.com'])
    def test_admin_mail_goes_to_configured_address(self):
        res = self.reservation()
        _send_admin_mail(res.pk, '예약 확정')
        self.assertEqual(mail.outbox[0].to, ['ops@example.com'])
        self.assertIn('김보호', mail.outbox[0].body)
        self.assertIn('예약 확정', mail.outbox[0].subject)

    @override_settings(SPECIAL_NOTIFY_EMAILS=[])
    def test_admin_mail_falls_back_to_superusers(self):
        User.objects.create_superuser('boss', 'boss@example.com', 'x')
        _send_admin_mail(self.reservation().pk, '대기 신청')
        self.assertEqual(mail.outbox[0].to, ['boss@example.com'])

    def test_admin_page_has_new_tools(self):
        self.reservation()
        self.staff()
        page = self.client.get(f"{reverse('special_admin_list')}?lecture={self.lecture.pk}")
        for text in ('참가자 명단(인쇄)', '엑셀(CSV) 내려받기', '참가 안내 알림 보내기', '취소·환불', '환불 없이 취소'):
            self.assertContains(page, text)
