"""메듀코드(블록코딩 도구) 서비스.

메듀코드는 별도 프로젝트(React + Vite)로 개발하고, 빌드 결과(dist)만 서버의 MEDUCODE_DIST 폴더에 복사해 둔다.
이 뷰가 /meducode/ 아래에서 그 파일들을 그대로 내려 준다. (메듀랩과 같은 서버·같은 도메인이라 로그인 연동도 쉽다)
"""
import json
import os

from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.views.static import serve

from .models import MeduCodeProject


def meducode_app(request, path=''):
    root = settings.MEDUCODE_DIST
    if not os.path.isdir(root):
        raise Http404('메듀코드가 아직 준비되지 않았어요.')
    path = path or 'index.html'
    response = serve(request, path, document_root=root)
    if path == 'index.html':
        response['Cache-Control'] = 'no-cache'   # 새로 배포하면 바로 최신 화면을 받도록
    elif path.startswith('assets/'):
        response['Cache-Control'] = 'public, max-age=31536000, immutable'   # 파일 이름에 해시가 붙어 있어 안전
    else:
        response['Cache-Control'] = 'public, max-age=3600'
    return response


# ───── 계정에 작품 저장/불러오기 API (같은 도메인이라 로그인 세션·CSRF 쿠키를 그대로 쓴다) ─────

def _json_error(message, status):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _summary(project):
    return {'id': project.pk, 'name': project.name, 'size': project.size,
            'updated_at': project.updated_at.isoformat()}


def _limits():
    return {'max_bytes': MeduCodeProject.MAX_BYTES, 'max_projects': MeduCodeProject.MAX_PER_USER}


def _parse_body(request):
    """요청에서 (이름, 작품 JSON 문자열)을 꺼낸다. 문제가 있으면 오류 응답을 돌려준다."""
    if len(request.body) > MeduCodeProject.MAX_BYTES + 4096:
        return _json_error('작품이 너무 커요. (한 작품은 2MB까지 저장할 수 있어요)', 413)
    try:
        body = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return _json_error('잘못된 요청이에요.', 400)
    if not isinstance(body, dict):
        return _json_error('잘못된 요청이에요.', 400)
    name = str(body.get('name') or '').strip()[:100] or '이름 없는 작품'
    data = body.get('data')
    if not isinstance(data, str) or not data:
        return _json_error('저장할 작품 내용이 없어요.', 400)
    if len(data.encode('utf-8')) > MeduCodeProject.MAX_BYTES:
        return _json_error('작품이 너무 커요. (한 작품은 2MB까지 저장할 수 있어요)', 413)
    try:
        if not isinstance(json.loads(data), dict):
            raise ValueError
    except ValueError:
        return _json_error('작품 데이터가 올바르지 않아요.', 400)
    return name, data


@ensure_csrf_cookie   # 화면에서 저장 요청을 보낼 때 쓸 CSRF 쿠키를 내려 준다
@require_http_methods(['GET', 'POST'])
def api_projects(request):
    """GET: 내 작품 목록(로그인 여부 포함). POST: 새 작품 저장."""
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'ok': True, 'logged_in': False, **_limits()})
        projects = [_summary(p) for p in request.user.meducode_projects.defer('data')]
        return JsonResponse({'ok': True, 'logged_in': True, 'username': request.user.get_username(),
                             'projects': projects, **_limits()})
    if not request.user.is_authenticated:
        return _json_error('로그인이 필요해요.', 401)
    parsed = _parse_body(request)
    if isinstance(parsed, JsonResponse):
        return parsed
    name, data = parsed
    if request.user.meducode_projects.count() >= MeduCodeProject.MAX_PER_USER:
        return _json_error(f'작품은 {MeduCodeProject.MAX_PER_USER}개까지 저장할 수 있어요. 안 쓰는 작품을 지워 주세요.', 400)
    project = MeduCodeProject.objects.create(user=request.user, name=name, data=data, size=len(data.encode('utf-8')))
    return JsonResponse({'ok': True, 'project': _summary(project)}, status=201)


@require_http_methods(['GET', 'PUT', 'DELETE'])
def api_project_detail(request, pk):
    if not request.user.is_authenticated:
        return _json_error('로그인이 필요해요.', 401)
    try:
        project = request.user.meducode_projects.get(pk=pk)   # 내 작품만 접근
    except MeduCodeProject.DoesNotExist:
        return _json_error('작품을 찾을 수 없어요.', 404)
    if request.method == 'GET':
        return JsonResponse({'ok': True, 'project': {**_summary(project), 'data': project.data}})
    if request.method == 'DELETE':
        project.delete()
        return JsonResponse({'ok': True})
    parsed = _parse_body(request)
    if isinstance(parsed, JsonResponse):
        return parsed
    project.name, project.data = parsed
    project.size = len(project.data.encode('utf-8'))
    project.save()
    return JsonResponse({'ok': True, 'project': _summary(project)})
