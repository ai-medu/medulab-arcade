"""관리자용 '안내 메시지' 관리: 자주 보내는 안내 문구를 저장해 두고, 복사 버튼으로 바로 가져다 쓴다."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import AdminMessage


def _staff(user):
    return user.is_staff


@login_required
@user_passes_test(_staff)
def message_list(request):
    items = list(AdminMessage.objects.all())
    return render(request, 'arcade/admin/message_list.html', {
        'items': items, 'title': '안내 메시지',
        'items_json': [{'id': m.pk, 'title': m.title, 'body': m.body, 'order': m.display_order} for m in items],
    })


@login_required
@user_passes_test(_staff)
@require_POST
def message_save(request, pk=None):
    title = request.POST.get('title', '').strip()[:100]
    body = request.POST.get('body', '').replace('\r\n', '\n').strip()
    if not title or not body:
        messages.error(request, '제목과 내용을 모두 입력해 주세요.')
        return redirect('admin_message_list')
    try:
        order = max(0, int(request.POST.get('display_order') or 0))
    except ValueError:
        order = 0
    if pk:
        item = get_object_or_404(AdminMessage, pk=pk)
        item.title, item.body, item.display_order = title, body, order
        item.save()
        messages.success(request, f'"{title}" 안내 메시지를 수정했어요.')
    else:
        if not request.POST.get('display_order'):
            last = AdminMessage.objects.order_by('-display_order').first()
            order = (last.display_order + 1) if last else 0
        AdminMessage.objects.create(title=title, body=body, display_order=order)
        messages.success(request, f'"{title}" 안내 메시지를 추가했어요.')
    return redirect('admin_message_list')


@login_required
@user_passes_test(_staff)
@require_POST
def message_delete(request, pk):
    item = get_object_or_404(AdminMessage, pk=pk)
    title = item.title
    item.delete()
    messages.success(request, f'"{title}" 안내 메시지를 삭제했어요.')
    return redirect('admin_message_list')
