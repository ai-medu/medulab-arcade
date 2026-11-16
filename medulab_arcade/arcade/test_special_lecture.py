import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from arcade.models import (
    NavItem, ParentChildLink, SpecialLecture, SpecialLectureCoupon, SpecialLectureParticipant,
    SpecialLectureReservation,
)
from arcade.special_lecture import available_coupon, compute_pricing, grant_welcome_coupon


def make_lecture(**kwargs):
    defaults = dict(title='AI 특강', lecture_at=timezone.now() + datetime.timedelta(days=7),
                    base_price=20000, friend_discount=10000, capacity=0)
    defaults.update(kwargs)
    return SpecialLecture.objects.create(**defaults)


def make_member(name, user_type='general', approved=True):
    user = User.objects.create_user(name, password='x', email=f'{name}@example.com')
    user.profile.user_type = user_type
    user.profile.is_approved = approved
    user.profile.real_name = name
    user.profile.phone_number = '01012345678'
    user.profile.save()
    return user


class PricingTests(TestCase):
    def setUp(self):
        self.lecture = make_lecture()

    def _p(self, n, free=False):
        return [{'name': f'학생{i}', 'free': free, 'is_friend': i > 0} for i in range(n)]

    def test_single_pays_base_price(self):
        rows, total, discount, coupon = compute_pricing(self.lecture, self._p(1))
        self.assertEqual((total, discount, coupon), (20000, 0, False))

    def test_friend_chance_discounts_each(self):
        rows, total, discount, _ = compute_pricing(self.lecture, self._p(2))
        self.assertEqual([r['price'] for r in rows], [10000, 10000])
        self.assertEqual((total, discount), (20000, 20000))

    def test_coupon_makes_first_paying_participant_free(self):
        rows, total, discount, used = compute_pricing(self.lecture, self._p(2), coupon=object())
        self.assertEqual([r['price'] for r in rows], [0, 10000])
        self.assertTrue(used)
        _, total, _, used = compute_pricing(self.lecture, self._p(1), coupon=object())
        self.assertEqual((total, used), (0, True))

    def test_free_member_child_with_friend(self):
        people = [{'name': '아이', 'free': True, 'is_friend': False}, {'name': '친구', 'free': False, 'is_friend': True}]
        rows, total, _, _ = compute_pricing(self.lecture, people)
        self.assertEqual([r['price'] for r in rows], [0, 10000])


class CouponTests(TestCase):
    def test_grant_once(self):
        user = make_member('coup1')
        self.assertIsNotNone(grant_welcome_coupon(user))
        self.assertIsNone(grant_welcome_coupon(user))
        self.assertEqual(SpecialLectureCoupon.objects.filter(user=user).count(), 1)

    def test_signup_grants_coupon(self):
        res = self.client.post(reverse('signup'), {
            'real_name': '가입자', 'birth_date': '1990.01.01', 'username': 'newbie1', 'phone_number': '01012345678',
            'email': 'newbie1@example.com', 'password1': 'Str0ng!pass9', 'password2': 'Str0ng!pass9',
            'user_type': 'general', 'signup_source': '블로그', 'signup_reason': '궁금해서'})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(SpecialLectureCoupon.objects.filter(user__username='newbie1').exists())

    def test_social_onboarding_grants_coupon(self):
        user = make_member('soc1')
        user.profile.onboarding_complete = False
        user.profile.save()
        self.client.force_login(user)
        res = self.client.post(reverse('social_onboarding'), {
            'real_name': '소셜', 'birth_date': '1990.01.01', 'phone_number': '01012345678', 'email': 'soc1@example.com',
            'user_type': 'general', 'signup_source': '블로그', 'signup_reason': 'x'})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(SpecialLectureCoupon.objects.filter(user=user).exists())


