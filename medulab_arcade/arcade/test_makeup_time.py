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
        patcher = mock.patch('arcade.parent_notify._spawn')   # 알림톡 발송 스레드는 띄우지 않는다
        patcher.start()
        self.addCleanup(patcher.stop)

    def _set(self, kind, **extra):
        return self.client.post(self.set_url, {'date': SAT.isoformat(), 'attendance_type': kind, **extra},
                                content_type='application/json')

    def test_times_list_covers_every_weekday(self):
        url = reverse('api_admin_makeup_times', args=[self.kid.pk])
        data = self.client.get(url, {'date': SAT.isoformat()}).json()
        expected = {'date': '2030-01-05', 'weekday': '토', 'day': '1/5', 'holiday': False,
                    'start': '15:00', 'end': '16:30', 'classes': '토요반'}
        self.assertEqual(data['times'], [expected])
        self.assertIsNone(data['current'])
        monday = SchoolClass.objects.create(name='화요반', days_of_week='2', start_time=datetime.time(16, 0),
                                            end_time=datetime.time(17, 0))
        ClassEnrollment.objects.create(school_class=monday, student=self.kid)
        times = self.client.get(url, {'date': SAT.isoformat()}).json()['times']
        self.assertEqual([(t['weekday'], t['date']) for t in times], [('토', '2030-01-05'), ('화', '2030-01-08')])
        self.client.force_login(self.kid)
        self.assertNotEqual(self.client.get(url, {'date': SAT.isoformat()}).status_code, 200)

    def test_time_is_saved_shown_and_cleared(self):
        later = SAT + datetime.timedelta(days=1)
        with self._at(later, 10), mock.patch('arcade.views.notify_attendance'):
            self._login(User.objects.get(username='boss'))
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

    def _at(self, day, hour):
        return mock.patch.object(timezone, 'now',
                                 return_value=timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour))))

    def _login(self, user):
        self.client.force_login(user)   # 로그인 유효기간은 바꾼 시각 기준

    def test_future_time_is_planned_and_past_time_is_attended(self):
        with self._at(SAT, 10), mock.patch('arcade.parent_notify._spawn') as spawn:
            self._login(User.objects.get(username='boss'))
            self.assertEqual(self._set('makeup', start_time='15:00', end_time='16:30').json()['attendance_type'], 'planned')
            spawn.assert_not_called()
            page = self.client.get(reverse('admin_student_report', args=[self.kid.pk]))
            self.assertEqual((page.context['planned_days'], page.context['makeup_days']), ([5], []))
            self.assertEqual(page.context['attendance_dates'], [])   # 예정은 출석 횟수에 안 들어간다
            self.assertContains(page, '예정 15:00')
            self.assertContains(page, '보강 예정')
            self.assertEqual(self._set('makeup', start_time='09:00', end_time='10:30').json()['attendance_type'], 'makeup')
            spawn.assert_called_once()

    def test_planned_keeps_absence_record_and_turns_into_no_show(self):
        with self._at(SAT, 10):
            self._login(User.objects.get(username='boss'))
            self._set('absent', reason='몸이 아파서')
            self._set('makeup', start_time='15:00', end_time='16:30')
            self.assertFalse(ClassAttendance.objects.get().is_present)
        with self._at(SAT + datetime.timedelta(days=1), 10):
            self._login(User.objects.get(username='boss'))
            page = self.client.get(reverse('admin_student_report', args=[self.kid.pk]))
            self.assertEqual((page.context['noshow_days'], page.context['planned_days']), ([5], []))
            self.assertContains(page, '보강 불참')

    def test_student_check_in_turns_planned_into_attended(self):
        profile = self.kid.profile
        profile.user_type = 'medulab_member'
        profile.save()
        ClassEnrollment.objects.all().delete()
        with self._at(SAT, 10):
            Attendance.objects.create(user=self.kid, date=SAT, attendance_type='planned',
                                      makeup_start=datetime.time(15), makeup_end=datetime.time(16))
            self._login(self.kid)
            self.assertContains(self.client.get(reverse('home')), '오늘 보강: 15:00')
            url = reverse('api_daily_checkin')
            post = lambda kind: self.client.post(url, {'attendance_type': kind}, content_type='application/json')
            self.assertEqual(post('planned').status_code, 400)
            self.assertEqual(post('access').json()['attendance_type'], 'planned')
            with mock.patch('arcade.views.notify_attendance'):
                self.assertEqual(post('makeup').json()['attendance_type'], 'makeup')
        self.assertEqual(Attendance.objects.get().makeup_start, datetime.time(15))

    def test_absence_reason_is_listed_under_calendar(self):
        self._set('absent', reason='몸이 아파서')
        ClassAttendance.objects.update(makeup_request='보강 희망: 1/12(토) 15:00~16:30')
        page = self.client.get(reverse('admin_student_report', args=[self.kid.pk]) + '?year=2030&month=1')
        self.assertContains(page, '이 달의 결석·보강 내역')
        self.assertContains(page, '관리자 결석 처리: 몸이 아파서 · 보강 희망: 1/12(토) 15:00~16:30')

    def test_admin_absence_with_makeup_links_both_days(self):
        next_sat = datetime.date(2030, 1, 12)
        with self._at(SAT, 10):
            self._login(User.objects.get(username='boss'))
            self.assertEqual(self._set('absent', reason='가족 여행', makeup='yes').status_code, 400)
            self._set('absent', reason='가족 여행', makeup='yes', makeup_date=next_sat.isoformat(),
                      start_time='15:00', end_time='16:30')
            record = Attendance.objects.get(user=self.kid)
            self.assertEqual((record.date, record.attendance_type, record.makeup_for), (next_sat, 'planned', SAT))
            self.assertEqual(ClassAttendance.objects.get().makeup_request, '보강 예정: 1/12(토) 15:00~16:30')
            page = self.client.get(reverse('admin_student_report', args=[self.kid.pk]))
            self.assertEqual((page.context['makeup_to'], page.context['makeup_from']), ({5: '1/12'}, {12: '1/5'}))
            self.assertContains(page, '→ 보강 1/12(토) 15:00~16:30 (예정)')
            self.assertContains(page, '← 1/5(토) 결석분')
            # 보강 날짜의 기록을 지우면 결석 칸의 안내도 사라진다
            self.client.post(self.set_url, {'date': next_sat.isoformat(), 'attendance_type': 'none'},
                             content_type='application/json')
            self.assertEqual(ClassAttendance.objects.get().makeup_request, '')

    def test_makeup_from_absent_day_links_and_cancel_absence_removes_plan(self):
        with self._at(SAT, 10):
            self._login(User.objects.get(username='boss'))
            self._set('absent', reason='몸이 아파서')
            self.client.post(self.set_url, {'date': '2030-01-12', 'attendance_type': 'makeup', 'start_time': '15:00',
                                            'end_time': '16:30', 'for_date': SAT.isoformat()},
                             content_type='application/json')
            self.assertEqual(Attendance.objects.get().makeup_for, SAT)
            self._set('present')   # 결석을 취소하면 잡아 둔 예정도 사라진다
            self.assertEqual([a.date for a in Attendance.objects.all()], [SAT])
