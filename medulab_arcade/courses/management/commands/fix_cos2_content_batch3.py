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
        "id": 315,
        "old": '<p>문장이 입력되면 단어 순서를 거꾸로 해 출력하세요.</p>',
        "problem_text": '문장이 입력되면 단어 순서를 거꾸로 해 출력하세요.',
        "marker": 'split과 슬라이싱으로 단어 순서 뒤집기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 split과 슬라이싱으로 단어 순서 뒤집기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문장을 단어 단위로 뒤집으려면, 먼저 <code>split()</code>으로 단어 리스트를 만들고, <code>[::-1]</code> 슬라이싱으로 리스트 순서를 뒤집은 다음 <code>join()</code>으로 다시 문장으로 합치면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">sentence = input()
words = sentence.split()
reversed_words = words[::-1]
print(" ".join(reversed_words))</pre>
</div>
""",
    },
    {
        "id": 316,
        "old": '<p>영숫자가 섞인 문자열이 입력되면 숫자만 이어 붙여 출력하세요.</p>',
        "problem_text": '영숫자가 섞인 문자열이 입력되면 숫자만 이어 붙여 출력하세요.',
        "marker": 'isdigit()으로 숫자 문자만 골라내기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 isdigit()으로 숫자 문자만 골라내기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열에서 글자 하나하나를 돌면서 <code>문자.isdigit()</code>으로 "이 글자가 숫자인지"를 확인할 수 있어요. 숫자인 글자만 모아 이어붙이면 숫자만 추출할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
digits = "".join(ch for ch in s if ch.isdigit())
print(digits)</pre>
</div>
""",
    },
    {
        "id": 317,
        "old": '<p>문장이 입력되면 가장 많이 등장한 단어를 출력하세요. 동률이면 먼저 나온 단어를 출력하세요.</p>',
        "problem_text": '문장이 입력되면 가장 많이 등장한 단어를 출력하세요. 동률이면 먼저 나온 단어를 출력하세요.',
        "marker": '가장 많이 나온 단어 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🏆 가장 많이 나온 단어 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">단어 빈도를 딕셔너리로 센 다음, 값이 가장 큰 키를 찾으면 돼요(306번과 같은 패턴). "동률이면 먼저 나온 단어"를 지키려면, 파이썬의 <code>max()</code>는 동일한 값일 때 먼저 만난 항목을 그대로 유지하므로 딕셔너리에 단어를 등장 순서대로 넣어두기만 하면 자동으로 해결돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1
print(max(count, key=count.get))</pre>
</div>
""",
    },
    {
        "id": 318,
        "old": '<p>camelCase 형식의 단어가 입력되면 snake_case 형식으로 변환해 출력하세요. 대문자 앞에 _ 를 붙이고 소문자로 바꾸세요.</p>',
        "problem_text": 'camelCase 형식의 단어가 입력되면 snake_case 형식으로 변환해 출력하세요. 대문자 앞에 _ 를 붙이고 소문자로 바꾸세요.',
        "marker": 'camelCase를 snake_case로 바꾸기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🐍 camelCase를 snake_case로 바꾸기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">camelCase는 <code>myVariableName</code>처럼 단어 경계마다 대문자로 시작하는 표기법이고, snake_case는 <code>my_variable_name</code>처럼 밑줄(_)로 단어를 구분하는 표기법이에요. 글자를 하나씩 보면서 "대문자를 만나면 그 앞에 _를 붙이고 소문자로 바꿔 넣는다"는 규칙을 적용하면 변환할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
result = ""
for ch in s:
    if ch.isupper():
        result += "_" + ch.lower()
    else:
        result += ch
print(result)</pre>
</div>
""",
    },
    {
        "id": 319,
        "old": '<p>문자열이 입력되면 연속된 같은 문자를 문자+개수로 압축해 출력하세요. 개수가 1이어도 표시하세요.</p>',
        "problem_text": '문자열이 입력되면 연속된 같은 문자를 문자+개수로 압축해 출력하세요. 개수가 1이어도 표시하세요.',
        "marker": '연속된 문자를 세어 압축하기 (Run-Length Encoding)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🗜️ 연속된 문자를 세어 압축하기 (Run-Length Encoding)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"aaabbc"처럼 같은 문자가 연달아 나오는 문자열은 "a3b2c1"처럼 "문자+개수"로 줄여 표현할 수 있어요. 현재 문자와 다음 문자를 비교하면서, 같으면 개수를 늘리고, 다르면 지금까지 센 걸 출력하고 새로 세기 시작하면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
result = ""
i = 0
while i < len(s):
    ch = s[i]
    cnt = 1
    while i + 1 < len(s) and s[i+1] == ch:
        cnt += 1
        i += 1
    result += ch + str(cnt)
    i += 1
print(result)</pre>
</div>
""",
    },
    {
        "id": 320,
        "old": '<p>첫 줄에 단어 여러 개, 둘째 줄에 접두사가 입력됩니다. 해당 접두사로 시작하는 단어만 순서대로 출력하세요.</p>',
        "problem_text": '첫 줄에 단어 여러 개, 둘째 줄에 접두사가 입력됩니다. 해당 접두사로 시작하는 단어만 순서대로 출력하세요.',
        "marker": 'startswith()로 접두사 확인하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🎯 startswith()로 접두사 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">단어가 특정 글자들로 "시작하는지"를 확인할 때는 <code>문자열.startswith(접두사)</code>를 쓰면 True/False로 바로 알려줘요. 각 단어마다 이걸 확인해서 True인 단어만 리스트에 모으면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
prefix = input()
result = [w for w in words if w.startswith(prefix)]
print(*result)</pre>
</div>
""",
    },
    {
        "id": 321,
        "old": '<p>이메일 주소가 입력되면 @ 뒤의 도메인 부분만 출력하세요.</p>',
        "problem_text": '이메일 주소가 입력되면 @ 뒤의 도메인 부분만 출력하세요.',
        "marker": "split('@')으로 이메일 도메인 추출하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📧 split('@')으로 이메일 도메인 추출하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이메일 주소는 "아이디@도메인" 형태예요. <code>split("@")</code>을 쓰면 @ 기호를 기준으로 문자열이 두 조각으로 나뉘어 리스트가 되는데, 그 중 두 번째([1]) 조각이 도메인이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">email = input()
domain = email.split("@")[1]
print(domain)</pre>
</div>
""",
    },
    {
        "id": 322,
        "old": '<p>첫 줄에 문자열, 둘째 줄에 찾을 부분 문자열이 입력됩니다. 처음 등장하는 인덱스를 출력하고, 없으면 -1을 출력하세요.</p>',
        "problem_text": '첫 줄에 문자열, 둘째 줄에 찾을 부분 문자열이 입력됩니다. 처음 등장하는 인덱스를 출력하고, 없으면 -1을 출력하세요.',
        "marker": 'find()로 부분 문자열 위치 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔍 find()로 부분 문자열 위치 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열 안에서 다른 문자열이 처음 등장하는 위치(인덱스)를 찾으려면 <code>문자열.find(찾을문자열)</code>을 써요. 찾으면 그 시작 인덱스를, 없으면 자동으로 -1을 돌려주기 때문에 별도 예외처리가 필요 없어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
target = input()
print(s.find(target))</pre>
</div>
""",
    },
    {
        "id": 323,
        "old": '<p>문장이 입력되면 각 단어의 첫 글자를 대문자로 바꿔 출력하세요.</p>',
        "problem_text": '문장이 입력되면 각 단어의 첫 글자를 대문자로 바꿔 출력하세요.',
        "marker": 'title()로 각 단어 첫 글자 대문자화',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔠 title()로 각 단어 첫 글자 대문자화</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문장의 각 단어 첫 글자만 대문자로 바꾸는 건 아주 자주 필요한 작업이라, 파이썬에는 <code>문자열.title()</code>이라는 전용 메서드가 있어요. 각 단어의 첫 글자는 대문자로, 나머지는 소문자로 자동으로 바꿔줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">sentence = input()
print(sentence.title())</pre>
</div>
""",
    },
    {
        "id": 324,
        "old": '<p>문자열과 너비가 한 줄씩 입력됩니다. 너비에 맞게 오른쪽 정렬해 출력하세요. 빈 자리는 공백으로 채우세요.</p>',
        "problem_text": '문자열과 너비가 한 줄씩 입력됩니다. 너비에 맞게 오른쪽 정렬해 출력하세요. 빈 자리는 공백으로 채우세요.',
        "marker": 'rjust()로 오른쪽 정렬하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➡️ rjust()로 오른쪽 정렬하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열을 지정한 너비에 맞춰 오른쪽으로 정렬하고, 빈 자리를 공백으로 채우려면 <code>문자열.rjust(너비)</code>를 써요. 반대로 왼쪽 정렬은 <code>ljust()</code>, 가운데 정렬은 <code>center()</code>가 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
width = int(input())
print(s.rjust(width))</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 3장(문자열 처리 심화) 문항 10건에 개념 설명 카드를 추가합니다."

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
