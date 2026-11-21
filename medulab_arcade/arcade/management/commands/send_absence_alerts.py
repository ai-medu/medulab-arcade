"""수업 시작 후 일정 시간(기본 10분)이 지나도 출석하지 않은 메듀랩 학생의 학부모에게 미출석 안내 알림톡을 보낸다.

서버 스케줄(cron)에 1~5분마다 실행하도록 등록해 둔다. 같은 학생에게는 하루에 한 번만 나간다.
- 대상: 메듀랩 학생 중 오늘 요일에 배정된 수업이 있고, 그 수업 시작 시각 + 기준 시간이 지났으며 아직 수업이 끝나지 않은 학생
- 제외: 오늘 이미 출석(출석/보강)한 학생, 휴원일, 학부모 '출석 알림 수신'을 끈 경우
"""
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from arcade.models import Attendance, ClassAttendance, ClassEnrollment, ScheduleEvent
from arcade.parent_notify import send_absence_notice

PY_WEEKDAY_TO_CODE = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '0'}


def is_holiday(now):
    return ScheduleEvent.objects.filter(
        event_type=ScheduleEvent.EVENT_TYPE_HOLIDAY, is_active=True, start_date__lte=now,
    ).filter(Q(end_date__gte=now) | Q(end_date__isnull=True, start_date__date=now.date())).exists()


def send_absence_alerts(now=None, minutes=10):
    """(발송한 학생 수, 대상 학생 수)"""
    now = timezone.localtime(now or timezone.now())
    today = now.date()
    if is_holiday(now):
        return 0, 0
    code = PY_WEEKDAY_TO_CODE[today.weekday()]
    attended = set(Attendance.objects.filter(
        date=today, attendance_type__in=[Attendance.TYPE_PRESENT, Attendance.TYPE_MAKEUP],
    ).values_list('user_id', flat=True))

    enrollments = ClassEnrollment.objects.filter(
        is_active=True, school_class__is_active=True, school_class__start_time__isnull=False,
        student__profile__user_type='medulab_member',
    ).select_related('school_class', 'student__profile')

    handled, sent_students, targets = set(), 0, 0
    for enrollment in enrollments:
        klass = enrollment.school_class
        student = enrollment.student
        if student.pk in handled or student.pk in attended:
            continue
        if code not in (klass.days_of_week or '').split(','):
            continue
        start = timezone.make_aware(datetime.datetime.combine(today, klass.start_time))
        if klass.end_time:
            end = timezone.make_aware(datetime.datetime.combine(today, klass.end_time))
        else:
            end = start + datetime.timedelta(minutes=klass.duration_minutes)
        if not (start + datetime.timedelta(minutes=minutes) <= now <= end):
            continue
        if ClassAttendance.objects.filter(enrollment=enrollment, date=today, is_present=True).exists():
            continue   # 선생님이 출석부에 이미 출석으로 표시한 학생
        handled.add(student.pk)
        targets += 1
        if send_absence_notice(student, today, klass.name, klass.start_time.strftime('%H:%M'), enrollment.pk):
            sent_students += 1
    return sent_students, targets


class Command(BaseCommand):
    help = '수업 시작 후 기준 시간(기본 10분)이 지나도 출석하지 않은 메듀랩 학생의 학부모에게 미출석 안내 알림톡을 보냅니다.'

    def add_arguments(self, parser):
        parser.add_argument('--minutes', type=int, default=10, help='수업 시작 후 몇 분이 지나도 출석이 없으면 안내할지 (기본 10분)')

    def handle(self, *args, **options):
        if not settings.SOLAPI_TEMPLATE_ABSENCE:
            return   # 알림톡 템플릿(SOLAPI_TEMPLATE_ABSENCE)을 등록하기 전에는 아무것도 하지 않는다 (발송 기록도 남기지 않음)
        sent, targets = send_absence_alerts(minutes=options['minutes'])
        if targets:
            self.stdout.write(f'미출석 안내: 대상 {targets}명 중 {sent}명 발송')
