"""결석과 보강 연결. 보강은 출석 기록(Attendance)에 시간과 '어느 날 결석분인지(makeup_for)'를 담아 두고,
출석부의 결석 칸에는 같은 내용을 글(makeup_request)로 남긴다."""
import calendar

from django.utils import timezone

from .models import Attendance, ClassAttendance

MAKEUP_NO = '보강 어려움'
SAME_MONTH_MESSAGE = '보강은 결석한 달 안에서만 가능해요.'
MAKEUP_PREFIX = '보강 예정: '
WEEKDAYS = '월화수목금토일'


def day_label(day):
    return f'{day.month}/{day.day}({WEEKDAYS[day.weekday()]})'


def same_month(a, b):
    return (a.year, a.month) == (b.year, b.month)


def month_end(day):
    return day.replace(day=calendar.monthrange(day.year, day.month)[1])


def slot_label(day, start, end):
    return f'{day_label(day)} {start:%H:%M}~{end:%H:%M}'


def made_up_dates(student_id, dates):
    """보강에 실제로 출석한 결석일 {결석일: 보강한 날}. 아직 '보강 예정'이거나 불참한 보강은 들어가지 않는다."""
    return dict(Attendance.objects.filter(
        user_id=student_id, makeup_for__in=dates,
        attendance_type__in=[Attendance.TYPE_PRESENT, Attendance.TYPE_MAKEUP],
    ).values_list('makeup_for', 'date'))


def sync_request_text(student, absent_date):
    """결석 칸의 보강 안내 글을 실제로 잡혀 있는 보강에 맞춘다 ('보강 어려움'은 보강이 없으면 그대로 둔다)"""
    rows = ClassAttendance.objects.filter(enrollment__student=student, date=absent_date, is_present=False)
    linked = Attendance.objects.filter(user=student, makeup_for=absent_date, makeup_start__isnull=False).order_by('date').last()
    if linked:
        rows.update(makeup_request=(MAKEUP_PREFIX + slot_label(linked.date, linked.makeup_start, linked.makeup_end))[:60])
    else:
        rows.exclude(makeup_request=MAKEUP_NO).update(makeup_request='')


def cancel_planned(student, absent_date):
    """그 결석에 대해 잡아 둔 '보강 예정'을 지운다 (이미 출석한 보강은 남긴다)"""
    Attendance.objects.filter(user=student, makeup_for=absent_date, attendance_type=Attendance.TYPE_PLANNED).delete()
    sync_request_text(student, absent_date)


def set_makeup(student, day, start, end, absent_date=None):
    """day 에 보강을 잡는다. 아직 시작 전이면 '보강 예정', 지난 시간이면 '보강'.
    absent_date 가 있으면 그 결석분으로 연결하고, 그 결석에 잡아 둔 다른 예정은 지운다. 저장한 기록을 돌려준다."""
    now = timezone.localtime()
    kind = Attendance.TYPE_PLANNED if (day, start) > (now.date(), now.time()) else Attendance.TYPE_MAKEUP
    previous = Attendance.objects.filter(user=student, date=day).first()
    old_link = previous.makeup_for if previous else None
    if absent_date:
        Attendance.objects.filter(user=student, makeup_for=absent_date,
                                  attendance_type=Attendance.TYPE_PLANNED).exclude(date=day).delete()
    record, _ = Attendance.objects.update_or_create(
        user=student, date=day,
        defaults={'attendance_type': kind, 'makeup_start': start, 'makeup_end': end,
                  'makeup_for': absent_date or old_link},
    )
    for target in {absent_date, old_link} - {None}:
        sync_request_text(student, target)
    return record
