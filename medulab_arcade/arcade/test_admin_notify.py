import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from arcade.admin_notify import notify_admins
from arcade.models import AdminNotification, ClassEnrollment, SchoolClass


class BellTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def test_bell_only_for_staff(self):
        self.assertContains(self.client.get(reverse('home')), 'id="bellBtn"')
        self.client.force_login(User.objects.create_user('kid', password='x'))
        self.assertNotContains(self.client.get(reverse('home')), 'id="bellBtn"')

    def test_list_read_and_read_all(self):
        notify_admins('consult', '첫 알림', '내용', '/x/')
        notify_admins('signup', '둘째 알림')
        data = self.client.get(reverse('admin_notification_list')).json()
        self.assertEqual(data['unread'], 2)
        self.assertEqual([i['title'] for i in data['items']], ['둘째 알림', '첫 알림'])   # 최신이 위
        first = AdminNotification.objects.get(title='첫 알림')
        self.assertEqual(self.client.post(reverse('admin_notification_read', args=[first.pk])).json()['unread'], 1)
        self.assertEqual(self.client.post(reverse('admin_notification_read_all')).json()['unread'], 0)

    def test_api_is_staff_only(self):
        self.client.force_login(User.objects.create_user('kid', password='x'))
        self.assertNotEqual(self.client.get(reverse('admin_notification_list')).status_code, 200)
        self.assertNotEqual(self.client.post(reverse('admin_notification_read_all')).status_code, 200)

    def test_old_notifications_are_trimmed(self):
        with mock.patch('arcade.admin_notify.KEEP_DAYS_COUNT', 3):
            for i in range(6):
                notify_admins('info', f'n{i}')
        self.assertEqual(AdminNotification.objects.count(), 3)
        self.assertTrue(AdminNotification.objects.filter(title='n5').exists())


class NotificationHookTests(TestCase):
    def test_new_consult_inquiry_creates_notification(self):
        with mock.patch('arcade.kakao_notify.send_kakao_memo_to_me'):
            self.client.post(reverse('consult_inquiry'), {
                'applicant_type': 'parent', 'child_name[]': ['하은'], 'child_age[]': ['초4'],
                'phone_number': '01057946461', 'interest_areas': ['로봇 코딩']})
        n = AdminNotification.objects.get()
        self.assertEqual(n.kind, 'consult')
        self.assertIn('새 상담 문의', n.title)
        self.assertEqual(n.url, reverse('consult_inquiry_admin_list'))

    def test_parent_absence_report_creates_notification(self):
        from arcade.absence_report import make_absence_token
        klass = SchoolClass.objects.create(name='AICE반', days_of_week='1', start_time=datetime.time(16, 0))
        kid = User.objects.create_user('kid', password='x')
        kid.profile.real_name = '홍길동'
        kid.profile.save()
        enrollment = ClassEnrollment.objects.create(school_class=klass, student=kid)
        url = f'/absence/{make_absence_token(enrollment.pk, timezone.localdate())}/'
        self.client.post(url, {'reason': 'sick'})
        n = AdminNotification.objects.get(kind='absence')
        self.assertIn('홍길동', n.title)
        self.assertIn('몸이 아파서', n.body)

    def test_signup_creates_notification(self):
        from arcade.views import _notify_new_member
        user = User.objects.create_user('newbie', password='x')
        user.profile.real_name = '김새회원'
        user.profile.user_type = 'medulab_parent'
        user.profile.is_approved = False
        user.profile.save()
        _notify_new_member(user)
        n = AdminNotification.objects.get(kind='signup')
        self.assertIn('김새회원', n.title)
        self.assertIn('승인 필요', n.body)

    def test_special_reservation_creates_notification(self):
        from arcade.test_special_lecture import make_lecture
        from arcade.models import SpecialLectureReservation
        from arcade.special_lecture import notify_admin
        lecture = make_lecture(title='머그컵 특강')
        res = SpecialLectureReservation.objects.create(lecture=lecture, applicant_name='김신청', phone='01012345678', amount=0)
        with mock.patch('arcade.special_lecture._spawn'):
            notify_admin(res, '예약 확정')
        n = AdminNotification.objects.get(kind='special')
        self.assertIn('김신청', n.title)
        self.assertIn('머그컵 특강', n.body)
