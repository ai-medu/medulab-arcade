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
        "id": 881,
        "old": "<div class='problem-box'><h3>[문제1] 짝수 판별</h3><p>숫자를 입력받아 짝수인지 홀수인지 출력하세요.</p></div>",
        "problem_title": "[문제1] 짝수 판별",
        "problem_text": "숫자를 입력받아 짝수인지 홀수인지 출력하세요.",
        "marker": "나머지 연산자",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➗ 나머지 연산자 %로 짝수/홀수 판별하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">사탕을 2개씩 짝지어 나눠줄 때, 하나도 안 남으면 짝수, 하나가 남으면 홀수죠. 파이썬에서는 나눈 뒤 "남는 수(나머지)"를 구하는 <code>%</code> 연산자로 이걸 확인해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">num = int(input())
if num % 2 == 0:     # 2로 나눈 나머지가 0이면 짝수
    print("짝수")
else:
    print("홀수")</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>num % 2</code>는 num을 2로 나눈 나머지예요. 짝수는 항상 0, 홀수는 항상 1이 나와요.</p>
</div>
""",
    },
    {
        "id": 883,
        "old": "<div class='problem-box'><h3>[문제3] 학년 판별</h3><p>학년 숫자를 입력받아 저학년(1~3), 고학년(4~6)을 출력하세요.</p></div>",
        "problem_title": "[문제3] 학년 판별",
        "problem_text": "학년 숫자를 입력받아 저학년(1~3), 고학년(4~6)을 출력하세요.",
        "marker": "elif",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚦 if / elif / else로 여러 조건 나누기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">조건이 두 가지뿐이면 if-else로 충분하지만, 조건이 3개, 4개로 늘어나면 중간에 <code>elif</code>(else if의 줄임말)를 추가해서 더 세밀하게 나눌 수 있어요. 위에서부터 차례로 검사하다가 맞는 조건을 만나면 그 블록만 실행해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">grade = int(input())
if grade <= 3:
    print("저학년")
else:
    print("고학년")</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 이 문제는 조건이 두 가지(저학년/고학년)라 if-else로 충분하지만, 조건이 더 늘어나면 <code>elif</code>를 추가해서 "저학년 / 중학년 / 고학년"처럼 세 가지 이상으로도 나눌 수 있어요.</p>
</div>
""",
    },
    {
        "id": 894,
        "old": "<div class='problem-box'><h3>[문제1] 숫자 출력</h3><p>1부터 5까지 출력하세요.</p></div>",
        "problem_title": "[문제1] 숫자 출력",
        "problem_text": "1부터 5까지 출력하세요.",
        "marker": "range()",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔁 for문과 range()로 반복하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">같은 동작을 여러 번 해야 할 때, print()를 5번 쓰는 대신 <strong>for문</strong>으로 "반복"시킬 수 있어요. <code>range(시작, 끝)</code>은 시작 숫자부터 (끝-1) 숫자까지 순서대로 숫자를 만들어줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">for i in range(1, 6):   # 1, 2, 3, 4, 5 (6은 포함 안 됨!)
    print(i)</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>range(1, 6)</code>처럼 끝 숫자는 "포함되지 않는다"는 점을 꼭 기억하세요.</p>
</div>
""",
    },
    {
        "id": 896,
        "old": "<div class='problem-box'><h3>[문제3] while 반복</h3><p>while을 사용해 1부터 3까지 출력하세요.</p></div>",
        "problem_title": "[문제3] while 반복",
        "problem_text": "while을 사용해 1부터 3까지 출력하세요.",
        "marker": "while문",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 while문: 조건이 참인 동안 반복</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">for문은 "몇 번 반복할지" 정해져 있을 때 쓰지만, <strong>while문</strong>은 "조건이 참(True)인 동안" 계속 반복해요. 줄넘기를 "다리가 안 아픈 동안" 계속하는 것과 비슷해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">i = 1
while i <= 3:    # i가 3보다 작거나 같은 동안 계속 반복
    print(i)
    i += 1         # i를 1씩 늘려줌 (안 늘리면 무한 반복!)</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>i += 1</code>처럼 변수를 꼭 변화시켜야 해요. 안 그러면 조건이 영원히 참이 되어 무한 반복에 걸려요.</p>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "파이썬기본과정 문제 문항(7~8장)에 부족한 개념 설명(나머지 연산자, elif, range(), while문)을 추가합니다."

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
