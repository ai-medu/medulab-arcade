"""코딩기초 미션 수업 화면. 설명·힌트는 이 화면에, 블록코딩과 무대는 메듀코드 미션 모드(iframe)가 맡는다.

Item.mission_data 가 있는 항목이 이 화면을 쓴다. 성공 판정은 메듀코드가 하고, 여기서는 기록(별·작성한 블록)만 저장한다.
"""
import json

from django.http import JsonResponse
from django.shortcuts import render

from .models import Item, UserProgress

MAX_XML = 40000


def load_record(progress):
    """UserProgress.code 에 보관한 미션 기록 {stars, xml}. 예전 기록(JSON 이 아닌 글)은 빈 기록으로 본다."""
    try:
        record = json.loads(getattr(progress, 'code', '') or '{}')
    except ValueError:
        record = {}
    if not isinstance(record, dict):
        record = {}
    stars = record.get('stars')
    return {'stars': stars if stars in (1, 2, 3) else 0, 'xml': record.get('xml') or ''}


def attach_stars(items, progresses):
    """목록 화면용: 항목마다 받은 별 수를 item.stars 에 담는다."""
    stars = {p.item_id: load_record(p)['stars'] for p in progresses}
    for item in items:
        item.stars = stars.get(item.id, 0)


def render_mission(request, item, prev_item, next_item, progress):
    data = item.mission_data
    siblings = list(Item.objects.filter(chapter__program=item.chapter.program, mission_data__isnull=False)
                    .order_by('chapter__number', 'number'))
    records = {p.item_id: p for p in UserProgress.objects.filter(user=request.user, item__in=siblings)} \
        if request.user.is_authenticated else {}
    steps = [{
        'id': other.id,
        'label': f'{other.chapter.number}-{other.number}',
        'title': other.title,
        'done': bool(records.get(other.id) and records[other.id].completed),
        'current': other.id == item.id,
    } for other in siblings if other.chapter_id == item.chapter_id]
    record = load_record(progress)
    return render(request, 'learning_program/item_page_mission.html', {
        'item': item,
        'program': item.chapter.program,
        'prev_item': prev_item,
        'next_item': next_item,
        'mission': data,
        'label': f'{item.chapter.number}-{item.number}',
        'steps': steps,
        'stars': record['stars'],
        'page_data': {'spec': data['spec'], 'xml': record['xml']},
        'completed': progress.completed,
    })


def save_result(request, item):
    """실행 결과 저장. 새로 생긴 배지를 알려 줄 수 있게 (응답, 성공 여부) 를 돌려준다."""
    try:
        body = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        body = None
    if not isinstance(body, dict):
        return JsonResponse({'ok': False, 'error': '잘못된 요청이에요.'}, status=400), False
    success, stars, xml = body.get('success'), body.get('stars'), body.get('xml', '')
    if type(success) is not bool or type(stars) is not int or not isinstance(xml, str) or len(xml) > MAX_XML \
            or (success and stars not in (1, 2, 3)):
        return JsonResponse({'ok': False, 'error': '결과를 저장할 수 없어요.'}, status=400), False
    progress, _ = UserProgress.objects.get_or_create(user=request.user, item=item)
    record = load_record(progress)
    if success:
        record['stars'] = max(record['stars'], stars)
        progress.completed = True
    # 성공한 풀이는 뒤에 실패한 시도로 덮어쓰지 않는다
    if success or not progress.completed:
        record['xml'] = xml
    progress.code = json.dumps(record, ensure_ascii=False)
    progress.score = round(record['stars'] * 100 / 3)
    progress.last_output = str(body.get('message', ''))[:200]
    progress.save()
    return None, success
