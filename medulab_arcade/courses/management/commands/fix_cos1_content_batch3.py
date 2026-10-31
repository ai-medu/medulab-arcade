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
        "id": 415,
        "old": '<p>괄호 문자열이 입력됩니다. 올바른 괄호 문자열이면 YES, 아니면 NO를 출력하세요.</p>',
        "problem_text": '괄호 문자열이 입력됩니다. 올바른 괄호 문자열이면 YES, 아니면 NO를 출력하세요.',
        "marker": '스택으로 괄호 유효성 검사하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧱 스택으로 괄호 유효성 검사하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">괄호가 올바른지 확인할 때는 \'여는 괄호는 쌓아두고, 닫는 괄호가 나오면 가장 최근에 쌓인 여는 괄호와 짝을 맞춰 꺼내는\' 스택을 쓰면 돼요. 마지막까지 짝이 맞으면(스택이 비면) 올바른 괄호, 중간에 꺼낼 괄호가 없거나 끝나고 스택이 남아있으면 올바르지 않은 괄호예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nstack = []\nvalid = True\nfor ch in s:\n    if ch == \'(\':\n        stack.append(ch)\n    elif ch == \')\':\n        if not stack:\n            valid = False\n            break\n        stack.pop()\nif stack:\n    valid = False\nprint("YES" if valid else "NO")</pre>\n</div>\n',
    },
    {
        "id": 416,
        "old": '<p>후위 표기식이 입력됩니다. 계산 결과를 출력하세요. (피연산자는 정수, 연산자는 + - * /)</p>',
        "problem_text": '후위 표기식이 입력됩니다. 계산 결과를 출력하세요. (피연산자는 정수, 연산자는 + - * /)',
        "marker": '스택으로 후위 표기식 계산하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➗ 스택으로 후위 표기식 계산하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">후위 표기식(postfix)은 \'연산자가 피연산자들 뒤에 오는\' 표기법이에요(예: 3 4 + 는 3+4). 계산할 때는 숫자를 만나면 스택에 쌓고, 연산자를 만나면 스택에서 숫자 2개를 꺼내 계산한 뒤 결과를 다시 스택에 넣어요. 마지막에 스택에 남은 하나의 값이 최종 결과예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">tokens = input().split()\nstack = []\nfor tok in tokens:\n    if tok in \'+-*/\':\n        b = stack.pop()\n        a = stack.pop()\n        if tok == \'+\': stack.append(a + b)\n        elif tok == \'-\': stack.append(a - b)\n        elif tok == \'*\': stack.append(a * b)\n        else: stack.append(a // b)\n    else:\n        stack.append(int(tok))\nprint(stack[0])</pre>\n</div>\n',
    },
    {
        "id": 417,
        "old": '<p>미로 크기 n m이 첫 줄에, 이후 n줄에 0(이동가능) 1(벽) 형태의 미로가 입력됩니다. (0,0)에서 (n-1,m-1)까지 최단 거리를 출력하세요. 도달 불가면 -1을 출력하세요.</p>',
        "problem_text": '미로 크기 n m이 첫 줄에, 이후 n줄에 0(이동가능) 1(벽) 형태의 미로가 입력됩니다. (0,0)에서 (n-1,m-1)까지 최단 거리를 출력하세요. 도달 불가면 -1을 출력하세요.',
        "marker": 'BFS로 미로 최단 거리 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧭 BFS로 미로 최단 거리 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">미로에서 \'최단 거리\'를 구할 때는 DFS가 아니라 BFS를 써야 해요. BFS는 가까운 칸부터 차례차례(한 칸, 두 칸, 세 칸...) 넓게 퍼지며 탐색하기 때문에, 처음 도착 지점에 닿는 순간이 곧 최단 거리예요. deque를 큐로 써서 (위치, 거리)를 넣고, 상하좌우로 이동 가능한 칸을 방문 처리하며 큐에 추가해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\nmaze = [list(map(int, input().split())) for _ in range(n)]\nvisited = [[False]*m for _ in range(n)]\n\nq = deque([(0, 0, 0)])  # (행, 열, 거리)\nvisited[0][0] = True\nwhile q:\n    r, c, d = q.popleft()\n    if (r, c) == (n-1, m-1):\n        print(d)\n        break\n    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n        nr, nc = r+dr, c+dc\n        if 0<=nr<n and 0<=nc<m and not visited[nr][nc] and maze[nr][nc]==0:\n            visited[nr][nc] = True\n            q.append((nr, nc, d+1))\nelse:\n    print(-1)</pre>\n</div>\n',
    },
    {
        "id": 418,
        "old": '<p>정수 여러 개가 입력됩니다. 각 원소에 대해 오른쪽에서 처음 만나는 큰 수를 출력하세요. 없으면 -1을 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 각 원소에 대해 오른쪽에서 처음 만나는 큰 수를 출력하세요. 없으면 -1을 출력하세요.',
        "marker": '모노토닉 스택으로 다음 큰 수 찾기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📈 모노토닉 스택으로 다음 큰 수 찾기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">각 원소마다 \'오른쪽에서 처음 만나는 더 큰 수\'를 매번 뒤로 훑어서 찾으면 O(n²)이 돼요. 모노토닉 스택(단조 스택)을 쓰면 O(n)에 가능해요. 왼쪽부터 보면서, 현재 값이 스택 맨 위(아직 답을 못 찾은 이전 원소)보다 크면 그 원소의 답이 바로 현재 값이 되는 거예요. 그렇게 답을 찾은 원소는 스택에서 빼고, 현재 인덱스를 다시 스택에 쌓아요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\nn = len(nums)\nanswer = [-1] * n\nstack = []  # 인덱스를 저장\nfor i in range(n):\n    while stack and nums[stack[-1]] < nums[i]:\n        idx = stack.pop()\n        answer[idx] = nums[i]\n    stack.append(i)\nprint(*answer)</pre>\n</div>\n',
    },
    {
        "id": 419,
        "old": '<p>첫 줄에 대기 중인 문서 우선순위, 둘째 줄에 확인할 문서 인덱스가 입력됩니다. 해당 문서가 몇 번째로 출력되는지 출력하세요.</p>',
        "problem_text": '첫 줄에 대기 중인 문서 우선순위, 둘째 줄에 확인할 문서 인덱스가 입력됩니다. 해당 문서가 몇 번째로 출력되는지 출력하세요.',
        "marker": '큐 시뮬레이션: 프린터 우선순위',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🖨️ 큐 시뮬레이션: 프린터 우선순위</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">우선순위가 높은 문서부터 인쇄되는 프린터를 흉내 낼 때는, 맨 앞 문서를 꺼내서(popleft) \'뒤에 더 높은 우선순위가 있는지\' 확인해요. 있으면 그 문서를 맨 뒤로 다시 보내고(append), 없으면 그 문서를 실제로 인쇄해요. 궁금한 문서가 인쇄될 때까지 이 과정을 반복하면서 몇 번째로 인쇄되는지 세면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\npriorities = list(map(int, input().split()))\ntarget = int(input())\n\nqueue = deque((i, p) for i, p in enumerate(priorities))\norder = 0\nwhile queue:\n    idx, pr = queue.popleft()\n    if any(pr < other_pr for _, other_pr in queue):\n        queue.append((idx, pr))\n    else:\n        order += 1\n        if idx == target:\n            print(order)\n            break</pre>\n</div>\n',
    },
    {
        "id": 420,
        "old": '<p>히스토그램의 각 막대 높이가 입력됩니다. 만들 수 있는 최대 직사각형 넓이를 출력하세요.</p>',
        "problem_text": '히스토그램의 각 막대 높이가 입력됩니다. 만들 수 있는 최대 직사각형 넓이를 출력하세요.',
        "marker": '모노토닉 스택으로 히스토그램 최대 직사각형',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🏛️ 모노토닉 스택으로 히스토그램 최대 직사각형</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">히스토그램에서 만들 수 있는 최대 직사각형을 구할 때, 각 막대를 \'그 막대 높이로 만들 수 있는 가장 넓은 직사각형의 오른쪽 경계\'라고 생각해요. 증가하는 높이를 스택에 쌓다가, 더 낮은 막대가 나오면 \'스택에서 꺼낸 막대 높이 × (현재 위치 - 새로운 스택 맨 위 인덱스 - 1)\'로 넓이를 계산해요. 이렇게 하면 모든 막대를 O(n)에 한 번씩만 처리할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">heights = list(map(int, input().split()))\nstack = []  # 인덱스\nmax_area = 0\nheights.append(0)  # 마지막에 0을 추가해 스택을 모두 비움\nfor i, h in enumerate(heights):\n    while stack and heights[stack[-1]] > h:\n        height = heights[stack.pop()]\n        width = i if not stack else i - stack[-1] - 1\n        max_area = max(max_area, height * width)\n    stack.append(i)\nprint(max_area)</pre>\n</div>\n',
    },
    {
        "id": 421,
        "old": '<p>n m이 첫 줄에, 이후 n줄에 0과 1로 이루어진 격자가 입력됩니다. 1로 연결된 영역의 개수를 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 n줄에 0과 1로 이루어진 격자가 입력됩니다. 1로 연결된 영역의 개수를 출력하세요.',
        "marker": 'BFS로 연결된 섬(영역) 개수 세기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🏝️ BFS로 연결된 섬(영역) 개수 세기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">격자에서 1로 이루어진 덩어리가 몇 개 있는지 세는 문제예요. 아직 방문하지 않은 1을 만날 때마다 \'새로운 섬을 발견한 것\'이므로 개수를 1 늘리고, 그 지점에서 BFS를 시작해 상하좌우로 연결된 1을 모두 방문 처리해요. 모든 칸을 다 훑고 나면 발견한 섬의 개수가 답이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, m = map(int, input().split())\ngrid = [list(map(int, input().split())) for _ in range(n)]\nvisited = [[False]*m for _ in range(n)]\n\ndef bfs(r, c):\n    q = deque([(r, c)])\n    visited[r][c] = True\n    while q:\n        cr, cc = q.popleft()\n        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n            nr, nc = cr+dr, cc+dc\n            if 0<=nr<n and 0<=nc<m and not visited[nr][nc] and grid[nr][nc]==1:\n                visited[nr][nc] = True\n                q.append((nr, nc))\n\ncount = 0\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == 1 and not visited[i][j]:\n            count += 1\n            bfs(i, j)\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 422,
        "old": '<p>괄호 문자열이 입력됩니다. 제거해야 할 최소 괄호 수를 출력하세요.</p>',
        "problem_text": '괄호 문자열이 입력됩니다. 제거해야 할 최소 괄호 수를 출력하세요.',
        "marker": '스택으로 최소 제거 괄호 수 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">✂️ 스택으로 최소 제거 괄호 수 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">짝이 맞지 않는 괄호를 모두 없애려면 몇 개를 지워야 하는지는, 스택으로 \'매칭되지 않고 남는 괄호\'를 세면 알 수 있어요. \'(\'는 스택에 쌓고, \')\'를 만났을 때 스택이 비어 있으면(짝이 없는 \')\') 바로 제거 대상으로 세요. 끝까지 처리한 뒤 스택에 남은 \'(\' 들도 모두 짝이 없는 것이므로 제거 대상에 더해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nstack = []\nremove = 0\nfor ch in s:\n    if ch == \'(\':\n        stack.append(ch)\n    else:  # ch == \')\'\n        if stack:\n            stack.pop()\n        else:\n            remove += 1   # 짝이 없는 \')\'\nremove += len(stack)      # 짝이 없는 \'(\' 들\nprint(remove)</pre>\n</div>\n',
    },
    {
        "id": 423,
        "old": '<p>정수 여러 개와 윈도우 크기 k가 한 줄씩 입력됩니다. 크기 k의 윈도우를 이동하며 각 윈도우의 최댓값을 출력하세요.</p>',
        "problem_text": '정수 여러 개와 윈도우 크기 k가 한 줄씩 입력됩니다. 크기 k의 윈도우를 이동하며 각 윈도우의 최댓값을 출력하세요.',
        "marker": 'deque로 슬라이딩 윈도우 최댓값 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📐 deque로 슬라이딩 윈도우 최댓값 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">매 윈도우마다 max()를 다시 계산하면 O(n·k)로 느려요. 대신 \'단조 감소 deque\'를 유지하면 O(n)에 가능해요. deque 앞쪽에 항상 현재 윈도우의 최댓값 후보를 두고, 새 값이 들어올 때 deque 뒤쪽의 더 작은 값들을 모두 버려요(어차피 그 값들은 다시는 최댓값이 될 수 없으니까). 윈도우 범위를 벗어난 인덱스는 앞에서 빼줘요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nnums = list(map(int, input().split()))\nk = int(input())\ndq = deque()  # 인덱스 저장, 값은 단조 감소\nresult = []\nfor i, x in enumerate(nums):\n    while dq and nums[dq[-1]] <= x:\n        dq.pop()\n    dq.append(i)\n    if dq[0] <= i - k:\n        dq.popleft()\n    if i >= k - 1:\n        result.append(nums[dq[0]])\nprint(*result)</pre>\n</div>\n',
    },
    {
        "id": 424,
        "old": '<p>n과 k가 입력됩니다. n명이 원형으로 서서 k번째마다 한 명씩 나올 때 나오는 순서를 출력하세요.</p>',
        "problem_text": 'n과 k가 입력됩니다. n명이 원형으로 서서 k번째마다 한 명씩 나올 때 나오는 순서를 출력하세요.',
        "marker": '큐 시뮬레이션: 요세푸스 문제',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🕯️ 큐 시뮬레이션: 요세푸스 문제</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">요세푸스 문제는 원 모양으로 선 사람들 중 k번째마다 한 명씩 제거하는 문제예요. deque에 1~n을 넣어두고, \'rotate(-(k-1))\'로 큐를 돌려 k번째 사람을 맨 앞으로 오게 만든 뒤 popleft로 제거하면 간단히 흉내 낼 수 있어요. 큐가 빌 때까지 이 과정을 반복하면 제거되는 순서가 그대로 나와요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from collections import deque\n\nn, k = map(int, input().split())\nq = deque(range(1, n + 1))\norder = []\nwhile q:\n    q.rotate(-(k - 1))   # k번째 사람을 맨 앞으로\n    order.append(q.popleft())\nprint(*order)</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 스택/큐/BFS 단원(41장) 문항 10건에 개념 설명 카드를 추가합니다."

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
