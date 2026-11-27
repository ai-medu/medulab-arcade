import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from arcade.models import Attendance, ClassAttendance, ClassEnrollment, SchoolClass

SAT = datetime.date(2030, 1, 5)


class MakeupTimeTests(TestCase):
    def setUp(self):
        self.klass = SchoolClass.objects.create(name='토요반', days_of_week='6', start_time=datetime.time(15, 0),
                                                end_time=datetime.time(16, 30))
        self.kid = User.objects.create_user('kid', password='x')
        ClassEnrollment.objects.create(school_class=self.klass, student=self.kid)
        self.client.force_login(User.objects.create_user('boss', password='x', is_staff=True))
        self.set_url = reverse('api_admin_set_attendance', args=[self.kid.pk])

    def _set(self, kind, **extra):
        return self.client.post(self.set_url, {'date': SAT.isoformat(), 'attendance_type': kind, **extra},
                                content_type='application/json')

    def test_times_list_for_the_weekday(self):
        url = reverse('api_admin_makeup_times', args=[self.kid.pk])
        data = self.client.get(url, {'date': SAT.isoformat()}).json()
        self.assertEqual(data['times'], [{'start': '15:00', 'end': '16:30', 'classes': '토요반'}])
        self.assertIsNone(data['current'])
        self.assertEqual(self.client.get(url, {'date': '2030-01-07'}).json()['times'], [])
        self.client.force_login(self.kid)
        self.assertNotEqual(self.client.get(url, {'date': SAT.isoformat()}).status_code, 200)

    def test_time_is_saved_shown_and_cleared(self):
        with mock.patch('arcade.views.notify_attendance'):
            self.assertEqual(self._set('makeup', start_time='15:00', end_time='16:30').status_code, 200)
            record = Attendance.objects.get(user=self.kid)
            self.assertEqual((record.makeup_start, record.makeup_end), (datetime.time(15), datetime.time(16, 30)))
            page = self.client.get(reverse('admin_student_report', args=[self.kid.pk]) + '?year=2030&month=1')
            self.assertContains(page, '보강 15:00')
            self.assertContains(page, '15:00~16:30')
            self.assertContains(page, 'id="mkOverlay"')
            self._set('present')
        self.assertIsNone(Attendance.objects.get(user=self.kid).makeup_start)

    def test_bad_times_are_rejected(self):
        self.assertEqual(self._set('makeup', start_time='15:00').status_code, 400)
        self.assertEqual(self._set('makeup', start_time='16:00', end_time='15:00').status_code, 400)
        self.assertFalse(Attendance.objects.exists())

    def test_later_today_does_not_send_attendance_notice(self):
        now = timezone.make_aware(datetime.datetime.combine(SAT, datetime.time(10, 0)))
        with mock.patch.object(timezone, 'now', return_value=now), \
                mock.patch('arcade.views.notify_attendance') as notify:
            self.client.force_login(User.objects.get(username='boss'))   # 로그인 유효기간은 바꾼 시각 기준
            self.assertEqual(self._set('makeup', start_time='15:00', end_time='16:30').status_code, 200)
            notify.assert_not_called()
            self._set('makeup', start_time='09:00', end_time='10:30')
            notify.assert_called_once()

    def test_absence_reason_is_listed_under_calendar(self):
        self._set('absent', reason='몸이 아파서')
        ClassAttendance.objects.update(makeup_request='보강 희망: 1/12(토) 15:00~16:30')
        page = self.client.get(reverse('admin_student_report', args=[self.kid.pk]) + '?year=2030&month=1')
        self.assertContains(page, '이 달의 결석·보강 내역')
        self.assertContains(page, '관리자 결석 처리: 몸이 아파서 · 보강 희망: 1/12(토) 15:00~16:30')
