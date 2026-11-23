"""관리자용 알림(종 모양 버튼). 새 상담 문의·특강 예약·학부모 결석 사유·신규 가입 같은 일이 생기면 한 줄 알림을 남기고,
홈페이지 상단 종 버튼에서 확인한다. 알림을 남기다 실패해도 원래 하던 일(접수, 결제 등)을 막지 않는다."""
import logging

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import AdminNotification

logger = logging.getLogger(__name__)
KEEP_DAYS_COUNT = 200   # 오래된 알림은 이 개수만 남기고 지운다


def notify_admins(kind, title, body='', url=''):
    try:
        AdminNotification.objects.create(kind=kind, title=title[:150], body=body[:300], url=url[:300])
        stale = AdminNotification.objects.order_by('-id').values_list('id', flat=True)[KEEP_DAYS_COUNT:KEEP_DAYS_COUNT + 1]
        if stale:
            AdminNotification.objects.filter(id__lte=stale[0]).delete()
    except Exception:
        logger.exception('관리자 알림 저장 실패')
    try:
        from .telegram_notify import send_telegram
        send_telegram(f'{title}\n{body}'.strip(), url)
    except Exception:
        logger.exception('텔레그램 알림 실패')


def _staff(user):
    return user.is_staff


def _row(n):
    from django.utils import timezone
    return {'id': n.pk, 'kind': n.kind, 'title': n.title, 'body': n.body, 'url': n.url, 'read': n.is_read,
            'at': timezone.localtime(n.created_at).strftime('%m.%d %H:%M')}


@login_required
@user_passes_test(_staff)
def notification_list(request):
    """종 버튼 목록 + 안 읽은 개수 (화면에서 주기적으로 불러 온다)"""
    items = [_row(n) for n in AdminNotification.objects.all()[:20]]
    return JsonResponse({'unread': AdminNotification.objects.filter(is_read=False).count(), 'items': items})


@login_required
@user_passes_test(_staff)
@require_POST
def notification_read(request, pk=None):
    """pk 가 있으면 그 알림만, 없으면 전체를 읽음 처리"""
    qs = AdminNotification.objects.filter(is_read=False)
    if pk:
        qs = qs.filter(pk=pk)
    qs.update(is_read=True)
    return JsonResponse({'ok': True, 'unread': AdminNotification.objects.filter(is_read=False).count()})