class ApplyFlowTests(TestCase):
    def setUp(self):
        self.lecture = make_lecture()
        self.apply_url = reverse('special_lecture_apply', args=[self.lecture.pk])
        self.guest = {'p_name': '김학생', 'p_grade': '4학년', 'applicant_name': '김보호', 'phone': '010-1234-5678'}

    def test_pages_render(self):
        self.assertContains(self.client.get(reverse('special_lecture_list')), 'AI 특강')
        res = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        self.assertContains(res, '20,000원')
        self.assertContains(res, '친구 찬스')

    def test_guest_applies_and_goes_to_checkout(self):
        res = self.client.post(self.apply_url, self.guest)
        reservation = SpecialLectureReservation.objects.get()
        self.assertRedirects(res, reverse('special_checkout', args=[reservation.token]), fetch_redirect_response=False)
        self.assertEqual((reservation.status, reservation.amount, reservation.phone), ('pending', 20000, '01012345678'))
        self.assertIsNone(reservation.applicant)
        self.assertContains(self.client.get(reverse('special_checkout', args=[reservation.token])), '20,000원')

    def test_guest_with_friend_pays_10000_each(self):
        self.client.post(self.apply_url, dict(self.guest, f_name=['친구'], f_grade=['4학년']))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual(reservation.amount, 20000)
        self.assertEqual(sorted(reservation.participants.values_list('price', flat=True)), [10000, 10000])

    def test_validation_errors(self):
        self.client.post(self.apply_url, dict(self.guest, phone='12'))
        self.client.post(self.apply_url, dict(self.guest, p_name=''))
        self.assertFalse(SpecialLectureReservation.objects.exists())

    def test_member_with_coupon_books_free(self):
        user = make_member('coupuser')
        grant_welcome_coupon(user)
        self.client.force_login(user)
        res = self.client.post(self.apply_url, dict(self.guest, use_coupon='1'))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual((reservation.status, reservation.amount), ('confirmed', 0))
        self.assertRedirects(res, reverse('special_reservation', args=[reservation.token]), fetch_redirect_response=False)
        self.assertIsNone(available_coupon(user))   # 쿠폰은 한 번만

    def test_coupon_not_usable_by_guest(self):
        self.client.post(self.apply_url, dict(self.guest, use_coupon='1'))
        self.assertEqual(SpecialLectureReservation.objects.get().amount, 20000)

    def test_coupon_returned_when_reservation_canceled(self):
        user = make_member('coupuser2')
        grant_welcome_coupon(user)
        self.client.force_login(user)
        self.client.post(self.apply_url, dict(self.guest, use_coupon='1'))
        admin = make_member('adm20')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        reservation = SpecialLectureReservation.objects.get()
        self.client.post(reverse('special_admin_cancel', args=[reservation.pk]))
        self.assertIsNotNone(available_coupon(user))

    def test_capacity_limit(self):
        limited = make_lecture(title='소규모', capacity=1)
        url = reverse('special_lecture_apply', args=[limited.pk])
        self.client.post(url, self.guest)
        self.client.post(url, dict(self.guest, p_name='다른학생'))
        self.assertEqual(SpecialLectureReservation.objects.filter(lecture=limited).count(), 1)
        self.assertTrue(limited.is_full)

    def test_closed_lecture_rejects(self):
        closed = make_lecture(title='닫힘', registration_open=False)
        self.client.post(reverse('special_lecture_apply', args=[closed.pk]), self.guest)
        self.assertFalse(SpecialLectureReservation.objects.exists())


class MedulabParentTests(TestCase):
    def setUp(self):
        self.lecture = make_lecture()
        self.parent = make_member('mparent', 'medulab_parent')
        self.parent.profile.children_info = [{'name': '정해준', 'birth_date': '20130903', 'school': '해솔초', 'grade': '5'}]
        self.parent.profile.save()
        self.kid = make_member('kidx', 'medulab_member')
        self.kid.profile.real_name = '박지우'
        self.kid.profile.save()
        ParentChildLink.objects.create(parent=self.parent, child=self.kid)
        self.client.force_login(self.parent)
        self.apply_url = reverse('special_lecture_apply', args=[self.lecture.pk])
        self.base = {'applicant_name': '학부모', 'phone': '01099998888'}

    def test_detail_lists_children(self):
        res = self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk]))
        self.assertContains(res, '박지우')
        self.assertContains(res, '정해준')

    def test_children_join_free_and_confirmed(self):
        self.client.post(self.apply_url, dict(self.base, child=[f'u{self.kid.id}', 'i0']))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual((reservation.status, reservation.amount), ('confirmed', 0))
        self.assertEqual(reservation.participants.count(), 2)
        self.assertEqual(reservation.participants.filter(student=self.kid).count(), 1)

    def test_need_to_pick_a_child(self):
        self.client.post(self.apply_url, self.base)
        self.assertFalse(SpecialLectureReservation.objects.exists())

    def test_friend_pays_discounted_price(self):
        self.client.post(self.apply_url, dict(self.base, child=[f'u{self.kid.id}'], f_name=['친구'], f_grade=['']))
        reservation = SpecialLectureReservation.objects.get()
        self.assertEqual((reservation.status, reservation.amount), ('pending', 10000))

    def test_unapproved_medulab_parent_is_not_free(self):
        self.parent.profile.is_approved = False
        self.parent.profile.save()
        self.client.post(self.apply_url, dict(self.base, child=[f'u{self.kid.id}'], p_name='아이', p_grade=''))
        self.assertEqual(SpecialLectureReservation.objects.get().amount, 20000)


