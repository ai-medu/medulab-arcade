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
        "id": 375,
        "old": '<p>정수 다섯 개가 한 줄에 입력됩니다. 최댓값과 최솟값을 각각 하나씩 제외하고 나머지의 합을 출력하세요.</p>',
        "problem_text": '정수 다섯 개가 한 줄에 입력됩니다. 최댓값과 최솟값을 각각 하나씩 제외하고 나머지의 합을 출력하세요.',
        "marker": '최댓값·최솟값 하나씩 제외하고 합계 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➕ 최댓값·최솟값 하나씩 제외하고 합계 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">전체 합에서 최댓값과 최솟값을 한 번씩만 빼면 돼요. <code>sum()</code>으로 전체 합을 구하고, <code>max()</code>와 <code>min()</code>으로 각각 최댓값·최솟값을 찾아 한 번씩 빼주면 됩니다.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
result = sum(nums) - max(nums) - min(nums)
print(result)</pre>
</div>
""",
    },
    {
        "id": 376,
        "old": '<p>물건 가격과 지불 금액이 한 줄에 입력됩니다. 500원, 100원, 50원, 10원 동전으로 거스름돈을 최소 개수로 주는 각 동전 수를 출력하세요.</p>',
        "problem_text": '물건 가격과 지불 금액이 한 줄에 입력됩니다. 500원, 100원, 50원, 10원 동전으로 거스름돈을 최소 개수로 주는 각 동전 수를 출력하세요.',
        "marker": '거스름돈을 동전 종류별로 최소 개수로 계산하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🪙 거스름돈을 동전 종류별로 최소 개수로 계산하기 (그리디)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">거스름돈을 최소 개수의 동전으로 주려면, "가장 큰 단위 동전부터 최대한 많이 사용"하면 돼요(그리디 알고리즘). 거스름돈을 500으로 나눈 몫만큼 500원 동전을 쓰고, 남은 금액을 다음 단위(100원)로 다시 나누는 걸 반복해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">price, paid = map(int, input().split())
change = paid - price
coins = [500, 100, 50, 10]
result = []
for coin in coins:
    result.append(change // coin)
    change %= coin
print(*result)</pre>
</div>
""",
    },
    {
        "id": 377,
        "old": '<p>키(cm)가 한 줄에 여러 개 입력됩니다. 170 이상인 값만 오름차순으로 출력하세요.</p>',
        "problem_text": '키(cm)가 한 줄에 여러 개 입력됩니다. 170 이상인 값만 오름차순으로 출력하세요.',
        "marker": '조건을 만족하는 값만 필터링 후 정렬',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📏 조건을 만족하는 값만 필터링 후 정렬</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">조건에 맞는 값만 골라내는 건 리스트 컴프리헨션의 if 조건으로, 그 다음 정렬은 <code>sorted()</code>로 처리하면 돼요. 두 단계를 이어붙이면 "필터링 → 정렬" 패턴을 간단히 구현할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">heights = list(map(int, input().split()))
result = sorted(h for h in heights if h >= 170)
print(*result)</pre>
</div>
""",
    },
    {
        "id": 378,
        "old": '<p>정수 여러 개와 구간 시작·끝 인덱스가 두 줄에 입력됩니다. 해당 구간의 평균을 소수 둘째 자리로 출력하세요.</p>',
        "problem_text": '정수 여러 개와 구간 시작·끝 인덱스가 두 줄에 입력됩니다. 해당 구간의 평균을 소수 둘째 자리로 출력하세요.',
        "marker": '리스트 구간 평균 구하기 (슬라이싱 + 평균)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📊 리스트 구간 평균 구하기 (슬라이싱 + 평균)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">특정 구간의 평균을 구하려면, 먼저 슬라이싱으로 그 구간만 잘라낸 다음 <code>sum()/len()</code>으로 평균을 계산하면 돼요. 소수 둘째 자리는 <code>round(값, 2)</code>로 맞춰요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
start, end = map(int, input().split())
segment = nums[start:end+1]
print(round(sum(segment) / len(segment), 2))</pre>
</div>
""",
    },
    {
        "id": 379,
        "old": '<p>단어 여러 개가 한 줄에 입력됩니다. 길이 4 이하와 5 이상으로 분류해 각각 오름차순으로 출력하세요.</p>',
        "problem_text": '단어 여러 개가 한 줄에 입력됩니다. 길이 4 이하와 5 이상으로 분류해 각각 오름차순으로 출력하세요.',
        "marker": '조건에 따라 두 그룹으로 나누기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔀 조건에 따라 두 그룹으로 나누기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">하나의 리스트를 조건에 따라 두 그룹으로 나눌 때는, 두 개의 리스트 컴프리헨션(또는 for문)을 각각 돌려서 조건을 만족하는 것과 만족하지 않는 것을 따로 모으면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
short_words = sorted(w for w in words if len(w) <= 4)
long_words = sorted(w for w in words if len(w) >= 5)
print(*short_words)
print(*long_words)</pre>
</div>
""",
    },
    {
        "id": 380,
        "old": '<p>두 줄에 정수 여러 개씩 입력됩니다. 두 리스트에 공통으로 있는 수를 오름차순으로 출력하세요.</p>',
        "problem_text": '두 줄에 정수 여러 개씩 입력됩니다. 두 리스트에 공통으로 있는 수를 오름차순으로 출력하세요.',
        "marker": '두 리스트의 공통 원소 찾기 (교집합)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔀 두 리스트의 공통 원소 찾기 (교집합)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 리스트에 공통으로 들어있는 값을 찾는 것은 집합의 교집합(<code>&</code>)과 똑같은 개념이에요(308번 참고). 각각 set으로 바꿔 교집합을 구하고, 보기 좋게 정렬해서 출력하면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = set(map(int, input().split()))
b = set(map(int, input().split()))
print(*sorted(a & b))</pre>
</div>
""",
    },
    {
        "id": 381,
        "old": '<p>문자열이 입력되면 재귀 함수로 뒤집어 출력하세요.</p>',
        "problem_text": '문자열이 입력되면 재귀 함수로 뒤집어 출력하세요.',
        "marker": '재귀로 문자열 뒤집기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔁 재귀로 문자열 뒤집기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열을 뒤집는 재귀 아이디어는 "첫 글자를 맨 뒤로 보내고, 나머지 문자열도 뒤집은 것"을 합치는 거예요. 즉 <code>reverse(s) = reverse(s[1:]) + s[0]</code> 형태로 쪼갤 수 있어요. 빈 문자열이 기저 조건이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def reverse(s):
    if s == "":
        return ""
    return reverse(s[1:]) + s[0]

s = input()
print(reverse(s))</pre>
</div>
""",
    },
    {
        "id": 382,
        "old": '<p>3행 3열 행렬이 세 줄에 입력됩니다. 전치 행렬을 출력하세요.</p>',
        "problem_text": '3행 3열 행렬이 세 줄에 입력됩니다. 전치 행렬을 출력하세요.',
        "marker": '행렬 전치(Transpose) 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 행렬 전치(Transpose) 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">전치 행렬은 행과 열을 서로 바꾼 행렬이에요. 즉 원래 행렬의 i행 j열 값이, 전치 행렬에서는 j행 i열로 가요. <code>zip(*행렬)</code>을 쓰면 이 변환을 한 번에 할 수 있어요 — <code>*</code>로 각 행을 풀어서 zip에 넘기면, 같은 열의 값들이 하나로 묶여요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">matrix = [list(map(int, input().split())) for _ in range(3)]
transposed = list(zip(*matrix))
for row in transposed:
    print(*row)</pre>
</div>
""",
    },
    {
        "id": 383,
        "old": '<p>정수 여러 개가 입력됩니다. 두 수의 합이 같은 쌍의 개수를 출력하세요. (중복 쌍 제외, i&lt;j)</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 두 수의 합이 같은 쌍의 개수를 출력하세요. (중복 쌍 제외, i&lt;j)',
        "marker": '합이 같은 쌍의 개수 세기 (이중 반복 + 조건)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 합이 같은 쌍의 개수 세기 (이중 반복 + 조건)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"i < j"라는 조건은 "같은 쌍을 두 번 세지 않도록" 순서를 정해주는 역할이에요. 이중 for문으로 모든 (i, j) 쌍을 확인하면서, 두 값의 합이 특정 조건(여기서는 서로 같은 합을 만드는 쌍의 개수)을 만족하면 세면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
n = len(nums)
sum_count = {}
for i in range(n):
    for j in range(i + 1, n):
        s = nums[i] + nums[j]
        sum_count[s] = sum_count.get(s, 0) + 1
# 가장 많이 나온 합을 만드는 쌍의 개수 등 문제 조건에 맞게 활용
print(max(sum_count.values()))</pre>
</div>
""",
    },
    {
        "id": 384,
        "old": '<p>첫 줄에 문장, 둘째 줄에 k가 입력됩니다. 빈도 높은 순으로 k개 단어를 출력하세요. 동률이면 알파벳 순으로 정렬하세요.</p>',
        "problem_text": '첫 줄에 문장, 둘째 줄에 k가 입력됩니다. 빈도 높은 순으로 k개 단어를 출력하세요. 동률이면 알파벳 순으로 정렬하세요.',
        "marker": '빈도수 상위 k개 단어 (빈도 내림차순, 동률은 알파벳순)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🏆 빈도수 상위 k개 단어 (빈도 내림차순, 동률은 알파벳순)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">단어 빈도를 딕셔너리로 구한 뒤(305번 참고), "빈도는 내림차순, 동률이면 알파벳 순"으로 정렬해야 해요. 343번에서 배운 트릭처럼 빈도에는 음수(-)를 붙이고 단어는 그대로 두면, 한 번의 <code>sorted(key=...)</code>로 두 기준을 동시에 처리할 수 있어요. 그 중 앞의 k개만 꺼내면 끝이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">sentence = input()
k = int(input())
words = sentence.split()
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1
ranked = sorted(count.items(), key=lambda x: (-x[1], x[0]))
for word, _ in ranked[:k]:
    print(word)</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 9장(실전 모의고사 1) 문항 10건에 개념 설명 카드를 추가합니다."

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
