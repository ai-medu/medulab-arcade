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
        "id": 255,
        "old": "<p>정수 두 개가 입력되면 add(a, b) 함수를 이용해 합을 출력하세요.</p>",
        "problem_text": "정수 두 개가 입력되면 add(a, b) 함수를 이용해 합을 출력하세요.",
        "marker": "함수(def)와 return이란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧰 함수(def)와 return이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">함수는 "자주 쓰는 작업을 담아두는 도구 상자"예요. 한 번 만들어두면 이름만 불러서(호출해서) 여러 번 다시 쓸 수 있어요. <code>def 함수이름(매개변수):</code>로 함수를 만들고, 함수 안에서 <code>return</code>으로 결과를 바깥으로 돌려줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def add(a, b):      # add라는 이름의 함수 정의 (a, b는 매개변수)
    return a + b      # 계산 결과를 돌려줌(return)

a, b = map(int, input().split())
print(add(a, b))     # 함수를 호출 → 반환값이 그 자리에 들어감</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 함수 안에서 쓰는 매개변수 이름(a, b)은 함수 밖의 변수와 이름이 같아도 서로 영향을 주지 않아요. return이 없으면 함수는 계산은 하지만 결과를 알려주지 않아요.</p>
</div>
""",
    },
    {
        "id": 274,
        "old": "<p>정수 n이 입력되면 1단부터 n단까지 각 단의 결과를 한 줄에 하나씩 출력하세요. 형식: 단×배수=결과</p>",
        "problem_text": "정수 n이 입력되면 1단부터 n단까지 각 단의 결과를 한 줄에 하나씩 출력하세요. 형식: 단×배수=결과",
        "marker": "중첩 반복문(for문 안의 for문)",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔁🔁 중첩 반복문(for문 안의 for문)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">구구단표처럼 "여러 단"을 반복하면서, 각 단마다 또 "1부터 9까지"를 반복해야 하는 경우가 있어요. 이럴 때는 반복문 안에 또 다른 반복문을 넣는 <strong>중첩 반복문</strong>을 써요. 바깥쪽 for문이 한 번 돌 때마다, 안쪽 for문이 처음부터 끝까지 전부 실행돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
for i in range(1, n + 1):       # 바깥: 몇 단인지
    for j in range(1, 10):      # 안쪽: 1부터 9까지 배수
        print(f'{i}x{j}={i*j}')</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 안쪽 for문은 반드시 바깥쪽 for문보다 한 단계 더 들여쓰기 되어 있어야 해요.</p>
</div>
""",
    },
    {
        "id": 276,
        "old": "<p>정수 두 개가 입력되면 두 수의 차의 절댓값을 출력하세요.</p>",
        "problem_text": "정수 두 개가 입력되면 두 수의 차의 절댓값을 출력하세요.",
        "marker": "abs() 함수로 절댓값 구하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➖ abs() 함수로 절댓값 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">절댓값은 숫자의 "부호를 빼고 생각한 크기"예요. -3의 절댓값도 3, 3의 절댓값도 3이죠. if문으로 "음수면 -1을 곱한다"라고 직접 구할 수도 있지만, 파이썬 내장 함수 <code>abs(값)</code>을 쓰면 한 번에 절댓값을 구할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
print(abs(a - b))   # a-b가 음수여도 양수로 바꿔서 출력</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 7장(함수 기초) 및 모의고사1 문항에 부족한 개념 설명(def/return, 중첩 for문, abs)을 추가합니다."

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
