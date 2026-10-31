# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

STYLE = """
<style>
.jz-card{background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:12px;padding:16px 18px;margin:14px 0;}
table.jz-table{width:100%;border-collapse:collapse;margin:12px 0;font-size:15px;}
table.jz-table th, table.jz-table td{border:1px solid var(--border);padding:8px 10px;text-align:left;color:#e5e7eb;}
table.jz-table th{background:rgba(255,255,255,0.06);color:#fff;}
</style>
"""

ENTRIES = [
    {
        "id": 455,
        "old": '<p>텍스트와 패턴이 한 줄씩 입력됩니다. 패턴이 처음 등장하는 인덱스를 출력하세요. 없으면 -1을 출력하세요.</p>',
        "problem_text": '텍스트와 패턴이 한 줄씩 입력됩니다. 패턴이 처음 등장하는 인덱스를 출력하세요. 없으면 -1을 출력하세요.',
        "marker": 'KMP 알고리즘으로 빠른 부분 문자열 검색',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔍 KMP 알고리즘으로 빠른 부분 문자열 검색</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">단순히 패턴을 한 글자씩 밀며 비교하면 최악의 경우 O(n·m)이 걸려요. KMP는 \'실패했을 때 이미 비교했던 정보를 버리지 않고 재활용\'해서 O(n+m)에 찾아요. 핵심은 패턴 자신에 대해 \'접두사와 접미사가 겹치는 길이\'를 미리 계산한 실패 함수(failure function)예요. 매칭이 실패하면 이 함수를 보고 다시 비교할 위치를 한 번에 점프해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def build_failure(pattern):\n    fail = [0] * len(pattern)\n    j = 0\n    for i in range(1, len(pattern)):\n        while j > 0 and pattern[i] != pattern[j]:\n            j = fail[j - 1]\n        if pattern[i] == pattern[j]:\n            j += 1\n            fail[i] = j\n    return fail\n\ndef kmp_search(text, pattern):\n    fail = build_failure(pattern)\n    j = 0\n    for i in range(len(text)):\n        while j > 0 and text[i] != pattern[j]:\n            j = fail[j - 1]\n        if text[i] == pattern[j]:\n            if j == len(pattern) - 1:\n                return i - j\n            j += 1\n    return -1\n\ntext = input()\npattern = input()\nprint(kmp_search(text, pattern))</pre>\n</div>\n',
    },
    {
        "id": 456,
        "old": '<p>문자열이 입력됩니다. 이메일 형식(영숫자@영숫자.영숫자)이면 VALID, 아니면 INVALID를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 이메일 형식(영숫자@영숫자.영숫자)이면 VALID, 아니면 INVALID를 출력하세요.',
        "marker": '정규표현식(re)으로 이메일 형식 검사',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📧 정규표현식(re)으로 이메일 형식 검사</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">정규표현식은 \'문자열이 어떤 패턴을 따르는지\' 검사하는 강력한 도구예요. 이메일은 대략 \'영숫자/점 + @ + 영숫자 + . + 영숫자\' 형태를 따르므로, re.match(r\'^[\\w.]+@[\\w]+\\.[\\w]+$\', s)처럼 패턴을 적어두면 그 형식을 만족하는지 한 번에 검사할 수 있어요. ^와 $는 문자열의 시작과 끝을 의미해서, 중간에 패턴이 일부만 맞는 경우를 걸러내요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import re\n\ns = input()\nif re.match(r\'^[\\w.]+@[\\w]+\\.[\\w]+$\', s):\n    print("VALID")\nelse:\n    print("INVALID")</pre>\n</div>\n',
    },
    {
        "id": 457,
        "old": '<p>단어 여러 개가 한 줄에 입력됩니다. 아나그램끼리 묶어 각 그룹을 사전 순 첫 단어 기준으로 오름차순 출력하세요.</p>',
        "problem_text": '단어 여러 개가 한 줄에 입력됩니다. 아나그램끼리 묶어 각 그룹을 사전 순 첫 단어 기준으로 오름차순 출력하세요.',
        "marker": '딕셔너리로 아나그램(anagram) 그룹화하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔤 딕셔너리로 아나그램(anagram) 그룹화하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">아나그램은 \'글자 구성은 같지만 순서만 다른\' 단어들이에요(eat, tea, ate). 각 단어의 글자를 정렬하면(sorted(word)) 아나그램끼리는 항상 똑같은 결과가 나와요. 그래서 정렬된 글자열을 키로 쓰는 딕셔너리에 원래 단어를 모아두면, 같은 키를 가진 단어들이 자동으로 한 그룹이 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import defaultdict\n\nwords = input().split()\ngroups = defaultdict(list)\nfor w in words:\n    key = \'\'.join(sorted(w))\n    groups[key].append(w)\n\nresult = sorted(\' \'.join(sorted(g)) for g in groups.values())\nfor line in result:\n    print(line)</pre>\n</div>\n',
    },
    {
        "id": 458,
        "old": '<p>문자열이 입력됩니다. 가장 긴 팰린드롬 부분 문자열을 출력하세요. 여러 개면 먼저 나오는 것을 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 가장 긴 팰린드롬 부분 문자열을 출력하세요. 여러 개면 먼저 나오는 것을 출력하세요.',
        "marker": '중심 확장법으로 최장 팰린드롬 부분 문자열 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪞 중심 확장법으로 최장 팰린드롬 부분 문자열 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">모든 (시작, 끝) 조합을 다 검사하면 느리지만, \'각 글자(또는 두 글자 사이)를 팰린드롬의 중심으로 놓고 양쪽으로 넓혀가는\' 중심 확장법을 쓰면 효율적으로 찾을 수 있어요. 팰린드롬은 길이가 홀수(중심이 글자 하나)거나 짝수(중심이 두 글자 사이)일 수 있어서, 두 경우를 모두 시도해야 해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def expand(s, left, right):\n    while left >= 0 and right < len(s) and s[left] == s[right]:\n        left -= 1\n        right += 1\n    return s[left+1:right]\n\ns = input()\nbest = \'\'\nfor i in range(len(s)):\n    odd = expand(s, i, i)\n    even = expand(s, i, i + 1)\n    for cand in (odd, even):\n        if len(cand) > len(best):\n            best = cand\nprint(best)</pre>\n</div>\n',
    },
    {
        "id": 459,
        "old": '<p>텍스트와 패턴이 한 줄씩 입력됩니다. 패턴이 텍스트에 몇 번 등장하는지 출력하세요. (중복 허용)</p>',
        "problem_text": '텍스트와 패턴이 한 줄씩 입력됩니다. 패턴이 텍스트에 몇 번 등장하는지 출력하세요. (중복 허용)',
        "marker": '패턴이 등장하는 개수 세기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔢 패턴이 등장하는 개수 세기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">텍스트 안에서 패턴이 몇 번(중복 허용) 등장하는지 셀 때는, 텍스트를 한 글자씩 밀며 그 위치부터 패턴 길이만큼이 패턴과 일치하는지 확인하면 돼요. 패턴 길이가 짧다면 이렇게 단순 탐색만으로도 충분히 빠르고, 더 긴 입력이 들어오면 KMP 같은 알고리즘으로 최적화할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">text = input()\npattern = input()\ncount = 0\nfor i in range(len(text) - len(pattern) + 1):\n    if text[i:i+len(pattern)] == pattern:\n        count += 1\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 460,
        "old": '<p>문자열이 입력됩니다. 모든 정수(연속 숫자)를 추출해 합계를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 모든 정수(연속 숫자)를 추출해 합계를 출력하세요.',
        "marker": '정규식으로 숫자 추출 후 합계 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧮 정규식으로 숫자 추출 후 합계 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열 속에 흩어진 숫자들을 모두 뽑아내고 싶을 때 re.findall(r\'\\d+\', s)를 쓰면 \'연속된 숫자(\\d+)\'를 모두 찾아 리스트로 돌려줘요. \\d는 숫자 한 글자, +는 \'1개 이상 반복\'을 뜻해요. 찾은 문자열들을 int()로 바꿔 더하면 합계를 구할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import re\n\ns = input()\nnumbers = re.findall(r\'\\d+\', s)\ntotal = sum(int(n) for n in numbers)\nprint(total)</pre>\n</div>\n',
    },
    {
        "id": 461,
        "old": '<p>텍스트와 패턴이 한 줄씩 입력됩니다. 패턴이 등장하는 모든 시작 인덱스를 오름차순으로 출력하세요.</p>',
        "problem_text": '텍스트와 패턴이 한 줄씩 입력됩니다. 패턴이 등장하는 모든 시작 인덱스를 오름차순으로 출력하세요.',
        "marker": 'Z 알고리즘으로 패턴 등장 위치 모두 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧬 Z 알고리즘으로 패턴 등장 위치 모두 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">Z 알고리즘은 문자열의 각 위치에서 \'그 위치부터 시작하는 부분 문자열이 전체 문자열의 접두사와 얼마나 길게 일치하는지\'를 O(n)에 구하는 방법이에요. 패턴 검색에 쓸 때는 s = 패턴 + 구분자(#) + 텍스트로 이어붙인 뒤 Z 배열을 구하고, Z값이 패턴 길이와 같은 위치들이 바로 패턴이 등장하는 자리예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def z_array(s):\n    n = len(s)\n    z = [0] * n\n    l, r = 0, 0\n    for i in range(1, n):\n        if i < r:\n            z[i] = min(r - i, z[i - l])\n        while i + z[i] < n and s[z[i]] == s[i + z[i]]:\n            z[i] += 1\n        if i + z[i] > r:\n            l, r = i, i + z[i]\n    return z\n\ntext = input()\npattern = input()\ncombined = pattern + \'#\' + text\nz = z_array(combined)\nplen = len(pattern)\npositions = [i - plen - 1 for i in range(len(combined)) if z[i] == plen]\nprint(*positions)</pre>\n</div>\n',
    },
    {
        "id": 462,
        "old": '<p>문자열이 입력됩니다. 앞에서부터 일정 단위로 잘라 압축(반복되면 횟수+문자열)할 때 가장 짧은 압축 결과의 길이를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 앞에서부터 일정 단위로 잘라 압축(반복되면 횟수+문자열)할 때 가장 짧은 압축 결과의 길이를 출력하세요.',
        "marker": '모든 압축 단위를 시도해 최소 길이 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🗜️ 모든 압축 단위를 시도해 최소 길이 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열을 \'단위 길이만큼 잘라 반복되면 횟수+문자열로 압축\'할 때, 어떤 단위 길이를 쓰느냐에 따라 압축 결과 길이가 달라져요. 그래서 1부터 전체 길이의 절반까지 모든 단위 길이를 하나씩 시도해보고, 각 경우의 압축 결과 길이를 계산해 그 중 최솟값을 찾는 완전탐색이 필요해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nn = len(s)\nbest = n  # 압축하지 않은 길이\nfor size in range(1, n // 2 + 1):\n    result = []\n    i = 0\n    while i < n:\n        chunk = s[i:i+size]\n        count = 1\n        while i + size * count < n and s[i+size*count:i+size*(count+1)] == chunk:\n            count += 1\n        piece = (str(count) if count > 1 else \'\') + chunk\n        result.append(piece)\n        i += size * count\n    best = min(best, sum(len(p) for p in result))\nprint(best)</pre>\n</div>\n',
    },
    {
        "id": 463,
        "old": '<p>문자열과 길이 k가 한 줄씩 입력됩니다. 길이 k의 부분 문자열 중 중복이 있으면 YES와 중복 문자열을, 없으면 NO를 출력하세요.</p>',
        "problem_text": '문자열과 길이 k가 한 줄씩 입력됩니다. 길이 k의 부분 문자열 중 중복이 있으면 YES와 중복 문자열을, 없으면 NO를 출력하세요.',
        "marker": 'set으로 중복 부분 문자열 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔑 set으로 중복 부분 문자열 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">길이 k인 모든 부분 문자열을 하나씩 만들어 set에 넣어보면서, 이미 set에 있는 부분 문자열이 다시 나오면 중복이 발견된 거예요(해시를 이용한 비교라서 \'롤링 해시\'의 아이디어와 같은 맥락이에요). set에 넣는 것 자체가 사실상 해시로 빠르게 비교하는 것과 같아요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nk = int(input())\nseen = set()\nfound = None\nfor i in range(len(s) - k + 1):\n    sub = s[i:i+k]\n    if sub in seen:\n        found = sub\n        break\n    seen.add(sub)\n\nif found:\n    print("YES")\n    print(found)\nelse:\n    print("NO")</pre>\n</div>\n',
    },
    {
        "id": 464,
        "old": '<p>두 문자열이 한 줄씩 입력됩니다. 첫 번째 문자열의 순열이 두 번째 문자열의 부분 문자열로 포함되면 YES, 아니면 NO를 출력하세요.</p>',
        "problem_text": '두 문자열이 한 줄씩 입력됩니다. 첫 번째 문자열의 순열이 두 번째 문자열의 부분 문자열로 포함되면 YES, 아니면 NO를 출력하세요.',
        "marker": '슬라이딩 윈도우로 순열 포함 여부 확인하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪟 슬라이딩 윈도우로 순열 포함 여부 확인하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">첫 번째 문자열의 \'순열\'이 두 번째 문자열에 부분 문자열로 들어있는지 확인하려면, 글자 하나하나의 순서가 아니라 \'글자 빈도\'가 같은 구간이 있는지를 보면 돼요. 첫 문자열과 같은 길이의 윈도우를 두 번째 문자열에서 한 칸씩 옮기며, 그 구간의 글자 빈도가 첫 문자열의 글자 빈도와 일치하는지 비교해요. Counter를 이용하면 빈도 비교가 간단해져요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import Counter\n\np = input()\ns = input()\nplen = len(p)\ntarget = Counter(p)\nfound = False\nfor i in range(len(s) - plen + 1):\n    window = Counter(s[i:i+plen])\n    if window == target:\n        found = True\n        break\nprint("YES" if found else "NO")</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 문자열 알고리즘 단원(45장) 문항 10건에 개념 설명 카드를 추가합니다."

    def handle(self, *args, **options):
        for entry in ENTRIES:
            try:
                item = Item.objects.get(id=entry["id"])
            except Item.DoesNotExist:
                raise CommandError(f"id={entry['id']} 문항을 찾을 수 없습니다.")

            current = (item.explain_html or "").strip()
            if entry["marker"] in current:
                self.stdout.write(self.style.WARNING(f"id={entry['id']} 이미 수정되어 있습니다."))
                continue

            if current != entry["old"].strip():
                raise CommandError(
                    f"id={entry['id']} 기존 내용이 예상과 달라 안전하게 교체할 수 없습니다. 문항 내용을 확인해 주세요."
                )

            problem_card = (
                '<div class="jz-card" style="background:rgba(0,255,180,0.06);'
                'border-color:rgba(0,255,180,0.3);">\n'
                '<strong style="color:#fff;font-size:16px;">📝 문제</strong>\n'
                f'<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">{entry["problem_text"]}</p>\n'
                "</div>\n"
            )
            new_html = (STYLE + entry["concept"] + problem_card).strip()
            item.explain_html = new_html
            item.save(update_fields=["explain_html"])
            self.stdout.write(self.style.SUCCESS(f"id={entry['id']} 설명을 추가했습니다."))
