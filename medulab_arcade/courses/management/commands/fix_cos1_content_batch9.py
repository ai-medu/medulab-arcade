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
        "id": 475,
        "old": '<p>단어 목록이 첫 줄에(공백 구분), 검색할 접두사가 둘째 줄에 입력됩니다. 해당 접두사로 시작하는 단어 수를 출력하세요.</p>',
        "problem_text": '단어 목록이 첫 줄에(공백 구분), 검색할 접두사가 둘째 줄에 입력됩니다. 해당 접두사로 시작하는 단어 수를 출력하세요.',
        "marker": '트라이(Trie)로 접두사 검색하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🌲 트라이(Trie)로 접두사 검색하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">트라이는 \'문자 하나하나가 트리의 가지가 되는\' 자료구조로, 접두사 검색에 아주 효율적이에요. 딕셔너리를 중첩해서 각 글자마다 다음 글자로 가는 노드를 만들고, 각 노드에 \'이 노드를 지나는 단어가 몇 개인지\' 카운트를 저장해요. 접두사를 검색할 때는 그 접두사를 따라 트라이를 내려가다가, 마지막 노드에 저장된 카운트를 읽으면 끝이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()\nprefix = input()\n\ntrie = {}\nfor word in words:\n    node = trie\n    for ch in word:\n        node = node.setdefault(ch, {})\n        node[\'#\'] = node.get(\'#\', 0) + 1\n\nnode = trie\nfor ch in prefix:\n    if ch not in node:\n        print(0)\n        break\n    node = node[ch]\nelse:\n    print(node.get(\'#\', 0))</pre>\n</div>\n',
    },
    {
        "id": 476,
        "old": '<p>n q가 첫 줄에, 정수 n개가 둘째 줄에, 이후 쿼리(sum l r 또는 update i v)가 입력됩니다. sum 쿼리 결과를 출력하세요.</p>',
        "problem_text": 'n q가 첫 줄에, 정수 n개가 둘째 줄에, 이후 쿼리(sum l r 또는 update i v)가 입력됩니다. sum 쿼리 결과를 출력하세요.',
        "marker": '구간 합 배열로 범위 합/수정 처리하기(간이 세그먼트)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➕ 구간 합 배열로 범위 합/수정 처리하기(간이 세그먼트)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">진짜 세그먼트 트리를 구현하지 않아도, 쿼리 수가 많지 않다면 prefix sum을 다시 계산하는 방식으로도 충분해요. sum 쿼리는 prefix 배열로 O(1)에, update 쿼리는 해당 값을 바꾼 뒤 prefix 배열을 O(n)에 다시 만들면 돼요. (데이터가 아주 크고 업데이트가 매우 잦다면 실제 세그먼트 트리가 필요하지만, 여기서는 핵심 아이디어인 \'구간 합을 빠르게 구하는 법\'에 집중해요.)</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, q = map(int, input().split())\nnums = list(map(int, input().split()))\n\ndef prefix_sum(arr):\n    p = [0] * (len(arr) + 1)\n    for i, v in enumerate(arr):\n        p[i+1] = p[i] + v\n    return p\n\nresults = []\nfor _ in range(q):\n    query = input().split()\n    if query[0] == \'sum\':\n        l, r = int(query[1]), int(query[2])\n        p = prefix_sum(nums)\n        results.append(p[r] - p[l-1])\n    else:\n        idx, val = int(query[1]), int(query[2])\n        nums[idx-1] = val\nfor r in results:\n    print(r)</pre>\n</div>\n',
    },
    {
        "id": 477,
        "old": '<p>n m과 m개 간선(u v w)이 입력됩니다. 1번에서 n번까지 최단 경로와 비용을 출력하세요.</p>',
        "problem_text": 'n m과 m개 간선(u v w)이 입력됩니다. 1번에서 n번까지 최단 경로와 비용을 출력하세요.',
        "marker": '다익스트라 + 경로 복원',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧭 다익스트라 + 경로 복원</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최단 거리뿐 아니라 실제 경로까지 필요하면, 다익스트라를 돌리면서 \'각 노드에 마지막으로 어떤 노드에서 도착했는지(prev)\'를 함께 기록해요. 끝 노드부터 prev를 따라 거슬러 올라가 시작 노드까지 가는 경로를 뒤집으면 올바른 순서의 경로가 나와요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import heapq\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nfor _ in range(m):\n    u, v, w = map(int, input().split())\n    graph[u].append((v, w))\n\nINF = float(\'inf\')\ndist = [INF] * (n + 1)\nprev = [0] * (n + 1)\ndist[1] = 0\nheap = [(0, 1)]\nwhile heap:\n    d, node = heapq.heappop(heap)\n    if d > dist[node]:\n        continue\n    for nxt, w in graph[node]:\n        nd = d + w\n        if nd < dist[nxt]:\n            dist[nxt] = nd\n            prev[nxt] = node\n            heapq.heappush(heap, (nd, nxt))\n\npath, cur = [], n\nwhile cur != 0:\n    path.append(cur)\n    cur = prev[cur]\nprint(*reversed(path))\nprint(dist[n])</pre>\n</div>\n',
    },
    {
        "id": 478,
        "old": '<p>물건 수 n과 용량 W가 첫 줄에, 이후 무게와 가치가 n줄 입력됩니다. 최대 가치와 선택한 물건 번호(1-indexed)를 출력하세요.</p>',
        "problem_text": '물건 수 n과 용량 W가 첫 줄에, 이후 무게와 가치가 n줄 입력됩니다. 최대 가치와 선택한 물건 번호(1-indexed)를 출력하세요.',
        "marker": '0-1 배낭 + 선택 경로 복원',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🎒 0-1 배낭 + 선택 경로 복원</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최대 가치뿐 아니라 \'실제로 어떤 물건을 골랐는지\'까지 알아야 할 때는, dp 테이블을 다 채운 뒤 거꾸로 추적해요. dp[i][w]가 dp[i-1][w]와 같다면 i번째 물건을 넣지 않은 것이고, 다르다면 넣은 것이므로 그 물건을 선택 목록에 추가하고 w를 그만큼 줄여 i-1로 내려가요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, W = map(int, input().split())\nitems = [tuple(map(int, input().split())) for _ in range(n)]\ndp = [[0]*(W+1) for _ in range(n+1)]\nfor i in range(1, n+1):\n    wt, val = items[i-1]\n    for w in range(W+1):\n        dp[i][w] = dp[i-1][w]\n        if wt <= w:\n            dp[i][w] = max(dp[i][w], dp[i-1][w-wt] + val)\n\nchosen = []\nw = W\nfor i in range(n, 0, -1):\n    if dp[i][w] != dp[i-1][w]:\n        chosen.append(i)\n        w -= items[i-1][0]\nprint(dp[n][W])\nprint(*sorted(chosen))</pre>\n</div>\n',
    },
    {
        "id": 479,
        "old": '<p>k[encoded_string] 형식의 인코딩된 문자열이 입력됩니다. 디코딩해 출력하세요. (k: 반복 횟수, 중첩 가능)</p>',
        "problem_text": 'k[encoded_string] 형식의 인코딩된 문자열이 입력됩니다. 디코딩해 출력하세요. (k: 반복 횟수, 중첩 가능)',
        "marker": '스택으로 중첩 문자열 복호화하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📦 스택으로 중첩 문자열 복호화하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">k[문자열] 형태로 중첩된 압축 표기를 풀 때는 스택이 딱 맞아요. 숫자와 \'[\'를 만나면 각각 스택에 쌓아두고, \']\'를 만나면 가장 최근에 쌓인 반복 횟수와 문자열을 꺼내 그만큼 반복한 뒤 바깥 문자열에 이어 붙여요. 중첩되어 있어도 스택이 자동으로 \'가장 안쪽부터\' 처리해줘요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nstack = [[\'\', 1]]\nnum = \'\'\nfor ch in s:\n    if ch.isdigit():\n        num += ch\n    elif ch == \'[\':\n        stack.append([\'\', int(num)])\n        num = \'\'\n    elif ch == \']\':\n        text, times = stack.pop()\n        stack[-1][0] += text * times\n    else:\n        stack[-1][0] += ch\nprint(stack[0][0])</pre>\n</div>\n',
    },
    {
        "id": 480,
        "old": '<p>정수 여러 개와 k가 한 줄씩 입력됩니다. 가장 작은 k개의 합을 출력하세요.</p>',
        "problem_text": '정수 여러 개와 k가 한 줄씩 입력됩니다. 가장 작은 k개의 합을 출력하세요.',
        "marker": '최소 힙으로 가장 작은 k개의 합 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⛏️ 최소 힙으로 가장 작은 k개의 합 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">가장 작은 k개를 찾을 때 전체를 다 정렬할 필요 없이, heapq.nsmallest(k, nums)로 작은 값 k개만 바로 뽑아낼 수 있어요. 내부적으로는 최소 힙 구조를 활용해 전체 정렬보다 더 적은 비교로 답을 구해요. 뽑은 k개를 더하면 끝이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">import heapq\n\nnums = list(map(int, input().split()))\nk = int(input())\nsmallest_k = heapq.nsmallest(k, nums)\nprint(sum(smallest_k))</pre>\n</div>\n',
    },
    {
        "id": 481,
        "old": '<p>정수 여러 개와 목표합 target이 한 줄씩 입력됩니다. 연속 부분 배열의 합이 target 인 경우의 수를 출력하세요.</p>',
        "problem_text": '정수 여러 개와 목표합 target이 한 줄씩 입력됩니다. 연속 부분 배열의 합이 target 인 경우의 수를 출력하세요.',
        "marker": 'prefix sum + 딕셔너리로 부분 배열 합 경우의 수',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➕ prefix sum + 딕셔너리로 부분 배열 합 경우의 수</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">연속 부분 배열의 합이 target인 경우의 수를 O(n²)으로 모두 따지면 느려요. prefix[i]를 \'처음부터 i번째까지의 합\'이라 하면, 구간 [l+1, r]의 합이 target이라는 건 prefix[r] - prefix[l] == target, 즉 prefix[l] == prefix[r] - target이라는 뜻이에요. 지금까지 등장한 prefix 값의 개수를 딕셔너리에 저장해두면 O(n)에 풀 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import defaultdict\n\nnums = list(map(int, input().split()))\ntarget = int(input())\ncount_map = defaultdict(int)\ncount_map[0] = 1\nprefix = 0\nresult = 0\nfor x in nums:\n    prefix += x\n    result += count_map[prefix - target]\n    count_map[prefix] += 1\nprint(result)</pre>\n</div>\n',
    },
    {
        "id": 482,
        "old": '<p>n m이 첫 줄에, m개의 친구 관계(a b)가 입력됩니다. 이후 q개의 질문(a b: 같은 그룹?)이 입력됩니다. YES/NO로 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, m개의 친구 관계(a b)가 입력됩니다. 이후 q개의 질문(a b: 같은 그룹?)이 입력됩니다. YES/NO로 출력하세요.',
        "marker": '유니온-파인드로 친구 관계(같은 그룹 여부) 확인하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔗 유니온-파인드로 친구 관계(같은 그룹 여부) 확인하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">친구 관계를 유니온-파인드로 묶어두면, \'두 사람이 친구 네트워크로 연결되어 있는지\'를 find()로 확인하는 루트가 같은지만 보면 돼요(직접 친구가 아니어도 친구의 친구를 통해 연결되어 있으면 같은 그룹이에요). 모든 친구 관계를 먼저 union으로 합친 뒤, 질문마다 find 결과를 비교해 YES/NO를 출력해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def find(x, parent):\n    while parent[x] != x:\n        x = parent[x]\n    return x\n\ndef union(a, b, parent):\n    ra, rb = find(a, parent), find(b, parent)\n    if ra != rb:\n        parent[ra] = rb\n\nn, m = map(int, input().split())\nparent = list(range(n + 1))\nfor _ in range(m):\n    a, b = map(int, input().split())\n    union(a, b, parent)\n\nq = int(input())\nfor _ in range(q):\n    a, b = map(int, input().split())\n    print("YES" if find(a, parent) == find(b, parent) else "NO")</pre>\n</div>\n',
    },
    {
        "id": 483,
        "old": '<p>초기 재고(상품:수량, 콤마 구분)가 첫 줄에, 이후 sell 상품 수량 또는 restock 상품 수량 명령이 입력됩니다. END가 나오면 재고가 0인 상품 이름을 사전 순으로 출력하세요.</p>',
        "problem_text": '초기 재고(상품:수량, 콤마 구분)가 첫 줄에, 이후 sell 상품 수량 또는 restock 상품 수량 명령이 입력됩니다. END가 나오면 재고가 0인 상품 이름을 사전 순으로 출력하세요.',
        "marker": '딕셔너리로 재고 시뮬레이션하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📦 딕셔너리로 재고 시뮬레이션하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">상품별 재고를 딕셔너리로 관리하면서, sell 명령이 오면 수량만큼 빼고(부족하면 처리를 생략하거나 메시지를 남기고), restock 명령이 오면 수량을 더해요. 마지막에 재고가 0인 상품을 사전 순으로 정렬해 출력하면 돼요. \'상태를 계속 갱신하며 명령을 처리하는\' 시뮬레이션 문제의 전형적인 패턴이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">raw = input().split(\', \')\nstock = {}\nfor item in raw:\n    name, qty = item.split(\':\')\n    stock[name] = int(qty)\n\nwhile True:\n    line = input()\n    if line == \'END\':\n        break\n    parts = line.split()\n    cmd, name, qty = parts[0], parts[1], int(parts[2])\n    if cmd == \'sell\':\n        if stock[name] >= qty:\n            stock[name] -= qty\n    else:\n        stock[name] += qty\n\nfor name in sorted(stock):\n    if stock[name] == 0:\n        print(name)</pre>\n</div>\n',
    },
    {
        "id": 484,
        "old": '<p>학생 수 n이 첫 줄에, 이름과 과목:점수 목록이 n줄 입력됩니다. 이후 rank 과목 명령이 입력되면 해당 과목 점수 내림차순 순위를 출력하세요. END로 종료하세요.</p>',
        "problem_text": '학생 수 n이 첫 줄에, 이름과 과목:점수 목록이 n줄 입력됩니다. 이후 rank 과목 명령이 입력되면 해당 과목 점수 내림차순 순위를 출력하세요. END로 종료하세요.',
        "marker": '딕셔너리 + 정렬로 학사 관리 시스템 구현하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🏫 딕셔너리 + 정렬로 학사 관리 시스템 구현하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">여러 학생의 여러 과목 점수를 저장해두고, 특정 과목 기준으로 순위를 매기는 문제예요. 학생별로 \'과목: 점수\' 딕셔너리를 저장한 뒤, rank 명령이 오면 그 과목 점수로 내림차순 정렬해요. 점수가 같으면 공동 순위를 매겨야 하므로, 순위를 \'앞에 몇 명이 더 높은 점수를 가졌는지 + 1\'로 계산해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\nstudents = []\nfor _ in range(n):\n    parts = input().split()\n    name = parts[0]\n    scores = {}\n    for pair in parts[1:]:\n        subject, score = pair.split(\':\')\n        scores[subject] = int(score)\n    students.append((name, scores))\n\nwhile True:\n    line = input()\n    if line == \'END\':\n        break\n    subject = line.split()[1]\n    ranked = sorted(students, key=lambda s: -s[1][subject])\n    for i, (name, scores) in enumerate(ranked):\n        rank = sum(1 for _, s in ranked if s[subject] > scores[subject]) + 1\n        print(f"{rank}. {name}: {scores[subject]}")</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 모의고사 2회 단원(47장) 문항 10건에 개념 설명 카드를 추가합니다."

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
