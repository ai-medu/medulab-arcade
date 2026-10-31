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
        "id": 465,
        "old": '<p>첫 줄에 메뉴:가격 쌍(콤마 구분), 이후 order 메뉴 또는 total 명령이 입력됩니다. order면 해당 메뉴 가격을 누적하고, total이면 총 금액을 출력하세요. END 로 종료하세요.</p>',
        "problem_text": '첫 줄에 메뉴:가격 쌍(콤마 구분), 이후 order 메뉴 또는 total 명령이 입력됩니다. order면 해당 메뉴 가격을 누적하고, total이면 총 금액을 출력하세요. END 로 종료하세요.',
        "marker": '클래스로 상태(재고/주문) 관리하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🍕 클래스로 상태(재고/주문) 관리하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">여러 종류의 명령(order, total 등)이 순서대로 들어오며 \'지금까지 쌓인 상태\'를 계속 관리해야 하는 문제는, 클래스의 인스턴스 변수에 상태를 들고 메서드로 명령을 처리하는 구조가 깔끔해요. 메뉴:가격 쌍을 딕셔너리로 저장해두고, order 명령이 오면 그 메뉴 가격을 총액에 더하고, total 명령이 오면 누적된 총액을 출력해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class PizzaStore:\n    def __init__(self, menu):\n        self.menu = menu\n        self.total_price = 0\n    def order(self, name):\n        self.total_price += self.menu[name]\n    def total(self):\n        return self.total_price\n\nraw = input().split(\', \')\nmenu = {}\nfor item in raw:\n    name, price = item.split(\':\')\n    menu[name] = int(price)\nstore = PizzaStore(menu)\n\nwhile True:\n    line = input()\n    if line == \'END\':\n        break\n    if line.startswith(\'order\'):\n        store.order(line.split()[1])\n    elif line == \'total\':\n        print(store.total())</pre>\n</div>\n',
    },
    {
        "id": 466,
        "old": '<p>enqueue 값 또는 dequeue 명령이 입력됩니다. END가 나오면 dequeue 결과를 순서대로 출력하세요.</p>',
        "problem_text": 'enqueue 값 또는 dequeue 명령이 입력됩니다. END가 나오면 dequeue 결과를 순서대로 출력하세요.',
        "marker": '스택 두 개로 큐 구현하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔁 스택 두 개로 큐 구현하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">스택(LIFO, 나중에 넣은 게 먼저 나옴)만으로 큐(FIFO, 먼저 넣은 게 먼저 나옴)를 만드는 고전 문제예요. enqueue할 때는 in_stack에 그냥 쌓고, dequeue할 때는 out_stack을 확인해요. out_stack이 비어 있으면 in_stack의 내용을 전부 pop해서 out_stack에 옮기는데(순서가 거꾸로 뒤집혀요), 그 다음 out_stack에서 pop하면 가장 먼저 들어온 값이 나와요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">in_stack, out_stack = [], []\n\ndef enqueue(x):\n    in_stack.append(x)\n\ndef dequeue():\n    if not out_stack:\n        while in_stack:\n            out_stack.append(in_stack.pop())\n    return out_stack.pop()\n\nresults = []\nwhile True:\n    line = input()\n    if line == \'END\':\n        break\n    if line.startswith(\'enqueue\'):\n        enqueue(int(line.split()[1]))\n    else:\n        results.append(dequeue())\nfor r in results:\n    print(r)</pre>\n</div>\n',
    },
    {
        "id": 467,
        "old": '<p>두 이진 문자열이 한 줄씩 입력됩니다. 두 문자열의 해밍 거리(다른 위치의 수)를 출력하세요. 길이가 다르면 -1을 출력하세요.</p>',
        "problem_text": '두 이진 문자열이 한 줄씩 입력됩니다. 두 문자열의 해밍 거리(다른 위치의 수)를 출력하세요. 길이가 다르면 -1을 출력하세요.',
        "marker": '해밍 거리(Hamming distance) 계산하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➗ 해밍 거리(Hamming distance) 계산하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">해밍 거리는 길이가 같은 두 문자열에서 \'같은 위치의 글자가 서로 다른 개수\'를 뜻해요. zip()으로 두 문자열의 같은 자리 글자를 짝지어 비교하면서, 다를 때마다 카운트를 늘리면 간단히 구할 수 있어요. 길이가 다르면 정의상 비교가 불가능하므로 -1을 출력해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = input()\nb = input()\nif len(a) != len(b):\n    print(-1)\nelse:\n    diff = sum(1 for x, y in zip(a, b) if x != y)\n    print(diff)</pre>\n</div>\n',
    },
    {
        "id": 468,
        "old": '<p>n m과 비용 격자가 입력됩니다. 좌상단에서 우하단까지 오른쪽·아래로만 이동할 때 최소 비용을 출력하세요.</p>',
        "problem_text": 'n m과 비용 격자가 입력됩니다. 좌상단에서 우하단까지 오른쪽·아래로만 이동할 때 최소 비용을 출력하세요.',
        "marker": 'DP로 격자 최소 비용 경로 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧭 DP로 격자 최소 비용 경로 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">좌상단에서 우하단까지 오른쪽·아래로만 이동하며 비용 합을 최소화하는 문제예요. 각 칸(i,j)에 도달하는 최소 비용은 \'위에서 왔을 때\'와 \'왼쪽에서 왔을 때\' 중 더 적은 비용에 현재 칸 비용을 더한 값이에요: dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1]).</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, m = map(int, input().split())\ngrid = [list(map(int, input().split())) for _ in range(n)]\ndp = [[0]*m for _ in range(n)]\ndp[0][0] = grid[0][0]\nfor j in range(1, m):\n    dp[0][j] = dp[0][j-1] + grid[0][j]\nfor i in range(1, n):\n    dp[i][0] = dp[i-1][0] + grid[i][0]\nfor i in range(1, n):\n    for j in range(1, m):\n        dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])\nprint(dp[n-1][m-1])</pre>\n</div>\n',
    },
    {
        "id": 469,
        "old": '<p>활동 수 n이 첫 줄에, 이후 시작·종료 시간이 n줄 입력됩니다. 최대한 많은 활동을 선택할 때 수를 출력하세요.</p>',
        "problem_text": '활동 수 n이 첫 줄에, 이후 시작·종료 시간이 n줄 입력됩니다. 최대한 많은 활동을 선택할 때 수를 출력하세요.',
        "marker": '그리디: 활동 선택 문제',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🗓️ 그리디: 활동 선택 문제</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">겹치지 않는 활동을 최대한 많이 고르는 문제예요. 종료 시간이 빠른 활동부터 고르는 그리디가 항상 최적이라는 걸 증명할 수 있어요(종료가 빠를수록 다음 활동을 고를 여유가 더 생기니까요). 종료 시간 기준으로 정렬한 뒤, 마지막으로 고른 활동의 종료 시간 이후에 시작하는 활동만 이어서 고르면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\nactivities = [tuple(map(int, input().split())) for _ in range(n)]\nactivities.sort(key=lambda x: x[1])\n\ncount = 0\nlast_end = -1\nfor start, end in activities:\n    if start >= last_end:\n        count += 1\n        last_end = end\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 470,
        "old": '<p>노드 수 n과 각 노드의 왼쪽·오른쪽 자식(없으면 -1)이 입력됩니다. 루트는 1번이며 전위 순회 결과를 출력하세요.</p>',
        "problem_text": '노드 수 n과 각 노드의 왼쪽·오른쪽 자식(없으면 -1)이 입력됩니다. 루트는 1번이며 전위 순회 결과를 출력하세요.',
        "marker": '트리 전위 순회(preorder traversal)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🌳 트리 전위 순회(preorder traversal)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">전위 순회는 \'현재 노드 출력 → 왼쪽 자식 → 오른쪽 자식\' 순서로 방문하는 방법이에요. 각 노드의 왼쪽·오른쪽 자식 번호를 미리 저장해두면, 재귀 함수가 자기 자신을 출력한 뒤 왼쪽 서브트리, 오른쪽 서브트리를 순서대로 재귀 호출하면 돼요. 자식이 -1이면 그 방향에는 더 내려갈 노드가 없다는 뜻이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\nleft = [0] * (n + 1)\nright = [0] * (n + 1)\nfor i in range(1, n + 1):\n    node, l, r = map(int, input().split())\n    left[node], right[node] = l, r\n\nresult = []\ndef preorder(node):\n    if node == -1:\n        return\n    result.append(node)\n    preorder(left[node])\n    preorder(right[node])\n\npreorder(1)\nprint(*result)</pre>\n</div>\n',
    },
    {
        "id": 471,
        "old": '<p>정수 여러 개가 입력됩니다. 세 수의 합이 0인 경우의 수를 출력하세요. (중복 조합 제외)</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 세 수의 합이 0인 경우의 수를 출력하세요. (중복 조합 제외)',
        "marker": '투 포인터로 세 수의 합(3Sum) 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🤝 투 포인터로 세 수의 합(3Sum) 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">세 수의 합이 0이 되는 조합의 수를 모든 쌍을 비교하면 O(n³)이 돼요. 먼저 정렬한 뒤 첫 번째 수를 하나씩 고정하고, 나머지 두 수는 \'왼쪽 포인터와 오른쪽 포인터를 양 끝에서 좁혀가는\' 투 포인터로 찾으면 O(n²)으로 줄어요. 두 포인터의 합이 목표보다 크면 오른쪽 포인터를 줄이고, 작으면 왼쪽 포인터를 늘려요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = sorted(map(int, input().split()))\nn = len(nums)\ncount = 0\nfor i in range(n - 2):\n    left, right = i + 1, n - 1\n    while left < right:\n        total = nums[i] + nums[left] + nums[right]\n        if total == 0:\n            count += 1\n            left += 1\n            right -= 1\n        elif total < 0:\n            left += 1\n        else:\n            right -= 1\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 472,
        "old": '<p>n m과 m개 간선(u v)이 입력됩니다. 1번에서 n번까지 최단 경로를 출력하세요. 없으면 NONE을 출력하세요.</p>',
        "problem_text": 'n m과 m개 간선(u v)이 입력됩니다. 1번에서 n번까지 최단 경로를 출력하세요. 없으면 NONE을 출력하세요.',
        "marker": 'BFS로 최단 경로 복원하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧵 BFS로 최단 경로 복원하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">최단 거리뿐 아니라 \'실제 경로\'까지 출력해야 할 때는, BFS를 하면서 각 노드를 \'어느 노드에서 왔는지(prev)\' 함께 기록해요. 도착 노드에서 prev를 따라 거꾸로 거슬러 올라가면 시작 노드까지의 경로가 나오고, 이걸 뒤집으면 올바른 순서의 경로가 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngraph = [[] for _ in range(n + 1)]\nfor _ in range(m):\n    u, v = map(int, input().split())\n    graph[u].append(v)\n    graph[v].append(u)\n\nprev = [0] * (n + 1)\nvisited = [False] * (n + 1)\nq = deque([1])\nvisited[1] = True\nwhile q:\n    node = q.popleft()\n    for nxt in graph[node]:\n        if not visited[nxt]:\n            visited[nxt] = True\n            prev[nxt] = node\n            q.append(nxt)\n\nif not visited[n]:\n    print("NONE")\nelse:\n    path = []\n    cur = n\n    while cur != 0:\n        path.append(cur)\n        cur = prev[cur]\n    print(*reversed(path))</pre>\n</div>\n',
    },
    {
        "id": 473,
        "old": '<p>정수 n과 q가 첫 줄에, 정수 n개가 둘째 줄에, 이후 q개의 쿼리(l r)가 입력됩니다. 각 쿼리에서 l~r 구간 합(1-indexed)을 출력하세요.</p>',
        "problem_text": '정수 n과 q가 첫 줄에, 정수 n개가 둘째 줄에, 이후 q개의 쿼리(l r)가 입력됩니다. 각 쿼리에서 l~r 구간 합(1-indexed)을 출력하세요.',
        "marker": '구간 합(prefix sum)으로 쿼리 빠르게 처리하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➕ 구간 합(prefix sum)으로 쿼리 빠르게 처리하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">l부터 r까지의 합을 쿼리마다 매번 반복문으로 더하면 쿼리가 많을 때 느려져요. 미리 prefix[i] = \'처음부터 i번째까지의 합\'을 한 번만 계산해두면, 구간 [l, r]의 합을 prefix[r] - prefix[l-1]로 O(1)에 구할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, q = map(int, input().split())\nnums = list(map(int, input().split()))\nprefix = [0] * (n + 1)\nfor i in range(1, n + 1):\n    prefix[i] = prefix[i-1] + nums[i-1]\n\nfor _ in range(q):\n    l, r = map(int, input().split())\n    print(prefix[r] - prefix[l-1])</pre>\n</div>\n',
    },
    {
        "id": 474,
        "old": '<p>용량 c가 첫 줄에, get 키 또는 put 키 값 명령이 입력됩니다. END가 나오면 종료. get은 캐시에 있으면 값을, 없으면 -1을 출력하세요.</p>',
        "problem_text": '용량 c가 첫 줄에, get 키 또는 put 키 값 명령이 입력됩니다. END가 나오면 종료. get은 캐시에 있으면 값을, 없으면 -1을 출력하세요.',
        "marker": '클래스로 LRU 캐시 구현하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🗂️ 클래스로 LRU 캐시 구현하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">LRU(Least Recently Used) 캐시는 용량이 다 차면 \'가장 오래 사용되지 않은\' 데이터를 지우는 자료구조예요. 파이썬의 OrderedDict를 쓰면 \'사용 순서\'를 쉽게 관리할 수 있어요: get/put할 때마다 move_to_end로 그 키를 맨 뒤(가장 최근)로 옮기고, 용량을 넘으면 popitem(last=False)로 맨 앞(가장 오래된) 항목을 지워요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import OrderedDict\n\ncapacity = int(input())\ncache = OrderedDict()\n\ndef get(key):\n    if key not in cache:\n        return -1\n    cache.move_to_end(key)\n    return cache[key]\n\ndef put(key, value):\n    if key in cache:\n        cache.move_to_end(key)\n    cache[key] = value\n    if len(cache) > capacity:\n        cache.popitem(last=False)\n\nwhile True:\n    line = input()\n    if line == \'END\':\n        break\n    parts = line.split()\n    if parts[0] == \'get\':\n        print(get(int(parts[1])))\n    else:\n        put(int(parts[1]), int(parts[2]))</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 모의고사 1회 단원(46장) 문항 10건에 개념 설명 카드를 추가합니다."

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
