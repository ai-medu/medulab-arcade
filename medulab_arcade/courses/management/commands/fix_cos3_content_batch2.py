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
        "id": 215,
        "old": "<p>정수 두 개가 입력되면 더 큰 수를 출력하세요.</p>",
        "problem_text": "정수 두 개가 입력되면 더 큰 수를 출력하세요.",
        "marker": "if-else 조건문이란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚦 if-else 조건문이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"비가 오면 우산을 쓰고, 안 오면 그냥 나간다"처럼 상황에 따라 다르게 행동하는 것을 파이썬에서는 <strong>조건문</strong>으로 표현해요. <code>if 조건:</code> 뒤에는 조건이 참(True)일 때 실행할 코드를, <code>else:</code> 뒤에는 조건이 거짓(False)일 때 실행할 코드를 적어요. 반드시 들여쓰기(스페이스 4칸)로 코드 블록을 구분해야 해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
if a > b:
    print(a)   # a가 더 크면 이 줄 실행
else:
    print(b)   # 아니면 이 줄 실행</pre>
</div>
""",
    },
    {
        "id": 217,
        "old": "<p>정수가 입력되면 양수, 음수, 0 중 알맞은 것을 출력하세요.</p>",
        "problem_text": "정수가 입력되면 양수, 음수, 0 중 알맞은 것을 출력하세요.",
        "marker": "elif로 세 가지 이상의 경우 나누기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🪜 elif로 세 가지 이상의 경우 나누기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">경우가 두 가지뿐이면 if-else로 충분하지만, "양수/음수/0"처럼 경우가 세 가지 이상이면 <code>elif</code>(else if의 줄임말)를 중간에 추가해요. 위에서부터 차례로 조건을 검사하다가, 맞는 조건을 만나면 그 블록만 실행하고 나머지는 건너뛰어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
if n > 0:
    print("양수")
elif n < 0:
    print("음수")
else:
    print("0")</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 elif는 개수 제한 없이 여러 번 쓸 수 있고, 마지막 else는 앞의 모든 조건이 거짓일 때 실행돼요.</p>
</div>
""",
    },
    {
        "id": 222,
        "old": "<p>정수가 입력되면 3과 5 모두의 배수이면 YES, 아니면 NO를 출력하세요.</p>",
        "problem_text": "정수가 입력되면 3과 5 모두의 배수이면 YES, 아니면 NO를 출력하세요.",
        "marker": "and 로 두 조건을 모두 확인하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔗 and 로 두 조건을 모두 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"3의 배수이면서 동시에 5의 배수"처럼 조건 두 개를 <strong>모두</strong> 만족해야 할 때는 <code>and</code>를 사용해요. 두 조건이 전부 참(True)일 때만 전체 결과가 참이 돼요. (참고로 둘 중 하나만 참이면 되는 경우는 <code>or</code>를 사용해요.)</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
if n % 3 == 0 and n % 5 == 0:
    print("YES")   # 3의 배수이면서 5의 배수일 때만
else:
    print("NO")</pre>
</div>
""",
    },
    {
        "id": 225,
        "old": "<p>정수 n이 입력되면 1부터 n까지 한 줄에 하나씩 출력하세요.</p>",
        "problem_text": "정수 n이 입력되면 1부터 n까지 한 줄에 하나씩 출력하세요.",
        "marker": "for 반복문과 range()란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔁 for 반복문과 range()란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">같은 작업을 여러 번 반복해야 할 때마다 코드를 여러 줄 복사해 쓰면 너무 비효율적이죠. <code>for</code> 반복문을 쓰면 "이 코드를 몇 번 반복해라"라고 간단하게 표현할 수 있어요. <code>range(1, n+1)</code>은 1부터 n까지(끝 숫자는 포함 안 됨!)의 숫자를 하나씩 만들어줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
for i in range(1, n + 1):   # i가 1, 2, 3, ... n 순서로 바뀌며 반복
    print(i)</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>range(1, n+1)</code>처럼 끝 숫자에 +1을 하는 건, range가 "끝 숫자는 포함하지 않기" 때문이에요. n까지 포함하려면 n+1로 적어야 해요.</p>
</div>
""",
    },
    {
        "id": 230,
        "old": "<p>정수 n이 입력되면 1행에 별 1개, 2행에 별 2개 … n행에 별 n개를 출력하세요.</p>",
        "problem_text": "정수 n이 입력되면 1행에 별 1개, 2행에 별 2개 … n행에 별 n개를 출력하세요.",
        "marker": "문자열 * 숫자 로 글자 반복하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⭐ 문자열 * 숫자 로 글자 반복하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬에서는 숫자끼리 곱하는 <code>*</code> 연산자를 문자열에도 쓸 수 있어요. <code>'문자' * 숫자</code>를 하면 그 문자가 숫자만큼 반복된 새 문자열이 만들어져요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">print('*' * 3)   # '***' 출력
n = int(input())
for i in range(1, n + 1):
    print('*' * i)   # i가 1,2,3,...일 때마다 별이 i개씩 늘어남</pre>
</div>
""",
    },
    {
        "id": 233,
        "old": "<p>정수를 한 줄씩 입력받아 0이 입력되면 중단하고 합계를 출력하세요.</p>",
        "problem_text": "정수를 한 줄씩 입력받아 0이 입력되면 중단하고 합계를 출력하세요.",
        "marker": "while True와 break로 반복 멈추기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔂 while True와 break로 반복 멈추기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>for</code>는 몇 번 반복할지 미리 정해져 있을 때 쓰지만, "0이 나올 때까지 계속 입력받기"처럼 몇 번 반복할지 모를 때는 <code>while</code>을 사용해요. <code>while True:</code>는 "조건이 항상 참이니 끝없이 반복해라"라는 뜻이고, 안에서 <code>break</code>를 만나면 그 즉시 반복을 멈추고 빠져나가요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">total = 0
while True:
    n = int(input())
    if n == 0:
        break        # 0이면 반복을 즉시 멈춤
    total += n       # 0이 아니면 계속 더함
print(total)</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 3~4장 문항에 부족한 개념 설명(if-elif-else, and, for/range, 문자열 반복, while+break)을 추가합니다."

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
