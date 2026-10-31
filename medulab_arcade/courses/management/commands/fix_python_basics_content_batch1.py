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
        "id": 822,
        "old": "<div class='problem-box'><h3>[문제3] 두 수의 합 구하기</h3><p>두 정수를 입력받아 합을 출력하는 프로그램을 만드세요.</p></div>",
        "problem_title": "[문제3] 두 수의 합 구하기",
        "problem_text": "두 정수를 입력받아 합을 출력하는 프로그램을 만드세요.",
        "marker": "숫자인 척하는 글자",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 input()은 항상 '글자'를 돌려줘요</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">키보드로 숫자 3을 입력해도, 파이썬은 그걸 숫자인 척하는 글자 "3"으로 받아요. 그래서 <code>a = input()</code> 뒤에 <code>a + b</code>를 하면 숫자를 더하는 게 아니라 글자를 이어 붙이게 돼요. 예를 들어 "3" + "5"는 15가 아니라 "35"가 돼버려요!</p>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔧 int()로 진짜 숫자로 바꾸기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>int()</code>를 쓰면 글자 "3"을 진짜 숫자 3으로 바꿔줘요. 그래야 덧셈, 뺄셈 같은 계산을 제대로 할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = int(input())  # 글자를 숫자로 바꿔서 저장
b = int(input())
print(a + b)       # 이제 진짜 숫자 덧셈이 됩니다</pre>
</div>
""",
    },
    {
        "id": 835,
        "old": "<div class='problem-box'><h3>[문제3] type()으로 자료형 확인하기</h3><p>정수, 실수, 문자열 세 개를 변수로 만들고 각각의 자료형을 출력하세요.</p></div>",
        "problem_title": "[문제3] type()으로 자료형 확인하기",
        "problem_text": "정수, 실수, 문자열 세 개를 변수로 만들고 각각의 자료형을 출력하세요.",
        "marker": "자료형(type)이란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📦 자료형(type)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">물건을 상자에 담을 때도 "과일 상자", "장난감 상자"처럼 종류를 구분하죠. 파이썬도 값마다 "어떤 종류의 값인지"를 구분하는데, 이걸 <strong>자료형(type)</strong>이라고 해요.</p>
<table class="jz-table">
  <tr><th>자료형</th><th>의미</th><th>예시</th></tr>
  <tr><td><code>int</code></td><td>정수 (소수점 없는 숫자)</td><td>10, -3, 0</td></tr>
  <tr><td><code>float</code></td><td>실수 (소수점 있는 숫자)</td><td>3.14, -0.5</td></tr>
  <tr><td><code>str</code></td><td>문자열 (글자들)</td><td>'hello', '안녕'</td></tr>
</table>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔍 type()으로 자료형 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>type(변수)</code>를 쓰면 그 변수가 어떤 자료형인지 알려줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = 10
print(type(a))  # &lt;class 'int'&gt; 가 출력됨</pre>
</div>
""",
    },
    {
        "id": 844,
        "old": "<h3>[문제2] 곱셈 우선순위 확인</h3><p>3 + 4 * 2 를 계산한 결과를 출력하세요.</p>",
        "problem_title": "[문제2] 곱셈 우선순위 확인",
        "problem_text": "3 + 4 * 2 를 계산한 결과를 출력하세요.",
        "marker": "연산자 우선순위",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➗ 연산자 우선순위란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">수학 시간에 배운 것처럼, 곱셈과 나눗셈(<code>*</code>, <code>/</code>)은 더하기와 빼기(<code>+</code>, <code>-</code>)보다 먼저 계산돼요. 이걸 <strong>연산자 우선순위</strong>라고 해요. 파이썬도 똑같은 규칙을 따라요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">print(3 + 4 * 2)
# 4 * 2 = 8 을 먼저 계산하고
# 3 + 8 = 11 이 출력됨</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 순서를 바꾸고 싶다면 괄호 <code>()</code>를 사용해요. 예: <code>(3 + 4) * 2</code>는 14가 돼요.</p>
</div>
""",
    },
    {
        "id": 845,
        "old": "<h3>[문제3] 함수로 두 수의 차 구하기</h3><p>두 수를 뺄셈하는 함수 subtract(x, y)를 만들어 출력하세요.</p>",
        "problem_title": "[문제3] 함수로 두 수의 차 구하기",
        "problem_text": "두 수를 뺄셈하는 함수 subtract(x, y)를 만들어 출력하세요.",
        "marker": "함수(function)란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧰 함수(function)란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">함수는 "자주 쓰는 작업을 담아두는 도구 상자"예요. 한 번 만들어두면 필요할 때마다 이름만 불러서(호출해서) 다시 사용할 수 있어요. <code>def</code> 라는 단어로 함수를 만들어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def subtract(x, y):   # subtract라는 이름의 함수를 만듦 (x, y는 입력값)
    return x - y        # return은 결과를 "돌려주는" 역할

print(subtract(10, 3))  # 함수를 호출 → 7이 출력됨</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>return</code>은 함수 계산 결과를 바깥으로 돌려주는 키워드예요. return이 없으면 함수가 계산은 하지만 결과를 알려주지 않아요.</p>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "파이썬기본과정 문제 문항(2~4장)에 부족한 개념 설명(int 변환, 자료형, 연산자 우선순위, 함수)을 추가합니다."

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
