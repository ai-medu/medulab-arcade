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
        "id": 345,
        "old": '<p>첫 줄에 정수 여러 개, 둘째 줄에 찾을 값이 입력됩니다. 처음 나오는 인덱스를 출력하고, 없으면 -1을 출력하세요.</p>',
        "problem_text": '첫 줄에 정수 여러 개, 둘째 줄에 찾을 값이 입력됩니다. 처음 나오는 인덱스를 출력하고, 없으면 -1을 출력하세요.',
        "marker": '선형 탐색(Linear Search)이란?',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚶 선형 탐색(Linear Search)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">선형 탐색은 "앞에서부터 하나씩 차례대로 확인하는" 가장 단순한 탐색 방법이에요. 원하는 값을 찾으면 그 자리의 인덱스를 바로 돌려주고, 끝까지 못 찾으면 -1을 돌려줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
target = int(input())
result = -1
for i, n in enumerate(nums):
    if n == target:
        result = i
        break
print(result)</pre>
</div>
""",
    },
    {
        "id": 346,
        "old": '<p>첫 줄에 오름차순 정수 여러 개, 둘째 줄에 찾을 값이 입력됩니다. 이진 탐색으로 인덱스를 출력하고, 없으면 -1을 출력하세요.</p>',
        "problem_text": '첫 줄에 오름차순 정수 여러 개, 둘째 줄에 찾을 값이 입력됩니다. 이진 탐색으로 인덱스를 출력하고, 없으면 -1을 출력하세요.',
        "marker": '이진 탐색(Binary Search)이란?',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⚔️ 이진 탐색(Binary Search)이란? - 반드시 정렬되어 있어야 해요</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이진 탐색은 정렬된 리스트에서 쓸 수 있는 훨씬 빠른 탐색법이에요. 가운데 값을 확인해서 찾는 값보다 크면 "왼쪽 절반"만, 작으면 "오른쪽 절반"만 다시 탐색해요. 매번 탐색 범위가 절반으로 줄어서 매우 빨라요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
target = int(input())
lo, hi = 0, len(nums) - 1
result = -1
while lo <= hi:
    mid = (lo + hi) // 2
    if nums[mid] == target:
        result = mid
        break
    elif nums[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
print(result)</pre>
</div>
""",
    },
    {
        "id": 347,
        "old": '<p>첫 줄에 오름차순 정수 여러 개, 둘째 줄에 기준값이 입력됩니다. 기준값보다 처음으로 큰 값의 인덱스를 출력하세요. 없으면 -1을 출력하세요.</p>',
        "problem_text": '첫 줄에 오름차순 정수 여러 개, 둘째 줄에 기준값이 입력됩니다. 기준값보다 처음으로 큰 값의 인덱스를 출력하세요. 없으면 -1을 출력하세요.',
        "marker": '이진 탐색 변형: 기준값보다 처음으로 큰 값의 인덱스',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔎 이진 탐색 변형: 기준값보다 처음으로 큰 값의 인덱스</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">정렬된 리스트에서 "기준값보다 큰 첫 번째 값"을 찾는 것도 이진 탐색으로 할 수 있어요. 가운데 값이 기준값보다 크면 "정답일 수도 있으니 기억해두고 왼쪽을 더 좁혀보고", 작거나 같으면 오른쪽을 탐색해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
target = int(input())
lo, hi = 0, len(nums) - 1
result = -1
while lo <= hi:
    mid = (lo + hi) // 2
    if nums[mid] > target:
        result = mid
        hi = mid - 1
    else:
        lo = mid + 1
print(result)</pre>
</div>
""",
    },
    {
        "id": 348,
        "old": '<p>정수 여러 개가 입력됩니다. 최솟값이 처음 나오는 인덱스를 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 최솟값이 처음 나오는 인덱스를 출력하세요.',
        "marker": '선형 탐색으로 최솟값의 위치(인덱스) 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📍 선형 탐색으로 최솟값의 위치(인덱스) 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최솟값 자체는 <code>min()</code>으로 구할 수 있지만, "그 값이 몇 번째에 있는지"는 <code>index()</code>를 쓰거나 직접 하나씩 비교하면서 "지금까지 본 것 중 가장 작은 값의 위치"를 기억해두면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
min_idx = 0
for i in range(1, len(nums)):
    if nums[i] < nums[min_idx]:
        min_idx = i
print(min_idx)</pre>
</div>
""",
    },
    {
        "id": 349,
        "old": '<p>첫 줄에 오름차순 정수 여러 개, 둘째 줄에 찾을 값이 입력됩니다. 이진 탐색이 몇 번의 비교 끝에 값을 찾는지 출력하세요. 없으면 -1을 출력하세요.</p>',
        "problem_text": '첫 줄에 오름차순 정수 여러 개, 둘째 줄에 찾을 값이 입력됩니다. 이진 탐색이 몇 번의 비교 끝에 값을 찾는지 출력하세요. 없으면 -1을 출력하세요.',
        "marker": '이진 탐색의 비교 횟수 세기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 이진 탐색의 비교 횟수 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이진 탐색 코드에서 반복문이 한 번 돌 때마다 "비교를 한 번 했다"고 볼 수 있어요. 카운터 변수를 하나 두고, while 루프 안에서 값을 찾는 비교를 할 때마다 1씩 늘려주면 몇 번째에 찾았는지 알 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
target = int(input())
lo, hi = 0, len(nums) - 1
count = 0
result = -1
while lo <= hi:
    count += 1
    mid = (lo + hi) // 2
    if nums[mid] == target:
        result = count
        break
    elif nums[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
print(result)</pre>
</div>
""",
    },
    {
        "id": 350,
        "old": '<p>첫 줄에 정수 여러 개(정렬 안 됨), 둘째 줄에 찾을 값이 입력됩니다. 정렬 후 이진 탐색으로 값의 존재 여부를 YES/NO로 출력하세요.</p>',
        "problem_text": '첫 줄에 정수 여러 개(정렬 안 됨), 둘째 줄에 찾을 값이 입력됩니다. 정렬 후 이진 탐색으로 값의 존재 여부를 YES/NO로 출력하세요.',
        "marker": '정렬 안 된 리스트도 먼저 정렬하면 이진 탐색 가능',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✅ 정렬 안 된 리스트도 먼저 정렬하면 이진 탐색 가능</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이진 탐색은 정렬된 상태에서만 동작하므로, 정렬이 안 되어 있다면 먼저 <code>sorted()</code>로 정렬한 다음 이진 탐색을 적용하면 돼요. 존재 여부만 궁금하다면 파이썬의 <code>in</code> 연산자로도 간단히 확인할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = sorted(map(int, input().split()))
target = int(input())
print("YES" if target in nums else "NO")</pre>
</div>
""",
    },
    {
        "id": 351,
        "old": '<p>첫 줄에 오름차순 정수 여러 개, 둘째 줄에 목표합이 입력됩니다. 합이 목표와 같은 두 수를 출력하세요. 없으면 NONE을 출력하세요.</p>',
        "problem_text": '첫 줄에 오름차순 정수 여러 개, 둘째 줄에 목표합이 입력됩니다. 합이 목표와 같은 두 수를 출력하세요. 없으면 NONE을 출력하세요.',
        "marker": '두 포인터(Two Pointer)로 두 수의 합 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">👈👉 두 포인터(Two Pointer)로 두 수의 합 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">정렬된 리스트에서 두 수를 더해 특정 목표값을 만드는 쌍을 찾을 때, 왼쪽 포인터는 맨 앞, 오른쪽 포인터는 맨 뒤에서 시작해요. 합이 목표보다 작으면 왼쪽을 오른쪽으로 한 칸, 크면 오른쪽을 왼쪽으로 한 칸 옮기며 좁혀가요. 이 방법은 모든 쌍을 다 비교하는 것보다 훨씬 빨라요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
target = int(input())
lo, hi = 0, len(nums) - 1
found = None
while lo < hi:
    s = nums[lo] + nums[hi]
    if s == target:
        found = (nums[lo], nums[hi])
        break
    elif s < target:
        lo += 1
    else:
        hi -= 1
print(f"{found[0]} {found[1]}" if found else "NONE")</pre>
</div>
""",
    },
    {
        "id": 352,
        "old": '<p>첫 줄에 정수 여러 개, 둘째 줄에 기준값이 입력됩니다. 기준값보다 큰 수를 모두 출력하세요. 없으면 NONE을 출력하세요.</p>',
        "problem_text": '첫 줄에 정수 여러 개, 둘째 줄에 기준값이 입력됩니다. 기준값보다 큰 수를 모두 출력하세요. 없으면 NONE을 출력하세요.',
        "marker": '선형 탐색으로 조건에 맞는 값 모두 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📋 선형 탐색으로 조건에 맞는 값 모두 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">하나만 찾는 게 아니라 조건을 만족하는 "모든" 값을 찾을 때는, 리스트 컴프리헨션으로 조건에 맞는 값만 전부 모으면 돼요(앞서 배운 조건부 컴프리헨션과 같은 원리예요).</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
threshold = int(input())
result = [n for n in nums if n > threshold]
print(*result if result else ["NONE"])</pre>
</div>
""",
    },
    {
        "id": 353,
        "old": '<p>첫 줄에 오름차순 정수 여러 개, 둘째 줄에 삽입할 값이 입력됩니다. 정렬을 유지하면서 삽입할 인덱스를 출력하세요.</p>',
        "problem_text": '첫 줄에 오름차순 정수 여러 개, 둘째 줄에 삽입할 값이 입력됩니다. 정렬을 유지하면서 삽입할 인덱스를 출력하세요.',
        "marker": '정렬을 유지하며 삽입할 위치 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📌 정렬을 유지하며 삽입할 위치 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">정렬된 리스트에 새 값을 넣어도 정렬 상태가 유지되는 위치를 찾는 문제예요. 이진 탐색으로 "이 값보다 작은 값들은 왼쪽에, 크거나 같은 값들은 오른쪽에" 두는 경계를 찾으면 그 경계가 바로 삽입 위치예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
val = int(input())
lo, hi = 0, len(nums)
while lo < hi:
    mid = (lo + hi) // 2
    if nums[mid] < val:
        lo = mid + 1
    else:
        hi = mid
print(lo)</pre>
</div>
""",
    },
    {
        "id": 354,
        "old": '<p>두 문자열이 한 줄씩 입력됩니다. 두 문자열이 아나그램이면 YES, 아니면 NO를 출력하세요.</p>',
        "problem_text": '두 문자열이 한 줄씩 입력됩니다. 두 문자열이 아나그램이면 YES, 아니면 NO를 출력하세요.',
        "marker": 'sorted()로 아나그램(Anagram) 확인하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 sorted()로 아나그램(Anagram) 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">아나그램은 "철자를 재배열하면 같아지는 두 단어"예요(예: listen, silent). 두 문자열을 각각 <code>sorted()</code>로 정렬하면 같은 글자들이 같은 순서로 나열되므로, 정렬된 결과가 같은지만 비교하면 쉽게 확인돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = input()
b = input()
print("YES" if sorted(a) == sorted(b) else "NO")</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 6장(탐색 알고리즘) 문항 10건에 개념 설명 카드를 추가합니다."

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
