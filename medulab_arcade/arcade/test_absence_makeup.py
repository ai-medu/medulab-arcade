import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from arcade.absence_report import make_absence_token, makeup_slots
from arcade.models import AdminNotification, ClassAttendance, ClassEnrollment, ScheduleEvent, SchoolClass

SAT = datetime.date(2030, 1, 5)   # 토요일


def at(day, hour, minute=0):
    return timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour, minute)))


class MakeupTests(TestCase):
    def setUp(self):
        self.mine = self._class('내반', '6', 9, 10)
        self.later = self._class('오후반', '6', 15, 16, students=1)
        self.monday = self._class('월요반', '1', 16, 17, students=1)
        self._class('빈반', '2', 16, 17)   # 수강생 없는 수업은 후보가 아니다
        self.kid = User.objects.create_user('kid', password='x')
        self.enrollment = ClassEnrollment.objects.create(school_class=self.mine, student=self.kid)
        self.url = f'/absence/{make_absence_token(self.enrollment.pk, SAT)}/'
        patcher = mock.patch.object(timezone, 'now', return_value=at(SAT, 9, 10))
        patcher.start()
        self.addCleanup(patcher.stop)

    def _class(self, name, days, start, end, students=0):
        klass = SchoolClass.objects.create(name=name, days_of_week=days, start_time=datetime.time(start),
                                           end_time=datetime.time(end))
        for i in range(students):
            ClassEnrollment.objects.create(school_class=klass, student=User.objects.create_user(f'{name}{i}'))
        return klass

    def _values(self):
        return [value for _, options in makeup_slots(self.kid, SAT) for value, _ in options]

    def test_slots_are_upcoming_times_of_classes_with_students(self):
        values = self._values()
        self.assertEqual(values[:3], ['2030-01-05 15:00~16:00', '2030-01-07 16:00~17:00', '2030-01-12 15:00~16:00'])
        self.assertFalse([v for v in values if '09:00' in v])        # 본인 정규 수업 시간
        self.assertFalse([v for v in values if v.startswith('2030-01-08')])   # 수강생 없는 화요반
        self.assertEqual(values[-1], '2030-01-19 15:00~16:00')       # 2주 안

    def test_holiday_is_excluded(self):
        ScheduleEvent.objects.create(title='휴원', event_type='holiday', start_date=at(datetime.date(2030, 1, 7), 0))
        self.assertNotIn('2030-01-07 16:00~17:00', self._values())

    def test_makeup_choice_is_required(self):
        self.assertContains(self.client.post(self.url, {'reason': 'sick'}), '보강이 가능한지')
        self.assertContains(self.client.post(self.url, {'reason': 'sick', 'makeup': 'yes'}), '보강 가능한 시간을 선택')
        res = self.client.post(self.url, {'reason': 'sick', 'makeup': 'yes', 'makeup_slot': '2030-01-08 16:00~17:00'})
        self.assertContains(res, '보강 가능한 시간을 선택')
        self.assertFalse(ClassAttendance.objects.exists())

    def test_chosen_time_is_saved_and_notified(self):
        res = self.client.post(self.url, {'reason': 'sick', 'makeup': 'yes', 'makeup_slot': '2030-01-07 16:00~17:00'})
        self.assertContains(res, '보강 희망: 1/7(월) 16:00~17:00')
        self.assertEqual(ClassAttendance.objects.get().makeup_request, '보강 희망: 1/7(월) 16:00~17:00')
        self.assertIn('1/7(월) 16:00', AdminNotification.objects.get(kind='absence').body)
        self.assertContains(self.client.get(self.url), '1/7(월) 16:00~17:00)')   # 다시 열면 알린 내용이 보인다
        self.client.post(self.url, {'reason': 'sick', 'makeup': 'no'})
        self.assertEqual(ClassAttendance.objects.get().makeup_request, '보강 어려움')
