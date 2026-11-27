import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from arcade.management.commands.send_absence_alerts import send_absence_alerts
from arcade.models import (
    Attendance, ClassAttendance, ClassEnrollment, NotificationLog, ParentChildLink, ScheduleEvent, SchoolClass,
)

SOLAPI = dict(SOLAPI_API_KEY='k', SOLAPI_API_SECRET='s', SOLAPI_PF_ID='pf', SOLAPI_SENDER='01000000000',
              SOLAPI_TEMPLATE_ABSENCE='TABS')

# 2030-01-07 은 월요일 (요일 코드 '1'), 수업은 16:00 ~ 17:30
DAY = datetime.date(2030, 1, 7)


def at(hour, minute):
    return timezone.make_aware(datetime.datetime.combine(DAY, datetime.time(hour, minute)))


@override_settings(**SOLAPI)
class AbsenceAlertTests(TestCase):
    def setUp(self):
        self.klass = SchoolClass.objects.create(name='AICE반', days_of_week='1,3', start_time=datetime.time(16, 0),
                                                end_time=datetime.time(17, 30))
        self.student = self.make_student('kid', 'medulab_member')
        parent = User.objects.create_user('mom', password='x')
        parent.profile.phone_number = '010-1234-5678'
        parent.profile.save()
        ParentChildLink.objects.create(parent=parent, child=self.student)
        self.parent = parent

    def make_student(self, name, user_type):
        user = User.objects.create_user(name, password='x')
        user.profile.user_type = user_type
        user.profile.save()
        ClassEnrollment.objects.create(school_class=self.klass, student=user)
        return user

    def run_alert(self, now):
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            result = send_absence_alerts(now=now)
        return result, post

    def test_sends_once_after_ten_minutes(self):
        (_, targets), post = self.run_alert(at(16, 9))
        self.assertEqual((targets, post.call_count), (0, 0))   # 아직 10분이 안 지남
        (sent, _), post = self.run_alert(at(16, 10))
        self.assertEqual((sent, post.call_count), (1, 1))
        body = post.call_args.kwargs['json']['message']['kakaoOptions']
        self.assertEqual(body['templateId'], 'TABS')
        self.assertEqual(body['variables']['#{수업명}'], 'AICE반')
        self.assertEqual(body['variables']['#{시작시간}'], '16:00')
        _, post = self.run_alert(at(16, 15))   # 다음 실행에서는 다시 보내지 않는다
        self.assertEqual(post.call_count, 0)
        self.assertEqual(NotificationLog.objects.filter(kind='absence', status='sent').count(), 1)

    def test_attended_students_are_skipped(self):
        Attendance.objects.create(user=self.student, date=DAY, attendance_type='present')
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 0)

    def test_access_only_login_does_not_count_as_attendance(self):
        Attendance.objects.create(user=self.student, date=DAY, attendance_type='access')
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 1)

    def test_teacher_marked_present_is_skipped(self):
        enrollment = ClassEnrollment.objects.get(student=self.student)
        ClassAttendance.objects.create(enrollment=enrollment, date=DAY, is_present=True)
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 0)

    def test_marked_absent_is_skipped(self):
        enrollment = ClassEnrollment.objects.get(student=self.student)
        for note in ('관리자 결석 처리', '학부모 신청: 몸이 아파서 못 가요'):
            ClassAttendance.objects.update_or_create(
                enrollment=enrollment, date=DAY, defaults={'is_present': False, 'note': note})
            _, post = self.run_alert(at(16, 20))
            self.assertEqual(post.call_count, 0)

    def test_blank_sheet_row_without_note_still_sends(self):
        enrollment = ClassEnrollment.objects.get(student=self.student)
        ClassAttendance.objects.create(enrollment=enrollment, date=DAY, is_present=False)
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 1)

    def test_only_medulab_students_and_class_days_and_class_hours(self):
        self.student.profile.user_type = 'student'
        self.student.profile.save()
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 0)
        self.student.profile.user_type = 'medulab_member'
        self.student.profile.save()
        self.klass.days_of_week = '2,4'   # 화·목 수업이면 월요일에는 대상이 아니다
        self.klass.save()
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 0)
        self.klass.days_of_week = '1'
        self.klass.save()
        _, post = self.run_alert(at(17, 45))   # 수업이 끝난 뒤에는 보내지 않는다
        self.assertEqual(post.call_count, 0)

    def test_holiday_is_skipped(self):
        ScheduleEvent.objects.create(title='휴원', event_type='holiday', start_date=at(0, 0), end_date=at(23, 59))
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 0)

    def test_parent_who_turned_off_notices_is_skipped(self):
        self.parent.profile.notify_attendance = False
        self.parent.profile.save()
        _, post = self.run_alert(at(16, 20))
        self.assertEqual(post.call_count, 0)
        self.assertEqual(NotificationLog.objects.get(kind='absence').status, 'skipped')

    def test_failed_send_is_retried_once_only(self):
        with mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 400
            post.return_value.text = 'bad'
            for minute in (10, 11, 12, 13):
                send_absence_alerts(now=at(16, minute))
        self.assertEqual(post.call_count, 2)

    @override_settings(SOLAPI_TEMPLATE_ABSENCE='')
    def test_without_template_only_logs_dry_run_once(self):
        for minute in (10, 11, 12):
            send_absence_alerts(now=at(16, minute))
        self.assertEqual(NotificationLog.objects.filter(kind='absence', status='dry_run').count(), 1)


