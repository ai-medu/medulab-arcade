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
        "id": 295,
        "old": '<p>정수 n이 입력되면 1부터 n까지 각 수의 제곱으로 이루어진 리스트를 출력하세요.</p>',
        "problem_text": '정수 n이 입력되면 1부터 n까지 각 수의 제곱으로 이루어진 리스트를 출력하세요.',
        "marker": '리스트 컴프리헨션',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧮 리스트 컴프리헨션(list comprehension)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">반복문으로 리스트를 만들 때 <code>for</code>문을 여러 줄 쓰는 대신, 한 줄로 리스트를 만드는 문법이에요. <code>[표현식 for 변수 in 반복대상]</code> 형태로 쓰며, 각 값을 표현식에 넣어 새 리스트를 만들어줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
result = [i**2 for i in range(1, n+1)]
print(result)
# n=3 이면 [1, 4, 9]</pre>
</div>
""",
    },
    {
        "id": 296,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 짝수만 추출해 리스트로 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 짝수만 추출해 리스트로 출력하세요.',
        "marker": '컴프리헨션에 조건(if) 붙이기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔍 컴프리헨션에 조건(if) 붙이기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트 컴프리헨션 뒤에 <code>if 조건</code>을 붙이면, 조건을 만족하는 값만 골라 새 리스트를 만들 수 있어요. 짝수만 고르고 싶다면 "2로 나눈 나머지가 0"이라는 조건을 붙이면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
evens = [x for x in nums if x % 2 == 0]
print(evens)</pre>
</div>
""",
    },
    {
        "id": 297,
        "old": '<p>3행 3열로 정수 9개가 세 줄에 걸쳐 입력됩니다. 모든 원소의 합을 출력하세요.</p>',
        "problem_text": '3행 3열로 정수 9개가 세 줄에 걸쳐 입력됩니다. 모든 원소의 합을 출력하세요.',
        "marker": '2차원 리스트와 이중 for문',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 2차원 리스트와 이중 for문</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">2차원 리스트는 "리스트 안에 리스트"가 들어있는 구조예요. 표(행과 열)를 떠올리면 쉬워요. 모든 원소를 하나하나 확인하려면 바깥 for문으로 행을 고르고, 안쪽 for문으로 그 행의 각 값을 확인하는 이중 for문을 써요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">matrix = [list(map(int, input().split())) for _ in range(3)]
total = 0
for row in matrix:
    for val in row:
        total += val
print(total)</pre>
</div>
""",
    },
    {
        "id": 298,
        "old": '<p>3행 3열 행렬이 세 줄에 입력됩니다. 왼쪽 위에서 오른쪽 아래로의 대각선 합을 출력하세요.</p>',
        "problem_text": '3행 3열 행렬이 세 줄에 입력됩니다. 왼쪽 위에서 오른쪽 아래로의 대각선 합을 출력하세요.',
        "marker": '대각선 원소 접근하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">↗️ 대각선 원소 접근하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">행렬에서 왼쪽 위 → 오른쪽 아래로 가는 대각선은 "행 번호와 열 번호가 같은 자리"예요. 즉 <code>matrix[0][0]</code>, <code>matrix[1][1]</code>, <code>matrix[2][2]</code>처럼 인덱스가 같은 값들만 모으면 대각선이 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">matrix = [list(map(int, input().split())) for _ in range(3)]
total = sum(matrix[i][i] for i in range(3))
print(total)</pre>
</div>
""",
    },
    {
        "id": 299,
        "old": '<p>단어 여러 개가 한 줄에 입력됩니다. 0번 인덱스부터 인덱스:단어 형식으로 한 줄씩 출력하세요.</p>',
        "problem_text": '단어 여러 개가 한 줄에 입력됩니다. 0번 인덱스부터 인덱스:단어 형식으로 한 줄씩 출력하세요.',
        "marker": 'enumerate로 인덱스와 값 함께 꺼내기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 enumerate로 인덱스와 값 함께 꺼내기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트를 반복할 때 값뿐 아니라 "몇 번째인지(인덱스)"도 같이 필요할 때가 많아요. 매번 번호를 따로 세는 변수를 만드는 대신, <code>enumerate(리스트)</code>를 쓰면 (인덱스, 값) 쌍을 바로 꺼낼 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
for idx, word in enumerate(words):
    print(f"{idx}:{word}")</pre>
</div>
""",
    },
    {
        "id": 300,
        "old": '<p>두 줄에 각각 정수 세 개씩 입력됩니다. 같은 위치의 값을 더한 결과를 공백으로 구분해 출력하세요.</p>',
        "problem_text": '두 줄에 각각 정수 세 개씩 입력됩니다. 같은 위치의 값을 더한 결과를 공백으로 구분해 출력하세요.',
        "marker": 'zip으로 두 리스트 짝지어 순회하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔗 zip으로 두 리스트 짝지어 순회하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 리스트의 같은 위치 값끼리 짝지어 쓰고 싶을 때, 인덱스로 하나씩 꺼내는 대신 <code>zip(리스트1, 리스트2)</code>를 쓰면 두 리스트를 같은 자리끼리 묶어서 한 번에 꺼낼 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = list(map(int, input().split()))
b = list(map(int, input().split()))
result = [x + y for x, y in zip(a, b)]
print(*result)</pre>
</div>
""",
    },
    {
        "id": 301,
        "old": '<p>한 줄에 정수 여섯 개가 입력됩니다. 인덱스 2부터 4까지(4 포함)의 원소를 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여섯 개가 입력됩니다. 인덱스 2부터 4까지(4 포함)의 원소를 출력하세요.',
        "marker": '리스트 슬라이싱(일부 구간 잘라내기)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✂️ 리스트 슬라이싱(일부 구간 잘라내기)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 일부 구간만 꺼내고 싶을 때는 <code>리스트[시작:끝]</code> 슬라이싱을 써요. 주의할 점은 "끝 인덱스는 포함되지 않는다"는 거예요. 인덱스 2부터 4까지(4 포함) 꺼내려면 끝 값에 1을 더해 <code>[2:5]</code>로 써야 해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
print(nums[2:5])   # 인덱스 2,3,4 포함</pre>
</div>
""",
    },
    {
        "id": 302,
        "old": '<p>정수 여러 개가 한 줄에 입력됩니다. 중복을 제거하고 오름차순으로 정렬해 출력하세요.</p>',
        "problem_text": '정수 여러 개가 한 줄에 입력됩니다. 중복을 제거하고 오름차순으로 정렬해 출력하세요.',
        "marker": 'set으로 중복 제거 후 sorted로 정렬',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧹 set으로 중복 제거 후 sorted로 정렬</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 중복된 값을 없애고 싶을 때는 <code>set()</code>으로 바꿔주면 돼요. 집합(set)은 같은 값을 하나만 저장하는 자료구조라서 자동으로 중복이 사라져요. 다만 set은 순서가 없기 때문에, 정렬된 결과가 필요하면 다시 <code>sorted()</code>로 리스트화해야 해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
result = sorted(set(nums))
print(*result)</pre>
</div>
""",
    },
    {
        "id": 303,
        "old": '<p>한 줄에 정수 다섯 개와 회전 횟수 k가 한 줄씩 입력됩니다. 리스트를 왼쪽으로 k번 회전한 결과를 출력하세요.</p>',
        "problem_text": '한 줄에 정수 다섯 개와 회전 횟수 k가 한 줄씩 입력됩니다. 리스트를 왼쪽으로 k번 회전한 결과를 출력하세요.',
        "marker": '리스트를 왼쪽으로 k번 회전시키기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 리스트를 왼쪽으로 k번 회전시키기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트를 왼쪽으로 1번 회전한다는 건 "맨 앞의 값을 떼서 맨 뒤에 붙이는 것"과 같아요. k번 회전하려면 이걸 k번 반복해도 되지만, 슬라이싱으로 한 번에 처리할 수도 있어요: 앞에서 k개를 떼어 뒤에 붙이면 끝!</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
k = int(input())
k %= len(nums)   # k가 길이보다 커도 안전하게
rotated = nums[k:] + nums[:k]
print(*rotated)</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>k %= len(nums)</code>를 해두면 회전 횟수가 리스트 길이보다 커도 문제없이 동작해요.</p>
</div>
""",
    },
    {
        "id": 304,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 짝수는 그대로, 홀수는 -1을 곱해 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 짝수는 그대로, 홀수는 -1을 곱해 출력하세요.',
        "marker": '조건에 따라 다르게 변환하기(삼항 표현식)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⚖️ 조건에 따라 다르게 변환하기(삼항 표현식)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 각 값을 조건에 따라 서로 다르게 바꿔야 할 때는, 컴프리헨션 안에 <code>값A if 조건 else 값B</code> 형태의 삼항 표현식을 넣으면 돼요. "조건이 맞으면 A, 아니면 B"를 한 줄로 표현하는 방법이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
result = [x if x % 2 == 0 else x * -1 for x in nums]
print(*result)</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 1장(리스트 심화) 문항 10건에 개념 설명 카드를 추가합니다."

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
