"""우리말샘 Open API에서 끝말잇기용 명사를 모아 파일로 저장한다.

사용법:  python scripts/harvest_urimalsaem.py [저장폴더]
 - 인증키는 실행하면 숨김 입력으로 물어본다(화면에 안 보이고, 파일/서버에 저장하지 않음).
 - 중간에 멈춰도 같은 폴더로 다시 실행하면 이어서 한다.
 - 하루 요청 한도(50,000건) 가까이 되면 스스로 멈춘다. 내일 다시 실행하면 이어서 한다.
출처: 국립국어원 우리말샘 (CC BY-SA 2.0 KR)
"""
import getpass
import json
import os
import sys
import time
import datetime
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

API = 'https://kdict.korean.go.kr/standard/api/search.do'  # 표준국어대사전
OUT = sys.argv[1] if len(sys.argv) > 1 else r'E:\making_project\wordharvest'
DAILY_LIMIT = 47000
os.makedirs(OUT, exist_ok=True)
WORDS_F = os.path.join(OUT, 'words.json')
STATE_F = os.path.join(OUT, 'state.json')


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default


words = load(WORDS_F, {})
state = load(STATE_F, {'done': [], 'day': '', 'count': 0})
today = datetime.date.today().isoformat()
if state['day'] != today:
    state['day'], state['count'] = today, 0


def save():
    snap = dict(list(words.items()))
    st = {'done': list(state['done']), 'day': state['day'], 'count': state['count']}
    with open(WORDS_F, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)
    with open(STATE_F, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False)


KEY = getpass.getpass('우리말샘 인증키를 입력하세요(입력해도 화면에 안 보입니다): ').strip()
if not KEY:
    sys.exit('키가 비어 있습니다.')


class Stop(Exception):
    pass


WORKERS = 10



def query(q, page, ls, le):
    if state['count'] >= DAILY_LIMIT:
        raise Stop('오늘 요청 한도에 가까워 멈춥니다. 내일 다시 실행하면 이어서 합니다.')
    params = {
        'key': KEY, 'q': q, 'req_type': 'json', 'advanced': 'y', 'method': 'start',
        'pos': '1', 'type1': 'word',
        'letter_s': ls, 'letter_e': le, 'num': 100, 'start': page,
    }
    url = API + '?' + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                raw = r.read().decode('utf-8', 'replace')
            state['count'] += 1
            if not raw.strip():
                return 0, []
            data = json.loads(raw)
            if 'error' in data:
                e = data['error']
                raise Stop('API 오류: %s %s' % (e.get('error_code'), e.get('message')))
            ch = data.get('channel', {})
            items = ch.get('item') or []
            if isinstance(items, dict):
                items = [items]
            return int(ch.get('total', 0) or 0), items
        except Stop:
            raise
        except Exception as e:
            extra = ''
            if hasattr(e, 'code'):
                try:
                    extra = ' 코드=%s %s' % (e.code, e.read().decode('utf-8', 'replace')[:200].replace(KEY, '***'))
                except Exception:
                    extra = ' 코드=%s' % e.code
            print('  재시도(%d) %s%s' % (attempt + 1, type(e).__name__, extra))
            time.sleep(2 * (attempt + 1))
    raise Stop('연결이 계속 실패해 멈춥니다.')


def add(items):
    n = 0
    for it in items:
        w = (it.get('word') or '').strip()
        if not (2 <= len(w) <= 6) or not all('가' <= c <= '힣' for c in w):
            continue
        sense = it.get('sense')
        if isinstance(sense, list):
            sense = sense[0] if sense else {}
        d = ((sense or {}).get('definition') or '')[:60]
        if w not in words:
            words[w] = d
            n += 1
    return n


def fetch_all(q, ls, le):
    total, items = query(q, 1, ls, le)
    got = add(items)
    page = 1
    while total > page * 100 and page < 11:
        page += 1
        _, items = query(q, page, ls, le)
        if not items:
            break
        got += add(items)
    return total, got


try:
    _t, _ = query('가', 1, 2, 3)
except Stop as e:
    sys.exit(str(e))
if _t == 0:
    sys.exit('키 확인 검사에서 결과가 없습니다. 키가 맞는지, 승인이 끝났는지 확인해 주세요.')
print('키 확인 OK (가로 시작하는 2~3글자 명사 %d개)' % _t)

# 낱말 첫 글자로 거의 안 쓰이는 조합(쌍자음 초성 일부, 겹모음, 드문 받침)은 건너뛰어 요청 수를 줄인다
_INIT = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
_VOW = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
_FIN = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
        'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
_OK_INIT = set('ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ')
_OK_VOW = set('ㅏㅐㅑㅓㅔㅕㅗㅘㅚㅛㅜㅝㅟㅠㅡㅢㅣ')
_OK_FIN = {'', 'ㄱ', 'ㄴ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ'}


def _common(ch):
    n = ord(ch) - 0xAC00
    return _INIT[n // 588] in _OK_INIT and _VOW[(n % 588) // 28] in _OK_VOW and _FIN[n % 28] in _OK_FIN


syllables = [chr(c) for c in range(0xAC00, 0xD7A4) if _common(chr(c))]
_done = set(state['done'])
todo = [s for s in syllables if s not in _done]
print('남은 글자 %d / %d, 지금까지 낱말 %d개, 오늘 요청 %d건' % (len(todo), len(syllables), len(words), state['count']))
def work(s):
    total, items = query(s, 1, 2, 8)
    if total > 0:
        if total > 1000:
            for ls, le in ((2, 2), (3, 3), (4, 4), (5, 8)):
                fetch_all(s, ls, le)
        else:
            add(items)
            page = 1
            while total > page * 100 and page < 11:
                page += 1
                _, more = query(s, page, 2, 8)
                if not more:
                    break
                add(more)
    return s


try:
    done_n = 0
    stop_msg = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(work, s) for s in todo]
        for f in as_completed(futs):
            try:
                s = f.result()
            except Stop as e:
                if not stop_msg:
                    stop_msg.append(str(e))
                    print(e)
                    for g in futs:
                        g.cancel()
                continue
            state['done'].append(s)
            done_n += 1
            if done_n % 50 == 0:
                save()
                print('진행 %d/%d  낱말 %d개  오늘 요청 %d건' % (done_n, len(todo), len(words), state['count']))
    if not stop_msg:
        print('수집 끝!')
except Stop as e:
    print(e)
except KeyboardInterrupt:
    print('중단했습니다. 다시 실행하면 이어서 합니다.')
finally:
    save()
    print('저장: %s (낱말 %d개)' % (OUT, len(words)))
