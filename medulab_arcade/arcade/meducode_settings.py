"""메듀코드 관리자 설정: 메듀코드 화면의 [설정] 창에서 관리자(is_staff)가 TTS 키·사용량 한도를 바꾼다 (목소리는 TTS 블록에서 고른다).

키는 비용이 드는 정보라서
 - DB 에는 SECRET_KEY 로 암호화해 저장하고 (DB 파일·백업만으로는 읽을 수 없게),
 - 화면에는 어떤 경우에도 다시 내려보내지 않는다 (저장돼 있는지와 끝 4자리만).
화면에서 정하지 않은 값은 settings.py(.env)의 값을 쓴다.
"""
import base64
import hashlib
import json
import re

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_variables
from django.views.decorators.http import require_http_methods

from .models import MeduCodeSetting, MeduCodeTtsUsage

# TTS 블록에서 고를 수 있는 한국어 표준 음성 (요금이 다른 종류의 음성은 넣지 않는다). 메듀코드 src/blocks/ttsVoices.js 와 같게
VOICES = ('ko-KR-Standard-A', 'ko-KR-Standard-B', 'ko-KR-Standard-C', 'ko-KR-Standard-D')
KEY_PATTERN = re.compile(r'[A-Za-z0-9_\-]{20,200}')
MAX_LIMIT = 10_000_000


def _cipher():
    digest = hashlib.sha256(b'meducode-setting|' + settings.SECRET_KEY.encode('utf-8')).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


@sensitive_variables()
def _stored_key(row):
    if not row or not row.tts_key_encrypted:
        return ''
    try:
        return _cipher().decrypt(row.tts_key_encrypted.encode('ascii')).decode('utf-8')
    except (InvalidToken, ValueError):   # SECRET_KEY 가 바뀌면 다시 입력해야 한다
        return ''


@sensitive_variables()
def tts_config():
    """지금 쓰는 TTS 설정. key_source: 'admin'(설정 창) | 'env'(.env) | ''(없음)"""
    row = MeduCodeSetting.objects.filter(pk=1).first()
    key = _stored_key(row)
    source = 'admin' if key else ('env' if settings.GOOGLE_TTS_API_KEY else '')

    def pick(value, default):
        return default if value in (None, '') else value

    return {
        'key': key or settings.GOOGLE_TTS_API_KEY,
        'key_source': source,
        'user_daily_chars': pick(row and row.tts_user_daily_chars, settings.MEDUCODE_TTS_USER_DAILY_CHARS),
        'monthly_chars': pick(row and row.tts_monthly_chars, settings.MEDUCODE_TTS_MONTHLY_CHARS),
    }


def _usage_by_member(month, today):
    """이번 달에 쓴 회원별 사용량 (많이 쓴 순서, 100명까지)"""
    rows = (month.values('user__username', 'user__last_name', 'user__first_name')
            .annotate(month_chars=Sum('chars'), today_chars=Sum('chars', filter=Q(date=today)))
            .filter(month_chars__gt=0).order_by('-month_chars', 'user__username')[:100])
    return [{'user': r['user__username'], 'name': f"{r['user__last_name']}{r['user__first_name']}".strip(),
             'today': r['today_chars'] or 0, 'month': r['month_chars']} for r in rows]


@sensitive_variables()
def _public_state():
    config = tts_config()
    today = timezone.localdate()
    month = MeduCodeTtsUsage.objects.filter(date__year=today.year, date__month=today.month)
    return {
        'ok': True,
        'has_key': bool(config['key']),
        'key_source': config['key_source'],
        'key_hint': config['key'][-4:],
        'user_daily_chars': config['user_daily_chars'],
        'monthly_chars': config['monthly_chars'],
        'used_today': month.filter(date=today).aggregate(total=Sum('chars'))['total'] or 0,
        'used_this_month': month.aggregate(total=Sum('chars'))['total'] or 0,
        'usage': _usage_by_member(month, today),
    }


def _error(message, status):
    return JsonResponse({'ok': False, 'error': message}, status=status)


@sensitive_variables()
def _save(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        if not isinstance(body, dict):
            raise ValueError
    except (ValueError, UnicodeDecodeError):
        return _error('잘못된 요청이에요.', 400)

    changes = {}
    key = body.get('api_key', '')
    if not isinstance(key, str):
        return _error('API 키 형식이 올바르지 않아요.', 400)
    key = key.strip()
    if key:
        if not KEY_PATTERN.fullmatch(key):
            return _error('API 키 형식이 올바르지 않아요. 복사한 키 전체를 그대로 넣어 주세요.', 400)
        changes['tts_key_encrypted'] = _cipher().encrypt(key.encode('utf-8')).decode('ascii')
    elif body.get('remove_key') is True:
        changes['tts_key_encrypted'] = ''
    for name, field, label in (('user_daily_chars', 'tts_user_daily_chars', '회원별 하루 글자 수'),
                               ('monthly_chars', 'tts_monthly_chars', '월 전체 글자 수')):
        if name in body:
            value = body[name]
            if type(value) is not int or not 0 <= value <= MAX_LIMIT:
                return _error(f'{label}는 0부터 {MAX_LIMIT:,}까지의 숫자로 적어 주세요.', 400)
            changes[field] = value

    row, _ = MeduCodeSetting.objects.get_or_create(pk=1)
    for field, value in changes.items():
        setattr(row, field, value)
    row.updated_by = request.user
    row.save()
    return JsonResponse(_public_state())


@ensure_csrf_cookie
@require_http_methods(['GET', 'POST'])
def api_settings(request):
    if not request.user.is_authenticated:
        return _error('로그인이 필요해요.', 401)
    if not request.user.is_staff:
        return _error('관리자만 바꿀 수 있어요.', 403)
    if request.method == 'GET':
        return JsonResponse(_public_state())
    return _save(request)
