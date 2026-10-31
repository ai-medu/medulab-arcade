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
        "id": 856,
        "old": "<div class='problem-box'><h3>[문제1] 문자열 자르기</h3><p>문자열 \"PythonStudy\"에서 \"Study\"만 출력하세요.</p></div>",
        "problem_title": "[문제1] 문자열 자르기",
        "problem_text": "문자열 \"PythonStudy\"에서 \"Study\"만 출력하세요.",
        "marker": "슬라이싱(slicing)",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✂️ 문자열 슬라이싱(slicing)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">긴 김밥을 원하는 부분만 칼로 잘라내는 것처럼, 문자열도 원하는 부분만 "잘라서" 꺼낼 수 있어요. 이걸 <strong>슬라이싱</strong>이라고 하고, <code>문자열[시작:끝]</code> 형태로 써요. 문자열은 맨 앞 글자부터 번호(인덱스)가 0부터 시작해요.</p>
<table class="jz-table">
  <tr><th>인덱스</th><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td></tr>
  <tr><th>글자</th><td>P</td><td>y</td><td>t</td><td>h</td><td>o</td><td>n</td><td>S</td><td>t</td><td>u</td><td>d</td><td>y</td></tr>
</table>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">word = "PythonStudy"
print(word[6:])   # 6번 인덱스부터 끝까지 → "Study"
print(word[:6])   # 처음부터 6번 인덱스 전까지 → "Python"</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>[6:]</code>처럼 끝 번호를 생략하면 "끝까지"라는 뜻이에요.</p>
</div>
""",
    },
    {
        "id": 857,
        "old": "<div class='problem-box'><h3>[문제2] 이름 대문자 출력</h3><p>입력받은 이름을 모두 대문자로 출력하세요.</p></div>",
        "problem_title": "[문제2] 이름 대문자 출력",
        "problem_text": "입력받은 이름을 모두 대문자로 출력하세요.",
        "marker": "upper()",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔠 문자열 메서드 upper()</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열은 자기만의 "특기 기술"들을 가지고 있는데, 이걸 <strong>메서드</strong>라고 불러요. <code>.upper()</code>는 문자열에 붙여 쓰면 모든 글자를 대문자로 바꿔주는 메서드예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">name = input()
print(name.upper())  # chulsoo → CHULSOO</pre>
</div>
""",
    },
    {
        "id": 858,
        "old": "<div class='problem-box'><h3>[문제3] 자기소개 출력</h3><p>이름과 학년을 입력받아 포매팅으로 출력하세요.</p></div>",
        "problem_title": "[문제3] 자기소개 출력",
        "problem_text": "이름과 학년을 입력받아 포매팅으로 출력하세요.",
        "marker": "f-string",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧵 f-string으로 문자열 꾸미기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">변수와 글자를 매번 <code>+</code>로 이어 붙이면 번거롭죠. <strong>f-string</strong>을 쓰면 문자열 앞에 <code>f</code>를 붙이고, 변수를 <code>{ }</code> 안에 넣어서 훨씬 쉽게 문장을 만들 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">name = input()
grade = input()
print(f"{name}은 {grade}학년입니다")
# 철수, 6 을 입력하면 → 철수은 6학년입니다</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>f"..."</code>처럼 문자열 앞에 꼭 <code>f</code>를 붙여야 <code>{ }</code> 안의 변수가 값으로 바뀌어요.</p>
</div>
""",
    },
    {
        "id": 870,
        "old": "<div class='problem-box'><h3>[문제2] 리스트 값 추가</h3><p>빈 리스트에 숫자 5를 추가하고 출력하세요.</p></div>",
        "problem_title": "[문제2] 리스트 값 추가",
        "problem_text": "빈 리스트에 숫자 5를 추가하고 출력하세요.",
        "marker": "append()",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➕ 리스트에 값 추가하기: append()</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">빈 가방에 물건을 하나씩 넣는 것처럼, 리스트에 값을 추가할 때는 <code>.append(값)</code>을 사용해요. 리스트의 맨 뒤에 값이 쌓여요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">arr = []          # 빈 리스트(빈 가방)
arr.append(5)     # 가방에 5를 넣음
print(arr)         # [5] 출력</pre>
</div>
""",
    },
    {
        "id": 871,
        "old": "<div class='problem-box'><h3>[문제3] 딕셔너리 만들기</h3><p>이름과 학교를 저장하는 딕셔너리를 만들어 출력하세요.</p></div>",
        "problem_title": "[문제3] 딕셔너리 만들기",
        "problem_text": "이름과 학교를 저장하는 딕셔너리를 만들어 출력하세요.",
        "marker": "딕셔너리(dictionary)",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📖 딕셔너리(dictionary)란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">진짜 사전을 생각해보세요. "단어(key)"를 찾으면 그 "설명(value)"이 나오죠. 파이썬의 <strong>딕셔너리</strong>도 똑같아요. <code>key:value</code> 짝을 <code>{ }</code> 안에 넣어서 만들어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">info = {"이름": "영희", "학교": "초등학교"}
print(info)
# {'이름': '영희', '학교': '초등학교'}</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 리스트는 순서(번호)로 값을 찾지만, 딕셔너리는 이름(key)으로 값을 찾아요.</p>
</div>
""",
    },
    {
        "id": 872,
        "old": "<div class='problem-box'><h3>[문제4] 딕셔너리 값 출력</h3><p>딕셔너리에서 나이 값을 출력하세요.</p></div>",
        "problem_title": "[문제4] 딕셔너리 값 출력",
        "problem_text": "딕셔너리에서 나이 값을 출력하세요.",
        "marker": "key로 value 꺼내기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔑 key로 value 꺼내기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">딕셔너리에서 원하는 값을 꺼낼 때는 <code>딕셔너리[key]</code> 형태로 key를 대괄호 안에 적어요. 사전에서 단어를 찾듯이, key를 알면 바로 그 value를 꺼낼 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">info = {"이름": "민수", "나이": 12}
print(info["나이"])   # key "나이"로 value 12를 꺼냄</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "파이썬기본과정 문제 문항(5~6장)에 부족한 개념 설명(슬라이싱, upper(), f-string, append(), 딕셔너리)을 추가합니다."

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