class AbsenceReportTests(TestCase):
    def setUp(self):
        self.klass = SchoolClass.objects.create(name='AICE반', days_of_week='1', start_time=datetime.time(16, 0))
        self.student = User.objects.create_user('kid', password='x')
        self.student.profile.real_name = '홍길동'
        self.student.profile.save()
        self.enrollment = ClassEnrollment.objects.create(school_class=self.klass, student=self.student)
        self.date = timezone.localdate()
        from arcade.absence_report import make_absence_token
        self.url = f'/absence/{make_absence_token(self.enrollment.pk, self.date)}/'

    def test_alert_message_carries_the_link_code(self):
        from arcade.parent_notify import send_absence_notice
        parent = User.objects.create_user('mom', password='x')
        parent.profile.phone_number = '010-1234-5678'
        parent.profile.save()
        ParentChildLink.objects.create(parent=parent, child=self.student)
        with override_settings(**SOLAPI), mock.patch('arcade.parent_notify.requests.post') as post:
            post.return_value.status_code = 200
            send_absence_notice(self.student, self.date, 'AICE반', '16:00', self.enrollment.pk)
        code = post.call_args.kwargs['json']['message']['kakaoOptions']['variables']['#{결석코드}']
        self.assertEqual(self.client.get(f'/absence/{code}/').status_code, 200)

    def test_form_shows_student_and_class(self):
        res = self.client.get(self.url)
        self.assertContains(res, '홍길동')
        self.assertContains(res, 'AICE반')
        self.assertContains(res, '몸이 아파서 못 가요')

    def test_submitting_reason_marks_absence_in_attendance_sheet(self):
        res = self.client.post(self.url, {'reason': 'sick', 'makeup': 'no'})
        self.assertContains(res, '결석</b>이 접수')
        record = ClassAttendance.objects.get(enrollment=self.enrollment, date=self.date)
        self.assertFalse(record.is_present)
        self.assertEqual(record.note, '학부모 신청: 몸이 아파서 못 가요')
        self.assertContains(self.client.get(self.url), '몸이 아파서 못 가요')   # 다시 열면 알린 사유가 보인다
        self.client.post(self.url, {'reason': 'other', 'makeup': 'no', 'detail': '치과 진료'})
        self.assertEqual(ClassAttendance.objects.get(enrollment=self.enrollment, date=self.date).note, '학부모 신청: 치과 진료')

    def test_reason_is_required_and_other_needs_text(self):
        self.assertContains(self.client.post(self.url, {}), '결석 사유를 선택해 주세요')
        self.assertContains(self.client.post(self.url, {'reason': 'other'}), '기타 사유를 입력해 주세요')
        self.assertFalse(ClassAttendance.objects.exists())

    def test_already_attended_cannot_be_marked_absent(self):
        Attendance.objects.create(user=self.student, date=self.date, attendance_type='present')
        self.assertContains(self.client.post(self.url, {'reason': 'sick', 'makeup': 'no'}), '이미 출석')
        self.assertFalse(ClassAttendance.objects.exists())

    def test_teacher_marked_present_is_kept(self):
        ClassAttendance.objects.create(enrollment=self.enrollment, date=self.date, is_present=True)
        self.client.post(self.url, {'reason': 'sick', 'makeup': 'no'})
        self.assertTrue(ClassAttendance.objects.get(enrollment=self.enrollment, date=self.date).is_present)

    def test_bad_or_expired_token(self):
        self.assertEqual(self.client.get('/absence/garbage/').status_code, 404)
        from arcade.absence_report import make_absence_token
        token = make_absence_token(self.enrollment.pk, self.date)
        with mock.patch('arcade.absence_report.MAX_AGE_SECONDS', -1):
            self.assertEqual(self.client.get(f'/absence/{token}/').status_code, 404)

    def test_attendance_sheet_shows_the_reason(self):
        self.client.post(self.url, {'reason': 'family', 'makeup': 'no'})
        staff = User.objects.create_user('boss', password='x', is_staff=True)
        self.client.force_login(staff)
        page = self.client.get(f'/admin-services/classes/{self.klass.pk}/attendance/')
        self.assertContains(page, '학부모 신청: 가족 행사·여행이 있어요')
