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
        "id": 1260,
        "old": "<p>문자열이 입력되면 그 안에 포함된 알파벳 대문자의 개수를 출력하세요.</p>",
        "problem_text": "문자열이 입력되면 그 안에 포함된 알파벳 대문자의 개수를 출력하세요.",
        "marker": "isupper()로 대문자 여부 확인하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔠 isupper()로 대문자 여부 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">글자 하나하나가 대문자인지 아닌지 알고 싶을 때, <code>글자.isupper()</code>를 쓰면 대문자이면 True, 아니면 False를 돌려줘요. 문자열을 한 글자씩 반복하면서 이 메서드로 확인하면 대문자 개수를 셀 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
cnt = 0
for c in s:
    if c.isupper():   # 이 글자가 대문자인지 확인
        cnt += 1
print(cnt)</pre>
</div>
""",
    },
    {
        "id": 1262,
        "old": "<p>문자열이 입력되면 전체 문자열부터 한 글자씩 줄여가며, 한 글자가 남을 때까지의 부분 문자열을 공백으로 구분해 출력하세요.</p>",
        "problem_text": "문자열이 입력되면 전체 문자열부터 한 글자씩 줄여가며, 한 글자가 남을 때까지의 부분 문자열을 공백으로 구분해 출력하세요.",
        "marker": "슬라이싱 일반형 s[시작:끝]",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✂️ 슬라이싱 일반형 s[시작:끝]</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">앞서 <code>s[::-1]</code>로 문자열 전체를 뒤집는 걸 배웠죠. 슬라이싱은 사실 더 일반적으로 <code>s[시작:끝]</code> 형태로 "시작 인덱스부터 끝 인덱스 바로 앞까지"를 잘라낼 수 있어요. 시작을 생략하면 처음부터, 끝을 생략하면 끝까지라는 뜻이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "hello"
print(s[:3])   # 'hel'  (처음부터 인덱스 3 바로 앞까지)
print(s[:1])   # 'h'    (처음부터 인덱스 1 바로 앞까지, 즉 첫 글자만)</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>range(len(s), 0, -1)</code>로 길이를 n, n-1, ..., 1로 줄여가면서 <code>s[:i]</code>를 모으면, 전체 문자열부터 한 글자씩 줄어드는 부분 문자열들을 차례로 얻을 수 있어요.</p>
</div>
""",
    },
    {
        "id": 1264,
        "old": "<p>숫자로 이루어진 리스트가 입력됩니다. 리스트에는 3이 정확히 한 번 들어있습니다.</p><p>3보다 뒤에 있는 숫자의 개수를 출력하세요.</p>",
        "problem_text": "숫자로 이루어진 리스트가 입력됩니다. 리스트에는 3이 정확히 한 번 들어있습니다.<br>3보다 뒤에 있는 숫자의 개수를 출력하세요.",
        "marker": "index() 메서드로 값의 위치 찾기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📍 index() 메서드로 값의 위치 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트 안에서 특정 값이 몇 번째(인덱스)에 있는지 찾고 싶을 때, 반복문으로 하나씩 비교하지 않아도 <code>리스트.index(값)</code>을 쓰면 그 값이 처음 나오는 위치를 바로 알려줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">arr = [5, 7, 3, 9, 1]
idx = arr.index(3)       # 3은 인덱스 2에 있음
print(idx)                 # 2
print(len(arr) - idx - 1)  # 3보다 "뒤에" 있는 숫자 개수 (전체 개수 - 위치 - 1)</pre>
</div>
""",
    },
    {
        "id": 1265,
        "old": "<p>정수 하나가 입력되면 삼항연산자를 사용해 홀수이면 홀수, 짝수이면 짝수를 출력하세요.</p>",
        "problem_text": "정수 하나가 입력되면 삼항연산자를 사용해 홀수이면 홀수, 짝수이면 짝수를 출력하세요.",
        "marker": "삼항연산자(조건부 표현식)란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">❓ 삼항연산자(조건부 표현식)란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">if-else를 여러 줄로 쓰는 대신, 값을 바로 골라내야 할 때는 한 줄로 쓸 수 있는 <strong>삼항연산자</strong>(조건부 표현식)가 있어요. <code>A if 조건 else B</code> 형태로 쓰면, 조건이 참이면 A, 거짓이면 B가 그 자리의 값이 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">num = int(input())
# 아래 두 코드는 똑같은 결과를 냅니다.

# 방법1) if-else 여러 줄
if num % 2 != 0:
    result = "홀수"
else:
    result = "짝수"

# 방법2) 삼항연산자 한 줄
result = "홀수" if num % 2 != 0 else "짝수"
print(result)</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 모의고사7 문항에 부족한 개념 설명(isupper, 슬라이싱 일반형, index, 삼항연산자)을 추가합니다."

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