@override_settings(PORTONE_API_SECRET='secret', PORTONE_STORE_ID='store')
class VerifyTests(TestCase):
    def setUp(self):
        self.lecture = make_lecture()
        self.reservation = SpecialLectureReservation.objects.create(
            lecture=self.lecture, applicant_name='김보호', phone='01012345678', amount=20000)
        SpecialLectureParticipant.objects.create(reservation=self.reservation, name='김학생', price=20000)
        self.url = reverse('special_verify', args=[self.reservation.token])

    def _paid(self, total):
        class Resp:
            status_code = 200

            def json(self_inner):
                return {'status': 'PAID', 'amount': {'total': total}, 'method': {'type': 'PaymentMethodCard'}}
        return mock.patch('requests.get', return_value=Resp())

    def test_verify_confirms_reservation(self):
        with self._paid(20000):
            res = self.client.post(self.url)
        self.assertTrue(res.json()['ok'])
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'confirmed')
        self.assertIsNotNone(self.reservation.paid_at)

    def test_amount_mismatch_rejected(self):
        with self._paid(1000):
            res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'pending')

    def test_checkout_and_result_pages(self):
        self.assertContains(self.client.get(reverse('special_checkout', args=[self.reservation.token])), '결제 금액')
        self.assertContains(self.client.get(reverse('special_reservation', args=[self.reservation.token])), '결제를 마치면')

    def test_unknown_token_404(self):
        self.assertEqual(self.client.get(reverse('special_reservation', args=['nope'])).status_code, 404)


class AdminAndNavTests(TestCase):
    def test_nav_item_under_learning(self):
        item = NavItem.objects.get(url_name='special_lecture_list')
        self.assertEqual((item.section, item.name), ('learning', '특강프로그램'))
        names = list(NavItem.objects.filter(section='learning').order_by('order', 'id').values_list('url_name', flat=True))
        self.assertEqual(names[1], 'special_lecture_list')

    def test_admin_pages_staff_only(self):
        self.assertEqual(self.client.get(reverse('special_admin_list')).status_code, 302)
        admin = make_member('adm21')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse('special_admin_list')).status_code, 200)
        res = self.client.post(reverse('special_admin_create'), {
            'title': '새 특강', 'lecture_at': '2030-01-01T14:00', 'capacity': 10, 'base_price': 20000,
            'friend_discount': 10000, 'registration_open': 'on', 'is_active': 'on'})
        self.assertEqual(res.status_code, 302)
        lecture = SpecialLecture.objects.get(title='새 특강')
        self.assertContains(self.client.get(f"{reverse('special_admin_list')}?lecture={lecture.pk}"), '새 특강')



class AdminDeleteAndSeedTests(TestCase):
    def _admin(self):
        admin = make_member('adm30')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)

    def test_november_lecture_seeded(self):
        lecture = SpecialLecture.objects.get(title='AI 활용 나만의 머그컵 만들기')
        local = timezone.localtime(lecture.lecture_at)
        self.assertEqual((local.month, local.day, local.hour, local.minute), (11, 21, 13, 0))
        self.assertIn('화개중앙로 51', lecture.location)

    def test_delete_lecture_without_reservations(self):
        self._admin()
        lecture = make_lecture(title='지울 특강')
        self.client.post(reverse('special_admin_delete', args=[lecture.pk]))
        self.assertFalse(SpecialLecture.objects.filter(pk=lecture.pk).exists())

    def test_delete_blocked_with_live_reservation_but_allowed_after_cancel(self):
        self._admin()
        lecture = make_lecture(title='예약 있는 특강')
        reservation = SpecialLectureReservation.objects.create(lecture=lecture, applicant_name='a', phone='01012345678', amount=20000)
        self.client.post(reverse('special_admin_delete', args=[lecture.pk]))
        self.assertTrue(SpecialLecture.objects.filter(pk=lecture.pk).exists())
        self.client.post(reverse('special_admin_cancel', args=[reservation.pk]))
        self.client.post(reverse('special_admin_delete', args=[lecture.pk]))
        self.assertFalse(SpecialLecture.objects.filter(pk=lecture.pk).exists())

    def test_delete_requires_staff_and_post(self):
        lecture = make_lecture(title='보호 특강')
        self.client.post(reverse('special_admin_delete', args=[lecture.pk]))
        self.assertTrue(SpecialLecture.objects.filter(pk=lecture.pk).exists())
        self._admin()
        self.assertEqual(self.client.get(reverse('special_admin_delete', args=[lecture.pk])).status_code, 405)
