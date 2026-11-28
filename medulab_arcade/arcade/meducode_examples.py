"""메듀코드 예제 업데이트: 관리자(is_staff)가 메듀코드 화면에서 예제를 열어 고치고 [예제 업데이트]를 누른다.

예제의 원본은 메듀코드 빌드에 들어 있고, 관리자가 업데이트한 것만 서버의 MEDUCODE_EXAMPLES 폴더에 보관한다.
  GET  /meducode/api/examples/?id=예제이름   → 업데이트한 내용(data), 없으면 null (화면은 원본을 연다)
  POST /meducode/api/examples/ {id, data}    → 저장 (직전 내용은 .bak 파일로 한 번 남긴다)
"""
import hashlib
import json
import os
import tempfile

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

MAX_BYTES = 2 * 1024 * 1024


def _error(message, status):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _valid_id(value):
    return isinstance(value, str) and 0 < len(value) <= 100 and value.isprintable()


def _path(example_id):
    # 파일 이름은 예제 이름의 해시: 어떤 이름이 와도 정해진 폴더 밖을 가리킬 수 없다
    name = hashlib.sha256(example_id.encode('utf-8')).hexdigest()[:32]
    return os.path.join(settings.MEDUCODE_EXAMPLES, f'{name}.json')


def _load(example_id):
    try:
        with open(_path(example_id), encoding='utf-8') as f:
            return json.load(f)['data']
    except FileNotFoundError:
        return None


def _save(request):
    too_big = '작품이 너무 커요. (2MB까지)'
    if len(request.body) > MAX_BYTES * 2:
        return _error(too_big, 413)
    try:
        body = json.loads(request.body.decode('utf-8'))
        example_id, data = body['id'], body['data']
        if not _valid_id(example_id) or not isinstance(data, str):
            raise ValueError
        project = json.loads(data)
        if not isinstance(project.get('scripts'), dict) or not isinstance(project.get('objects'), list):
            raise ValueError
        size = len(data.encode('utf-8'))
    except (ValueError, KeyError, TypeError, AttributeError):
        return _error('작품 데이터가 올바르지 않아요.', 400)
    if size > MAX_BYTES:
        return _error(too_big, 413)

    os.makedirs(settings.MEDUCODE_EXAMPLES, exist_ok=True)
    path = _path(example_id)
    if os.path.exists(path):
        with open(path, 'rb') as old, open(path + '.bak', 'wb') as backup:
            backup.write(old.read())
    # 임시 파일에 다 쓴 뒤 바꿔치기: 저장 중에 여는 사람이 반쪽짜리를 읽지 않게
    handle, temp = tempfile.mkstemp(dir=settings.MEDUCODE_EXAMPLES, suffix='.tmp')
    with os.fdopen(handle, 'w', encoding='utf-8') as f:
        json.dump({'id': example_id, 'data': data, 'updated_by': request.user.get_username(),
                   'updated_at': timezone.now().isoformat()}, f, ensure_ascii=False)
    os.replace(temp, path)
    return JsonResponse({'ok': True})


@ensure_csrf_cookie
@require_http_methods(['GET', 'POST'])
def api_examples(request):
    if request.method == 'GET':
        example_id = request.GET.get('id', '')
        if not _valid_id(example_id):
            return _error('잘못된 요청이에요.', 400)
        response = JsonResponse({'ok': True, 'data': _load(example_id)})
        response['Cache-Control'] = 'no-store'
        return response
    if not request.user.is_authenticated:
        return _error('로그인이 필요해요.', 401)
    if not request.user.is_staff:
        return _error('관리자만 바꿀 수 있어요.', 403)
    return _save(request)
