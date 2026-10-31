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
        "id": 365,
        "old": '<p>문자열이 입력됩니다. 정수로 변환 가능하면 2배 값을, 불가능하면 오류를 출력하세요.</p>',
        "problem_text": '문자열이 입력됩니다. 정수로 변환 가능하면 2배 값을, 불가능하면 오류를 출력하세요.',
        "marker": 'try-except로 예외(에러) 다루기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⚠️ try-except로 예외(에러) 다루기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">프로그램이 실행되다가 문제가 생기면 "예외(exception)"가 발생하고, 그대로 두면 프로그램이 멈춰요. <code>try:</code> 블록 안에서 문제가 생길 수 있는 코드를 실행하고, 문제가 생기면 <code>except:</code> 블록이 실행돼서 프로그램이 멈추지 않고 원하는 처리를 할 수 있어요. 문자열을 숫자로 바꿀 수 없으면 <code>ValueError</code>가 발생해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s = input()
try:
    n = int(s)
    print(n * 2)
except ValueError:
    print("오류")</pre>
</div>
""",
    },
    {
        "id": 366,
        "old": '<p>두 정수가 입력됩니다. 두 번째가 0이면 0으로 나눌 수 없습니다를 출력하고, 아니면 나눗셈 결과를 출력하세요.</p>',
        "problem_text": '두 정수가 입력됩니다. 두 번째가 0이면 0으로 나눌 수 없습니다를 출력하고, 아니면 나눗셈 결과를 출력하세요.',
        "marker": '0으로 나누기 예외(ZeroDivisionError)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">➗ 0으로 나누기 예외(ZeroDivisionError)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">어떤 수를 0으로 나누면 수학적으로 정의되지 않으므로, 파이썬은 <code>ZeroDivisionError</code>를 발생시켜요. 나누기 전에 미리 "나누는 수가 0인지" 확인해서 분기해도 되고, try-except로 감싸도 돼요. 여기서는 미리 확인하는 방식이 더 명확해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
if b == 0:
    print("0으로 나눌 수 없습니다")
else:
    print(a / b)</pre>
</div>
""",
    },
    {
        "id": 367,
        "old": '<p>정수 여러 개와 인덱스가 한 줄씩 입력됩니다. 해당 인덱스의 값을 출력하고, 범위를 벗어나면 범위 오류를 출력하세요.</p>',
        "problem_text": '정수 여러 개와 인덱스가 한 줄씩 입력됩니다. 해당 인덱스의 값을 출력하고, 범위를 벗어나면 범위 오류를 출력하세요.',
        "marker": '리스트 인덱스 예외(IndexError)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📏 리스트 인덱스 예외(IndexError)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">리스트의 범위를 벗어난 인덱스에 접근하면 <code>IndexError</code>가 발생해요. try-except로 감싸면, 범위를 벗어났을 때 프로그램이 멈추지 않고 원하는 메시지를 출력할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">nums = list(map(int, input().split()))
idx = int(input())
try:
    print(nums[idx])
except IndexError:
    print("범위 오류")</pre>
</div>
""",
    },
    {
        "id": 368,
        "old": '<p>문자열과 인덱스가 한 줄씩 입력됩니다. 인덱스를 정수로 변환해 해당 문자를 출력하세요. 변환 오류면 변환오류, 범위 오류면 범위오류를 출력하세요.</p>',
        "problem_text": '문자열과 인덱스가 한 줄씩 입력됩니다. 인덱스를 정수로 변환해 해당 문자를 출력하세요. 변환 오류면 변환오류, 범위 오류면 범위오류를 출력하세요.',
        "marker": '여러 종류의 예외를 각각 처리하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔀 여러 종류의 예외를 각각 처리하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">한 코드에서 여러 종류의 예외가 발생할 수 있다면, <code>except</code>를 여러 번 써서 "어떤 예외가 났는지"에 따라 다른 메시지를 출력할 수 있어요. 파이썬은 위에서부터 차례대로 맞는 except 블록을 찾아 실행해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">s, idx = input().split()
idx_str = idx
try:
    idx = int(idx_str)
    print(s[idx])
except ValueError:
    print("변환오류")
except IndexError:
    print("범위오류")</pre>
</div>
""",
    },
    {
        "id": 369,
        "old": '<p>나이가 입력됩니다. 0 미만이면 InvalidAgeError 를 발생시키고 잘못된 나이: 값 을 출력하세요. 아니면 나이: 값 을 출력하세요.</p>',
        "problem_text": '나이가 입력됩니다. 0 미만이면 InvalidAgeError 를 발생시키고 잘못된 나이: 값 을 출력하세요. 아니면 나이: 값 을 출력하세요.',
        "marker": '사용자 정의 예외(Custom Exception) 만들기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚨 사용자 정의 예외(Custom Exception) 만들기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬이 기본으로 제공하는 예외 외에, "내가 원하는 상황"을 나타내는 나만의 예외를 만들 수도 있어요. <code>Exception</code>을 상속받는 클래스를 만들면 되고, <code>raise 예외이름(메시지)</code>로 직접 예외를 발생시킬 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class InvalidAgeError(Exception):
    pass

age = int(input())
try:
    if age < 0:
        raise InvalidAgeError("나이는 0 이상이어야 합니다")
    print(f"나이: {age}")
except InvalidAgeError:
    print(f"잘못된 나이: {age}")</pre>
</div>
""",
    },
    {
        "id": 370,
        "old": '<p>두 정수가 입력됩니다. 나눗셈을 시도하고 결과 또는 오류 메시지를 출력하세요. 성공/실패 여부에 관계없이 작업 종료를 출력하세요.</p>',
        "problem_text": '두 정수가 입력됩니다. 나눗셈을 시도하고 결과 또는 오류 메시지를 출력하세요. 성공/실패 여부에 관계없이 작업 종료를 출력하세요.',
        "marker": 'finally로 항상 실행되는 코드 만들기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">☑️ finally로 항상 실행되는 코드 만들기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>finally:</code> 블록은 try 안에서 예외가 나든 안 나든 "무조건 마지막에 실행"돼요. 파일을 닫거나, "작업이 끝났다"는 메시지를 항상 출력하고 싶을 때처럼, 성공·실패와 관계없이 꼭 해야 할 일을 적어두는 곳이에요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
try:
    print(a / b)
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")
finally:
    print("작업 종료")</pre>
</div>
""",
    },
    {
        "id": 371,
        "old": '<p>양의 정수가 입력됩니다. 0 이하면 양수를 입력하세요를 출력하고, 맞으면 입력 성공: 값 을 출력하세요.</p>',
        "problem_text": '양의 정수가 입력됩니다. 0 이하면 양수를 입력하세요를 출력하고, 맞으면 입력 성공: 값 을 출력하세요.',
        "marker": '입력값 검증 패턴 (조건 확인 후 처리)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">✅ 입력값 검증 패턴 (조건 확인 후 처리)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">사용자가 보낸 값이 "내가 원하는 조건"을 만족하는지 먼저 확인하고, 만족하지 않으면 안내 메시지를, 만족하면 정상 처리를 하는 패턴이에요. 꼭 예외를 써야 하는 건 아니고, if문으로도 충분히 검증할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">n = int(input())
if n <= 0:
    print("양수를 입력하세요")
else:
    print(f"입력 성공: {n}")</pre>
</div>
""",
    },
    {
        "id": 372,
        "old": '<p>이름:점수 쌍이 콤마로 구분되어 입력되고 둘째 줄에 찾을 이름이 입력됩니다. 점수를 출력하고, 없으면 이름 없음을 출력하세요.</p>',
        "problem_text": '이름:점수 쌍이 콤마로 구분되어 입력되고 둘째 줄에 찾을 이름이 입력됩니다. 점수를 출력하고, 없으면 이름 없음을 출력하세요.',
        "marker": '딕셔너리 키 예외(KeyError)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔑 딕셔너리 키 예외(KeyError)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">딕셔너리에 없는 키로 값을 꺼내려고 하면 <code>KeyError</code>가 발생해요. 311번 문제에서 배운 <code>in</code> 연산자로 먼저 확인하거나, try-except로 KeyError를 감싸는 두 가지 방법 모두 가능해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">pairs = [kv.split(":") for kv in input().split(",")]
scores = {name: int(score) for name, score in pairs}
name = input()
if name in scores:
    print(scores[name])
else:
    print("이름 없음")</pre>
</div>
""",
    },
    {
        "id": 373,
        "old": '<p>한 줄에 값들이 공백으로 입력됩니다. 각 값을 정수로 변환해 합산하고, 정수로 변환할 수 없는 값은 건너뜁니다. 최종 합계를 출력하세요.</p>',
        "problem_text": '한 줄에 값들이 공백으로 입력됩니다. 각 값을 정수로 변환해 합산하고, 정수로 변환할 수 없는 값은 건너뜁니다. 최종 합계를 출력하세요.',
        "marker": '변환 실패는 건너뛰며 누적 합 구하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">⏭️ 변환 실패는 건너뛰며 누적 합 구하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">여러 값 중에는 숫자로 바꿀 수 없는 값이 섞여 있을 수 있어요. 각 값을 try-except로 하나씩 확인하면서, 성공하면 합계에 더하고 실패(ValueError)하면 그냥 <code>continue</code>로 넘어가면 전체가 멈추지 않고 가능한 값들만 모아 합산할 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">values = input().split()
total = 0
for v in values:
    try:
        total += int(v)
    except ValueError:
        continue
print(total)</pre>
</div>
""",
    },
    {
        "id": 374,
        "old": '<p>두 정수가 입력됩니다. 두 번째 수가 0이 아닌지 assert 로 확인하고 나눗셈 결과를 출력하세요. assert 실패 시 AssertionError 를 잡아 조건 오류를 출력하세요.</p>',
        "problem_text": '두 정수가 입력됩니다. 두 번째 수가 0이 아닌지 assert 로 확인하고 나눗셈 결과를 출력하세요. assert 실패 시 AssertionError 를 잡아 조건 오류를 출력하세요.',
        "marker": 'assert로 조건을 미리 검사하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🛡️ assert로 조건을 미리 검사하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>assert 조건, 메시지</code>는 "이 조건이 반드시 True여야 한다"고 선언하는 문장이에요. 조건이 False이면 <code>AssertionError</code>가 발생해요. 이를 try-except로 감싸면, 조건이 깨졌을 때 원하는 메시지를 출력하도록 만들 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">a, b = map(int, input().split())
try:
    assert b != 0, "0으로 나눌 수 없음"
    print(a / b)
except AssertionError:
    print("조건 오류")</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 8장(예외처리와 실전 코딩 패턴) 문항 10건에 개념 설명 카드를 추가합니다."

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
