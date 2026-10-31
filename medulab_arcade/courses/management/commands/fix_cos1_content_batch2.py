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
        "id": 405,
        "old": '<p>정수 여러 개가 입력됩니다. 병합 정렬로 오름차순 정렬해 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 병합 정렬로 오름차순 정렬해 출력하세요.',
        "marker": '병합 정렬(merge sort)의 원리',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪄 병합 정렬(merge sort)의 원리</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">병합 정렬은 \'나누고(divide) 합친다(conquer)\'는 분할정복 전략을 써요. 리스트를 반으로 계속 쪼개다가 원소가 1개만 남으면(이미 정렬된 상태) 더 못 쪼개고, 그 작은 조각들을 두 개씩 비교하며 정렬된 상태로 합쳐 나가요. 합칠 때는 두 정렬된 리스트의 맨 앞끼리 비교해서 더 작은 걸 꺼내는 방식(두 포인터)을 써요. 시간복잡도는 항상 O(n log n)으로 안정적이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    result, i, j = [], 0, 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i]); i += 1\n        else:\n            result.append(right[j]); j += 1\n    return result + left[i:] + right[j:]\n\nnums = list(map(int, input().split()))\nprint(*merge_sort(nums))</pre>\n</div>\n',
    },
    {
        "id": 406,
        "old": '<p>정수 여러 개가 입력됩니다. 퀵 정렬로 오름차순 정렬해 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 퀵 정렬로 오름차순 정렬해 출력하세요.',
        "marker": '퀵 정렬(quick sort)의 원리',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🎯 퀵 정렬(quick sort)의 원리</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">퀵 정렬은 기준값(피벗)을 하나 정해서, 피벗보다 작은 값들과 큰 값들로 리스트를 나눈 뒤 각각을 다시 재귀적으로 정렬해요. 피벗보다 작은 그룹 + 피벗 + 피벗보다 큰 그룹을 이어 붙이면 전체가 정렬돼요. 리스트 컴프리헨션으로 작은 값/같은 값/큰 값을 나누면 코드가 아주 간결해져요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    smaller = [x for x in arr if x < pivot]\n    equal = [x for x in arr if x == pivot]\n    larger = [x for x in arr if x > pivot]\n    return quick_sort(smaller) + equal + quick_sort(larger)\n\nnums = list(map(int, input().split()))\nprint(*quick_sort(nums))</pre>\n</div>\n',
    },
    {
        "id": 407,
        "old": '<p>정수 여러 개가 입력됩니다. 역전쌍(i&lt;j 이고 a[i]&gt;a[j])의 수를 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 역전쌍(i&lt;j 이고 a[i]&gt;a[j])의 수를 출력하세요.',
        "marker": '병합 정렬로 역전쌍(inversion) 세기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔁 병합 정렬로 역전쌍(inversion) 세기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">역전쌍은 \'앞에 있는 수가 뒤에 있는 수보다 큰 쌍\'이에요. 모든 쌍을 다 비교하면 O(n²)이지만, 병합 정렬 과정을 활용하면 O(n log n)에 셀 수 있어요. 두 정렬된 반쪽을 합칠 때, 오른쪽 원소가 왼쪽 원소보다 먼저 선택된다는 건 \'왼쪽에 아직 남은 원소 전부\'가 그 오른쪽 원소보다 크다는 뜻이에요. 그래서 그 순간 남은 왼쪽 원소 개수만큼 역전쌍이 한꺼번에 생겨요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def merge_count(arr):\n    if len(arr) <= 1:\n        return arr, 0\n    mid = len(arr) // 2\n    left, cl = merge_count(arr[:mid])\n    right, cr = merge_count(arr[mid:])\n    result, i, j, cnt = [], 0, 0, cl + cr\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i]); i += 1\n        else:\n            result.append(right[j]); j += 1\n            cnt += len(left) - i   # 왼쪽 남은 개수만큼 역전쌍\n    result += left[i:] + right[j:]\n    return result, cnt\n\nnums = list(map(int, input().split()))\n_, total = merge_count(nums)\nprint(total)</pre>\n</div>\n',
    },
    {
        "id": 408,
        "old": '<p>정수 여러 개와 k가 한 줄씩 입력됩니다. k번째로 작은 값을 힙으로 구해 출력하세요.</p>',
        "problem_text": '정수 여러 개와 k가 한 줄씩 입력됩니다. k번째로 작은 값을 힙으로 구해 출력하세요.',
        "marker": '힙(heap)으로 k번째 작은 값 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⛏️ 힙(heap)으로 k번째 작은 값 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">힙은 \'가장 작은(또는 큰) 값을 빠르게 꺼낼 수 있는\' 특수한 자료구조예요. 파이썬의 heapq 모듈은 리스트를 최소 힙으로 다룰 수 있게 해줘요. k번째로 작은 값을 찾고 싶을 때, 전체를 다 정렬할 필요 없이 heapq.nsmallest(k, nums)로 작은 값 k개만 뽑아내면 그 중 마지막(가장 큰) 값이 바로 k번째로 작은 값이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\nk = int(input())\n\nimport heapq\nsmallest_k = heapq.nsmallest(k, nums)\nprint(smallest_k[-1])</pre>\n</div>\n',
    },
    {
        "id": 409,
        "old": '<p>0 이상 100 이하 정수 여러 개가 입력됩니다. 카운팅 정렬로 오름차순 출력하세요.</p>',
        "problem_text": '0 이상 100 이하 정수 여러 개가 입력됩니다. 카운팅 정렬로 오름차순 출력하세요.',
        "marker": '카운팅 정렬(counting sort)이란?',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧮 카운팅 정렬(counting sort)이란?</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">카운팅 정렬은 값의 범위가 작을 때(여기선 0~100) 아주 빠르게 정렬하는 방법이에요. 비교를 전혀 하지 않고, 각 값이 몇 번 등장했는지 세는 카운트 배열을 만든 뒤, 0부터 차례로 \'등장한 만큼\' 출력하면 자동으로 정렬된 순서가 나와요. 시간복잡도는 O(n + 범위)로, 일반 정렬(O(n log n))보다도 빠를 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\ncount = [0] * 101\nfor x in nums:\n    count[x] += 1\n\nresult = []\nfor value in range(101):\n    result.extend([value] * count[value])\nprint(*result)</pre>\n</div>\n',
    },
    {
        "id": 410,
        "old": '<p>노드 수 n과 간선 수 m이 첫 줄에, 이후 m개의 간선(u v: u→v)이 입력됩니다. 위상 정렬 결과를 출력하세요.</p>',
        "problem_text": '노드 수 n과 간선 수 m이 첫 줄에, 이후 m개의 간선(u v: u→v)이 입력됩니다. 위상 정렬 결과를 출력하세요.',
        "marker": '위상 정렬(topological sort)이란?',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📶 위상 정렬(topological sort)이란?</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">위상 정렬은 \'먼저 해야 할 일 → 나중에 할 일\' 같은 순서 관계(방향이 있는 그래프)를 지키며 전체 순서를 정하는 방법이에요. 핵심은 진입차수(자신을 가리키는 간선의 수)가 0인 노드, 즉 \'선행 조건이 없는 노드\'부터 큐에 넣고 처리하는 거예요. 한 노드를 처리하면 그 노드가 가리키던 다음 노드들의 진입차수를 1씩 줄이고, 0이 되면 큐에 추가해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nindegree = [0] * (n + 1)\nfor _ in range(m):\n    u, v = map(int, input().split())\n    graph[u].append(v)\n    indegree[v] += 1\n\nq = deque([i for i in range(1, n + 1) if indegree[i] == 0])\nresult = []\nwhile q:\n    node = q.popleft()\n    result.append(node)\n    for nxt in graph[node]:\n        indegree[nxt] -= 1\n        if indegree[nxt] == 0:\n            q.append(nxt)\nprint(*result)</pre>\n</div>\n',
    },
    {
        "id": 411,
        "old": '<p>회의 수 n이 첫 줄에, 이후 시작·종료 시간이 n줄 입력됩니다. 겹치지 않게 최대한 많은 회의를 배정할 때 회의 수를 출력하세요.</p>',
        "problem_text": '회의 수 n이 첫 줄에, 이후 시작·종료 시간이 n줄 입력됩니다. 겹치지 않게 최대한 많은 회의를 배정할 때 회의 수를 출력하세요.',
        "marker": '정렬 기반 그리디: 회의실 배정',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🏢 정렬 기반 그리디: 회의실 배정</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">겹치지 않는 회의를 최대한 많이 배정하는 문제의 핵심은 \'종료 시간이 빠른 회의부터 고르는 것\'이 항상 최적이라는 사실이에요(그리디). 종료 시간 기준으로 정렬한 뒤, 마지막으로 선택한 회의의 종료 시간보다 시작 시간이 크거나 같은 회의를 만나면 선택하고 종료 시간을 갱신해 나가요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\nmeetings = [tuple(map(int, input().split())) for _ in range(n)]\nmeetings.sort(key=lambda x: x[1])   # 종료 시간 기준 정렬\n\ncount = 0\nlast_end = -1\nfor start, end in meetings:\n    if start >= last_end:\n        count += 1\n        last_end = end\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 412,
        "old": '<p>물건 수 n과 배낭 무게 W가 첫 줄에, 이후 무게:가치 쌍이 n줄 입력됩니다. 단위 무게당 가치가 높은 것부터 넣어 최대 가치를 소수 첫째 자리로 출력하세요. (물건은 쪼갤 수 있습니다)</p>',
        "problem_text": '물건 수 n과 배낭 무게 W가 첫 줄에, 이후 무게:가치 쌍이 n줄 입력됩니다. 단위 무게당 가치가 높은 것부터 넣어 최대 가치를 소수 첫째 자리로 출력하세요. (물건은 쪼갤 수 있습니다)',
        "marker": '그리디 배낭(Fractional Knapsack)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🎒 그리디 배낭(Fractional Knapsack)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">물건을 쪼갤 수 있는 배낭 문제는 0-1 배낭(DP가 필요)과 다르게 그리디로 풀려요. \'무게당 가치(가치/무게)\'가 높은 물건부터 최대한 채워 넣는 게 항상 최적이에요. 배낭이 남아있는 동안 비율이 가장 높은 물건을 꽉 채워 넣고, 마지막 물건은 남은 무게만큼만 쪼개서 넣으면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, cap = map(int, input().split())\nitems = []\nfor _ in range(n):\n    w, v = map(int, input().split())\n    items.append((v / w, w, v))\nitems.sort(reverse=True)   # 무게당 가치 내림차순\n\ntotal = 0.0\nfor ratio, w, v in items:\n    if cap <= 0:\n        break\n    take = min(w, cap)\n    total += ratio * take\n    cap -= take\nprint(round(total, 1))</pre>\n</div>\n',
    },
    {
        "id": 413,
        "old": '<p>정수 여러 개가 입력됩니다. 중앙값을 출력하세요. (정렬 후 가운데 값, 짝수 개면 가운데 두 값의 평균)</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 중앙값을 출력하세요. (정렬 후 가운데 값, 짝수 개면 가운데 두 값의 평균)',
        "marker": '정렬로 중앙값(median) 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📊 정렬로 중앙값(median) 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">중앙값은 데이터를 정렬했을 때 가운데에 오는 값이에요. 원소가 홀수 개면 정확히 가운데 인덱스(n//2) 하나를 쓰면 되고, 짝수 개면 가운데 두 값의 평균을 내야 해요. 정렬만 해두면 인덱스 계산만으로 바로 구할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = sorted(map(int, input().split()))\nn = len(nums)\nif n % 2 == 1:\n    median = nums[n // 2]\nelse:\n    median = (nums[n // 2 - 1] + nums[n // 2]) / 2\nprint(median)</pre>\n</div>\n',
    },
    {
        "id": 414,
        "old": '<p>정수 여러 개와 윈도우 크기 k가 한 줄씩 입력됩니다. 크기 k의 연속 부분 배열 중 합이 가장 큰 값을 출력하세요.</p>',
        "problem_text": '정수 여러 개와 윈도우 크기 k가 한 줄씩 입력됩니다. 크기 k의 연속 부분 배열 중 합이 가장 큰 값을 출력하세요.',
        "marker": '슬라이딩 윈도우로 구간 최대합 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪟 슬라이딩 윈도우로 구간 최대합 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">크기 k인 윈도우(구간)를 한 칸씩 오른쪽으로 옮길 때마다 합을 매번 처음부터 다시 더하면 느려요. 대신 \'맨 앞에서 빠지는 값은 빼고, 새로 들어오는 값만 더하는\' 방식으로 이전 합을 재활용하면 한 번에 O(1)로 갱신할 수 있어요. 첫 윈도우의 합만 직접 구하고, 이후부터는 슬라이딩하며 최댓값을 추적해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\nk = int(input())\n\nwindow_sum = sum(nums[:k])\nmax_sum = window_sum\nfor i in range(k, len(nums)):\n    window_sum += nums[i] - nums[i - k]   # 새로 들어온 값 더하고, 빠진 값 빼기\n    max_sum = max(max_sum, window_sum)\nprint(max_sum)</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 정렬 알고리즘 단원(40장) 문항 10건에 개념 설명 카드를 추가합니다."

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
