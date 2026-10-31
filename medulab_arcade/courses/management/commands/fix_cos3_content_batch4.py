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
        "id": 245,
        "old": "<p>한 줄에 정수 다섯 개가 입력됩니다. 합계를 출력하세요.</p>",
        "problem_text": "한 줄에 정수 다섯 개가 입력됩니다. 합계를 출력하세요.",
        "marker": "리스트(list)란 무엇인가",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📦 리스트(list)란 무엇인가?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">변수 하나에 값 하나씩만 담는 대신, 여러 개의 값을 한 번에 담는 "장바구니" 같은 그릇이 <strong>리스트</strong>예요. <code>map(int, 입력.split())</code>의 결과를 <code>list()</code>로 감싸면, 입력받은 숫자들을 리스트 하나에 모두 담을 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
print(nums)        # [1, 2, 3, 4, 5] 처럼 리스트로 저장됨</pre>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➕ sum() 함수로 리스트 전체 합 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트 안의 모든 값을 반복문으로 하나씩 더할 수도 있지만, <code>sum(리스트)</code>를 쓰면 한 번에 전체 합을 구해줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">print(sum(nums))   # 리스트 안 값들의 합계</pre>
</div>
""",
    },
    {
        "id": 248,
        "old": "<p>한 줄에 정수 네 개가 입력됩니다. 오름차순으로 정렬해 공백으로 구분해 출력하세요.</p>",
        "problem_text": "한 줄에 정수 네 개가 입력됩니다. 오름차순으로 정렬해 공백으로 구분해 출력하세요.",
        "marker": "sort() 메서드로 리스트 정렬하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📶 sort() 메서드로 리스트 정렬하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트 안의 값을 작은 수부터 큰 수(오름차순) 순서로 정리하고 싶을 때, <code>리스트.sort()</code>를 호출하면 리스트 "그 자체"가 정렬된 순서로 바뀌어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = [3, 1, 4, 2]
nums.sort()
print(nums)   # [1, 2, 3, 4]</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>print(*리스트)</code>처럼 리스트 앞에 <code>*</code>를 붙이면, 리스트의 값들을 대괄호 없이 공백으로 구분해서 출력할 수 있어요.</p>
</div>
""",
    },
    {
        "id": 249,
        "old": "<p>한 줄에 단어 네 개가 입력됩니다. 순서를 뒤집어 공백으로 구분해 출력하세요.</p>",
        "problem_text": "한 줄에 단어 네 개가 입력됩니다. 순서를 뒤집어 공백으로 구분해 출력하세요.",
        "marker": "reverse() 메서드로 리스트 순서 뒤집기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 reverse() 메서드로 리스트 순서 뒤집기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열을 뒤집을 때 <code>[::-1]</code> 슬라이싱을 썼던 것처럼, 리스트도 순서를 뒤집을 수 있어요. <code>리스트.reverse()</code>를 호출하면 리스트 안의 순서가 그대로 거꾸로 바뀌어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = ['apple', 'banana', 'cherry']
words.reverse()
print(*words)   # cherry banana apple</pre>
</div>
""",
    },
    {
        "id": 252,
        "old": "<p>첫 줄에 정수 다섯 개, 둘째 줄에 정수 한 개가 입력됩니다. 해당 정수가 리스트에 있으면 YES, 없으면 NO를 출력하세요.</p>",
        "problem_text": "첫 줄에 정수 다섯 개, 둘째 줄에 정수 한 개가 입력됩니다. 해당 정수가 리스트에 있으면 YES, 없으면 NO를 출력하세요.",
        "marker": "in 연산자로 포함 여부 확인하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔍 in 연산자로 포함 여부 확인하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">어떤 값이 리스트 안에 있는지 없는지 확인할 때, 반복문으로 하나씩 비교할 필요 없이 <code>값 in 리스트</code>라고 쓰면 바로 True/False로 알려줘요. 글자 하나가 문자열에 포함되어 있는지 확인할 때도 똑같이 쓸 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = [1, 2, 3, 4, 5]
print(3 in nums)    # True
print(9 in nums)    # False</pre>
</div>
""",
    },
    {
        "id": 253,
        "old": "<p>한 줄에 정수 다섯 개가 입력됩니다. 마지막 값을 제거하고 남은 리스트의 길이를 출력하세요.</p>",
        "problem_text": "한 줄에 정수 다섯 개가 입력됩니다. 마지막 값을 제거하고 남은 리스트의 길이를 출력하세요.",
        "marker": "pop() 메서드로 리스트에서 값 제거하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🗑️ pop() 메서드로 리스트에서 값 제거하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>리스트.pop()</code>을 호출하면 리스트의 맨 마지막 값을 꺼내서 제거해요. 괄호 안에 인덱스를 넣으면 그 위치의 값을 제거할 수도 있어요. 값을 제거하고 나면 리스트의 길이(개수)도 하나 줄어들어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = [1, 2, 3, 4, 5]
nums.pop()          # 마지막 값 5를 제거
print(nums)          # [1, 2, 3, 4]
print(len(nums))     # 4</pre>
</div>
""",
    },
    {
        "id": 254,
        "old": "<p>첫 줄에 정수 세 개, 둘째 줄에 정수 한 개가 입력됩니다. 둘째 줄 정수를 리스트에 추가한 뒤 합계를 출력하세요.</p>",
        "problem_text": "첫 줄에 정수 세 개, 둘째 줄에 정수 한 개가 입력됩니다. 둘째 줄 정수를 리스트에 추가한 뒤 합계를 출력하세요.",
        "marker": "append() 메서드로 리스트에 값 추가하기",
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➕ append() 메서드로 리스트에 값 추가하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">장바구니(리스트)에 물건을 하나 더 담듯, <code>리스트.append(값)</code>을 호출하면 그 값이 리스트의 맨 뒤에 새로 추가돼요. pop()이 마지막 값을 "빼는" 것이라면, append()는 마지막에 값을 "넣는" 것이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = [1, 2, 3]
nums.append(4)
print(nums)          # [1, 2, 3, 4]
print(sum(nums))      # 10</pre>
</div>
""",
    },
]


class Command(BaseCommand):
    help = "COS Pro 3급 대비 6장(리스트 기초) 문항에 부족한 개념 설명(리스트, sum, sort, reverse, in, pop, append)을 추가합니다."

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
