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
        "id": 305,
        "old": '<p>단어 여러 개가 한 줄에 입력됩니다. 각 단어가 몇 번 나오는지 단어:횟수 형식으로 입력 순서에 따라 출력하세요.</p>',
        "problem_text": '단어 여러 개가 한 줄에 입력됩니다. 각 단어가 몇 번 나오는지 단어:횟수 형식으로 입력 순서에 따라 출력하세요.',
        "marker": '딕셔너리로 개수 세기(빈도수 세기 패턴)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📊 딕셔너리로 개수 세기(빈도수 세기 패턴)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">같은 단어가 몇 번 나왔는지 세려면, "단어를 키(key), 등장 횟수를 값(value)"으로 하는 딕셔너리를 만들면 돼요. 단어가 이미 딕셔너리에 있으면 값을 1 늘리고, 없으면 1로 새로 등록하는 패턴을 자주 써요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">words = input().split()
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1
for w, c in count.items():
    print(f"{w}:{c}")</pre>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 <code>count.get(w, 0)</code>은 "w라는 키가 있으면 그 값을, 없으면 기본값 0을 가져와라"는 뜻이에요. 키가 없을 때 에러가 나는 것을 막아줘요.</p>
</div>
""",
    },
    {
        "id": 306,
        "old": '<p>딕셔너리 형태로 이름:점수 쌍이 여러 줄 입력됩니다. 점수가 가장 높은 이름을 출력하세요. 입력의 마지막은 END 입니다.</p>',
        "problem_text": '딕셔너리 형태로 이름:점수 쌍이 여러 줄 입력됩니다. 점수가 가장 높은 이름을 출력하세요. 입력의 마지막은 END 입니다.',
        "marker": '딕셔너리에서 값이 최대인 키 찾기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🏆 딕셔너리에서 값이 최대인 키 찾기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">딕셔너리에서 "값이 가장 큰 항목의 키"를 찾고 싶을 때는 <code>max()</code> 함수에 <code>key=딕셔너리.get</code>을 넘기면 돼요. max는 기본적으로 키들만 비교하는데, key 옵션으로 "비교 기준을 값으로 바꿔라"고 알려주는 거예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">scores = {}
while True:
    line = input()
    if line == "END":
        break
    name, score = line.split()
    scores[name] = int(score)
print(max(scores, key=scores.get))</pre>
</div>
""",
    },
    {
        "id": 307,
        "old": '<p>두 줄에 각각 key:value 쌍이 콤마로 구분되어 입력됩니다. 두 딕셔너리를 합쳐 key를 오름차순으로 정렬해 출력하세요.</p>',
        "problem_text": '두 줄에 각각 key:value 쌍이 콤마로 구분되어 입력됩니다. 두 딕셔너리를 합쳐 key를 오름차순으로 정렬해 출력하세요.',
        "marker": '딕셔너리 병합하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔀 딕셔너리 병합하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 딕셔너리를 하나로 합치고 싶을 때는 <code>{**d1, **d2}</code> 문법이나 <code>update()</code> 메서드를 써요. 같은 키가 양쪽에 있으면 뒤쪽(d2) 값으로 덮어써진다는 점을 기억하세요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">d1 = dict(kv.split(":") for kv in input().split(","))
d2 = dict(kv.split(":") for kv in input().split(","))
merged = {**d1, **d2}
for k in sorted(merged):
    print(f"{k}:{merged[k]}")</pre>
</div>
""",
    },
    {
        "id": 308,
        "old": '<p>두 줄에 각각 정수 여러 개가 입력됩니다. 합집합, 교집합, 차집합(첫째-둘째)을 각각 정렬해 출력하세요.</p>',
        "problem_text": '두 줄에 각각 정수 여러 개가 입력됩니다. 합집합, 교집합, 차집합(첫째-둘째)을 각각 정렬해 출력하세요.',
        "marker": '집합(set) 연산: 합집합·교집합·차집합',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔴🔵 집합(set) 연산: 합집합·교집합·차집합</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">집합은 벤 다이어그램을 떠올리면 쉬워요. 파이썬은 연산자로 바로 집합 연산을 할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = set(map(int, input().split()))
b = set(map(int, input().split()))
print(*sorted(a | b))   # 합집합
print(*sorted(a & b))   # 교집합
print(*sorted(a - b))   # 차집합(a에만 있는 것)</pre>
</div>
""",
    },
    {
        "id": 309,
        "old": '<p>이름과 점수가 공백으로 구분된 줄이 여러 개 입력됩니다. 마지막 줄은 END 입니다. 모든 학생의 평균 점수를 소수 첫째 자리로 출력하세요.</p>',
        "problem_text": '이름과 점수가 공백으로 구분된 줄이 여러 개 입력됩니다. 마지막 줄은 END 입니다. 모든 학생의 평균 점수를 소수 첫째 자리로 출력하세요.',
        "marker": '딕셔너리 없이도 평균은 리스트 누적으로',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📈 딕셔너리 없이도 평균은 리스트 누적으로</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">여러 줄의 "이름 점수" 데이터를 받을 때는, 점수만 리스트에 계속 추가(append)해두고, 입력이 끝나면 <code>sum(리스트) / len(리스트)</code>로 평균을 구하면 돼요. 소수 첫째 자리까지는 <code>round(값, 1)</code>로 맞춰요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">scores = []
while True:
    line = input()
    if line == "END":
        break
    name, score = line.split()
    scores.append(int(score))
print(round(sum(scores) / len(scores), 1))</pre>
</div>
""",
    },
    {
        "id": 310,
        "old": '<p>문자열이 입력되면 서로 다른 문자의 수를 출력하세요.</p>',
        "problem_text": '문자열이 입력되면 서로 다른 문자의 수를 출력하세요.',
        "marker": 'set으로 서로 다른 문자 개수 세기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 set으로 서로 다른 문자 개수 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">문자열에서 "서로 다른 문자가 몇 개인지"는 중복을 없애야 세기 쉬워요. 문자열을 <code>set()</code>으로 바꾸면 같은 문자는 한 번만 남기 때문에, 그 집합의 길이(<code>len()</code>)가 바로 서로 다른 문자의 개수가 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
print(len(set(s)))</pre>
</div>
""",
    },
    {
        "id": 311,
        "old": '<p>첫 줄에 초기 재고(상품명:수량, 콤마 구분), 둘째 줄에 판매 상품명이 입력됩니다. 판매 후 해당 상품 수량을 1 줄이고 출력하세요. 없으면 없음을 출력하세요.</p>',
        "problem_text": '첫 줄에 초기 재고(상품명:수량, 콤마 구분), 둘째 줄에 판매 상품명이 입력됩니다. 판매 후 해당 상품 수량을 1 줄이고 출력하세요. 없으면 없음을 출력하세요.',
        "marker": '딕셔너리에 키가 있는지 확인하기 (in 연산자)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">❓ 딕셔너리에 키가 있는지 확인하기 (in 연산자)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">딕셔너리에 특정 키가 있는지 확인할 때는 <code>키 in 딕셔너리</code> 형태로 물어보면 돼요(True/False로 답해줘요). 있으면 값을 바꾸고, 없으면 "없음" 같은 메시지를 출력하는 패턴이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">stock = dict(kv.split(":") for kv in input().split(","))
stock = {k: int(v) for k, v in stock.items()}
item = input()
if item in stock:
    stock[item] -= 1
    print(f"{item}:{stock[item]}")
else:
    print("없음")</pre>
</div>
""",
    },
    {
        "id": 312,
        "old": '<p>두 줄에 각각 정수 여러 개가 입력됩니다. 두 집합이 같으면 SAME, 다르면 DIFFERENT를 출력하세요.</p>',
        "problem_text": '두 줄에 각각 정수 여러 개가 입력됩니다. 두 집합이 같으면 SAME, 다르면 DIFFERENT를 출력하세요.',
        "marker": '두 집합이 같은지 비교하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⚖️ 두 집합이 같은지 비교하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">두 리스트에 같은 값들이 들어있는지(순서는 상관없이) 확인하려면, 각각 <code>set()</code>으로 바꿔서 <code>==</code>로 비교하면 돼요. 집합은 순서를 따지지 않고 "어떤 값들이 들어있는가"만 비교하기 때문이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a = set(map(int, input().split()))
b = set(map(int, input().split()))
print("SAME" if a == b else "DIFFERENT")</pre>
</div>
""",
    },
    {
        "id": 313,
        "old": '<p>이름:점수 쌍 여러 개가 콤마로 구분되어 입력됩니다. 점수 높은 순으로 이름만 한 줄씩 출력하세요.</p>',
        "problem_text": '이름:점수 쌍 여러 개가 콤마로 구분되어 입력됩니다. 점수 높은 순으로 이름만 한 줄씩 출력하세요.',
        "marker": '딕셔너리 정렬: 값 기준으로 내림차순 정렬',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 딕셔너리 정렬: 값 기준으로 내림차순 정렬</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">딕셔너리의 (키, 값) 쌍들을 값 기준으로 정렬하려면 <code>sorted()</code>에 <code>key=</code>로 "무엇을 기준으로 비교할지"를 람다 함수로 알려주면 돼요. 내림차순으로 하려면 <code>reverse=True</code>를 추가해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">pairs = [kv.split(":") for kv in input().split(",")]
pairs = [(name, int(score)) for name, score in pairs]
for name, score in sorted(pairs, key=lambda x: x[1], reverse=True):
    print(name)</pre>
</div>
""",
    },
    {
        "id": 314,
        "old": '<p>키 목록과 값 목록이 한 줄씩 입력됩니다. 두 리스트를 묶어 딕셔너리로 만든 뒤 키 오름차순으로 출력하세요.</p>',
        "problem_text": '키 목록과 값 목록이 한 줄씩 입력됩니다. 두 리스트를 묶어 딕셔너리로 만든 뒤 키 오름차순으로 출력하세요.',
        "marker": 'zip과 dict()로 두 리스트를 딕셔너리로 합치기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔗 zip과 dict()로 두 리스트를 딕셔너리로 합치기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">키 목록과 값 목록이 따로 있을 때, 같은 자리끼리 짝지어주는 <code>zip()</code>을 <code>dict()</code>로 감싸면 바로 딕셔너리가 만들어져요. <code>dict(zip(키리스트, 값리스트))</code> 형태를 기억해두면 아주 자주 쓰여요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">keys = input().split()
values = input().split()
d = dict(zip(keys, values))
for k in sorted(d):
    print(f"{k}:{d[k]}")</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 2장(딕셔너리와 집합 심화) 문항 10건에 개념 설명 카드를 추가합니다."

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
