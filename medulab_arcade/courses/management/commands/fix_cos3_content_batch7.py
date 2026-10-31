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
        "id": 1253,
        "old": "<p>정수 n이 입력되면 is_prime(n) 함수로 소수이면 소수, 아니면 합성수를 출력하세요.</p>",
        "problem_text": "정수 n이 입력되면 is_prime(n) 함수로 소수이면 소수, 아니면 합성수를 출력하세요.",
        "marker": "소수(prime number)란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 소수(prime number)란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><strong>소수</strong>는 1과 자기 자신으로만 나누어지는 2 이상의 수예요. 예를 들어 7은 1과 7로만 나누어지니 소수이고, 6은 1, 2, 3, 6으로 나누어지니 소수가 아니에요(합성수).</p>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔍 2부터 n-1까지 나눠보며 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">n이 소수인지 확인하려면, 2부터 n-1까지의 모든 수로 나눠보면서 "딱 나누어지는(나머지가 0인) 수"가 하나라도 있는지 살펴보면 돼요. 그런 수가 있다면 소수가 아니고, 끝까지 없다면 소수예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:   # 나누어지는 수를 찾으면
            return False   # 바로 소수가 아니라고 결론
    return True            # 끝까지 못 찾으면 소수</pre>
</div>
""",
    },
    {
        "id": 1254,
        "old": "<p>단어 여러 개가 공백으로 입력됩니다. apple 이라는 단어가 몇 번 나오는지 출력하세요.</p>",
        "problem_text": "단어 여러 개가 공백으로 입력됩니다. apple 이라는 단어가 몇 번 나오는지 출력하세요.",
        "marker": "딕셔너리(dict)란 무엇인가",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📖 딕셔너리(dict)란 무엇인가?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">진짜 사전을 생각해보세요. "단어"를 찾으면 그 "뜻"이 바로 나오죠. 파이썬의 <strong>딕셔너리</strong>도 마찬가지로 <code>키(key)</code>와 <code>값(value)</code>을 한 쌍으로 저장해요. <code>{}</code>로 빈 딕셔너리를 만들고, <code>딕셔너리[키] = 값</code>으로 저장하거나 수정할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">count = {}
count['apple'] = 3
print(count['apple'])   # 3</pre>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧮 get()으로 안전하게 값 꺼내며 개수 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">아직 키가 없는 상태에서 <code>딕셔너리[키]</code>로 바로 접근하면 에러가 나요. <code>딕셔너리.get(키, 기본값)</code>을 쓰면 키가 없을 때 에러 대신 기본값을 돌려줘서 안전해요. 그래서 "단어별 등장 횟수"를 셀 때 아주 유용해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1   # 없으면 0에서 시작해 1 더함
print(count.get('apple', 0))          # apple의 등장 횟수 (없으면 0)</pre>
</div>
""",
    },
    {
        "id": 1256,
        "old": "<p>정수 두 개가 입력되면 유클리드 호제법으로 최대공약수를 출력하세요.</p>",
        "problem_text": "정수 두 개가 입력되면 유클리드 호제법으로 최대공약수를 출력하세요.",
        "marker": "유클리드 호제법으로 최대공약수(GCD) 구하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➗ 최대공약수(GCD)란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 수를 동시에 나눌 수 있는 가장 큰 수를 <strong>최대공약수</strong>라고 해요. 예를 들어 12와 18은 둘 다 6으로 나누어지고, 6보다 큰 공통 약수는 없으니 최대공약수는 6이에요.</p>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🌀 유클리드 호제법으로 최대공약수(GCD) 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 수를 1부터 하나씩 나눠보며 공약수를 찾는 건 느려요. <strong>유클리드 호제법</strong>은 "두 수의 최대공약수는, 큰 수를 작은 수로 나눈 나머지와 작은 수의 최대공약수와 같다"는 성질을 이용해요. 나머지가 0이 될 때까지 (a, b) → (b, a % b)로 계속 바꿔가면 마지막 a가 바로 최대공약수예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
while b != 0:
    a, b = b, a % b   # (a, b)를 (b, a를 b로 나눈 나머지)로 갱신
print(a)                # b가 0이 되면 a가 최대공약수</pre>
</div>
""",
    },
    {
        "id": 1257,
        "old": "<p>영소문자로만 이루어진 문자열이 입력되면 각 글자를 알파벳 순서상 바로 다음 글자로 바꿔 출력하세요. (z는 고려하지 않습니다)</p>",
        "problem_text": "영소문자로만 이루어진 문자열이 입력되면 각 글자를 알파벳 순서상 바로 다음 글자로 바꿔 출력하세요. (z는 고려하지 않습니다)",
        "marker": "ord()와 chr()로 문자와 코드값 변환하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔡 ord()와 chr()로 문자와 코드값 변환하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">컴퓨터 안에서는 모든 글자가 사실 숫자(코드값)로 저장돼요. 예를 들어 'a'는 97번, 'b'는 98번이에요. <code>ord(문자)</code>는 글자를 그 코드 숫자로 바꿔주고, 반대로 <code>chr(숫자)</code>는 코드 숫자를 다시 글자로 바꿔줘요. 그래서 "다음 글자"를 구하려면 코드값에 1을 더한 뒤 다시 글자로 바꾸면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">print(ord('a'))        # 97
print(chr(98))         # 'b'

s = input().strip()
result = ''
for ch in s:
    result += chr(ord(ch) + 1)   # 코드값에 1을 더해 다음 글자로
print(result)</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 모의고사6 문항에 부족한 개념 설명(소수 판별, 딕셔너리, 유클리드 호제법, ord/chr)을 추가합니다."

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
