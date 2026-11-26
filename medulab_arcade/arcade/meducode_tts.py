"""메듀코드 TTS: 글자를 받아 로봇에 저장할 음성(16kHz WAV)으로 만들어 준다.

구글 Text-to-Speech 의 키는 브라우저에 넣으면 누구나 볼 수 있으므로 서버가 대신 호출한다.
호출량이 곧 비용이라서: 로그인한 회원만, 회원별 하루 글자 수와 전체 월 글자 수를 제한하고,
한 번 만든 문장은 파일로 보관해 다시 만들지 않는다.

메듀코드(src/hardware/rb100/ttsSynth.js)와의 약속:
  POST /meducode/api/tts/  {"text": "안녕하세요", "voice": "ko-KR-Standard-A"}   (voice 는 없어도 됨)
  "speed"·"pitch"·"volume" 은 STYLES 의 낱말 (없으면 "normal")
  성공 {"ok": true, "audio": "<WAV base64>"}   실패 {"ok": false, "error": "화면에 보여 줄 까닭"}
"""
import base64
import binascii
import hashlib
import json
import logging
import os
import tempfile
from pathlib import Path

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables
from django.views.decorators.http import require_http_methods

from .meducode_settings import VOICES, tts_config
from .models import MeduCodeTtsUsage

logger = logging.getLogger(__name__)

GOOGLE_TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
MAX_TEXT_LENGTH = 100        # 메듀코드의 TTS 블록 제한과 같게
SAMPLE_RATE = 16000          # 로봇에 저장하는 음성의 속도


# TTS 블록의 설정 → 구글의 값. 메듀코드 tools/dev-tts-server.js 의 STYLES 와 같게
STYLES = {
    'speed': ('speakingRate', {'slow': 0.8, 'normal': 1.0, 'fast': 1.25}),
    'pitch': ('pitch', {'low': -4.0, 'normal': 0.0, 'high': 4.0}),
    'volume': ('volumeGainDb', {'low': -6.0, 'normal': 0.0, 'high': 6.0}),
}


def _audio_config(body):
    """요청의 설정 → 구글 audioConfig. 목록에 없는 값이면 None."""
    audio = {'audioEncoding': 'LINEAR16', 'sampleRateHertz': SAMPLE_RATE}
    for name, (field, values) in STYLES.items():
        choice = body.get(name) or 'normal'
        if not isinstance(choice, str) or choice not in values:
            return None
        audio[field] = values[choice]
    return audio


def _error(message, status):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _cache_path(voice, audio, text):
    key = hashlib.sha256(f'{voice}|{json.dumps(audio, sort_keys=True)}|{text}'.encode('utf-8')).hexdigest()
    return Path(settings.MEDUCODE_TTS_CACHE) / f'{key}.wav'


def _save_cache(path, audio):
    """쓰다가 끊겨도 반쪽 파일이 남지 않게 임시 파일에 쓰고 이름을 바꾼다. 보관에 실패해도 응답은 한다."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
        with os.fdopen(fd, 'wb') as f:
            f.write(audio)
        os.replace(temp, path)
    except OSError:
        logger.warning('메듀코드 TTS 음성을 보관하지 못했습니다', exc_info=True)


@transaction.atomic
def _reserve(user, count, config):
    """쓸 글자 수를 미리 올려 둔다. 한도를 넘으면 까닭을 돌려준다."""
    today = timezone.localdate()
    MeduCodeTtsUsage.objects.get_or_create(user=user, date=today)
    usage = MeduCodeTtsUsage.objects.select_for_update().get(user=user, date=today)
    if usage.chars + count > config['user_daily_chars']:
        return '오늘 만들 수 있는 음성을 모두 썼어요. 내일 다시 해 주세요.'
    month = MeduCodeTtsUsage.objects.filter(date__year=today.year, date__month=today.month)
    if (month.aggregate(total=Sum('chars'))['total'] or 0) + count > config['monthly_chars']:
        return '이번 달 음성 사용량이 가득 찼어요. 선생님께 알려 주세요.'
    usage.chars += count
    usage.save(update_fields=['chars'])
    return None


def _refund(user, count):
    MeduCodeTtsUsage.objects.filter(user=user, date=timezone.localdate(), chars__gte=count).update(chars=F('chars') - count)


@sensitive_variables()
def _ask_google(text, voice, audio_config, config):
    """구글에서 WAV 바이트를 받아 온다. 실패하면 None."""
    try:
        res = requests.post(
            GOOGLE_TTS_URL,
            headers={'X-Goog-Api-Key': config['key']},   # 주소에 넣으면 접속 기록에 남는다
            json={
                'input': {'text': text},
                'voice': {'languageCode': '-'.join(voice.split('-')[:2]), 'name': voice},
                'audioConfig': audio_config,
            },
            timeout=15,
        )
        if res.status_code != 200:
            logger.error('구글 TTS 실패: %s %s', res.status_code, res.text[:300])
            return None
        return base64.b64decode(res.json()['audioContent'], validate=True) or None
    except (requests.RequestException, KeyError, ValueError, binascii.Error):
        logger.exception('구글 TTS 호출 오류')
        return None


def _my_usage(user):
    usage = MeduCodeTtsUsage.objects.filter(user=user, date=timezone.localdate()).first()
    return JsonResponse({'ok': True, 'used_today': usage.chars if usage else 0,
                         'user_daily_chars': tts_config()['user_daily_chars']})


@require_http_methods(['GET', 'POST'])
@sensitive_variables()
def api_tts(request):
    """GET: 내 오늘 사용량.  POST: 음성 만들기."""
    if not request.user.is_authenticated:
        return _error('로봇에 말을 저장하려면 메듀랩에 로그인해 주세요.', 401)
    if request.method == 'GET':
        return _my_usage(request.user)
    try:
        body = json.loads(request.body.decode('utf-8'))
        text = body['text']
        if not isinstance(text, str):
            raise ValueError
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return _error('잘못된 요청이에요.', 400)
    text = text.strip()
    if not text:
        return _error('말할 글자를 적어 주세요.', 400)
    if len(text) > MAX_TEXT_LENGTH:
        return _error(f'문장은 {MAX_TEXT_LENGTH}자까지 말할 수 있어요.', 400)

    voice = body.get('voice') or settings.MEDUCODE_TTS_VOICE
    if voice != settings.MEDUCODE_TTS_VOICE and voice not in VOICES:
        return _error('고를 수 없는 목소리예요.', 400)

    audio_config = _audio_config(body)
    if audio_config is None:
        return _error('고를 수 없는 설정이에요.', 400)

    config = tts_config()
    path = _cache_path(voice, audio_config, text)
    if path.is_file():   # 이미 만든 문장은 사용량에 넣지 않는다
        return JsonResponse({'ok': True, 'audio': base64.b64encode(path.read_bytes()).decode('ascii')})
    if not config['key']:
        return _error('음성 서비스가 아직 설정되지 않았어요. 선생님께 알려 주세요.', 503)
    refused = _reserve(request.user, len(text), config)
    if refused:
        return _error(refused, 429)
    audio = _ask_google(text, voice, audio_config, config)
    if audio is None:
        _refund(request.user, len(text))
        return _error('음성을 만들지 못했어요. 잠시 뒤에 다시 해 주세요.', 502)
    _save_cache(path, audio)
    return JsonResponse({'ok': True, 'audio': base64.b64encode(audio).decode('ascii')})
