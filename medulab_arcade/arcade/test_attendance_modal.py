from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import parent_notify
from .models import Attendance, ClassEnrollment, SchoolClass


class AttendanceModalTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.student = User.objects.create_user('kid', password='x')
        self.student.profile.user_type = 'medulab_member'
        self.student.profile.save()
        klass = SchoolClass.objects.create(name='AICE반', tuition_fee=100000, days_of_week='0,1,2,3,4,5,6')
        ClassEnrollment.objects.create(school_class=klass, student=self.student)
        self.client.force_login(self.staff)
        # 알림톡은 별도 스레드로 보내는데, 테스트 DB(sqlite)와 부딪치지 않게 같은 스레드에서 실행한다
        patcher = mock.patch.object(parent_notify, '_spawn', lambda fn, *a: fn(*a))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_dashboard_has_attendance_modal(self):
        res = self.client.get(reverse('my_report'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'id="attendOverlay"')
        self.assertContains(res, f'openAttendModal({self.student.id},')

    def test_change_today_attendance_via_admin_api(self):
        today = timezone.localdate().strftime('%Y-%m-%d')
        url = reverse('api_admin_set_attendance', args=[self.student.id])
        post = lambda t: self.client.post(url, {'date': today, 'attendance_type': t}, content_type='application/json')
        self.assertEqual(post('present').json()['attendance_type'], 'present')
        self.assertEqual(Attendance.objects.get(user=self.student).attendance_type, 'present')
        post('makeup')
        self.assertEqual(Attendance.objects.get(user=self.student).attendance_type, 'makeup')
        post('none')
        self.assertFalse(Attendance.objects.filter(user=self.student).exists())
