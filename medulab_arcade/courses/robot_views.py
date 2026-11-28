"""로봇 수업(이론·문제 → 로봇 제작 → 로봇 코딩 → 미션 퀘스트) 화면.

Item.robot_data 가 있는 항목이 이 화면을 쓴다. 조립서·교재 그림은 settings.ROBOT_LESSON_DIR 에 두고
로그인한 회원에게만 보낸다 (완성 로봇 작은 그림만 목록 화면용으로 누구에게나 보인다).
"""
import json
import os
import re

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Item, UserProgress

ASSET_NAME = re.compile(r'^(thumb\.jpg|theory\.jpg|guide\.jpg|code\.svg|build-\d{2}\.jpg|ext-\d{2}\.jpg)$')
PASS_PERCENT = 80


def asset_dir(item):
    folder = (item.robot_data or {}).get('key', '')
    if not re.match(r'^[a-z0-9_]+$', folder):
        return None
    return os.path.join(str(settings.ROBOT_LESSON_DIR), folder)


def asset_url(item, name):
    return reverse('robot_asset', args=[item.id, name])


def _asset_urls(item, prefix):
    folder = asset_dir(item)
    if not folder or not os.path.isdir(folder):
        return []
    names = sorted(n for n in os.listdir(folder) if n.startswith(prefix) and ASSET_NAME.match(n))
    return [asset_url(item, n) for n in names]


def send_asset(item, name):
    folder = asset_dir(item) if ASSET_NAME.match(name) else None
    path = os.path.join(folder, name) if folder else None
    if not path or not os.path.isfile(path):
        raise Http404('그림이 없어요.')
    response = FileResponse(open(path, 'rb'), content_type='image/svg+xml' if name.endswith('.svg') else 'image/jpeg')
    response['Cache-Control'] = ('public' if name == 'thumb.jpg' else 'private') + ', max-age=86400'
    if name.endswith('.svg'):
        response['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; img-src data:"
    return response


def load_state(progress):
    """UserProgress.code 에 보관한 로봇 수업 기록 {quiz_best, missions}."""
    try:
        state = json.loads(getattr(progress, 'code', '') or '{}')
    except ValueError:
        state = {}
    if not isinstance(state, dict):
        state = {}
    return {'quiz_best': state.get('quiz_best'), 'missions': list(state.get('missions') or [])}


def render_lesson(request, item, prev_item, next_item, progress):
    data = item.robot_data
    code = data.get('code') or {}
    state = load_state(progress)
    return render(request, 'learning_program/item_page_robot.html', {
        'item': item,
        'program': item.chapter.program,
        'prev_item': prev_item,
        'next_item': next_item,
        'lesson': data,
        'code': code,
        # 정답과 해설은 채점하기 전에는 화면에 보내지 않는다
        'quiz': [{'q': q['q'], 'choices': q['choices']} for q in data.get('quiz', [])],
        'state': state,
        'completed': progress.completed,
        'thumb_url': asset_url(item, 'thumb.jpg'),
        'theory_url': asset_url(item, 'theory.jpg'),
        'guide_url': asset_url(item, 'guide.jpg'),
        'code_url': asset_url(item, 'code.svg'),
        'build_pages': _asset_urls(item, 'build-'),
        'ext_pages': _asset_urls(item, 'ext-'),
        'pass_percent': PASS_PERCENT,
    })


def _body(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def _lesson_item(item_id):
    item = get_object_or_404(Item, id=item_id)
    if not item.robot_data:
        raise Http404
    return item


def grade_quiz(request, item_id):
    item = _lesson_item(item_id)
    quiz = item.robot_data.get('quiz', [])
    answers = _body(request).get('answers')
    if not isinstance(answers, list) or len(answers) != len(quiz) or not all(type(a) is int for a in answers):
        return JsonResponse({'ok': False, 'error': '모든 문제의 답을 골라 주세요.'}, status=400)
    results = [{'correct': a == q['answer'], 'answer': q['answer'], 'explain': q.get('explain', '')}
               for a, q in zip(answers, quiz)]
    right = sum(r['correct'] for r in results)
    percent = round(right * 100 / len(quiz)) if quiz else 0
    progress, _ = UserProgress.objects.get_or_create(user=request.user, item=item)
    state = load_state(progress)
    state['quiz_best'] = max(percent, state['quiz_best'] or 0)
    progress.code = json.dumps(state)
    progress.score = state['quiz_best']
    progress.completed = progress.completed or percent >= PASS_PERCENT
    progress.save()
    return JsonResponse({'ok': True, 'results': results, 'right': right, 'total': len(quiz),
                         'percent': percent, 'passed': percent >= PASS_PERCENT})


def save_mission(request, item_id):
    item = _lesson_item(item_id)
    body = _body(request)
    mission_id = body.get('id')
    if mission_id not in [m['id'] for m in item.robot_data.get('missions', [])]:
        return JsonResponse({'ok': False, 'error': '없는 미션이에요.'}, status=400)
    progress, _ = UserProgress.objects.get_or_create(user=request.user, item=item)
    state = load_state(progress)
    done = set(state['missions'])
    done.add(mission_id) if body.get('done') else done.discard(mission_id)
    state['missions'] = sorted(done)
    progress.code = json.dumps(state)
    progress.save()
    return JsonResponse({'ok': True, 'missions': state['missions']})


quiz_view = require_POST(grade_quiz)
mission_view = require_POST(save_mission)
