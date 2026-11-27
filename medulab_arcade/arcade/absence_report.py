"""미출석 안내 알림톡의 링크에서 학부모가 결석 사유를 알리는 화면.

알림톡 버튼 주소(/absence/<코드>/)로 들어오면 로그인 없이 결석 사유를 고를 수 있고,
제출하면 그 수업일이 출석부(ClassAttendance)에 '결석'으로 기록된다. (결석 차감은 출석부 기준으로 자동 계산된다)
코드는 서버 비밀키로 서명된 값이라 위조할 수 없고, 일정 기간이 지나면 만료된다.
"""
import datetime

from django.core import signing
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from .makeup import MAKEUP_NO, MAKEUP_PREFIX, WEEKDAYS, cancel_planned, month_end, set_makeup
from .models import Attendance, ClassAttendance, ClassEnrollment, SchoolClass

SALT = 'absence-report'
MAX_AGE_SECONDS = 3 * 24 * 3600   # 알림톡을 받고 3일 안에만 열 수 있다

REASONS = [
    ('sick', '몸이 아파서 못 가요'),
    ('school', '학교 행사·시험·방과후 일정이 있어요'),
    ('family', '가족 행사·여행이 있어요'),
    ('other_plan', '다른 학원·일정이 있어요'),
    ('other', '기타 (직접 입력)'),
]
REASON_LABELS = dict(REASONS)
NOTE_PREFIX = '학부모 신청: '




def makeup_slots(student, absent_date, now=None):
    """보강으로 고를 수 있는 시간: 수강생이 있는 수업의 결석한 달의 남은 수업 시간 (같은 시간은 하나로).
    휴원일과, 학생 본인의 정규 수업과 겹치는 시간은 뺀다. [(날짜, [(값, 표시), ...]), ...]"""
    from .views import _holiday_dates_in_month

    now = timezone.localtime(now or timezone.now())
    classes = list(SchoolClass.objects.filter(
        is_active=True, start_time__isnull=False, enrollments__is_active=True).distinct())
    own = list(SchoolClass.objects.filter(
        is_active=True, start_time__isnull=False, enrollments__student=student, enrollments__is_active=True))

    def span(klass, day):
        start = datetime.datetime.combine(day, klass.start_time)
        end = datetime.datetime.combine(day, klass.end_time) if klass.end_time else \
            start + datetime.timedelta(minutes=klass.duration_minutes)
        return start, end

    def meets(klass, day):
        return str(day.isoweekday() % 7) in (klass.days_of_week or '').split(',')

    # 이미 출석했거나 다른 결석의 보강이 잡힌 날은 뺀다
    taken = set(Attendance.objects.filter(user=student).filter(
        Q(attendance_type__in=[Attendance.TYPE_PRESENT, Attendance.TYPE_MAKEUP])
        | Q(attendance_type=Attendance.TYPE_PLANNED) & ~Q(makeup_for=absent_date)
    ).exclude(date=absent_date).values_list('date', flat=True))
    holidays, months, groups = set(), set(), []
    first = max(absent_date, now.date())
    for offset in range((month_end(absent_date) - first).days + 1):   # 보강은 결석한 달 안에서만
        day = first + datetime.timedelta(days=offset)
        if (day.year, day.month) not in months:
            months.add((day.year, day.month))
            holidays |= _holiday_dates_in_month(day.year, day.month)
        if day in holidays or day in taken:
            continue
        busy = [span(k, day) for k in own if meets(k, day)]
        times = set()
        for klass in classes:
            if not meets(klass, day):
                continue
            start, end = span(klass, day)
            if start <= now.replace(tzinfo=None) or any(start < b_end and b_start < end for b_start, b_end in busy):
                continue
            times.add((start.time(), end.time()))
        if times:
            label = f'{day.month}/{day.day}({WEEKDAYS[day.weekday()]})'
            groups.append((label, [(f'{day.isoformat()} {s:%H:%M}', f'{label} {s:%H:%M}~{e:%H:%M}', f'{e:%H:%M}')
                                   for s, e in sorted(times)]))
    # 시작 시각이 같고 끝나는 시각이 다른 수업이 있으므로 값에는 끝나는 시각까지 넣는다
    return [(label, [(f'{value}~{end}', text) for value, text, end in options]) for label, options in groups]


