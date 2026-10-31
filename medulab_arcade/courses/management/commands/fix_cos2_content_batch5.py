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
        "id": 335,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 버블 정렬을 직접 구현해 오름차순 결과를 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 버블 정렬을 직접 구현해 오름차순 결과를 출력하세요.',
        "marker": '버블 정렬(Bubble Sort)이란?',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🐑 버블 정렬(Bubble Sort)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">버블 정렬은 "이웃한 두 값을 계속 비교해서, 순서가 잘못돼 있으면 서로 바꿔주는" 방식이에요. 한 번 전체를 쭉 훑으면 가장 큰 값이 거품(bubble)처럼 맨 뒤로 떠오르고, 이걸 리스트 길이만큼 반복하면 전체가 정렬돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
n = len(nums)
for i in range(n):
    for j in range(n - 1 - i):
        if nums[j] > nums[j+1]:
            nums[j], nums[j+1] = nums[j+1], nums[j]
print(*nums)</pre>
</div>
""",
    },
    {
        "id": 336,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 선택 정렬을 직접 구현해 오름차순 결과를 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 선택 정렬을 직접 구현해 오름차순 결과를 출력하세요.',
        "marker": '선택 정렬(Selection Sort)이란?',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🎯 선택 정렬(Selection Sort)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">선택 정렬은 "아직 정렬 안 된 부분에서 가장 작은 값을 찾아, 맨 앞으로 보내는" 방식을 반복해요. 한 번 반복할 때마다 정렬된 부분이 한 칸씩 늘어나요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
n = len(nums)
for i in range(n):
    min_idx = i
    for j in range(i + 1, n):
        if nums[j] < nums[min_idx]:
            min_idx = j
    nums[i], nums[min_idx] = nums[min_idx], nums[i]
print(*nums)</pre>
</div>
""",
    },
    {
        "id": 337,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 삽입 정렬을 직접 구현해 오름차순 결과를 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 삽입 정렬을 직접 구현해 오름차순 결과를 출력하세요.',
        "marker": '삽입 정렬(Insertion Sort)이란?',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🃏 삽입 정렬(Insertion Sort)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">삽입 정렬은 카드를 손으로 정렬할 때처럼, "이미 정렬된 부분에 새 값을 알맞은 위치에 끼워넣는" 방식이에요. 새 값보다 큰 값들을 한 칸씩 뒤로 밀어내면서 자리를 만들어줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
for i in range(1, len(nums)):
    key = nums[i]
    j = i - 1
    while j >= 0 and nums[j] > key:
        nums[j+1] = nums[j]
        j -= 1
    nums[j+1] = key
print(*nums)</pre>
</div>
""",
    },
    {
        "id": 338,
        "old": '<p>한 줄에 정수 여러 개가 입력됩니다. 내림차순으로 정렬해 출력하세요.</p>',
        "problem_text": '한 줄에 정수 여러 개가 입력됩니다. 내림차순으로 정렬해 출력하세요.',
        "marker": 'sorted()의 reverse 옵션으로 내림차순 정렬',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⬇️ sorted()의 reverse 옵션으로 내림차순 정렬</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">직접 정렬 알고리즘을 구현하지 않아도, 파이썬의 <code>sorted(리스트, reverse=True)</code>를 쓰면 큰 값부터 작은 값 순서로(내림차순) 바로 정렬할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
print(*sorted(nums, reverse=True))</pre>
</div>
""",
    },
    {
        "id": 339,
        "old": '<p>단어 여러 개가 한 줄에 입력됩니다. 길이 오름차순으로 정렬하고, 길이가 같으면 알파벳 순으로 출력하세요.</p>',
        "problem_text": '단어 여러 개가 한 줄에 입력됩니다. 길이 오름차순으로 정렬하고, 길이가 같으면 알파벳 순으로 출력하세요.',
        "marker": '정렬 기준이 여러 개일 때 (튜플 key)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 정렬 기준이 여러 개일 때 (튜플 key)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"길이로 먼저 정렬하고, 길이가 같으면 알파벳 순으로"처럼 기준이 두 개 이상일 때는 <code>key=lambda x: (기준1, 기준2)</code> 형태로 튜플을 주면 돼요. 파이썬은 튜플을 비교할 때 첫 번째 기준이 같으면 자동으로 두 번째 기준을 비교해줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
result = sorted(words, key=lambda w: (len(w), w))
print(*result)</pre>
</div>
""",
    },
    {
        "id": 340,
        "old": '<p>첫 줄에 정수 여러 개, 둘째 줄에 k가 입력됩니다. k번째로 작은 값을 출력하세요. (k는 1부터 시작)</p>',
        "problem_text": '첫 줄에 정수 여러 개, 둘째 줄에 k가 입력됩니다. k번째로 작은 값을 출력하세요. (k는 1부터 시작)',
        "marker": '정렬 후 인덱스로 k번째 값 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 정렬 후 인덱스로 k번째 값 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"k번째로 작은 값"을 구하는 가장 쉬운 방법은, 정렬을 한 뒤 (k-1)번 인덱스를 꺼내는 거예요. k는 1부터 시작하는데, 인덱스는 0부터 시작하니까 1을 빼줘야 해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
k = int(input())
sorted_nums = sorted(nums)
print(sorted_nums[k - 1])</pre>
</div>
""",
    },
    {
        "id": 341,
        "old": '<p>정수 홀수 개가 한 줄에 입력됩니다. 정렬 후 중앙값을 출력하세요.</p>',
        "problem_text": '정수 홀수 개가 한 줄에 입력됩니다. 정렬 후 중앙값을 출력하세요.',
        "marker": '정렬 후 중앙값(median) 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⚖️ 정렬 후 중앙값(median) 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">중앙값은 "정렬했을 때 정확히 가운데 있는 값"이에요. 원소 개수가 홀수일 때는 정렬 후 <code>len(리스트)//2</code> 위치의 값이 바로 중앙값이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
sorted_nums = sorted(nums)
print(sorted_nums[len(sorted_nums) // 2])</pre>
</div>
""",
    },
    {
        "id": 342,
        "old": '<p>두 줄에 각각 정수 여러 개가 입력됩니다. 두 리스트를 합쳐 오름차순 정렬해 출력하세요.</p>',
        "problem_text": '두 줄에 각각 정수 여러 개가 입력됩니다. 두 리스트를 합쳐 오름차순 정렬해 출력하세요.',
        "marker": '두 리스트를 합쳐 정렬하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➕ 두 리스트를 합쳐 정렬하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 리스트를 하나로 합치려면 <code>+</code> 연산자를 쓰면 돼요(리스트 연결). 합친 뒤 <code>sorted()</code>로 정렬하면 끝이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = list(map(int, input().split()))
b = list(map(int, input().split()))
print(*sorted(a + b))</pre>
</div>
""",
    },
    {
        "id": 343,
        "old": '<p>이름:점수 쌍 여러 개가 콤마로 구분되어 입력됩니다. 점수 내림차순으로, 동점이면 이름 오름차순으로 출력하세요.</p>',
        "problem_text": '이름:점수 쌍 여러 개가 콤마로 구분되어 입력됩니다. 점수 내림차순으로, 동점이면 이름 오름차순으로 출력하세요.',
        "marker": '안정 정렬(Stable Sort): 동점일 때 보조 기준 적용',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🤝 안정 정렬(Stable Sort): 동점일 때 보조 기준 적용</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"점수 내림차순, 동점이면 이름 오름차순"처럼 1차·2차 기준이 서로 다른 방향일 때는, key에 튜플을 주되 내림차순이 필요한 값에는 음수(-)를 붙이는 트릭을 써요. 음수를 붙이면 오름차순 정렬이 원래 값 기준 내림차순처럼 동작해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">pairs = [kv.split(":") for kv in input().split(",")]
pairs = [(name, int(score)) for name, score in pairs]
result = sorted(pairs, key=lambda x: (-x[1], x[0]))
for name, score in result:
    print(name)</pre>
</div>
""",
    },
    {
        "id": 344,
        "old": '<p>한 줄에 정수 네 개가 입력됩니다. 버블 정렬의 각 패스 후 상태를 한 줄씩 출력하세요.</p>',
        "problem_text": '한 줄에 정수 네 개가 입력됩니다. 버블 정렬의 각 패스 후 상태를 한 줄씩 출력하세요.',
        "marker": '버블 정렬의 각 단계(패스) 출력하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">👀 버블 정렬의 각 단계(패스) 출력하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">버블 정렬은 바깥 for문 한 바퀴가 끝날 때마다 "한 패스"가 끝난 거예요. 그 시점의 리스트 상태를 바깥 for문 안, 안쪽 for문 밖에서 출력하면 각 패스 후의 중간 상태를 볼 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
n = len(nums)
for i in range(n):
    for j in range(n - 1 - i):
        if nums[j] > nums[j+1]:
            nums[j], nums[j+1] = nums[j+1], nums[j]
    print(*nums)   # 한 패스가 끝날 때마다 출력</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 5장(정렬 알고리즘 기초) 문항 10건에 개념 설명 카드를 추가합니다."

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
