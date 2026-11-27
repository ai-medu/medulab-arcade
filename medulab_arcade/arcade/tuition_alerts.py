"""납부 관리 관련 관리자 알림(종 모양 버튼): 학부모 결제 완료, 환불·취소, 납부 기한 안내.
알림을 만들다 실패해도 결제 처리나 화면을 막지 않는다."""
import logging

from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from .admin_notify import notify_admins
from .models import AdminNotification, TuitionInvoice

logger = logging.getLogger(__name__)


def _name(student):
    profile = getattr(student, 'profile', None)
    return (profile.real_name if profile else '') or student.username


def _student_url(student_id):
    return f"{reverse('tuition_admin_dashboard')}?student_id={student_id}"


def notify_paid(invoices, method=''):
    """학부모가 온라인으로 결제를 마쳤을 때. 여러 건을 한 번에 결제하면 알림 한 줄로 묶는다."""
    try:
        invoices = list(invoices)
        if not invoices:
            return
        names = list(dict.fromkeys(_name(inv.student) for inv in invoices))
        who = names[0] + (f' 외 {len(names) - 1}명' if len(names) > 1 else '')
        total = sum(inv.amount for inv in invoices)
        first = invoices[0]
        what = f'{first.billing_period_label} {first.school_class.name}'
        if len(invoices) > 1:
            what += f' 외 {len(invoices) - 1}건'
        url = (_student_url(first.student_id) if len(names) == 1
               else reverse('tuition_admin_dashboard') + '?view=paid')
        body = ' · '.join(x for x in (what, method) if x)
        notify_admins('tuition_paid', f'💳 학원비 결제 완료 — {who} {total:,}원', body, url)
    except Exception:
        logger.exception('결제 완료 알림 실패')


def notify_canceled(invoice, refunded, reason, by=''):
    """관리자가 완납 청구서를 취소(환불)했을 때"""
    try:
        label = '환불' if refunded else '취소(환불 없음)'
        amount = refunded or invoice.amount
        body = ' · '.join(x for x in (
            f'{invoice.billing_period_label} {invoice.school_class.name}', reason, f'처리: {by}' if by else '') if x)
        notify_admins('tuition_cancel', f'↩️ 학원비 {label} — {_name(invoice.student)} {amount:,}원',
                      body, _student_url(invoice.student_id))
    except Exception:
        logger.exception('환불 알림 실패')


def notify_due_summary():
    """오늘이 납부 기한이거나 기한이 지난 미납이 있으면 하루에 한 번 알린다.
    따로 예약 작업을 두지 않고, 관리자가 사이트를 열어 종 알림을 불러올 때 확인한다."""
    try:
        today = timezone.localdate()
        start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        if AdminNotification.objects.filter(kind='tuition_due', created_at__gte=start).exists():
            return
        unpaid = TuitionInvoice.objects.filter(status=TuitionInvoice.STATUS_UNPAID)
        overdue = unpaid.filter(due_date__lt=today)
        due_today = unpaid.filter(due_date=today)
        overdue_count, today_count = overdue.count(), due_today.count()
        if not overdue_count and not today_count:
            return
        parts, body = [], []
        if overdue_count:
            parts.append(f'기한 지난 미납 {overdue_count}건')
            body.append(f"기한 지남 {overdue.aggregate(s=Sum('amount'))['s']:,}원")
        if today_count:
            parts.append(f'오늘 기한 {today_count}건')
            body.append(f"오늘 기한 {due_today.aggregate(s=Sum('amount'))['s']:,}원")
        notify_admins('tuition_due', '⏰ 학원비 납부 안내 — ' + ', '.join(parts), ' · '.join(body),
                      reverse('tuition_admin_dashboard') + '?view=unpaid')
    except Exception:
        logger.exception('미납 요약 알림 실패')