def make_absence_token(enrollment_id, date):
    return signing.dumps({'e': enrollment_id, 'd': date.isoformat()}, salt=SALT, compress=True)


def _load(token):
    try:
        data = signing.loads(token, salt=SALT, max_age=MAX_AGE_SECONDS)
        return ClassEnrollment.objects.select_related('school_class', 'student__profile').get(pk=data['e']), \
            datetime.date.fromisoformat(data['d'])
    except (signing.BadSignature, ClassEnrollment.DoesNotExist, KeyError, ValueError):
        return None, None


def absence_report(request, token):
    enrollment, date = _load(token)
    if enrollment is None:
        return render(request, 'arcade/absence_report.html', {'state': 'invalid'}, status=404)

    student = enrollment.student
    profile = getattr(student, 'profile', None)
    context = {
        'token': token, 'reasons': REASONS, 'date': date,
        'student_name': (profile.real_name if profile and profile.real_name else student.username),
        'class_name': enrollment.school_class.name,
        'start_time': enrollment.school_class.start_time,
    }
    checked_in = Attendance.objects.filter(
        user=student, date=date, attendance_type__in=[Attendance.TYPE_PRESENT, Attendance.TYPE_MAKEUP]).exists()
    marked_present = ClassAttendance.objects.filter(enrollment=enrollment, date=date, is_present=True).exists()
    if checked_in or marked_present:
        return render(request, 'arcade/absence_report.html', {**context, 'state': 'attended'})

    record = ClassAttendance.objects.filter(enrollment=enrollment, date=date, is_present=False).first()
    slots = makeup_slots(student, date)
    slot_labels = {value: text for _, options in slots for value, text in options}
    context['slots'] = slots
    if request.method == 'POST':
        code = request.POST.get('reason', '')
        detail = request.POST.get('detail', '').strip()[:60]
        makeup = request.POST.get('makeup', '')
        slot = request.POST.get('makeup_slot', '')
        if not slots:
            makeup = 'no'   # 이번 달에 고를 시간이 없으면 보강 없이 접수한다
        error = ''
        if code not in REASON_LABELS:
            error = '결석 사유를 선택해 주세요.'
        elif code == 'other' and not detail:
            error = '기타 사유를 입력해 주세요.'
        elif makeup not in ('yes', 'no'):
            error = '보강이 가능한지 선택해 주세요.'
        elif makeup == 'yes' and slot not in slot_labels:
            error = '보강 가능한 시간을 선택해 주세요.'
        if error:
            context.update(state='form', error=error, selected=code, detail=detail, makeup=makeup, slot=slot)
            return render(request, 'arcade/absence_report.html', context)
        reason = detail if code == 'other' else REASON_LABELS[code]
        makeup_text = MAKEUP_NO if makeup == 'no' else MAKEUP_PREFIX + slot_labels[slot]
        ClassAttendance.objects.update_or_create(
            enrollment=enrollment, date=date,
            defaults={'is_present': False, 'note': (NOTE_PREFIX + reason)[:100], 'makeup_request': makeup_text[:60]},
        )
        if makeup == 'yes' and slot in slot_labels:
            day_text, time_text = slot.split(' ')
            start, end = (datetime.datetime.strptime(x, '%H:%M').time() for x in time_text.split('~'))
            set_makeup(student, datetime.date.fromisoformat(day_text), start, end, absent_date=date)
        else:
            cancel_planned(student, date)   # 보강을 바꾸거나 취소하면 전에 잡은 예정은 지운다
        from django.urls import reverse
        from .admin_notify import notify_admins
        notify_admins('absence', f'❌ 결석 사유 접수 — {context["student_name"]}',
                      f'{context["class_name"]} · {date.month}/{date.day} · {reason} · {makeup_text}',
                      reverse('class_admin_attendance', args=[enrollment.school_class_id]))
        return render(request, 'arcade/absence_report.html',
                      {**context, 'state': 'done', 'reason': reason, 'makeup_text': makeup_text})

    if record and record.note.startswith(NOTE_PREFIX):
        context.update(state='form', already=record.note[len(NOTE_PREFIX):], already_makeup=record.makeup_request)
    else:
        context['state'] = 'form'
    return render(request, 'arcade/absence_report.html', context)
