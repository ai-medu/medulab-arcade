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
        "id": 435,
        "old": '<p>n m이 첫 줄에, 이후 m개의 간선(u v)이 입력됩니다. 연결 요소의 수를 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 m개의 간선(u v)이 입력됩니다. 연결 요소의 수를 출력하세요.',
        "marker": 'DFS로 연결 요소 개수 세기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧩 DFS로 연결 요소 개수 세기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">그래프에서 서로 연결된 노드들의 묶음(연결 요소)이 몇 개인지 세는 문제예요. 아직 방문하지 않은 노드를 만날 때마다 \'새로운 연결 요소를 발견했다\'는 뜻이므로 count를 늘리고, 그 노드에서 DFS(또는 BFS)로 연결된 모든 노드를 방문 처리해요. 모든 노드를 다 확인할 때까지 반복하면 count가 곧 연결 요소의 개수예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import sys\nsys.setrecursionlimit(10000)\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nfor _ in range(m):\n    u, v = map(int, input().split())\n    graph[u].append(v)\n    graph[v].append(u)\n\nvisited = [False] * (n + 1)\ndef dfs(node):\n    visited[node] = True\n    for nxt in graph[node]:\n        if not visited[nxt]:\n            dfs(nxt)\n\ncount = 0\nfor i in range(1, n + 1):\n    if not visited[i]:\n        count += 1\n        dfs(i)\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 436,
        "old": '<p>n m이 첫 줄에, 이후 m개의 간선(u v w)이 입력됩니다. 1번 노드에서 각 노드까지 최단 거리를 출력하세요. 도달 불가는 INF로 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 m개의 간선(u v w)이 입력됩니다. 1번 노드에서 각 노드까지 최단 거리를 출력하세요. 도달 불가는 INF로 출력하세요.',
        "marker": '다익스트라(Dijkstra) 최단 경로',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🛣️ 다익스트라(Dijkstra) 최단 경로</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">가중치가 있는 그래프에서 한 지점부터 모든 노드까지의 최단 거리를 구하는 알고리즘이에요. 핵심은 \'아직 확정되지 않은 노드 중 현재까지 거리가 가장 짧은 노드\'를 매번 고르는 것인데, 이걸 효율적으로 하기 위해 최소 힙(heapq)을 사용해요. 어떤 노드까지의 거리가 더 짧은 경로로 갱신되면 그 정보를 힙에 다시 넣어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import heapq\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nfor _ in range(m):\n    u, v, w = map(int, input().split())\n    graph[u].append((v, w))\n\nINF = float(\'inf\')\ndist = [INF] * (n + 1)\ndist[1] = 0\nheap = [(0, 1)]\nwhile heap:\n    d, node = heapq.heappop(heap)\n    if d > dist[node]:\n        continue\n    for nxt, w in graph[node]:\n        nd = d + w\n        if nd < dist[nxt]:\n            dist[nxt] = nd\n            heapq.heappush(heap, (nd, nxt))\n\nfor i in range(1, n + 1):\n    print(dist[i] if dist[i] != INF else \'INF\')</pre>\n</div>\n',
    },
    {
        "id": 437,
        "old": '<p>n m이 첫 줄에, 이후 m개의 간선(u v)이 입력됩니다. 사이클이 존재하면 YES, 없으면 NO를 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 m개의 간선(u v)이 입력됩니다. 사이클이 존재하면 YES, 없으면 NO를 출력하세요.',
        "marker": '유니온-파인드로 사이클 탐지하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔗 유니온-파인드로 사이클 탐지하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">유니온-파인드(union-find)는 \'여러 원소를 그룹으로 묶고, 같은 그룹인지 빠르게 확인하는\' 자료구조예요. 간선 (u, v)를 하나씩 보면서, u와 v가 이미 같은 그룹(같은 루트)이라면 이 간선을 추가하는 순간 사이클이 생겨요. 같은 그룹이 아니라면 union으로 두 그룹을 합쳐줘요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def find(x, parent):\n    while parent[x] != x:\n        x = parent[x]\n    return x\n\ndef union(a, b, parent):\n    ra, rb = find(a, parent), find(b, parent)\n    if ra != rb:\n        parent[ra] = rb\n\nn, m = map(int, input().split())\nparent = list(range(n + 1))\nhas_cycle = False\nfor _ in range(m):\n    u, v = map(int, input().split())\n    if find(u, parent) == find(v, parent):\n        has_cycle = True\n    else:\n        union(u, v, parent)\nprint("YES" if has_cycle else "NO")</pre>\n</div>\n',
    },
    {
        "id": 438,
        "old": '<p>시작 단어, 끝 단어, 단어 목록이 입력됩니다. 한 번에 한 글자씩 바꿔 끝 단어에 도달하는 최소 단계를 출력하세요. 불가능하면 0을 출력하세요.</p>',
        "problem_text": '시작 단어, 끝 단어, 단어 목록이 입력됩니다. 한 번에 한 글자씩 바꿔 끝 단어에 도달하는 최소 단계를 출력하세요. 불가능하면 0을 출력하세요.',
        "marker": 'BFS로 단어 사다리(word ladder) 최소 변환',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪜 BFS로 단어 사다리(word ladder) 최소 변환</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">한 번에 한 글자씩 바꿔 시작 단어에서 끝 단어까지 가는 최소 단계를 구하는 문제는, 단어들을 그래프의 노드로 보고 \'한 글자만 다른 단어끼리 연결되어 있다\'고 생각하면 그냥 BFS 최단 거리 문제가 돼요. 큐에 (현재 단어, 단계)를 넣고, 아직 안 쓴 단어 중 한 글자만 다른 단어를 찾아 큐에 추가해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nstart = input()\nend = input()\nwords = set(input().split())\n\ndef diff_one(a, b):\n    return sum(1 for x, y in zip(a, b) if x != y) == 1\n\nq = deque([(start, 0)])\nvisited = {start}\nwhile q:\n    word, step = q.popleft()\n    if word == end:\n        print(step)\n        break\n    for nxt in list(words):\n        if nxt not in visited and diff_one(word, nxt):\n            visited.add(nxt)\n            q.append((nxt, step + 1))\nelse:\n    print(0)</pre>\n</div>\n',
    },
    {
        "id": 439,
        "old": '<p>n m이 첫 줄에, 이후 m개의 간선(u v w)이 입력됩니다. 모든 쌍의 최단 거리 행렬을 출력하세요. 도달 불가는 INF로 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 m개의 간선(u v w)이 입력됩니다. 모든 쌍의 최단 거리 행렬을 출력하세요. 도달 불가는 INF로 출력하세요.',
        "marker": '플로이드-워셜로 모든 쌍 최단 거리 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🌐 플로이드-워셜로 모든 쌍 최단 거리 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">모든 노드 쌍 사이의 최단 거리를 한꺼번에 구할 때 쓰는 알고리즘이에요. \'경유 노드 k를 하나씩 추가해보며, i에서 j로 가는 더 짧은 길이 k를 거쳐 생기는지\' 계속 확인해요. dp[i][j] = min(dp[i][j], dp[i][k] + dp[k][j])를 k, i, j 세 번 중첩된 for문으로 갱신하면 끝이에요. 노드 수가 적을 때(수백 개 이하) 적합해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, m = map(int, input().split())\nINF = float(\'inf\')\ndist = [[INF]*(n+1) for _ in range(n+1)]\nfor i in range(1, n+1):\n    dist[i][i] = 0\nfor _ in range(m):\n    u, v, w = map(int, input().split())\n    dist[u][v] = min(dist[u][v], w)\n\nfor k in range(1, n+1):\n    for i in range(1, n+1):\n        for j in range(1, n+1):\n            if dist[i][k] + dist[k][j] < dist[i][j]:\n                dist[i][j] = dist[i][k] + dist[k][j]\n\nfor i in range(1, n+1):\n    print(*[dist[i][j] if dist[i][j] != INF else \'INF\' for j in range(1, n+1)])</pre>\n</div>\n',
    },
    {
        "id": 440,
        "old": '<p>n m이 첫 줄에, 이후 m개의 간선(u v w)이 입력됩니다. 최소 신장 트리의 총 비용을 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 m개의 간선(u v w)이 입력됩니다. 최소 신장 트리의 총 비용을 출력하세요.',
        "marker": '크루스칼(Kruskal) 알고리즘으로 MST 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🌲 크루스칼(Kruskal) 알고리즘으로 MST 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최소 신장 트리(MST)는 모든 노드를 가장 적은 총 비용으로 연결하는 간선들의 집합이에요. 크루스칼 알고리즘은 \'간선을 가중치가 작은 순서로 정렬해, 사이클이 생기지 않는 선에서 하나씩 선택\'하는 그리디 방법이에요. 사이클이 생기는지는 유니온-파인드로 확인해요(두 노드가 이미 같은 그룹이면 사이클이 생기므로 그 간선은 버려요).</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def find(x, parent):\n    while parent[x] != x:\n        x = parent[x]\n    return x\n\nn, m = map(int, input().split())\nedges = [tuple(map(int, input().split())) for _ in range(m)]\nedges.sort(key=lambda e: e[2])  # 가중치 오름차순\n\nparent = list(range(n + 1))\ntotal = 0\nfor u, v, w in edges:\n    ru, rv = find(u, parent), find(v, parent)\n    if ru != rv:\n        parent[ru] = rv\n        total += w\nprint(total)</pre>\n</div>\n',
    },
    {
        "id": 441,
        "old": '<p>방향 그래프 n m과 m개의 간선이 입력됩니다. 가장 짧은 사이클의 길이를 출력하세요. 없으면 -1을 출력하세요.</p>',
        "problem_text": '방향 그래프 n m과 m개의 간선이 입력됩니다. 가장 짧은 사이클의 길이를 출력하세요. 없으면 -1을 출력하세요.',
        "marker": 'DFS/BFS로 방향 그래프의 최소 사이클 길이 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔁 DFS/BFS로 방향 그래프의 최소 사이클 길이 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">방향 그래프에서 가장 짧은 사이클을 찾을 때는, 각 노드를 출발점으로 BFS를 돌려 \'자기 자신으로 다시 돌아오는 최단 거리\'를 구하는 방법을 써요. 모든 노드를 각각 출발점으로 시도해보고, 그 중 가장 짧게 자기 자신으로 돌아온 거리가 전체 그래프의 최소 사이클 길이예요. 한 번도 돌아오지 못했다면 사이클이 없다는 뜻이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nfor _ in range(m):\n    u, v = map(int, input().split())\n    graph[u].append(v)\n\ndef shortest_cycle_from(start):\n    dist = {start: 0}\n    q = deque([start])\n    while q:\n        node = q.popleft()\n        for nxt in graph[node]:\n            if nxt == start:\n                return dist[node] + 1\n            if nxt not in dist:\n                dist[nxt] = dist[node] + 1\n                q.append(nxt)\n    return float(\'inf\')\n\nbest = min(shortest_cycle_from(i) for i in range(1, n + 1))\nprint(best if best != float(\'inf\') else -1)</pre>\n</div>\n',
    },
    {
        "id": 442,
        "old": '<p>n m과 미로가 입력됩니다. S는 시작, E는 출구, #은 벽, .은 통로입니다. 탈출 가능하면 YES와 최단 경로 길이, 불가능하면 NO를 출력하세요.</p>',
        "problem_text": 'n m과 미로가 입력됩니다. S는 시작, E는 출구, #은 벽, .은 통로입니다. 탈출 가능하면 YES와 최단 경로 길이, 불가능하면 NO를 출력하세요.',
        "marker": 'BFS로 미로 탈출 가능 여부 확인하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🚪 BFS로 미로 탈출 가능 여부 확인하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">S(시작)에서 출발해 E(출구)까지 통로(.)만 지나며 도달할 수 있는지, 도달한다면 최단 거리는 몇인지 구하는 문제예요. 입력에서 S의 위치를 찾은 뒤 BFS를 시작하고, 상하좌우 중 벽(#)이 아닌 칸만 방문해요. BFS 중 E에 도착하면 그 시점의 거리가 최단 거리이고, 큐가 다 비었는데도 못 도착했으면 탈출이 불가능한 거예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngrid = [input() for _ in range(n)]\n\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == \'S\':\n            start = (i, j)\n\nvisited = [[False]*m for _ in range(n)]\nq = deque([(start[0], start[1], 0)])\nvisited[start[0]][start[1]] = True\nfound = False\nwhile q:\n    r, c, d = q.popleft()\n    if grid[r][c] == \'E\':\n        print("YES")\n        print(d)\n        found = True\n        break\n    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n        nr, nc = r+dr, c+dc\n        if 0<=nr<n and 0<=nc<m and not visited[nr][nc] and grid[nr][nc] != \'#\':\n            visited[nr][nc] = True\n            q.append((nr, nc, d+1))\nif not found:\n    print("NO")</pre>\n</div>\n',
    },
    {
        "id": 443,
        "old": '<p>과목 수 n과 선수 관계 m이 첫 줄에, 이후 m개의 관계(a b: a 먼저)가 입력됩니다. 위상 정렬로 수강 순서를 출력하세요. 사이클이 있으면 CYCLE을 출력하세요.</p>',
        "problem_text": '과목 수 n과 선수 관계 m이 첫 줄에, 이후 m개의 관계(a b: a 먼저)가 입력됩니다. 위상 정렬로 수강 순서를 출력하세요. 사이클이 있으면 CYCLE을 출력하세요.',
        "marker": '위상 정렬로 선수과목 순서 정하기 + 사이클 판정',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📚 위상 정렬로 선수과목 순서 정하기 + 사이클 판정</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">진입차수가 0인 과목부터 큐에 넣어 처리하는 위상 정렬 그대로인데, 추가로 \'사이클이 있으면 CYCLE을 출력\'하는 조건이 붙어요. 사이클이 있는 그래프는 아무리 진행해도 진입차수가 0이 되지 않는 노드가 남기 때문에, 결과로 나온 노드 수가 전체 노드 수 n보다 적다는 특징이 있어요. 이 특징으로 사이클 여부를 판단해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nindegree = [0] * (n + 1)\nfor _ in range(m):\n    a, b = map(int, input().split())\n    graph[a].append(b)\n    indegree[b] += 1\n\nq = deque([i for i in range(1, n+1) if indegree[i] == 0])\nresult = []\nwhile q:\n    node = q.popleft()\n    result.append(node)\n    for nxt in graph[node]:\n        indegree[nxt] -= 1\n        if indegree[nxt] == 0:\n            q.append(nxt)\n\nif len(result) < n:\n    print("CYCLE")\nelse:\n    print(*result)</pre>\n</div>\n',
    },
    {
        "id": 444,
        "old": '<p>n과 목표값 m이 첫 줄에, n개의 높이가 둘째 줄에 입력됩니다. 절단기를 H로 설정할 때 H 이상인 부분을 잘라 얻는 합이 m 이상이 되는 최대 H를 출력하세요.</p>',
        "problem_text": 'n과 목표값 m이 첫 줄에, n개의 높이가 둘째 줄에 입력됩니다. 절단기를 H로 설정할 때 H 이상인 부분을 잘라 얻는 합이 m 이상이 되는 최대 H를 출력하세요.',
        "marker": '이분 탐색(파라메트릭 서치)으로 최적값 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔎 이분 탐색(파라메트릭 서치)으로 최적값 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">\'조건을 만족하는 최대/최소값 찾기\' 문제는 답 후보를 직접 이분 탐색하는 파라메트릭 서치로 풀 수 있어요. 절단 높이 H를 바꿔보며 \'H로 잘랐을 때 얻는 합이 m 이상인가?\'를 확인하는 함수를 만들고, H를 이분 탐색으로 좁혀가요. H가 커질수록 얻는 합은 줄어드는 단조적인 성질이 있어서 이분 탐색이 가능해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, target = map(int, input().split())\nheights = list(map(int, input().split()))\n\ndef get_sum(h):\n    return sum(x - h for x in heights if x > h)\n\nlo, hi = 0, max(heights)\nanswer = 0\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    if get_sum(mid) >= target:\n        answer = mid\n        lo = mid + 1\n    else:\n        hi = mid - 1\nprint(answer)</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 그래프 알고리즘 단원(43장) 문항 10건에 개념 설명 카드를 추가합니다."

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
