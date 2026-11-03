"""학부모에게 보내는 카카오 알림톡 (출석 알림, 학원비 청구/미납 안내).

발송은 솔라피(Solapi) API를 사용한다. 수신번호는 '학부모-자녀 연결'된 학부모 회원의 전화번호.
SOLAPI_* 설정이 비어 있으면 실제 발송 없이 NotificationLog에 '테스트(미발송)'으로만 남긴다.
알림 실패가 출석 기록이나 청구서 생성을 막지 않도록, 바깥으로 예외를 던지지 않는다.
"""
import hashlib
import hmac
import logging
import re
import secrets
import threading
from datetime import datetime, timezone as dt_timezone

import requests
from django.conf import settings
from django.db import close_old_connections
from django.urls import reverse
from django.utils import timezone

from .models import NotificationLog, ParentChildLink, TuitionInvoice

logger = logging.getLogger(__name__)

SOLAPI_SEND_URL = 'https://api.solapi.com/messages/v4/send'


def _normalize_phone(raw):
    digits = re.sub(r'\D', '', raw or '')
    if digits.startswith('82') and len(digits) >= 11:
        digits = '0' + digits[2:]
    return digits if re.fullmatch(r'01\d{8,9}', digits) else ''


def parent_phones(student):
    """학생에게 연결된 학부모 회원들의 휴대폰 번호 (중복 제거)"""
    phones = []
    links = ParentChildLink.objects.filter(child=student).select_related('parent__profile')
    for link in links:
        profile = getattr(link.parent, 'profile', None)
        phone = _normalize_phone(profile.phone_number if profile else '')
        if phone and phone not in phones:
            phones.append(phone)
    return phones


def _student_name(student):
    profile = getattr(student, 'profile', None)
    return (profile.real_name if profile and profile.real_name else student.username)


def _is_configured(template_id):
    return all([settings.SOLAPI_API_KEY, settings.SOLAPI_API_SECRET, settings.SOLAPI_PF_ID,
                settings.SOLAPI_SENDER, template_id])


