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
        "id": 235,
        "old": "<p>문자열이 입력되면 글자 수를 출력하세요.</p>",
        "problem_text": "문자열이 입력되면 글자 수를 출력하세요.",
        "marker": "len() 함수로 길이 구하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📏 len() 함수로 길이 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">줄자로 물건 길이를 재는 것처럼, 문자열이 몇 글자인지 세어주는 함수가 <code>len()</code>이에요. 문자열뿐 아니라 뒤에서 배울 리스트의 "개수"를 셀 때도 똑같이 쓸 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
print(len(s))   # 글자 개수를 출력</pre>
</div>
""",
    },
    {
        "id": 236,
        "old": "<p>영문 문자열이 입력되면 모두 대문자로 출력하세요.</p>",
        "problem_text": "영문 문자열이 입력되면 모두 대문자로 출력하세요.",
        "marker": "문자열 메서드란",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧰 문자열 메서드란? (upper/lower)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열은 <code>변수.기능이름()</code> 형태로 자기 자신에게 쓸 수 있는 전용 기능들을 갖고 있어요. 이런 기능을 <strong>메서드</strong>라고 불러요. <code>upper()</code>는 전부 대문자로, <code>lower()</code>는 전부 소문자로 바꿔서 "새로운" 문자열을 돌려줘요(원본은 바뀌지 않아요).</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "Hello"
print(s.upper())   # 'HELLO'
print(s.lower())   # 'hello'</pre>
</div>
""",
    },
    {
        "id": 238,
        "old": "<p>문자열이 입력되면 뒤집어 출력하세요.</p>",
        "problem_text": "문자열이 입력되면 뒤집어 출력하세요.",
        "marker": "슬라이싱([::-1])으로 문자열 뒤집기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✂️ 슬라이싱([::-1])으로 문자열 뒤집기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">인덱싱이 글자 "하나"를 꺼내는 거라면, <strong>슬라이싱</strong>은 문자열의 "구간"을 잘라내는 거예요. <code>문자열[시작:끝:간격]</code> 형태로 쓰는데, <code>[::-1]</code>은 시작과 끝을 비워두고 간격을 -1(거꾸로 한 칸씩)로 줘서 문자열 전체를 거꾸로 뒤집는 아주 유명한 표현이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "hello"
print(s[::-1])   # 'olleh' (거꾸로 뒤집힘)</pre>
</div>
""",
    },
    {
        "id": 239,
        "old": "<p>문장이 입력되면 공백을 모두 밑줄(_)로 바꿔 출력하세요.</p>",
        "problem_text": "문장이 입력되면 공백을 모두 밑줄(_)로 바꿔 출력하세요.",
        "marker": "replace() 메서드로 문자 바꾸기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔁 replace() 메서드로 문자 바꾸기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문서 작성 프로그램의 "찾아 바꾸기" 기능처럼, <code>replace(찾을 글자, 바꿀 글자)</code>를 쓰면 문자열 안의 특정 글자(들)를 전부 다른 글자로 바꿔서 새 문자열을 만들 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "hi there"
print(s.replace(' ', '_'))   # 'hi_there' (공백을 밑줄로 교체)</pre>
</div>
""",
    },
    {
        "id": 240,
        "old": "<p>첫 줄에 문장, 둘째 줄에 찾을 문자가 입력됩니다. 해당 문자의 개수를 출력하세요.</p>",
        "problem_text": "첫 줄에 문장, 둘째 줄에 찾을 문자가 입력됩니다. 해당 문자의 개수를 출력하세요.",
        "marker": "count() 메서드로 개수 세기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 count() 메서드로 개수 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열 안에 특정 글자나 단어가 몇 번 나오는지 직접 반복문으로 셀 수도 있지만, <code>count(찾을 문자)</code> 메서드를 쓰면 한 줄로 바로 구할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "banana"
print(s.count('a'))   # 3 ('a'가 3번 등장)</pre>
</div>
""",
    },
    {
        "id": 241,
        "old": "<p>문자열이 입력되면 첫 글자와 마지막 글자를 공백으로 구분해 출력하세요.</p>",
        "problem_text": "문자열이 입력되면 첫 글자와 마지막 글자를 공백으로 구분해 출력하세요.",
        "marker": "음수 인덱스로 끝에서부터 세기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">↩️ 음수 인덱스로 끝에서부터 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">인덱스는 앞에서부터 0, 1, 2...로 셀 수도 있지만, 뒤에서부터는 -1, -2, -3...으로 셀 수도 있어요. 마지막 글자는 항상 <code>[-1]</code>이에요. 문자열이 몇 글자인지 몰라도 마지막 글자를 바로 꺼낼 수 있어서 편해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "hello"
print(s[0])    # 'h'  (첫 글자)
print(s[-1])   # 'o'  (마지막 글자)</pre>
</div>
""",
    },
    {
        "id": 244,
        "old": '<p>문자열이 입력되면 양쪽에 큰따옴표를 붙여 출력하세요. 예: hello → &quot;hello&quot;</p>',
        "problem_text": '문자열이 입력되면 양쪽에 큰따옴표를 붙여 출력하세요. 예: hello → &quot;hello&quot;',
        "marker": "f-string으로 문자열에 값 끼워넣기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧵 f-string으로 문자열에 값 끼워넣기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열 중간에 변수 값을 끼워 넣고 싶을 때, <code>+</code>로 이어 붙이는 것보다 훨씬 편한 방법이 있어요. 문자열 앞에 <code>f</code>를 붙이고(<strong>f-string</strong>), 중괄호 <code>{ }</code> 안에 변수를 적으면 그 자리에 변수의 값이 그대로 들어가요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = "hello"
print(f'"{s}"')   # "hello"  (양옆에 큰따옴표가 붙어서 출력됨)</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 5장(문자열 처리) 문항에 부족한 개념 설명(len, upper/lower, 슬라이싱, replace, count, 음수 인덱스, f-string)을 추가합니다."

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
