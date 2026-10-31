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
        "id": 355,
        "old": '<p>이름과 나이가 한 줄에 입력됩니다. Person 클래스를 만들어 introduce 메서드가 이름: X, 나이: Y 를 출력하게 하세요.</p>',
        "problem_text": '이름과 나이가 한 줄에 입력됩니다. Person 클래스를 만들어 introduce 메서드가 이름: X, 나이: Y 를 출력하게 하세요.',
        "marker": '클래스와 객체란? - __init__과 메서드',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🏷️ 클래스와 객체란? - __init__과 메서드</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">클래스는 "어떤 데이터와 동작을 가질지"를 정의하는 설계도예요. <code>__init__</code>은 객체가 만들어질 때 자동으로 실행되며 초깃값을 저장하는 특별한 메서드이고, <code>self</code>는 "지금 만들어지는 그 객체 자신"을 가리켜요. 클래스 안에 정의한 함수를 메서드라고 부르며, <code>객체.메서드()</code>로 호출해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def introduce(self):
        print(f"이름: {self.name}, 나이: {self.age}")

name, age = input().split()
p = Person(name, int(age))
p.introduce()</pre>
</div>
""",
    },
    {
        "id": 356,
        "old": '<p>연산자(+ - * /)와 두 정수가 한 줄에 입력됩니다. Calculator 클래스의 compute 메서드로 결과를 출력하세요. 나눗셈은 실수로 출력하세요.</p>',
        "problem_text": '연산자(+ - * /)와 두 정수가 한 줄에 입력됩니다. Calculator 클래스의 compute 메서드로 결과를 출력하세요. 나눗셈은 실수로 출력하세요.',
        "marker": '클래스에 여러 기능(메서드) 담기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧮 클래스에 여러 기능(메서드) 담기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">클래스 하나에 여러 개의 메서드를 넣어 "관련된 기능들을 한 곳에 모아둘" 수 있어요. 연산 기호에 따라 분기하는 메서드를 만들어, 사칙연산을 모두 처리하게 해봐요. 나눗셈은 실수가 되므로 자동으로 float이 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Calculator:
    def compute(self, op, a, b):
        if op == "+":
            return a + b
        elif op == "-":
            return a - b
        elif op == "*":
            return a * b
        else:
            return a / b

op, a, b = input().split()
calc = Calculator()
print(calc.compute(op, int(a), int(b)))</pre>
</div>
""",
    },
    {
        "id": 357,
        "old": '<p>동물 이름이 입력됩니다. Animal 을 상속하는 Dog 클래스를 만들어 speak 메서드가 이름: 멍멍! 을 출력하게 하세요.</p>',
        "problem_text": '동물 이름이 입력됩니다. Animal 을 상속하는 Dog 클래스를 만들어 speak 메서드가 이름: 멍멍! 을 출력하게 하세요.',
        "marker": '클래스 상속(Inheritance) 기초',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧬 클래스 상속(Inheritance) 기초</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">상속은 "기존 클래스의 기능을 그대로 물려받아 새로운 클래스를 만드는 것"이에요. <code>class Dog(Animal):</code>처럼 쓰면 Dog는 Animal이 가진 것을 전부 물려받고, 필요한 부분만 새로 정의하거나 덮어쓸 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def speak(self):
        print(f"{self.name}: 멍멍!")

name = input()
d = Dog(name)
d.speak()</pre>
</div>
""",
    },
    {
        "id": 358,
        "old": '<p>초기 잔액이 입력됩니다. 그 다음 줄부터 deposit 금액 또는 withdraw 금액 형식으로 입력되고 END가 나오면 최종 잔액을 출력하세요. 잔액 부족 시 잔액 부족을 출력하세요.</p>',
        "problem_text": '초기 잔액이 입력됩니다. 그 다음 줄부터 deposit 금액 또는 withdraw 금액 형식으로 입력되고 END가 나오면 최종 잔액을 출력하세요. 잔액 부족 시 잔액 부족을 출력하세요.',
        "marker": '클래스로 상태를 계속 바꿔나가기 (은행 계좌)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🏦 클래스로 상태를 계속 바꿔나가기 (은행 계좌)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">객체는 자기만의 데이터(예: 잔액)를 가지고, 메서드를 호출할 때마다 그 데이터가 바뀌어요(상태 변화). 입금/출금 명령을 반복해서 처리하면서 <code>self.balance</code>를 계속 갱신하는 방식이에요. 출금할 때는 잔액이 충분한지 먼저 확인해야 해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Account:
    def __init__(self, balance):
        self.balance = balance
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

acc = Account(int(input()))
while True:
    line = input()
    if line == "END":
        break
    cmd, amount = line.split()
    amount = int(amount)
    if cmd == "deposit":
        acc.deposit(amount)
    else:
        if not acc.withdraw(amount):
            print("잔액 부족")
print(acc.balance)</pre>
</div>
""",
    },
    {
        "id": 359,
        "old": '<p>이름들이 한 줄씩 입력되고 END가 나오면 총 생성된 Student 객체 수를 출력하세요.</p>',
        "problem_text": '이름들이 한 줄씩 입력되고 END가 나오면 총 생성된 Student 객체 수를 출력하세요.',
        "marker": '클래스 변수(class variable)로 생성된 객체 수 세기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔢 클래스 변수(class variable)로 생성된 객체 수 세기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>self.변수</code>는 객체마다 따로 가지는 값이지만, 클래스 안에서 <code>클래스이름.변수</code>처럼 쓰는 "클래스 변수"는 그 클래스로 만든 모든 객체가 공유해요. <code>__init__</code>이 실행될 때마다 이 클래스 변수를 1씩 늘리면, 지금까지 몇 개의 객체가 만들어졌는지 셀 수 있어요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Student:
    count = 0
    def __init__(self, name):
        self.name = name
        Student.count += 1

while True:
    line = input()
    if line == "END":
        break
    Student(line)
print(Student.count)</pre>
</div>
""",
    },
    {
        "id": 360,
        "old": '<p>상품명과 가격이 한 줄에 입력됩니다. Product 클래스의 __str__ 이 상품명 - 가격원 을 반환하도록 구현해 print로 출력하세요.</p>',
        "problem_text": '상품명과 가격이 한 줄에 입력됩니다. Product 클래스의 __str__ 이 상품명 - 가격원 을 반환하도록 구현해 print로 출력하세요.',
        "marker": '__str__ 메서드로 print 결과 꾸미기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🖨️ __str__ 메서드로 print 결과 꾸미기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">객체를 그냥 <code>print(객체)</code>하면 보기 어려운 주소값 같은 게 나와요. 클래스에 <code>__str__(self)</code> 메서드를 정의해두면, print가 그 메서드가 반환하는 문자열을 대신 보여줘요. "이 객체를 글자로 어떻게 표현할지"를 직접 정하는 거예요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    def __str__(self):
        return f"{self.name} - {self.price}원"

name, price = input().split()
p = Product(name, int(price))
print(p)</pre>
</div>
""",
    },
    {
        "id": 361,
        "old": '<p>도형 종류(circle 또는 rect)와 치수가 입력됩니다. circle 이면 반지름, rect 이면 가로 세로가 입력됩니다. 넓이를 소수 둘째 자리로 출력하세요. (π=3.14)</p>',
        "problem_text": '도형 종류(circle 또는 rect)와 치수가 입력됩니다. circle 이면 반지름, rect 이면 가로 세로가 입력됩니다. 넓이를 소수 둘째 자리로 출력하세요. (π=3.14)',
        "marker": '메서드 오버라이딩(overriding)',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🔄 메서드 오버라이딩(overriding)</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">자식 클래스에서 부모 클래스와 "같은 이름의 메서드"를 다시 정의하면, 부모의 것 대신 자식의 것이 실행돼요. 이를 오버라이딩이라고 해요. 도형마다 넓이 구하는 공식이 다르므로, 각 자식 클래스가 자신만의 area() 메서드를 가지면 깔끔해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Shape:
    def area(self):
        return 0

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return 3.14 * self.r ** 2

class Rect(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h

parts = input().split()
if parts[0] == "circle":
    shape = Circle(float(parts[1]))
else:
    shape = Rect(float(parts[1]), float(parts[2]))
print(round(shape.area(), 2))</pre>
</div>
""",
    },
    {
        "id": 362,
        "old": '<p>섭씨 온도가 입력됩니다. Temperature 클래스에서 @property 로 fahrenheit 를 계산해 출력하세요.</p>',
        "problem_text": '섭씨 온도가 입력됩니다. Temperature 클래스에서 @property 로 fahrenheit 를 계산해 출력하세요.',
        "marker": '@property로 "계산된 속성" 만들기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🏷️ @property로 "계산된 속성" 만들기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><code>@property</code>를 메서드 위에 붙이면, 그 메서드를 함수처럼 <code>()</code>를 붙여 호출하지 않고 변수처럼 <code>객체.이름</code>으로 바로 쓸 수 있어요. 매번 새로 계산해서 돌려주는 "읽기 전용 속성"을 만들 때 유용해요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius
    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

t = Temperature(float(input()))
print(t.fahrenheit)</pre>
</div>
""",
    },
    {
        "id": 363,
        "old": '<p>push 값 또는 pop 명령이 한 줄씩 입력됩니다. END가 나오면 종료하고 pop 결과를 순서대로 출력하세요. 스택이 비어 있을 때 pop 하면 EMPTY를 출력하세요.</p>',
        "problem_text": 'push 값 또는 pop 명령이 한 줄씩 입력됩니다. END가 나오면 종료하고 pop 결과를 순서대로 출력하세요. 스택이 비어 있을 때 pop 하면 EMPTY를 출력하세요.',
        "marker": '클래스로 스택(Stack) 구현하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📦 클래스로 스택(Stack) 구현하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">스택은 "마지막에 넣은 것이 가장 먼저 나오는" 자료구조예요(LIFO: Last In First Out). 책을 쌓아올리는 걸 떠올리면 돼요. 파이썬 리스트의 <code>append()</code>가 push(넣기), <code>pop()</code>이 pop(꺼내기) 역할을 그대로 해줘요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Stack:
    def __init__(self):
        self.items = []
    def push(self, val):
        self.items.append(val)
    def pop(self):
        if not self.items:
            return "EMPTY"
        return self.items.pop()

s = Stack()
results = []
while True:
    line = input()
    if line == "END":
        break
    if line.startswith("push"):
        s.push(line.split()[1])
    else:
        results.append(str(s.pop()))
for r in results:
    print(r)</pre>
</div>
""",
    },
    {
        "id": 364,
        "old": '<p>enqueue 값 또는 dequeue 명령이 한 줄씩 입력됩니다. END가 나오면 종료하고 dequeue 결과를 순서대로 출력하세요. 큐가 비어 있을 때 dequeue 하면 EMPTY를 출력하세요.</p>',
        "problem_text": 'enqueue 값 또는 dequeue 명령이 한 줄씩 입력됩니다. END가 나오면 종료하고 dequeue 결과를 순서대로 출력하세요. 큐가 비어 있을 때 dequeue 하면 EMPTY를 출력하세요.',
        "marker": '클래스로 큐(Queue) 구현하기',
        "concept": """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚶 클래스로 큐(Queue) 구현하기</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">큐는 "먼저 들어온 것이 먼저 나가는" 자료구조예요(FIFO: First In First Out). 줄서기를 떠올리면 돼요. 리스트의 맨 뒤에 추가(<code>append</code>)하고, 맨 앞에서 꺼낼 때는 <code>pop(0)</code>을 쓰면 돼요.</p>
<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Queue:
    def __init__(self):
        self.items = []
    def enqueue(self, val):
        self.items.append(val)
    def dequeue(self):
        if not self.items:
            return "EMPTY"
        return self.items.pop(0)

q = Queue()
results = []
while True:
    line = input()
    if line == "END":
        break
    if line.startswith("enqueue"):
        q.enqueue(line.split()[1])
    else:
        results.append(str(q.dequeue()))
for r in results:
    print(r)</pre>
</div>
""",
    },

]


class Command(BaseCommand):
    help = "COS Pro 2급 대비 7장(클래스와 객체지향 기초) 문항 10건에 개념 설명 카드를 추가합니다."

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
