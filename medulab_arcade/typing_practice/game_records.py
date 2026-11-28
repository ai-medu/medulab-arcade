"""타자게임 레벨 기록. 성공한 레벨만 저장하고, 순위는 '더 높은 레벨'이 앞서며 같은 레벨이면 점수가 높거나 시간이 짧은 쪽이 앞선다."""
import json
import math

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import TypingGameRecord

SCORE_GAMES = ('rain', 'meteor', 'balloon', 'zombie', 'ninja', 'rhythm', 'brick', 'hamster', 'chain')   # 클수록 좋은 기록
TIME_GAMES = ('car', 'rabbit', 'scramble', 'pic', 'blank', 'vault', 'bomb')                          # 짧을수록 좋은 기록(초)
GAMES = SCORE_GAMES + TIME_GAMES
LANGUAGES = ('ko', 'en')
MAX_LEVEL = 10
CHAIN_LEVELS = 4          # 끝말잇기: 1 쉬움, 2 보통, 3 어려움, 4 무한
MIN_SECONDS, MAX_SECONDS = 3, 3600
MAX_SCORE = 5000


def max_level(game):
    return CHAIN_LEVELS if game == 'chain' else MAX_LEVEL


def _better(a, b, game):
    """기록 a 가 b 보다 앞서는가 (a, b 는 (레벨, 값))"""
    if b is None:
        return True
    if a[0] != b[0]:
        return a[0] > b[0]
    return a[1] < b[1] if game in TIME_GAMES else a[1] > b[1]


def display_name(row_user, viewer):
    """전체 최고에 보이는 이름(없으면 아이디). 로그인하지 않은 방문자에게는 가운데를 가린다."""
    profile = getattr(row_user, 'profile', None)
    name = ((profile.real_name if profile else '') or '').strip() or row_user.username
    if viewer.is_authenticated:
        return name
    if len(name) <= 2:
        return name[:1] + '*'
    return name[0] + '*' * (len(name) - 2) + name[-1]


def summary(user, language):
    """게임별 {mine: 내 최고, top: 전체 최고, cleared: 내가 성공한 가장 높은 레벨}. 선생님(직원) 기록은 전체 최고에서 뺀다."""
    games = {g: {'mine': None, 'top': None, 'cleared': 0} for g in GAMES}
    best_top, best_mine = {}, {}
    rows = TypingGameRecord.objects.filter(language=language, game__in=GAMES).select_related('user__profile').order_by(
        'achieved_at', 'id')   # 같은 기록이면 먼저 세운 사람이 최고
    for row in rows:
        key = (row.level, row.value)
        if user.is_authenticated and row.user_id == user.id:
            games[row.game]['cleared'] = max(games[row.game]['cleared'], row.level)
            if _better(key, best_mine.get(row.game), row.game):
                best_mine[row.game] = key
                games[row.game]['mine'] = {'level': row.level, 'value': row.value}
        if not row.user.is_staff and row.user.is_active and _better(key, best_top.get(row.game), row.game):
            best_top[row.game] = key
            games[row.game]['top'] = {'level': row.level, 'value': row.value, 'name': display_name(row.user, user),
                                      'me': user.is_authenticated and row.user_id == user.id}
    return games


def _payload(request, language, **extra):
    return JsonResponse({'ok': True, 'logged_in': request.user.is_authenticated,
                         'unlock_all': request.user.is_staff, 'games': summary(request.user, language), **extra})


def _fail(message, status=400):
    return JsonResponse({'ok': False, 'error': message}, status=status)


@require_http_methods(['GET', 'POST'])
def game_records(request):
    if request.method == 'GET':
        language = request.GET.get('lang', 'ko')
        return _payload(request, language if language in LANGUAGES else 'ko')

    if not request.user.is_authenticated:
        return _fail('로그인하면 기록이 저장돼요.', 401)
    try:
        data = json.loads(request.body)
        game, language = data['game'], data['lang']
        level, value = int(data['level']), float(data['value'])
    except (ValueError, KeyError, TypeError):
        return _fail('기록 형식이 올바르지 않아요.')
    if game not in GAMES or language not in LANGUAGES or not 1 <= level <= max_level(game):
        return _fail('기록 형식이 올바르지 않아요.')
    low, high = (MIN_SECONDS, MAX_SECONDS) if game in TIME_GAMES else (1, MAX_SCORE)
    if not math.isfinite(value) or not low <= value <= high:
        return _fail('기록 값이 올바르지 않아요.')
    mine = TypingGameRecord.objects.filter(user=request.user, game=game, language=language)
    # 앞 레벨을 성공해야 다음 레벨 기록을 남길 수 있다 (끝말잇기 난이도와 선생님은 제외)
    if game != 'chain' and not request.user.is_staff and level > 1 and not mine.filter(level__gte=level - 1).exists():
        return _fail('앞 레벨을 먼저 성공해야 해요.')

    value = round(value, 1)
    record = mine.filter(level=level).first()
    new_best = record is None or _better((level, value), (level, record.value), game)
    if record is None:
        TypingGameRecord.objects.create(user=request.user, game=game, language=language, level=level, value=value)
    elif new_best:
        record.value = value
        record.save()
    response = _payload(request, language, new_best=new_best)
    top = json.loads(response.content)['games'][game]['top']
    is_top = bool(top) and top['me'] and top['level'] == level and top['value'] == value
    return _payload(request, language, new_best=new_best, new_top=new_best and is_top)
