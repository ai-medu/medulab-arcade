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
        "id": 325,
        "old": '<p>정수 n이 입력되면 재귀 함수로 n! 을 계산해 출력하세요.</p>',
        "problem_text": '정수 n이 입력되면 재귀 함수로 n! 을 계산해 출력하세요.',
        "marker": '재귀 함수란? - 팩토리얼로 이해하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔁 재귀 함수란? - 팩토리얼로 이해하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">재귀 함수는 "자기 자신을 다시 호출하는 함수"예요. n! (n 팩토리얼)은 n × (n-1)! 로 표현할 수 있는데, 이렇게 "더 작은 문제로 쪼개서 자기 자신을 부르는 것"이 재귀의 핵심이에요. 반드시 더 이상 쪼갤 수 없는 "기저 조건"(여기서는 n=1일 때 1을 반환)이 있어야 무한히 반복되지 않아요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def factorial(n):
    if n == 1:        # 기저 조건
        return 1
    return n * factorial(n - 1)

n = int(input())
print(factorial(n))</pre>
</div>
""",
    },
    {
        "id": 326,
        "old": '<p>정수 n이 입력되면 피보나치 수열의 n번째 값을 출력하세요. (F(1)=1, F(2)=1)</p>',
        "problem_text": '정수 n이 입력되면 피보나치 수열의 n번째 값을 출력하세요. (F(1)=1, F(2)=1)',
        "marker": '재귀로 피보나치 수열 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🐰 재귀로 피보나치 수열 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">피보나치 수열은 "바로 앞 두 수를 더한 값"이 다음 수가 되는 수열이에요(F(n) = F(n-1) + F(n-2)). 이 정의 자체가 재귀식이기 때문에 함수로 그대로 옮길 수 있어요. 기저 조건은 F(1)=1, F(2)=1 두 가지가 필요해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def fib(n):
    if n == 1 or n == 2:
        return 1
    return fib(n-1) + fib(n-2)

n = int(input())
print(fib(n))</pre>
</div>
""",
    },
    {
        "id": 327,
        "old": '<p>밑(base)과 지수(exp)가 입력되면 재귀로 base^exp 를 계산해 출력하세요.</p>',
        "problem_text": '밑(base)과 지수(exp)가 입력되면 재귀로 base^exp 를 계산해 출력하세요.',
        "marker": '재귀로 거듭제곱 계산하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✖️ 재귀로 거듭제곱 계산하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">base^exp는 "base를 exp번 곱한 것"인데, base^exp = base × base^(exp-1) 로 쪼갤 수 있어요. exp가 0이 되면 어떤 수든 1이 되는 것이 기저 조건이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def power(base, exp):
    if exp == 0:
        return 1
    return base * power(base, exp - 1)

base, exp = map(int, input().split())
print(power(base, exp))</pre>
</div>
""",
    },
    {
        "id": 328,
        "old": '<p>이름:점수 쌍 여러 개가 콤마로 구분되어 입력됩니다. 점수 오름차순으로 이름을 출력하세요.</p>',
        "problem_text": '이름:점수 쌍 여러 개가 콤마로 구분되어 입력됩니다. 점수 오름차순으로 이름을 출력하세요.',
        "marker": 'lambda와 sorted(key=...)로 정렬 기준 정하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 lambda와 sorted(key=...)로 정렬 기준 정하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>lambda</code>는 이름 없이 간단하게 만드는 "한 줄 함수"예요. <code>lambda x: x[1]</code>은 "x를 받아서 x[1]을 돌려주는 함수"라는 뜻이에요. <code>sorted(리스트, key=함수)</code>에 이 람다를 넣으면 "각 항목의 x[1](점수)을 기준으로 정렬해줘"라는 의미가 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">pairs = [kv.split(":") for kv in input().split(",")]
pairs = [(name, int(score)) for name, score in pairs]
for name, score in sorted(pairs, key=lambda x: x[1]):
    print(name)</pre>
</div>
""",
    },
    {
        "id": 329,
        "old": '<p>정수 여러 개가 입력됩니다. 각 값에 2를 곱한 결과를 공백으로 구분해 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 각 값에 2를 곱한 결과를 공백으로 구분해 출력하세요.',
        "marker": 'map()으로 리스트 전체를 한 번에 변환하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✨ map()으로 리스트 전체를 한 번에 변환하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 모든 값에 같은 작업(예: 2배 하기)을 적용하려면 for문을 쓸 수도 있지만, <code>map(함수, 리스트)</code>를 쓰면 "리스트의 모든 값에 함수를 적용한 결과"를 한 번에 만들 수 있어요. 결과는 리스트로 바꿔서 쓰려면 <code>list()</code>로 감싸줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
doubled = list(map(lambda x: x * 2, nums))
print(*doubled)</pre>
</div>
""",
    },
    {
        "id": 330,
        "old": '<p>정수 여러 개가 입력됩니다. 양수만 추출해 공백으로 구분해 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 양수만 추출해 공백으로 구분해 출력하세요.',
        "marker": 'filter()로 조건에 맞는 값만 골라내기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔍 filter()로 조건에 맞는 값만 골라내기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>filter(조건함수, 리스트)</code>는 "조건함수가 True를 돌려주는 값만" 걸러서 남겨줘요. 리스트 컴프리헨션의 if 조건과 같은 역할을 하는 또 다른 방법이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
positives = list(filter(lambda x: x > 0, nums))
print(*positives)</pre>
</div>
""",
    },
    {
        "id": 331,
        "old": '<p>이름과 선택적으로 인삿말이 한 줄에 입력됩니다(인삿말 없으면 이름만). 인삿말이 없으면 안녕하세요를 기본값으로 사용해 인삿말, 이름님! 형식으로 출력하세요.</p>',
        "problem_text": '이름과 선택적으로 인삿말이 한 줄에 입력됩니다(인삿말 없으면 이름만). 인삿말이 없으면 안녕하세요를 기본값으로 사용해 인삿말, 이름님! 형식으로 출력하세요.',
        "marker": '함수의 기본값(default) 인수',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⚙️ 함수의 기본값(default) 인수</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">함수를 정의할 때 <code>def greet(name, greeting="안녕하세요"):</code>처럼 매개변수에 기본값을 지정하면, 그 인수를 넘기지 않고 함수를 불러도 기본값이 자동으로 사용돼요. 입력이 한 줄에 몰려 들어올 때는 <code>split()</code> 결과의 개수에 따라 분기해서 처리하면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def greet(name, greeting="안녕하세요"):
    print(f"{greeting}, {name}님!")

parts = input().split()
if len(parts) == 1:
    greet(parts[0])
else:
    greet(parts[0], parts[1])</pre>
</div>
""",
    },
    {
        "id": 332,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 재귀 함수로 합계를 계산해 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 재귀 함수로 합계를 계산해 출력하세요.',
        "marker": '재귀로 리스트 합계 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➕ 재귀로 리스트 합계 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 합을 재귀로 구하려면 "리스트의 합 = 첫 번째 값 + (나머지 리스트의 합)"으로 생각하면 돼요. 리스트가 비어 있으면 더 더할 게 없으니 0을 반환하는 게 기저 조건이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def total(nums):
    if not nums:          # 빈 리스트면
        return 0
    return nums[0] + total(nums[1:])

nums = list(map(int, input().split()))
print(total(nums))</pre>
</div>
""",
    },
    {
        "id": 333,
        "old": '<p>두 양의 정수가 입력되면 유클리드 알고리즘(재귀)으로 GCD를 구해 출력하세요.</p>',
        "problem_text": '두 양의 정수가 입력되면 유클리드 알고리즘(재귀)으로 GCD를 구해 출력하세요.',
        "marker": '재귀로 최대공약수(GCD) 구하기 - 유클리드 알고리즘',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧮 재귀로 최대공약수(GCD) 구하기 - 유클리드 알고리즘</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 수 a, b의 최대공약수는 "b와, a를 b로 나눈 나머지의 최대공약수"와 같다는 성질이 있어요(유클리드 알고리즘). 나머지가 0이 되는 순간이 기저 조건이고, 그때의 b(혹은 a)가 바로 최대공약수예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

a, b = map(int, input().split())
print(gcd(a, b))</pre>
</div>
""",
    },
    {
        "id": 334,
        "old": '<p>정수 여러 개와 연산 기호(+, *)가 입력됩니다. + 면 합계, * 면 곱을 출력하세요.</p>',
        "problem_text": '정수 여러 개와 연산 기호(+, *)가 입력됩니다. + 면 합계, * 면 곱을 출력하세요.',
        "marker": '함수를 다른 함수의 인수로 전달하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧩 함수를 다른 함수의 인수로 전달하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬에서는 함수도 변수처럼 다른 함수에 "전달"할 수 있어요. 연산 기호에 따라 실제로 쓸 함수를 미리 정해두고, 그 함수를 매개변수로 받아 실행하는 방식이에요. 예를 들어 딕셔너리에 "기호: 함수"를 매핑해두면 깔끔하게 분기할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def add(nums):
    return sum(nums)

def mul(nums):
    result = 1
    for n in nums:
        result *= n
    return result

ops = {"+": add, "*": mul}   # 기호에 맞는 함수를 딕셔너리에 저장
parts = input().split()
op_symbol = parts[0]
nums = list(map(int, parts[1:]))
print(ops[op_symbol](nums))   # 함수를 값처럼 꺼내서 바로 호출</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 4장(함수 심화: 재귀·람다·고급) 문항 10건에 개념 설명 카드를 추가합니다."

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
