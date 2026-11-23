"""미출석 안내 알림톡의 링크에서 학부모가 결석 사유를 알리는 화면.

알림톡 버튼 주소(/absence/<코드>/)로 들어오면 로그인 없이 결석 사유를 고를 수 있고,
제출하면 그 수업일이 출석부(ClassAttendance)에 '결석'으로 기록된다. (결석 차감은 출석부 기준으로 자동 계산된다)
코드는 서버 비밀키로 서명된 값이라 위조할 수 없고, 일정 기간이 지나면 만료된다.
"""
import datetime

from django.core import signing
from django.shortcuts import render
from django.utils import timezone

from .models import Attendance, ClassAttendance, ClassEnrollment

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
    if request.method == 'POST':
        code = request.POST.get('reason', '')
        detail = request.POST.get('detail', '').strip()[:60]
        if code not in REASON_LABELS:
            context.update(state='form', error='결석 사유를 선택해 주세요.')
            return render(request, 'arcade/absence_report.html', context)
        if code == 'other' and not detail:
            context.update(state='form', error='기타 사유를 입력해 주세요.', selected=code)
            return render(request, 'arcade/absence_report.html', context)
        reason = detail if code == 'other' else REASON_LABELS[code]
        ClassAttendance.objects.update_or_create(
            enrollment=enrollment, date=date,
            defaults={'is_present': False, 'note': (NOTE_PREFIX + reason)[:100]},
        )
        from django.urls import reverse
        from .admin_notify import notify_admins
        notify_admins('absence', f'❌ 결석 사유 접수 — {context["student_name"]}',
                      f'{context["class_name"]} · {date.month}/{date.day} · {reason}',
                      reverse('class_admin_attendance', args=[enrollment.school_class_id]))
        return render(request, 'arcade/absence_report.html', {**context, 'state': 'done', 'reason': reason})

    if record and record.note.startswith(NOTE_PREFIX):
        context.update(state='form', already=record.note[len(NOTE_PREFIX):])
    else:
        context['state'] = 'form'
    return render(request, 'arcade/absence_report.html', context)
