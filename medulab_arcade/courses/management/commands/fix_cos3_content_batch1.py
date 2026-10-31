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
        "id": 205,
        "old": "<p>한 줄에 정수 두 개가 공백으로 입력됩니다. 두 수의 합을 출력하세요.</p>",
        "problem_text": "한 줄에 정수 두 개가 공백으로 입력됩니다. 두 수의 합을 출력하세요.",
        "marker": "한 줄에 값 여러 개 입력받기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📥 한 줄에 값 여러 개 입력받기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">지금까지는 <code>input()</code>으로 한 번에 값 하나만 받았죠. 그런데 "3 5"처럼 한 줄에 숫자가 공백으로 여러 개 적혀 있다면 어떻게 나눠 받을까요? <code>split()</code>을 쓰면 공백을 기준으로 글자를 잘라 리스트로 만들어줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">input().split()
# "3 5" 를 입력하면 ['3', '5'] 가 됩니다 (아직 글자 상태)</pre>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔧 map(int, ...)로 한꺼번에 숫자로 바꾸기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>split()</code>으로 나눈 값들은 아직 글자(문자열)예요. 하나씩 <code>int()</code>로 바꾸는 대신, <code>map(int, 리스트)</code>를 쓰면 리스트 안의 모든 값을 한꺼번에 숫자로 바꿀 수 있어요. 그리고 <code>a, b = ...</code> 형태로 쓰면 바뀐 두 값을 각각의 변수에 바로 나눠 담을 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
print(a + b)   # 두 숫자를 진짜 숫자로 받아 더함</pre>
</div>
""",
    },
    {
        "id": 208,
        "old": "<p>한 줄에 정수 두 개가 입력됩니다. 첫 번째를 두 번째로 나눈 몫과 나머지를 공백으로 구분해 출력하세요.</p>",
        "problem_text": "한 줄에 정수 두 개가 입력됩니다. 첫 번째를 두 번째로 나눈 몫과 나머지를 공백으로 구분해 출력하세요.",
        "marker": "몫(//)과 나머지(%) 연산자",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🍬 몫(//)과 나머지(%) 연산자</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">사탕 7개를 2명에게 나눠주면, 한 명당 3개씩 받고 1개가 남죠. 여기서 "3개씩"이 <strong>몫</strong>, "1개 남음"이 <strong>나머지</strong>예요. 파이썬에서는 <code>//</code>가 몫, <code>%</code>가 나머지를 구해줘요.</p>
<table class="jz-table">
  <tr><th>연산</th><th>의미</th><th>예시</th><th>결과</th></tr>
  <tr><td><code>a // b</code></td><td>나눈 몫(소수점 버림)</td><td><code>7 // 2</code></td><td>3</td></tr>
  <tr><td><code>a % b</code></td><td>나누고 남은 나머지</td><td><code>7 % 2</code></td><td>1</td></tr>
</table>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
print(a // b, a % b)</pre>
</div>
""",
    },
    {
        "id": 209,
        "old": "<p>섭씨 온도가 입력되면 화씨 온도를 소수 첫째 자리까지 출력하세요. (공식: F = C × 9/5 + 32)</p>",
        "problem_text": "섭씨 온도가 입력되면 화씨 온도를 소수 첫째 자리까지 출력하세요. (공식: F = C × 9/5 + 32)",
        "marker": "round() 함수로 소수점 반올림",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 round() 함수로 소수점 반올림하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">계산 결과가 3.14159265... 처럼 소수점이 아주 길게 나올 때, "소수 몇째 자리까지만 보여줘"라고 정리하고 싶을 수 있어요. 이때 <code>round(값, 자리수)</code>를 사용해요. 돈 계산할 때 원 단위로 반올림하는 것과 같은 개념이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">print(round(3.14159, 1))   # 3.1  (소수 첫째 자리까지)
print(round(3.14159, 2))   # 3.14 (소수 둘째 자리까지)</pre>
</div>
""",
    },
    {
        "id": 214,
        "old": "<p>두 자리 정수가 입력되면 십의 자리와 일의 자리의 합을 출력하세요.</p>",
        "problem_text": "두 자리 정수가 입력되면 십의 자리와 일의 자리의 합을 출력하세요.",
        "marker": "문자열 인덱싱(글자 하나씩 꺼내기)",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔤 문자열 인덱싱(글자 하나씩 꺼내기)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열은 글자들이 순서대로 쭉 늘어선 줄이에요. 각 글자에는 앞에서부터 0, 1, 2... 순서로 번호(<strong>인덱스</strong>)가 붙어있어요. <code>문자열[번호]</code> 형태로 원하는 위치의 글자 하나를 꺼낼 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = "25"
print(n[0])  # '2'  (0번째 글자, 십의 자리)
print(n[1])  # '5'  (1번째 글자, 일의 자리)</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 이렇게 꺼낸 글자는 아직 "글자"이기 때문에, 숫자로 더하려면 <code>int()</code>로 바꿔줘야 해요. 예: <code>int(n[0]) + int(n[1])</code></p>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 1~2장 문항에 부족한 개념 설명(다중 입력, //와 %, round, 문자열 인덱싱)을 추가합니다."

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
