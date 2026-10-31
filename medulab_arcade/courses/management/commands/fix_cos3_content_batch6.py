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
        "id": 1234,
        "old": "<p>정수 n(2 이상)이 입력되면 피보나치 수열(1, 1, 2, 3, 5, ...)의 n번째 항을 출력하세요.</p>",
        "problem_text": "정수 n(2 이상)이 입력되면 피보나치 수열(1, 1, 2, 3, 5, ...)의 n번째 항을 출력하세요.",
        "marker": "동시 대입(튜플 언패킹)",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🐚 피보나치 수열이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">피보나치 수열은 "바로 앞 두 항을 더해서 다음 항을 만드는" 수열이에요. 1, 1로 시작해서 1+1=2, 1+2=3, 2+3=5... 이렇게 계속 이어져요.</p>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔀 동시 대입(튜플 언패킹)으로 값 두 개 한꺼번에 갱신하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 변수의 값을 "동시에" 바꿔야 할 때, <code>a, b = b, a + b</code>처럼 쉼표로 묶어서 한 줄에 쓸 수 있어요. 이렇게 하면 오른쪽 값들(b, a+b)이 먼저 전부 계산된 다음에 왼쪽 변수들(a, b)에 동시에 들어가요. 그래서 a를 먼저 바꿔버려서 b 계산이 틀어지는 실수를 막을 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
a, b = 1, 1          # 1번째, 2번째 항
for _ in range(n - 2):
    a, b = b, a + b   # a는 이전 b값, b는 a+b값으로 동시에 갱신
print(b)</pre>
</div>
""",
    },
    {
        "id": 1238,
        "old": "<p>한 줄에 정수 여러 개가 입력됩니다. 중복을 제거했을 때 남는 값의 개수를 출력하세요.</p>",
        "problem_text": "한 줄에 정수 여러 개가 입력됩니다. 중복을 제거했을 때 남는 값의 개수를 출력하세요.",
        "marker": "set(집합)으로 중복 제거하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧺 set(집합)으로 중복 제거하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트는 같은 값이 여러 번 들어갈 수 있지만, <strong>집합(set)</strong>은 "같은 값은 딱 하나만 가지는" 특별한 그릇이에요. 리스트를 <code>set()</code>으로 감싸면 중복된 값이 자동으로 사라져요. 그래서 set의 개수(<code>len()</code>)를 구하면 "중복을 제거했을 때 남는 값의 개수"를 바로 알 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = [1, 2, 2, 3, 3, 3]
unique = set(nums)
print(unique)        # {1, 2, 3} (중복 제거됨, 순서는 보장되지 않음)
print(len(unique))   # 3</pre>
</div>
""",
    },
    {
        "id": 1239,
        "old": "<p>정수 세 개가 입력되면 크기순으로 가운데 값을 출력하세요.</p>",
        "problem_text": "정수 세 개가 입력되면 크기순으로 가운데 값을 출력하세요.",
        "marker": "sorted() 함수와 sort() 메서드의 차이",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🆚 sorted() 함수와 sort() 메서드의 차이</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>리스트.sort()</code>는 원본 리스트 자체의 순서를 바꿔버리지만, <code>sorted(리스트)</code>는 원본은 그대로 두고 <strong>정렬된 새 리스트</strong>를 만들어서 돌려줘요. 값 세 개를 바로 리스트로 묶어서 정렬하면, 가운데 값은 인덱스 1에 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b, c = map(int, input().split())
nums = sorted([a, b, c])   # 작은 값부터 순서대로 담긴 새 리스트
print(nums[1])              # 가운데(두 번째) 값</pre>
</div>
""",
    },
    {
        "id": 1245,
        "old": "<p>정수 n이 입력되면 재귀함수 factorial(n)으로 n!을 출력하세요.</p>",
        "problem_text": "정수 n이 입력되면 재귀함수 factorial(n)으로 n!을 출력하세요.",
        "marker": "재귀함수(recursion)란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🪞 재귀함수(recursion)란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">러시아 인형 마트료시카처럼, 인형 안에 똑같이 생긴 더 작은 인형이 들어있는 구조를 생각해보세요. <strong>재귀함수</strong>는 함수가 자기 자신을 다시 호출하는 함수예요. n! (n 팩토리얼)은 "n × (n-1)!"로 정의할 수 있는데, 이게 바로 "더 작은 문제를 푸는 나 자신을 다시 부르는" 재귀적인 구조예요.</p>
<table class="jz-table">
  <tr><th>개념</th><th>설명</th></tr>
  <tr><td>종료 조건(base case)</td><td>더 이상 자기 자신을 부르지 않고 바로 답을 내는 경우. 없으면 무한히 호출돼요.</td></tr>
  <tr><td>재귀 호출</td><td>더 작은 문제로 줄여서 자기 자신을 다시 부르는 부분.</td></tr>
</table>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def factorial(n):
    if n <= 1:                  # 종료 조건: 1이하면 더 쪼개지 않고 1을 반환
        return 1
    return n * factorial(n - 1)  # 재귀 호출: n보다 하나 작은 문제를 풀어서 곱함

n = int(input())
print(factorial(n))</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 예를 들어 factorial(3)은 3 * factorial(2), factorial(2)는 2 * factorial(1), factorial(1)은 바로 1을 반환해요. 그래서 3 * 2 * 1 = 6이 됩니다.</p>
</div>
""",
    },
    {
        "id": 1247,
        "old": "<p>두 줄에 걸쳐 정수 다섯 개씩 입력됩니다. 두 줄에 공통으로 들어있는 수의 개수를 출력하세요.</p>",
        "problem_text": "두 줄에 걸쳐 정수 다섯 개씩 입력됩니다. 두 줄에 공통으로 들어있는 수의 개수를 출력하세요.",
        "marker": "집합의 교집합(&) 연산",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔗 집합의 교집합(&) 연산</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 집합에 "공통으로 들어있는 값"을 수학에서는 <strong>교집합</strong>이라고 불러요. 파이썬에서는 두 set 사이에 <code>&</code> 기호를 쓰면 교집합을 바로 구할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = set([1, 2, 3, 4, 5])
b = set([3, 4, 5, 6, 7])
print(a & b)        # {3, 4, 5}  (두 집합에 공통으로 있는 값)
print(len(a & b))    # 3</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 모의고사4~5 문항에 부족한 개념 설명(동시 대입, set, sorted, 재귀함수, 교집합)을 추가합니다."

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
