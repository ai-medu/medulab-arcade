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
        "id": 425,
        "old": '<p>계단 수 n이 첫 줄에, 각 계단의 점수가 둘째 줄에 입력됩니다. 연속 3칸 규칙 없이 얻을 수 있는 최고 점수를 출력하세요.</p>',
        "problem_text": '계단 수 n이 첫 줄에, 각 계단의 점수가 둘째 줄에 입력됩니다. 연속 3칸 규칙 없이 얻을 수 있는 최고 점수를 출력하세요.',
        "marker": 'DP: 연속 3칸 제약 계단 오르기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪜 DP: 연속 3칸 제약 계단 오르기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이 문제는 단순 계단 오르기와 달리 \'연속으로 3칸을 밟으면 안 된다\'는 제약이 있어요. 그래서 i번째 계단에 도착하는 방법을 \'전전 칸에서 한 번에 오고 전 칸도 밟은 경우\'와 \'전전전 칸에서 와서 전전 칸은 건너뛰고 전 칸만 밟은 경우\' 두 가지로 나눠요. dp[i] = max(dp[i-2]+s[i], dp[i-3]+s[i-1]+s[i])가 그 점화식이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())\ns = [0] + list(map(int, input().split()))  # 1-indexed\ndp = [0] * (n + 1)\ndp[1] = s[1]\nif n >= 2:\n    dp[2] = s[1] + s[2]\nfor i in range(3, n + 1):\n    dp[i] = max(dp[i-2] + s[i], dp[i-3] + s[i-1] + s[i])\nprint(dp[n])</pre>\n</div>\n',
    },
    {
        "id": 426,
        "old": '<p>물건 수 n과 배낭 무게 W가 첫 줄에, 이후 무게와 가치가 n줄 입력됩니다. 최대 가치를 출력하세요.</p>',
        "problem_text": '물건 수 n과 배낭 무게 W가 첫 줄에, 이후 무게와 가치가 n줄 입력됩니다. 최대 가치를 출력하세요.',
        "marker": 'DP: 0-1 배낭 문제',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🎒 DP: 0-1 배낭 문제</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">0-1 배낭은 물건을 쪼갤 수 없고(전부 넣거나 안 넣거나) 무게 제한이 있는 문제예요. dp[i][w]를 \'i번째 물건까지 고려했을 때 무게 w 이하로 담을 수 있는 최대 가치\'로 정의하면, i번째 물건을 안 넣는 경우 dp[i-1][w], 넣는 경우 dp[i-1][w-무게]+가치 중 더 큰 값을 선택해요. 그리디로는 풀 수 없고 반드시 DP가 필요한 대표 문제예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, W = map(int, input().split())\nitems = [tuple(map(int, input().split())) for _ in range(n)]\ndp = [[0]*(W+1) for _ in range(n+1)]\nfor i in range(1, n+1):\n    wt, val = items[i-1]\n    for w in range(W+1):\n        if wt > w:\n            dp[i][w] = dp[i-1][w]\n        else:\n            dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt] + val)\nprint(dp[n][W])</pre>\n</div>\n',
    },
    {
        "id": 427,
        "old": '<p>정수 여러 개가 입력됩니다. LIS의 길이를 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. LIS의 길이를 출력하세요.',
        "marker": 'DP: 최장 증가 부분수열(LIS)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📈 DP: 최장 증가 부분수열(LIS)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">LIS는 \'순서를 유지하면서 값이 계속 증가하는 가장 긴 부분수열\'의 길이예요. dp[i]를 \'i번째 원소로 끝나는 LIS의 길이\'라고 정의하면, i 이전의 모든 j에 대해 a[j] < a[i]이면 dp[i] = max(dp[i], dp[j]+1)로 갱신할 수 있어요. 모든 dp[i] 중 최댓값이 전체 LIS 길이예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\nn = len(nums)\ndp = [1] * n\nfor i in range(n):\n    for j in range(i):\n        if nums[j] < nums[i]:\n            dp[i] = max(dp[i], dp[j] + 1)\nprint(max(dp))</pre>\n</div>\n',
    },
    {
        "id": 428,
        "old": '<p>두 문자열이 한 줄씩 입력됩니다. LCS의 길이를 출력하세요.</p>',
        "problem_text": '두 문자열이 한 줄씩 입력됩니다. LCS의 길이를 출력하세요.',
        "marker": 'DP: 최장 공통 부분수열(LCS)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔗 DP: 최장 공통 부분수열(LCS)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">LCS는 두 문자열에 공통으로 들어있는, 순서를 유지한 가장 긴 부분수열의 길이예요. dp[i][j]를 \'a의 앞 i글자, b의 앞 j글자 사이의 LCS 길이\'로 정의하면, 마지막 글자가 같으면(a[i-1]==b[j-1]) dp[i-1][j-1]+1, 다르면 dp[i-1][j]와 dp[i][j-1] 중 큰 값을 선택해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = input()\nb = input()\nn, m = len(a), len(b)\ndp = [[0]*(m+1) for _ in range(n+1)]\nfor i in range(1, n+1):\n    for j in range(1, m+1):\n        if a[i-1] == b[j-1]:\n            dp[i][j] = dp[i-1][j-1] + 1\n        else:\n            dp[i][j] = max(dp[i-1][j], dp[i][j-1])\nprint(dp[n][m])</pre>\n</div>\n',
    },
    {
        "id": 429,
        "old": '<p>동전 종류와 목표 금액이 한 줄씩 입력됩니다. 목표 금액을 만드는 방법의 수를 출력하세요.</p>',
        "problem_text": '동전 종류와 목표 금액이 한 줄씩 입력됩니다. 목표 금액을 만드는 방법의 수를 출력하세요.',
        "marker": 'DP: 동전 교환 경우의 수',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">💰 DP: 동전 교환 경우의 수</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">목표 금액을 만드는 \'방법의 수\'를 구할 때는 동전 종류를 바깥 루프로, 금액을 안쪽 루프로 돌리는 순서가 중요해요. 각 동전 coin에 대해 dp[i] += dp[i-coin]을 적용하면, 그 동전을 이미 쓴 상태에서 또 쓸 수 있는 조합(순서 상관없이 개수만 다른 조합)이 정확히 한 번씩만 세어져요. 동전을 바깥 루프에 두는 게 핵심 포인트예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">coins = list(map(int, input().split()))\ntarget = int(input())\ndp = [0] * (target + 1)\ndp[0] = 1\nfor coin in coins:\n    for i in range(coin, target + 1):\n        dp[i] += dp[i - coin]\nprint(dp[target])</pre>\n</div>\n',
    },
    {
        "id": 430,
        "old": '<p>두 문자열이 한 줄씩 입력됩니다. 첫 번째 문자열을 두 번째로 바꾸기 위한 최소 편집 거리를 출력하세요. (삽입·삭제·교체 각 1회)</p>',
        "problem_text": '두 문자열이 한 줄씩 입력됩니다. 첫 번째 문자열을 두 번째로 바꾸기 위한 최소 편집 거리를 출력하세요. (삽입·삭제·교체 각 1회)',
        "marker": 'DP: 편집 거리(edit distance)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">✏️ DP: 편집 거리(edit distance)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">한 문자열을 다른 문자열로 바꾸는 데 필요한 최소 삽입·삭제·교체 횟수를 구하는 문제예요. dp[i][j]를 \'a의 앞 i글자를 b의 앞 j글자로 바꾸는 최소 연산 수\'라 하면, 마지막 글자가 같으면 dp[i-1][j-1] 그대로, 다르면 삽입(dp[i][j-1]), 삭제(dp[i-1][j]), 교체(dp[i-1][j-1]) 중 가장 작은 값에 1을 더해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = input()\nb = input()\nn, m = len(a), len(b)\ndp = [[0]*(m+1) for _ in range(n+1)]\nfor i in range(n+1):\n    dp[i][0] = i\nfor j in range(m+1):\n    dp[0][j] = j\nfor i in range(1, n+1):\n    for j in range(1, m+1):\n        if a[i-1] == b[j-1]:\n            dp[i][j] = dp[i-1][j-1]\n        else:\n            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])\nprint(dp[n][m])</pre>\n</div>\n',
    },
    {
        "id": 431,
        "old": '<p>n m이 첫 줄에, 이후 n줄에 0과 1로 이루어진 행렬이 입력됩니다. 1로만 이루어진 최대 정사각형의 넓이를 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 n줄에 0과 1로 이루어진 행렬이 입력됩니다. 1로만 이루어진 최대 정사각형의 넓이를 출력하세요.',
        "marker": 'DP: 행렬에서 최대 정사각형 넓이',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🟦 DP: 행렬에서 최대 정사각형 넓이</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">1로만 이루어진 가장 큰 정사각형을 찾을 때, dp[i][j]를 \'(i,j)를 오른쪽 아래 꼭짓점으로 하는 가장 큰 정사각형의 한 변의 길이\'로 정의해요. grid[i][j]가 1이면, 왼쪽·위·왼쪽위 세 칸의 dp 값 중 최솟값에 1을 더한 값이 돼요(세 방향 모두 그만큼은 보장되어야 정사각형이 만들어지니까요). 정사각형 한 변의 길이의 최댓값을 제곱하면 넓이예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, m = map(int, input().split())\ngrid = [list(map(int, input().split())) for _ in range(n)]\ndp = [[0]*m for _ in range(n)]\nmax_side = 0\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == 1:\n            if i == 0 or j == 0:\n                dp[i][j] = 1\n            else:\n                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1\n            max_side = max(max_side, dp[i][j])\nprint(max_side * max_side)</pre>\n</div>\n',
    },
    {
        "id": 432,
        "old": '<p>문자열이 입력됩니다. 모든 부분 문자열이 팰린드롬이 되도록 분할할 때 최소 컷 수를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 모든 부분 문자열이 팰린드롬이 되도록 분할할 때 최소 컷 수를 출력하세요.',
        "marker": 'DP: 팰린드롬 최소 분할 수',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪞 DP: 팰린드롬 최소 분할 수</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열을 팰린드롬 조각들로 나눌 때 필요한 최소 컷 수를 구하는 문제예요. 먼저 모든 구간이 팰린드롬인지 is_pal[i][j]로 미리 계산해두면, dp[i] = \'i번째 글자까지 자르는 최소 컷 수\'를 \'0부터 i까지가 통째로 팰린드롬이면 0컷\', 아니면 \'j+1부터 i까지가 팰린드롬인 모든 j에 대해 dp[j]+1 중 최솟값\'으로 구할 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()\nn = len(s)\nis_pal = [[False]*n for _ in range(n)]\nfor i in range(n):\n    is_pal[i][i] = True\nfor length in range(2, n+1):\n    for i in range(n - length + 1):\n        j = i + length - 1\n        if s[i] == s[j] and (length == 2 or is_pal[i+1][j-1]):\n            is_pal[i][j] = True\n\ndp = [0] * n\nfor i in range(n):\n    if is_pal[0][i]:\n        dp[i] = 0\n        continue\n    dp[i] = min(dp[j] + 1 for j in range(i) if is_pal[j+1][i])\nprint(dp[n-1])</pre>\n</div>\n',
    },
    {
        "id": 433,
        "old": '<p>정수 여러 개가 입력됩니다. 연속 부분 배열의 합이 최대인 값을 DP로 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 연속 부분 배열의 합이 최대인 값을 DP로 출력하세요.',
        "marker": 'DP: 카데인 알고리즘으로 최대 연속 부분합',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">📉 DP: 카데인 알고리즘으로 최대 연속 부분합</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">연속된 부분 배열의 합이 최대가 되는 값을 구하는 대표적인 DP예요. dp[i]를 \'i번째 원소로 끝나는 연속 부분합의 최댓값\'으로 정의하면, dp[i] = max(nums[i], dp[i-1] + nums[i])가 성립해요. 이전까지의 합이 음수라면 그냥 현재 값부터 새로 시작하는 게 더 낫다는 뜻이에요. 전체 dp 중 최댓값이 답이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))\ncur = best = nums[0]\nfor x in nums[1:]:\n    cur = max(x, cur + x)\n    best = max(best, cur)\nprint(best)</pre>\n</div>\n',
    },
    {
        "id": 434,
        "old": '<p>n m이 첫 줄에, 이후 n줄에 정수로 된 격자가 입력됩니다. 좌상단에서 우하단까지 이동(오른쪽·아래)하며 최소 합을 출력하세요.</p>',
        "problem_text": 'n m이 첫 줄에, 이후 n줄에 정수로 된 격자가 입력됩니다. 좌상단에서 우하단까지 이동(오른쪽·아래)하며 최소 합을 출력하세요.',
        "marker": 'DP: 격자 최소 경로합',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧭 DP: 격자 최소 경로합</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">좌상단에서 우하단까지 오른쪽·아래로만 이동하며 지나는 칸 값의 합이 최소가 되는 경로를 찾는 문제예요. dp[i][j]를 \'(0,0)에서 (i,j)까지의 최소 합\'이라 하면, (i,j)는 위 칸이나 왼쪽 칸에서만 올 수 있으므로 dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])이에요. 첫 행과 첫 열은 한 방향으로만 올 수 있으니 따로 채워줘요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n, m = map(int, input().split())\ngrid = [list(map(int, input().split())) for _ in range(n)]\ndp = [[0]*m for _ in range(n)]\ndp[0][0] = grid[0][0]\nfor j in range(1, m):\n    dp[0][j] = dp[0][j-1] + grid[0][j]\nfor i in range(1, n):\n    dp[i][0] = dp[i-1][0] + grid[i][0]\nfor i in range(1, n):\n    for j in range(1, m):\n        dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])\nprint(dp[n-1][m-1])</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 동적 계획법(DP) 단원(42장) 문항 10건에 개념 설명 카드를 추가합니다."

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
