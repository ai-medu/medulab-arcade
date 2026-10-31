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
        "id": 395,
        "old": '<p>정수 n이 입력되면 메모이제이션을 활용한 재귀로 피보나치 수열의 n번째 값을 출력하세요. (F(1)=1, F(2)=1)</p>',
        "problem_text": '정수 n이 입력되면 메모이제이션을 활용한 재귀로 피보나치 수열의 n번째 값을 출력하세요. (F(1)=1, F(2)=1)',
        "marker": '메모이제이션(memoization)이란?',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧠 메모이제이션(memoization)이란?</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">재귀로 피보나치를 구하면 같은 F(k) 값을 수없이 다시 계산하게 돼요(f(5)를 구하려고 f(4), f(3)을 계산하는데, f(4)를 구할 때도 똑같은 f(3)을 또 계산하죠). 메모이제이션은 한 번 구한 값을 딕셔너리(memo)에 저장해두고, 다음에 같은 입력이 들어오면 저장된 값을 바로 꺼내 쓰는 기법이에요. 계산량이 지수적으로 줄어 n이 커져도 빠르게 동작해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">memo = {1: 1, 2: 1}\ndef fib(n):\n    if n in memo:\n        return memo[n]\n    memo[n] = fib(n-1) + fib(n-2)\n    return memo[n]\n\nn = int(input())\nprint(fib(n))</pre>\n</div>\n',
    },
    {
        "id": 396,
        "old": '<p>밑(base)과 지수(exp)가 입력됩니다. 분할정복 방식으로 base^exp 를 계산해 출력하세요.</p>',
        "problem_text": '밑(base)과 지수(exp)가 입력됩니다. 분할정복 방식으로 base^exp 를 계산해 출력하세요.',
        "marker": '분할정복으로 거듭제곱 빠르게 계산하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⚡ 분할정복으로 거듭제곱 빠르게 계산하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">base**exp를 그냥 반복문으로 exp번 곱하면 exp가 커질수록 느려져요. 분할정복(divide and conquer)을 쓰면 \'지수를 반으로 쪼개는\' 방식으로 훨씬 빠르게 계산할 수 있어요. exp가 짝수면 절반을 구해 제곱하면 되고, 홀수면 1을 떼어내 짝수로 만든 뒤 같은 방법을 적용해요. 이렇게 하면 곱셈 횟수가 exp가 아니라 log(exp)에 비례해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def power(base, exp):\n    if exp == 0:\n        return 1\n    half = power(base, exp // 2)\n    if exp % 2 == 0:\n        return half * half\n    else:\n        return half * half * base\n\nb, e = map(int, input().split())\nprint(power(b, e))</pre>\n</div>\n',
    },
    {
        "id": 397,
        "old": '<p>정수 n이 입력되면 1부터 n까지의 숫자로 만들 수 있는 모든 순열을 사전 순으로 한 줄씩 출력하세요.</p>',
        "problem_text": '정수 n이 입력되면 1부터 n까지의 숫자로 만들 수 있는 모든 순열을 사전 순으로 한 줄씩 출력하세요.',
        "marker": '재귀 + 백트래킹으로 순열 만들기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔀 재귀 + 백트래킹으로 순열 만들기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">순열은 \'순서가 다르면 다른 결과\'로 치는 나열이에요. 재귀로 만들 때는 지금까지 고른 숫자들을 path에 쌓아두고, 아직 쓰지 않은 숫자(used가 False인 것)를 하나씩 골라 다음 자리로 내려가요. path의 길이가 n이 되면 완성된 순열 하나를 출력하고, 다시 되돌아와(백트래킹) 다른 숫자를 시도해요. \'선택 → 재귀 → 선택 취소\'의 반복이라고 생각하면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\nused = [False] * (n + 1)\npath = []\n\ndef backtrack():\n    if len(path) == n:\n        print(*path)\n        return\n    for num in range(1, n + 1):\n        if not used[num]:\n            used[num] = True\n            path.append(num)\n            backtrack()\n            path.pop()          # 선택 취소\n            used[num] = False\n\nbacktrack()</pre>\n</div>\n',
    },
    {
        "id": 398,
        "old": '<p>n과 k가 입력됩니다. 1부터 n까지에서 k개를 고르는 모든 조합을 사전 순으로 출력하세요.</p>',
        "problem_text": 'n과 k가 입력됩니다. 1부터 n까지에서 k개를 고르는 모든 조합을 사전 순으로 출력하세요.',
        "marker": '재귀로 조합 생성하기(순열과의 차이)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🎯 재귀로 조합 생성하기(순열과의 차이)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">조합은 순열과 달리 \'순서를 구분하지 않는\' 선택이에요(1,2와 2,1은 같은 조합). 그래서 재귀 함수에 start 인덱스를 넘겨, 이전에 고른 숫자보다 큰 숫자만 다음 후보로 보게 만들면 돼요. 이렇게 하면 같은 조합을 거꾸로도 세는 중복이 자동으로 사라져요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, k = map(int, input().split())\npath = []\n\ndef backtrack(start):\n    if len(path) == k:\n        print(*path)\n        return\n    for num in range(start, n + 1):\n        path.append(num)\n        backtrack(num + 1)   # 다음엔 num보다 큰 수만\n        path.pop()\n\nbacktrack(1)</pre>\n</div>\n',
    },
    {
        "id": 399,
        "old": '<p>원판 수 n이 입력됩니다. 하노이 탑 이동 과정을 A→C (B 보조) 순서로 출력하세요.</p>',
        "problem_text": '원판 수 n이 입력됩니다. 하노이 탑 이동 과정을 A→C (B 보조) 순서로 출력하세요.',
        "marker": '재귀로 하노이 탑 풀기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🗼 재귀로 하노이 탑 풀기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">하노이 탑의 핵심 아이디어는 \'n개를 옮기는 문제\'를 \'n-1개를 옮기는 작은 문제 2번 + 맨 아래 원판 이동 1번\'으로 쪼개는 거예요. n개의 원판을 from 기둥에서 to 기둥으로 옮긴다면: ① 위쪽 n-1개를 from에서 via(보조)로 옮기고, ② 맨 아래 원판을 from에서 to로 옮긴 뒤, ③ via에 있던 n-1개를 다시 via에서 to로 옮기면 돼요. 이 3단계가 그대로 재귀 호출이 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def hanoi(n, frm, to, via):\n    if n == 0:\n        return\n    hanoi(n - 1, frm, via, to)\n    print(f"{frm} -> {to}")\n    hanoi(n - 1, via, to, frm)\n\nn = int(input())\nhanoi(n, \'A\', \'C\', \'B\')</pre>\n</div>\n',
    },
    {
        "id": 400,
        "old": '<p>정수 리스트와 목표 합이 한 줄씩 입력됩니다. 부분 집합의 합이 목표와 일치하는 부분 집합의 수를 출력하세요.</p>',
        "problem_text": '정수 리스트와 목표 합이 한 줄씩 입력됩니다. 부분 집합의 합이 목표와 일치하는 부분 집합의 수를 출력하세요.',
        "marker": '재귀로 부분집합의 합 세기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➕ 재귀로 부분집합의 합 세기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 각 원소를 \'부분집합에 포함한다 / 포함하지 않는다\' 두 가지로 나눠 재귀적으로 탐색하면, 모든 부분집합을 빠짐없이 만들어볼 수 있어요. 마지막 원소까지 다 결정했을 때 지금까지 고른 값들의 합이 목표와 같으면 카운트를 1 늘려요. 원소가 n개면 선택의 경우의 수는 2^n개예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def count_subsets(nums, idx, target):\n    if idx == len(nums):\n        return 1 if target == 0 else 0\n    # 포함하지 않는 경우 + 포함하는 경우\n    return (count_subsets(nums, idx + 1, target)\n            + count_subsets(nums, idx + 1, target - nums[idx]))\n\nnums = list(map(int, input().split()))\ntarget = int(input())\nprint(count_subsets(nums, 0, target))</pre>\n</div>\n',
    },
    {
        "id": 401,
        "old": '<p>동전 종류가 한 줄에, 목표 금액이 둘째 줄에 입력됩니다. 목표 금액을 만드는 최소 동전 수를 출력하세요. 불가능하면 -1을 출력하세요.</p>',
        "problem_text": '동전 종류가 한 줄에, 목표 금액이 둘째 줄에 입력됩니다. 목표 금액을 만드는 최소 동전 수를 출력하세요. 불가능하면 -1을 출력하세요.',
        "marker": '메모이제이션으로 최소 동전 수 구하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪙 메모이제이션으로 최소 동전 수 구하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">목표 금액 amount를 만드는 최소 동전 수를 구할 때, \'맨 마지막에 어떤 동전을 썼는지\'로 나눠 생각해요. 마지막에 coin을 썼다면 그 전 상태는 amount-coin을 만든 최소 동전 수였을 거예요. 즉 memo[amount] = 1 + min(memo[amount-coin] for coin in coins)로 점화식을 세울 수 있고, 같은 amount를 반복 계산하지 않도록 memo에 저장해요. 만들 수 없는 금액은 무한대(또는 -1)로 처리해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">coins = list(map(int, input().split()))\namount = int(input())\nmemo = {0: 0}\n\ndef solve(a):\n    if a < 0:\n        return float(\'inf\')\n    if a in memo:\n        return memo[a]\n    memo[a] = min(solve(a - c) + 1 for c in coins)\n    return memo[a]\n\nresult = solve(amount)\nprint(result if result != float(\'inf\') else -1)</pre>\n</div>\n',
    },
    {
        "id": 402,
        "old": '<p>문자열이 입력됩니다. 모든 부분 문자열이 팰린드롬이 되도록 분할하는 방법의 수를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 모든 부분 문자열이 팰린드롬이 되도록 분할하는 방법의 수를 출력하세요.',
        "marker": '재귀로 팰린드롬 분할 경우의 수 세기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪞 재귀로 팰린드롬 분할 경우의 수 세기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열을 앞에서부터 잘라가며, \'지금 자른 조각이 팰린드롬인지\' 확인하고 팰린드롬일 때만 다음 재귀로 넘어가는 방식이에요. 모든 글자를 다 쓸 때까지 이렇게 자르는 방법의 수를 더하면 전체 분할 방법의 수가 돼요. 팰린드롬 검사는 s == s[::-1]처럼 간단히 할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nn = len(s)\n\ndef is_pal(sub):\n    return sub == sub[::-1]\n\ndef count(start):\n    if start == n:\n        return 1\n    total = 0\n    for end in range(start + 1, n + 1):\n        piece = s[start:end]\n        if is_pal(piece):\n            total += count(end)\n    return total\n\nprint(count(0))</pre>\n</div>\n',
    },
    {
        "id": 403,
        "old": '<p>정수 n이 입력되면 n×n 체스판에서 n개의 퀸이 서로 공격하지 않도록 놓는 경우의 수를 출력하세요.</p>',
        "problem_text": '정수 n이 입력되면 n×n 체스판에서 n개의 퀸이 서로 공격하지 않도록 놓는 경우의 수를 출력하세요.',
        "marker": '재귀 백트래킹으로 N-Queen 풀기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">👑 재귀 백트래킹으로 N-Queen 풀기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">N-Queen은 각 행에 퀸을 하나씩 놓으면서, 같은 열이나 대각선에 이미 놓인 퀸이 있는지 확인하는 백트래킹 문제예요. row번째 행에 col 열로 퀸을 놓으려 할 때, 이미 놓인 퀸들과 열이 같거나(col == 기존col) 대각선이 같으면(row 차이 == col 차이) 놓을 수 없어요. 모든 행에 안전하게 퀸을 놓으면 해 하나를 찾은 것이고, 더 이상 놓을 곳이 없으면 되돌아가요(백트래킹).</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\ncols = []\ncount = 0\n\ndef is_safe(row, col):\n    for r, c in enumerate(cols):\n        if c == col or abs(row - r) == abs(col - c):\n            return False\n    return True\n\ndef backtrack(row):\n    global count\n    if row == n:\n        count += 1\n        return\n    for col in range(n):\n        if is_safe(row, col):\n            cols.append(col)\n            backtrack(row + 1)\n            cols.pop()\n\nbacktrack(0)\nprint(count)</pre>\n</div>\n',
    },
    {
        "id": 404,
        "old": '<p>계단 수 n이 입력됩니다. 한 번에 1칸 또는 2칸을 오를 수 있을 때 n개의 계단을 오르는 경우의 수를 메모이제이션 재귀로 출력하세요.</p>',
        "problem_text": '계단 수 n이 입력됩니다. 한 번에 1칸 또는 2칸을 오를 수 있을 때 n개의 계단을 오르는 경우의 수를 메모이제이션 재귀로 출력하세요.',
        "marker": '메모이제이션 재귀로 계단 오르기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪜 메모이제이션 재귀로 계단 오르기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">한 번에 1칸 또는 2칸을 오를 수 있다면, n번째 계단에 도착하는 방법은 \'n-1번째에서 1칸 오르기\'와 \'n-2번째에서 2칸 오르기\' 두 가지뿐이에요. 그래서 stairs(n) = stairs(n-1) + stairs(n-2)라는 점화식이 성립해요(피보나치와 똑같은 구조죠). 기저 조건만 stairs(1)=1, stairs(2)=2로 잡고, 메모이제이션으로 중복 계산을 없애면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">memo = {1: 1, 2: 2}\ndef stairs(n):\n    if n in memo:\n        return memo[n]\n    memo[n] = stairs(n - 1) + stairs(n - 2)\n    return memo[n]\n\nn = int(input())\nprint(stairs(n))</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 재귀/메모이제이션 단원(39장) 문항 10건에 개념 설명 카드를 추가합니다."

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