def _auth_header():
    date = datetime.now(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    salt = secrets.token_hex(16)
    signature = hmac.new(settings.SOLAPI_API_SECRET.encode(), (date + salt).encode(), hashlib.sha256).hexdigest()
    return f'HMAC-SHA256 apiKey={settings.SOLAPI_API_KEY}, date={date}, salt={salt}, signature={signature}'


def _post_alimtalk(phone, template_id, variables, buttons=None):
    """솔라피에 알림톡 1건 발송. (성공 여부, 상세 메시지) 반환"""
    kakao = {
        'pfId': settings.SOLAPI_PF_ID,
        'templateId': template_id,
        'variables': variables,
        'disableSms': not settings.SOLAPI_SMS_FALLBACK,
    }
    if buttons:
        kakao['buttons'] = buttons
    body = {'message': {'to': phone, 'from': _normalize_phone(settings.SOLAPI_SENDER), 'kakaoOptions': kakao}}
    try:
        resp = requests.post(SOLAPI_SEND_URL, json=body, headers={'Authorization': _auth_header()}, timeout=10)
    except requests.RequestException as exc:
        return False, f'요청 오류: {exc}'[:300]
    if resp.status_code != 200:
        return False, f'HTTP {resp.status_code}: {resp.text}'[:300]
    return True, ''


def _deliver(kind, student, phone, template_id, variables, buttons=None, invoice=None, target_date=None):
    """한 수신자에게 발송하고 NotificationLog를 남긴다"""
    common = dict(kind=kind, student=student, invoice=invoice, target_date=target_date, phone=phone)
    if not _is_configured(template_id):
        NotificationLog.objects.create(status=NotificationLog.STATUS_DRYRUN, detail='알림톡 설정 미완료로 발송하지 않음', **common)
        return False
    ok, detail = _post_alimtalk(phone, template_id, variables, buttons)
    NotificationLog.objects.create(status=NotificationLog.STATUS_SENT if ok else NotificationLog.STATUS_FAILED,
                                   detail=detail, **common)
    if not ok:
        logger.warning('알림톡 발송 실패 student=%s kind=%s: %s', student.pk, kind, detail)
    return ok


def _already_sent(**filters):
    return NotificationLog.objects.filter(status=NotificationLog.STATUS_SENT, **filters).exists()


def _no_parent(kind, student, **extra):
    NotificationLog.objects.create(kind=kind, student=student, status=NotificationLog.STATUS_SKIPPED,
                                   detail='연결된 학부모 휴대폰 번호가 없음', **extra)


# ---------------------------------------------------------------- 출석 알림

def _send_attendance_now(student_id, date, attendance_type, time_label):
    from django.contrib.auth.models import User
    try:
        student = User.objects.select_related('profile').get(pk=student_id)
        if _already_sent(kind=NotificationLog.KIND_ATTENDANCE, student=student, target_date=date):
            return
        phones = parent_phones(student)
        if not phones:
            _no_parent(NotificationLog.KIND_ATTENDANCE, student, target_date=date)
            return
        variables = {
            '#{학생이름}': _student_name(student),
            '#{구분}': '보강 출석' if attendance_type == 'makeup' else '출석',
            '#{시각}': time_label,
            '#{날짜}': f'{date.month}월 {date.day}일',
        }
        for phone in phones:
            _deliver(NotificationLog.KIND_ATTENDANCE, student, phone,
                     settings.SOLAPI_TEMPLATE_ATTENDANCE, variables, target_date=date)
    except Exception:
        logger.exception('출석 알림톡 처리 중 오류')
    finally:
        close_old_connections()


def notify_attendance(attendance):
    """학원 출석(정규 출석/보강)이 기록되면 학부모에게 알림톡을 보낸다. 하루 한 번만 보낸다.
    외부 API 대기가 학생의 화면 응답을 지연시키지 않도록 별도 스레드에서 처리한다."""
    if attendance.attendance_type not in ('present', 'makeup'):
        return
    if attendance.date != timezone.localdate():
        return
    time_label = timezone.localtime().strftime('%H:%M')
    _spawn(_send_attendance_now, attendance.user_id, attendance.date, attendance.attendance_type, time_label)


def _spawn(target, *args):
    threading.Thread(target=target, args=args, daemon=True).start()


# ---------------------------------------------------------------- 학원비 청구/미납 안내

def tuition_pay_url(invoice):
    token = invoice.ensure_pay_token()
    return settings.SITE_BASE_URL.rstrip('/') + reverse('tuition_pay_public', args=[token])


def send_invoice_notice(invoice, kind=NotificationLog.KIND_INVOICE):
    """청구서 안내 알림톡 (결제 링크 포함). 보낸 건수를 반환. 이미 발송했거나 완납/취소면 0.
    kind=KIND_REMINDER 이면 미납 독촉 안내(이미 보낸 청구 안내와 별개로 하루 한 번 제한)."""
    if invoice.status != TuitionInvoice.STATUS_UNPAID:
        return 0
    today = timezone.localdate()
    if kind == NotificationLog.KIND_INVOICE:
        if _already_sent(kind=kind, invoice=invoice):
            return 0
    elif _already_sent(kind=kind, invoice=invoice, target_date=today):
        return 0

    student = invoice.student
    phones = parent_phones(student)
    if not phones:
        _no_parent(kind, student, invoice=invoice, target_date=today)
        return 0

    pay_token = invoice.ensure_pay_token()
    overdue = invoice.due_date < today
    variables = {
        '#{학생이름}': _student_name(student),
        '#{청구월}': invoice.billing_period_label,
        '#{수업명}': invoice.school_class.name,
        '#{금액}': f'{invoice.amount:,}원',
        '#{납부기한}': invoice.due_date.strftime('%Y.%m.%d'),
        '#{납부상태}': '납부 기한이 지난 미납 상태입니다.' if overdue else '아직 납부 전입니다.',
        # 템플릿 버튼 링크를 https://medulab.kr/pay/#{결제코드}/ 로 등록해 두면 이 값으로 결제 주소가 완성된다
        '#{결제코드}': pay_token,
    }
    sent = 0
    for phone in phones:
        if _deliver(kind, student, phone, settings.SOLAPI_TEMPLATE_INVOICE, variables,
                    invoice=invoice, target_date=today):
            sent += 1
    return sent
