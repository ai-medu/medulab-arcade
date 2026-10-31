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
        "id": 385,
        "old": '<p>정수 여러 개가 입력됩니다. 평균 이상인 원소의 개수를 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 평균 이상인 원소의 개수를 출력하세요.',
        "marker": '평균 이상 원소 개수 세기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📊 평균 이상 원소 개수 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">먼저 <code>sum(리스트)/len(리스트)</code>로 평균을 구하고, 그 평균보다 크거나 같은 값이 몇 개인지 조건부 컴프리헨션이나 <code>sum(조건)</code> 패턴으로 세면 돼요. 파이썬에서 True는 1, False는 0으로 취급되기 때문에 조건식을 <code>sum()</code>에 바로 넣어도 개수를 셀 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
avg = sum(nums) / len(nums)
count = sum(1 for n in nums if n >= avg)
print(count)</pre>
</div>
""",
    },
    {
        "id": 386,
        "old": '<p>정수 여러 개가 입력됩니다. 연속된 부분 수열의 합이 최대인 값을 출력하세요.</p>',
        "problem_text": '정수 여러 개가 입력됩니다. 연속된 부분 수열의 합이 최대인 값을 출력하세요.',
        "marker": '연속 부분합 최대값 구하기 (Kadane 알고리즘)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📈 연속 부분합 최대값 구하기 (Kadane 알고리즘)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">"연속된 구간의 합 중 최댓값"을 구하는 유명한 방법이 Kadane 알고리즘이에요. 왼쪽에서부터 "지금까지의 연속합(cur)"을 유지하면서, cur이 음수가 되면 거기서 끊고 새로 시작하는 게 더 유리하므로 0으로 리셋해요. 매 단계에서 지금까지 나온 최댓값을 기록해두면 끝났을 때 답이 나와요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
best = nums[0]
cur = 0
for n in nums:
    cur += n
    best = max(best, cur)
    if cur < 0:
        cur = 0
print(best)</pre>
</div>
""",
    },
    {
        "id": 387,
        "old": '<p>이름:점수 쌍이 콤마로 구분되어 입력됩니다. 최고점 이름, 최저점 이름, 평균을 각각 출력하세요.</p>',
        "problem_text": '이름:점수 쌍이 콤마로 구분되어 입력됩니다. 최고점 이름, 최저점 이름, 평균을 각각 출력하세요.',
        "marker": '딕셔너리로 최고점·최저점·평균 한 번에 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📊 딕셔너리로 최고점·최저점·평균 한 번에 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이름:점수 딕셔너리를 만든 뒤, 306번에서 배운 <code>max(key=...)</code>와 같은 방식으로 <code>min(key=...)</code>도 쓸 수 있어요. 평균은 점수들(<code>values()</code>)의 합을 개수로 나누면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">pairs = [kv.split(":") for kv in input().split(",")]
scores = {name: int(score) for name, score in pairs}
print(max(scores, key=scores.get))
print(min(scores, key=scores.get))
print(round(sum(scores.values()) / len(scores), 1))</pre>
</div>
""",
    },
    {
        "id": 388,
        "old": '<p>3행 4열 행렬이 세 줄에 입력됩니다. 각 행의 최댓값을 한 줄씩 출력하세요.</p>',
        "problem_text": '3행 4열 행렬이 세 줄에 입력됩니다. 각 행의 최댓값을 한 줄씩 출력하세요.',
        "marker": '각 행의 최댓값 구하기 (2차원 리스트 + max)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 각 행의 최댓값 구하기 (2차원 리스트 + max)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">2차원 리스트의 각 행은 그 자체로 하나의 리스트예요. 바깥 for문으로 각 행을 하나씩 꺼내면서, 그 행에 바로 <code>max()</code>를 적용하면 그 행의 최댓값을 구할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">matrix = [list(map(int, input().split())) for _ in range(3)]
for row in matrix:
    print(max(row))</pre>
</div>
""",
    },
    {
        "id": 389,
        "old": '<p>원판 개수 n이 입력되면 하노이 탑을 옮기는 데 필요한 최소 이동 횟수를 출력하세요.</p>',
        "problem_text": '원판 개수 n이 입력되면 하노이 탑을 옮기는 데 필요한 최소 이동 횟수를 출력하세요.',
        "marker": '하노이 탑 이동 횟수 - 재귀와 공식',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🗼️ 하노이 탑 이동 횟수 - 재귀와 공식</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">하노이 탑은 원판 n개를 옮기려면, "위 n-1개를 다른 기둥으로 옮기고(2^(n-1)-1번) → 가장 큰 원판 1개를 옮기고(1번) → n-1개를 다시 목표 기둥으로 옮기는(2^(n-1)-1번)" 과정이 필요해요. 이를 모두 더하면 <code>2^n - 1</code>이라는 깔끔한 공식이 나와요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
print(2 ** n - 1)</pre>
</div>
""",
    },
    {
        "id": 390,
        "old": '<p>문장이 입력됩니다. 단어 순서를 뒤집고 각 단어의 첫 글자를 대문자로 변환해 출력하세요.</p>',
        "problem_text": '문장이 입력됩니다. 단어 순서를 뒤집고 각 단어의 첫 글자를 대문자로 변환해 출력하세요.',
        "marker": '단어 역순 + 대문자 변환 조합하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔀 단어 역순 + 대문자 변환 조합하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">이미 배운 두 가지 기법을 순서대로 적용하면 돼요: 315번처럼 <code>split()</code>과 <code>[::-1]</code>로 단어 순서를 뒤집고, 그 다음 323번처럼 <code>title()</code>로 각 단어의 첫 글자를 대문자로 바꿔요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">sentence = input()
words = sentence.split()[::-1]
result = " ".join(words).title()
print(result)</pre>
</div>
""",
    },
    {
        "id": 391,
        "old": '<p>양의 정수가 입력되면 이진수 문자열(0b 제외)로 변환해 출력하세요.</p>',
        "problem_text": '양의 정수가 입력되면 이진수 문자열(0b 제외)로 변환해 출력하세요.',
        "marker": '10진수를 2진수로 변환하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 10진수를 2진수로 변환하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬 내장 함수 <code>bin(n)</code>은 "0b1010"처럼 앞에 0b가 붙은 문자열을 줘요. 이 2글자를 떼려면 <code>bin(n)[2:]</code>로 슬라이싱하면 돼요. 직접 구현하려면 2로 나눈 나머지를 계속 모아 뒤집는 방법도 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
print(bin(n)[2:])</pre>
</div>
""",
    },
    {
        "id": 392,
        "old": '<p>이름과 점수가 공백으로 구분된 줄이 여러 개 입력됩니다. END가 나오면 평균 이상 점수를 받은 학생 이름을 입력 순으로 출력하세요.</p>',
        "problem_text": '이름과 점수가 공백으로 구분된 줄이 여러 개 입력됩니다. END가 나오면 평균 이상 점수를 받은 학생 이름을 입력 순으로 출력하세요.',
        "marker": '객체를 리스트에 모아 여러 명 관리하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">👥 객체를 리스트에 모아 여러 명 관리하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">학생 한 명을 객체로 표현하고, 여러 명을 리스트에 계속 추가(<code>append</code>)해 관리할 수 있어요. 모든 입력이 끝난 뒤, 리스트를 순회하면서 조건(평균 이상 점수)을 만족하는 객체만 걸러 출력하면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

students = []
while True:
    line = input()
    if line == "END":
        break
    name, score = line.split()
    students.append(Student(name, int(score)))

avg = sum(s.score for s in students) / len(students)
for s in students:
    if s.score >= avg:
        print(s.name)</pre>
</div>
""",
    },
    {
        "id": 393,
        "old": '<p>정수 n이 입력되면 2부터 n까지의 소수를 한 줄에 하나씩 출력하세요.</p>',
        "problem_text": '정수 n이 입력되면 2부터 n까지의 소수를 한 줄에 하나씩 출력하세요.',
        "marker": '소수(prime) 판별하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 소수(prime) 판별하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">소수는 "1과 자기 자신 외에는 나누어지지 않는 수"예요. 어떤 수 x가 소수인지 확인하려면, 2부터 x-1까지(또는 더 빠르게 <code>int(x**0.5)</code>까지) 나누어보면서 나누어지는 수가 있으면 소수가 아니에요. 이걸 2부터 n까지 모든 수에 적용하면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def is_prime(x):
    if x < 2:
        return False
    for i in range(2, int(x ** 0.5) + 1):
        if x % i == 0:
            return False
    return True

n = int(input())
for i in range(2, n + 1):
    if is_prime(i):
        print(i)</pre>
</div>
""",
    },
    {
        "id": 394,
        "old": '<p>영문 소문자 문자열이 입력됩니다. 각 문자를 알파벳 순서에서 3칸 뒤 문자로 바꿔 출력하세요. z를 넘으면 a로 돌아오세요.</p>',
        "problem_text": '영문 소문자 문자열이 입력됩니다. 각 문자를 알파벳 순서에서 3칸 뒤 문자로 바꿔 출력하세요. z를 넘으면 a로 돌아오세요.',
        "marker": '문자 치환 암호화 - 카이사르 암호(Caesar Cipher)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔒 문자 치환 암호화 - 카이사르 암호(Caesar Cipher)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">각 문자를 알파벳에서 일정한 칸수만큼 뒤로 미는 암호를 카이사르 암호라고 해요. 'z'를 넘어가면 다시 'a'로 돌아와야 하는데, 이럴 때 나머지 연산(<code>% 26</code>)을 쓰면 자동으로 순환시켜줘요. <code>ord()</code>로 문자를 숫자로, <code>chr()</code>로 숫자를 다시 문자로 바꿔요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
result = ""
for ch in s:
    shifted = (ord(ch) - ord('a') + 3) % 26
    result += chr(shifted + ord('a'))
print(result)</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 10장(실전 모의고사 2) 문항 10건에 개념 설명 카드를 추가합니다."

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
