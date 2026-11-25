"""수집한 words.json 으로 끝말잇기 낱말 파일을 만든다.

만드는 파일
 - typing_practice/data/ko_words.txt           : 사전에 있는 모든 낱말(서버가 '사전에 있는 말인지' 검사할 때 사용)
 - typing_practice/static/typing_practice/ko_common.json : 컴퓨터가 낼 '자주 쓰는 낱말' (보통/어려움 난이도)
출처: 국립국어원 표준국어대사전 (CC BY-SA 2.0 KR)

'자주 쓰는 낱말'은 사전 뜻풀이에 얼마나 자주 등장하는지로 판단한다(자주 쓰는 말일수록 다른 낱말 뜻풀이에도 많이 나온다).
사용법: python scripts/build_chain_words.py [words.json 경로]
"""
import json
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else r'E:\making_project\wordharvest\words.json'
with open(SRC, encoding='utf-8') as f:
    words = json.load(f)

allw = sorted(w for w in words if 2 <= len(w) <= 6)
wset = set(allw)
print('전체 낱말', len(allw))

# 뜻풀이에 등장하는 횟수 세기 (2~4글자 부분 문자열)
cnt = Counter()
run = re.compile(r'[가-힣]+')
JOSA = ['으로', '에서', '에게', '이다', '하는', '하고', '한다', '하여', '이나', '이며', '보다', '처럼', '까지',
        '을', '를', '이', '가', '은', '는', '의', '에', '로', '와', '과', '도', '만', '나', '고', '며', '인', '한', '함']
for d in words.values():
    seen = set()
    for r in run.findall(d):
        # 낱말 전체 또는 뒤의 조사를 떼어낸 것이 사전 낱말과 같을 때만 센다(부분 문자열은 세지 않음)
        if r in wset:
            seen.add(r)
        for j in JOSA:
            if r.endswith(j) and len(r) > len(j) and r[:-len(j)] in wset:
                seen.add(r[:-len(j)])
    cnt.update(seen)

# 이름·지명·옛말 같은 낱말을 걸러내는 뜻풀이 단서
BAD = re.compile(r'(지명|인명|도시|수도|나라의|시대|왕조|성씨|본관|신라|고려|조선|백제|고구려|한자|옛|준말|약어|어원|화학|물리|의학|생물|식물의|동물의|벼슬|관청|관직|제도|조약|전쟁|종교|불교|천주교|기독교|유교|음악|악기)')
ok = lambda w: not BAD.search(words[w]) and w[-1] not in '의은고'

# 컴퓨터가 낼 낱말: 2~4글자, 뜻풀이에 3번 이상 등장(자주 쓰는 말)이면서 단서에 안 걸리는 것
common = [w for w in allw if 2 <= len(w) <= 4 and cnt[w] >= 3 and ok(w)]
# 보통 난이도: 2~3글자이면서 더 자주 등장하는 것
mid = [w for w in common if len(w) <= 3 and cnt[w] >= 8]
print('자주 쓰는 낱말', len(common), ' 보통용', len(mid))

os.makedirs(os.path.join(BASE, 'typing_practice', 'data'), exist_ok=True)
with open(os.path.join(BASE, 'typing_practice', 'data', 'ko_words.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(allw))
out = os.path.join(BASE, 'typing_practice', 'data')
with open(os.path.join(out, 'ko_common.json'), 'w', encoding='utf-8') as f:
    json.dump({'mid': ' '.join(mid), 'hard': ' '.join(w for w in common if w not in set(mid))}, f, ensure_ascii=False)
print('저장 완료')
for t in ('보통 샘플', mid[::max(1, len(mid) // 25)][:25]), ('어려움 샘플', common[::max(1, len(common) // 25)][:25]):
    print(*t)
