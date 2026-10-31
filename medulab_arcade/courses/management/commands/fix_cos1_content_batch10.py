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
        "id": 485,
        "old": '<p>n m이 첫 줄에, m개의 간선(u v w)이 입력됩니다. 프림 알고리즘으로 MST 비용을 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, m개의 간선(u v w)이 입력됩니다. 프림 알고리즘으로 MST 비용을 출력하세요.',
        "marker": '프림(Prim) 알고리즘으로 MST 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🌲 프림(Prim) 알고리즘으로 MST 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">프림 알고리즘은 \'이미 연결된 영역에서, 바깥으로 나가는 가장 비용이 작은 간선\'을 계속 골라 트리를 키워가는 방법이에요. 크루스칼과 달리 전체 간선을 정렬하지 않고, 최소 힙으로 \'현재 트리에 연결 가능한 가장 싼 간선\'을 그때그때 꺼내요. 모든 노드가 트리에 포함될 때까지 반복하면 MST가 완성돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import heapq\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nfor _ in range(m):\n    u, v, w = map(int, input().split())\n    graph[u].append((w, v))\n    graph[v].append((w, u))\n\nvisited = [False] * (n + 1)\nheap = [(0, 1)]\ntotal = 0\nwhile heap:\n    w, node = heapq.heappop(heap)\n    if visited[node]:\n        continue\n    visited[node] = True\n    total += w\n    for nw, nxt in graph[node]:\n        if not visited[nxt]:\n            heapq.heappush(heap, (nw, nxt))\nprint(total)</pre>\n</div>\n',
    },
    {
        "id": 486,
        "old": '<p>정수 여러 개가 입력됩니다. LIS를 구성하는 수열 중 하나를 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. LIS를 구성하는 수열 중 하나를 출력하세요.',
        "marker": 'LIS 실제 수열 역추적하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📈 LIS 실제 수열 역추적하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">LIS의 길이만이 아니라 실제 수열이 궁금할 때는, dp[i]를 구하는 동시에 \'그 dp[i]를 만든 이전 인덱스(prev[i])\'도 함께 기록해요. 모든 dp를 채운 뒤 가장 긴 dp를 가진 인덱스에서 시작해, prev를 따라 거슬러 올라가며 수열을 복원하고 마지막에 순서를 뒤집어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\nn = len(nums)\ndp = [1] * n\nprev = [-1] * n\nfor i in range(n):\n    for j in range(i):\n        if nums[j] < nums[i] and dp[j] + 1 > dp[i]:\n            dp[i] = dp[j] + 1\n            prev[i] = j\n\nidx = dp.index(max(dp))\nresult = []\nwhile idx != -1:\n    result.append(nums[idx])\n    idx = prev[idx]\nprint(*reversed(result))</pre>\n</div>\n',
    },
    {
        "id": 487,
        "old": '<p>n q가 첫 줄에, n개의 정수가 둘째 줄에, 이후 min l r 쿼리가 입력됩니다. 각 구간 최솟값을 출력하세요.</p>',
        "problem_text": 'n q가 첫 줄에, n개의 정수가 둘째 줄에, 이후 min l r 쿼리가 입력됩니다. 각 구간 최솟값을 출력하세요.',
        "marker": '구간 최솟값 쿼리 처리하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📏 구간 최솟값 쿼리 처리하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">구간 [l, r]의 최솟값을 구하는 쿼리가 많지 않다면, 매 쿼리마다 그 구간을 슬라이싱해서 min()을 호출하는 것으로도 충분히 빠르게 풀 수 있어요(데이터와 쿼리가 아주 많아지면 세그먼트 트리로 O(log n) 쿼리가 필요해지지만, 핵심은 \'구간을 빠르게 질의하는 아이디어\'를 이해하는 거예요).</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, q = map(int, input().split())\nnums = list(map(int, input().split()))\nfor _ in range(q):\n    _, l, r = input().split()\n    l, r = int(l), int(r)\n    print(min(nums[l-1:r]))</pre>\n</div>\n',
    },
    {
        "id": 488,
        "old": '<p>n과 n-1개의 간선이 입력됩니다. 간선 하나를 끊었을 때 두 영역 크기 차이의 최솟값을 출력하세요.</p>',
        "problem_text": 'n과 n-1개의 간선이 입력됩니다. 간선 하나를 끊었을 때 두 영역 크기 차이의 최솟값을 출력하세요.',
        "marker": '완전탐색으로 전력망 분할 균형 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⚡ 완전탐색으로 전력망 분할 균형 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">트리 형태의 전력망에서 간선 하나를 끊으면 두 영역으로 나뉘는데, 어떤 간선을 끊어야 두 영역의 크기 차이가 가장 작을지 찾는 문제예요. 간선이 n-1개뿐이라 모든 간선을 하나씩 끊어보며 BFS/DFS로 한쪽 영역의 크기를 계산하는 완전탐색이 충분히 빠르게 동작해요. 한쪽 크기를 알면 다른 쪽은 (n - 그 크기)예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn = int(input())\nedges = [tuple(map(int, input().split())) for _ in range(n - 1)]\n\ndef size_of(root, banned, all_nodes):\n    graph = {x: [] for x in all_nodes}\n    for u, v in edges:\n        if (u, v) == banned or (v, u) == banned:\n            continue\n        graph[u].append(v)\n        graph[v].append(u)\n    visited = {root}\n    q = deque([root])\n    while q:\n        node = q.popleft()\n        for nxt in graph[node]:\n            if nxt not in visited:\n                visited.add(nxt)\n                q.append(nxt)\n    return len(visited)\n\nall_nodes = set()\nfor u, v in edges:\n    all_nodes.add(u); all_nodes.add(v)\n\nbest = n\nfor u, v in edges:\n    size_a = size_of(u, (u, v), all_nodes)\n    size_b = n - size_a\n    best = min(best, abs(size_a - size_b))\nprint(best)</pre>\n</div>\n',
    },
    {
        "id": 489,
        "old": '<p>문자열이 입력됩니다. 팰린드롬으로 분할하는 최소 컷 수와 한 가지 분할 결과를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 팰린드롬으로 분할하는 최소 컷 수와 한 가지 분할 결과를 출력하세요.',
        "marker": '팰린드롬 분할 최소 컷 + 분할 결과 복원',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪞 팰린드롬 분할 최소 컷 + 분할 결과 복원</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최소 컷 수뿐 아니라 \'실제로 어떻게 나눴는지\'까지 보여주려면, dp로 최소 컷 수를 구하면서 각 위치에서 \'어디서 끊었는지(prev)\'를 함께 저장해요. 끝에서부터 prev를 따라가며 나눈 조각들을 모으고, 마지막에 순서를 뒤집어 |로 이어 출력해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nn = len(s)\nis_pal = [[False]*n for _ in range(n)]\nfor i in range(n):\n    is_pal[i][i] = True\nfor length in range(2, n+1):\n    for i in range(n - length + 1):\n        j = i + length - 1\n        if s[i] == s[j] and (length == 2 or is_pal[i+1][j-1]):\n            is_pal[i][j] = True\n\ndp = [0] * n\nprev = [-1] * n\nfor i in range(n):\n    if is_pal[0][i]:\n        dp[i] = 0\n        continue\n    best = float(\'inf\')\n    for j in range(i):\n        if is_pal[j+1][i] and dp[j] + 1 < best:\n            best = dp[j] + 1\n            prev[i] = j\n    dp[i] = best\n\npieces = []\nidx = n - 1\nwhile idx >= 0:\n    start = prev[idx] + 1\n    pieces.append(s[start:idx+1])\n    idx = prev[idx]\nprint(dp[n-1])\nprint(\'|\'.join(reversed(pieces)))</pre>\n</div>\n',
    },
    {
        "id": 490,
        "old": '<p>이벤트 수 n이 첫 줄에, 이름 시작시간 종료시간이 n줄 입력됩니다. 겹치지 않게 최대 이벤트를 선택해 이름을 출력하세요.</p>',
        "problem_text": '이벤트 수 n이 첫 줄에, 이름 시작시간 종료시간이 n줄 입력됩니다. 겹치지 않게 최대 이벤트를 선택해 이름을 출력하세요.',
        "marker": '클래스로 이벤트 스케줄러 만들기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🗓️ 클래스로 이벤트 스케줄러 만들기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">겹치지 않게 최대한 많은 이벤트를 고르는 건 \'그리디: 활동 선택\'과 똑같은 구조예요. Event 클래스로 이름·시작·종료를 묶어두고, 종료 시간 기준으로 정렬한 뒤 앞에서부터 겹치지 않는 이벤트를 선택하면 돼요. 클래스를 쓰면 여러 속성을 하나로 묶어 다루기가 편해져요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Event:\n    def __init__(self, name, start, end):\n        self.name, self.start, self.end = name, start, end\n\nn = int(input())\nevents = []\nfor _ in range(n):\n    name, s, e = input().split()\n    events.append(Event(name, int(s), int(e)))\n\nevents.sort(key=lambda ev: ev.end)\nselected = []\nlast_end = -1\nfor ev in events:\n    if ev.start >= last_end:\n        selected.append(ev.name)\n        last_end = ev.end\nfor name in selected:\n    print(name)</pre>\n</div>\n',
    },
    {
        "id": 491,
        "old": '<p>두 줄에 각각 정수 여러 개가 입력됩니다. 두 큐의 합이 같아지도록 원소를 이동할 때 최소 이동 횟수를 출력하세요. 불가능하면 -1을 출력하세요.</p>',
        "problem_text": '두 줄에 각각 정수 여러 개가 입력됩니다. 두 큐의 합이 같아지도록 원소를 이동할 때 최소 이동 횟수를 출력하세요. 불가능하면 -1을 출력하세요.',
        "marker": '두 큐의 합을 같게 만드는 최소 이동 횟수',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⚖️ 두 큐의 합을 같게 만드는 최소 이동 횟수</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 큐의 전체 합이 다르면 아무리 옮겨도 똑같아질 수 없으니 먼저 홀짝을 확인해요(전체 합이 홀수면 절대 둘로 똑같이 나눌 수 없어요). 가능한 경우라면, 두 큐 중 합이 더 큰 쪽에서 맨 앞 원소를 꺼내 다른 쪽 큐의 맨 뒤에 넣는 식으로 조금씩 옮기며 목표(전체 합의 절반)에 도달할 때까지의 이동 횟수를 세요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\na = deque(map(int, input().split()))\nb = deque(map(int, input().split()))\ntotal = sum(a) + sum(b)\nif total % 2 != 0:\n    print(-1)\nelse:\n    target = total // 2\n    sum_a = sum(a)\n    count = 0\n    limit = (len(a) + len(b)) * 2\n    while sum_a != target and count <= limit:\n        if sum_a > target:\n            v = a.popleft()\n            b.append(v)\n            sum_a -= v\n        else:\n            v = b.popleft()\n            a.append(v)\n            sum_a += v\n        count += 1\n    print(count if sum_a == target else -1)</pre>\n</div>\n',
    },
    {
        "id": 492,
        "old": '<p>정수 여러 개가 입력됩니다. 공집합을 포함한 모든 부분집합을 사전 순으로 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 공집합을 포함한 모든 부분집합을 사전 순으로 출력하세요.',
        "marker": '재귀로 모든 부분집합 사전 순 출력하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧩 재귀로 모든 부분집합 사전 순 출력하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">각 원소를 \'포함/제외\' 두 갈래로 나누는 재귀로 모든 부분집합(2^n개)을 만들 수 있어요. 사전 순으로 출력하려면, 먼저 원소들을 정렬한 뒤 재귀에서 \'현재 원소를 포함하는 경우를 먼저\' 탐색하도록 순서를 맞추거나, 모든 부분집합을 만든 뒤 한 번에 정렬해서 출력하면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = sorted(map(int, input().split()))\nn = len(nums)\nresult = []\n\ndef backtrack(idx, path):\n    if idx == n:\n        result.append(list(path))\n        return\n    path.append(nums[idx])\n    backtrack(idx + 1, path)\n    path.pop()\n    backtrack(idx + 1, path)\n\nbacktrack(0, [])\nresult.sort(key=lambda s: (len(s), s))\nfor subset in result:\n    print(\'{}\' if not subset else \' \'.join(map(str, subset)))</pre>\n</div>\n',
    },
    {
        "id": 493,
        "old": '<p>두 문자열이 한 줄씩 입력됩니다. 최소 편집 거리를 출력하고 변환 과정을 출력하세요. (삽입 I, 삭제 D, 교체 R)</p>',
        "problem_text": '두 문자열이 한 줄씩 입력됩니다. 최소 편집 거리를 출력하고 변환 과정을 출력하세요. (삽입 I, 삭제 D, 교체 R)',
        "marker": '편집 거리 + 연산 경로 복원',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">✏️ 편집 거리 + 연산 경로 복원</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최소 편집 거리뿐 아니라 \'어떤 연산을 어디에 적용했는지\'까지 알아야 할 때는, DP 테이블을 다 채운 뒤 (n, m)에서 거꾸로 추적해요. 글자가 같으면 그대로 대각선 위로, 다르면 DP 값이 어느 방향(삽입 I/삭제 D/교체 R)에서 왔는지 비교해 그 연산을 기록하며 이동해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = input()\nb = input()\nn, m = len(a), len(b)\ndp = [[0]*(m+1) for _ in range(n+1)]\nfor i in range(n+1):\n    dp[i][0] = i\nfor j in range(m+1):\n    dp[0][j] = j\nfor i in range(1, n+1):\n    for j in range(1, m+1):\n        if a[i-1] == b[j-1]:\n            dp[i][j] = dp[i-1][j-1]\n        else:\n            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])\n\nops = []\ni, j = n, m\nwhile i > 0 or j > 0:\n    if i > 0 and j > 0 and a[i-1] == b[j-1]:\n        i -= 1; j -= 1\n    elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:\n        ops.append(f"R:{a[i-1]}->{b[j-1]}")\n        i -= 1; j -= 1\n    elif i > 0 and dp[i][j] == dp[i-1][j] + 1:\n        ops.append(f"D:{a[i-1]}")\n        i -= 1\n    else:\n        ops.append(f"I:{b[j-1]}")\n        j -= 1\nprint(dp[n][m])\nfor op in reversed(ops):\n    print(op)</pre>\n</div>\n',
    },
    {
        "id": 494,
        "old": '<p>n m이 첫 줄에, m개의 친구 관계(u v)가 입력됩니다. 이후 가장 많은 친구를 가진 사람과 수, 친구 수가 같으면 번호 작은 순으로 출력하세요. 그 다음 줄에 모든 사람과 연결된 사람(허브) 번호를 오름차순으로 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, m개의 친구 관계(u v)가 입력됩니다. 이후 가장 많은 친구를 가진 사람과 수, 친구 수가 같으면 번호 작은 순으로 출력하세요. 그 다음 줄에 모든 사람과 연결된 사람(허브) 번호를 오름차순으로 출력하세요.',
        "marker": '그래프 차수 + BFS로 소셜 네트워크 분석하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🕸️ 그래프 차수 + BFS로 소셜 네트워크 분석하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">친구 관계 그래프에서 \'가장 많은 친구를 가진 사람\'은 각 노드의 차수(연결된 간선 수)를 세면 바로 알 수 있어요. \'모든 사람과 연결된 허브\'를 찾는 건, 그 노드에서 BFS를 돌렸을 때 모든 노드에 도달 가능한지(즉 연결 요소의 크기가 전체 n과 같은지)를 확인하면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\ndegree = [0] * (n + 1)\nfor _ in range(m):\n    u, v = map(int, input().split())\n    graph[u].append(v)\n    graph[v].append(u)\n    degree[u] += 1\n    degree[v] += 1\n\nmax_deg = max(degree[1:])\ntop = min(i for i in range(1, n+1) if degree[i] == max_deg)\nprint(top, max_deg)\n\ndef reachable_all(start):\n    visited = {start}\n    q = deque([start])\n    while q:\n        node = q.popleft()\n        for nxt in graph[node]:\n            if nxt not in visited:\n                visited.add(nxt)\n                q.append(nxt)\n    return len(visited) == n\n\nhubs = [i for i in range(1, n+1) if reachable_all(i)]\nprint(*hubs)</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 모의고사 3회 단원(48장) 문항 10건에 개념 설명 카드를 추가합니다."

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
