import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from arcade.models import Attendance, ClassAttendance, ClassEnrollment, SchoolClass

TODAY = datetime.date(2030, 12, 5)


class AttendanceSheetSaveTests(TestCase):
    def setUp(self):
        self.klass = SchoolClass.objects.create(name='AICE반', days_of_week='4', start_time=datetime.time(16, 0))
        self.kid = User.objects.create_user('kid', password='x')
        self.enrollment = ClassEnrollment.objects.create(school_class=self.klass, student=self.kid)
        self.client.force_login(User.objects.create_user('boss', password='x', is_staff=True))
        self.url = reverse('class_admin_attendance', args=[self.klass.pk]) + '?year=2030&month=12'
        patcher = mock.patch.object(timezone, 'localdate', return_value=TODAY)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _save(self, checked=(), was=()):
        data = {f'att_{self.enrollment.pk}_2030-12-{d:02d}': 'on' for d in checked}
        data.update({f'was_{self.enrollment.pk}_2030-12-{d:02d}': '1' for d in was})
        self.assertEqual(self.client.post(self.url, data).status_code, 302)

    def _saved(self):
        return {r.date.day: r.is_present for r in ClassAttendance.objects.filter(enrollment=self.enrollment)}

    def test_untouched_today_and_future_are_not_saved(self):
        self._save(checked=[4])
        saved = self._saved()
        self.assertEqual(sorted(saved), [1, 2, 3, 4])   # 지난 날짜만 저장
        self.assertTrue(saved[4])
        self.assertFalse(saved[3])

    def test_changed_today_and_future_are_saved(self):
        self._save(checked=[12], was=[5])   # 오늘 체크 해제(결석), 12일 미리 체크
        saved = self._saved()
        self.assertFalse(saved[5])
        self.assertTrue(saved[12])
        self.assertNotIn(19, saved)

    def test_later_self_check_in_shows_as_present(self):
        self._save()
        Attendance.objects.create(user=self.kid, date=datetime.date(2030, 12, 12), attendance_type='present')
        rows = self.client.get(self.url).context['rows']
        cell = next(c for c in rows[0]['cells'] if c['date'].day == 12)
        self.assertTrue(cell['is_present'])

    def test_page_marks_checked_cells(self):
        Attendance.objects.create(user=self.kid, date=TODAY, attendance_type='present')
        self.assertContains(self.client.get(self.url), f'name="was_{self.enrollment.pk}_2030-12-05"')
