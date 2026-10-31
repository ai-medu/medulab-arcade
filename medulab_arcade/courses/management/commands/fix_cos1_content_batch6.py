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
        "id": 445,
        "old": '<p>도형 종류(circle/rect/triangle)와 치수가 입력됩니다. 각 도형의 넓이를 소수 둘째 자리로 출력하세요. (π=3.14)</p>',
        "problem_text": '도형 종류(circle/rect/triangle)와 치수가 입력됩니다. 각 도형의 넓이를 소수 둘째 자리로 출력하세요. (π=3.14)',
        "marker": '추상 클래스(abstract class)로 공통 인터페이스 만들기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔷 추상 클래스(abstract class)로 공통 인터페이스 만들기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">여러 도형(원, 직사각형, 삼각형)이 모두 \'넓이를 구한다\'는 동작을 가져야 하지만, 각자 계산 방법은 다르죠. 이럴 때 abc.ABC를 상속한 추상 클래스에 @abstractmethod로 area()를 선언해두면, \'이 메서드는 자식 클래스가 반드시 구현해야 한다\'는 규칙을 강제할 수 있어요. 추상 클래스 자체는 인스턴스를 만들 수 없고, 구현을 강제함으로써 일관된 사용법을 보장해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">from abc import ABC, abstractmethod\nimport math\n\nclass Shape(ABC):\n    @abstractmethod\n    def area(self):\n        pass\n\nclass Circle(Shape):\n    def __init__(self, r):\n        self.r = r\n    def area(self):\n        return math.pi * self.r ** 2\n\nclass Rect(Shape):\n    def __init__(self, w, h):\n        self.w, self.h = w, h\n    def area(self):\n        return self.w * self.h</pre>\n</div>\n',
    },
    {
        "id": 446,
        "old": '<p>학생 이름과 점수가 여러 줄 입력됩니다. END 가 나오면 점수 기준 오름차순으로 정렬해 출력하세요.</p>',
        "problem_text": '학생 이름과 점수가 여러 줄 입력됩니다. END 가 나오면 점수 기준 오름차순으로 정렬해 출력하세요.',
        "marker": '__eq__ 와 __lt__ 로 비교 기준 직접 정의하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⚖️ __eq__ 와 __lt__ 로 비교 기준 직접 정의하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬 객체는 기본적으로 <, == 같은 비교를 할 수 없어요(주소값만 비교돼요). 클래스에 __lt__(less than)을 정의하면 \'어떤 기준으로 작다/크다를 판단할지\' 직접 알려줄 수 있고, 그러면 sorted()나 min()/max() 같은 내장 함수가 그 기준으로 자동 정렬해줘요. __eq__는 == 비교 기준을 정의해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Student:\n    def __init__(self, name, score):\n        self.name, self.score = name, score\n    def __lt__(self, other):\n        return self.score < other.score\n\nstudents = []\nwhile True:\n    line = input()\n    if line == \'END\':\n        break\n    name, score = line.split()\n    students.append(Student(name, int(score)))\n\nfor s in sorted(students):\n    print(f"{s.name}:{s.score}")</pre>\n</div>\n',
    },
    {
        "id": 447,
        "old": '<p>두 벡터가 한 줄씩 입력됩니다(x y 형식). 두 벡터의 합을 출력하세요.</p>',
        "problem_text": '두 벡터가 한 줄씩 입력됩니다(x y 형식). 두 벡터의 합을 출력하세요.',
        "marker": '__add__ 로 연산자 오버로딩하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">➕ __add__ 로 연산자 오버로딩하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬에서 + 연산자는 사실 내부적으로 __add__ 메서드를 호출해요. 클래스에 __add__를 직접 정의하면, 내가 만든 객체끼리도 숫자처럼 + 로 더할 수 있게 만들 수 있어요(연산자 오버로딩). 벡터 덧셈이라면 각 좌표를 따로 더한 새 Vector 객체를 반환하면 돼요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Vector:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __add__(self, other):\n        return Vector(self.x + other.x, self.y + other.y)\n\nx1, y1 = map(int, input().split())\nx2, y2 = map(int, input().split())\nv3 = Vector(x1, y1) + Vector(x2, y2)\nprint(v3.x, v3.y)</pre>\n</div>\n',
    },
    {
        "id": 448,
        "old": '<p>비행기 정보가 입력됩니다. FlyingVehicle 과 Vehicle 을 다중 상속한 Airplane 클래스를 구현해 info() 가 이름 비행 가능 출력하도록 하세요.</p>',
        "problem_text": '비행기 정보가 입력됩니다. FlyingVehicle 과 Vehicle 을 다중 상속한 Airplane 클래스를 구현해 info() 가 이름 비행 가능 출력하도록 하세요.',
        "marker": '다중 상속(multiple inheritance)',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧬 다중 상속(multiple inheritance)</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬 클래스는 여러 부모 클래스를 동시에 상속할 수 있어요(class Child(ParentA, ParentB)). 비행기는 \'날 수 있는 것\'과 \'탈 수 있는 것\'의 성질을 모두 가지므로, FlyingVehicle과 Vehicle 두 부모를 함께 상속하면 두 부모의 메서드를 모두 물려받게 돼요. 메서드 이름이 겹치면 왼쪽에 적은 부모가 먼저 우선권을 가져요(MRO, 메서드 결정 순서).</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Vehicle:\n    def __init__(self, name):\n        self.name = name\n\nclass FlyingVehicle:\n    def fly(self):\n        return "비행 가능"\n\nclass Airplane(FlyingVehicle, Vehicle):\n    def info(self):\n        return f"{self.name} {self.fly()}"\n\nname = input()\na = Airplane(name)\nprint(a.info())</pre>\n</div>\n',
    },
    {
        "id": 449,
        "old": '<p>시작값 s와 끝값 e가 입력됩니다. EvenIterator 클래스로 s부터 e까지의 짝수를 한 줄씩 출력하세요.</p>',
        "problem_text": '시작값 s와 끝값 e가 입력됩니다. EvenIterator 클래스로 s부터 e까지의 짝수를 한 줄씩 출력하세요.',
        "marker": '__iter__ 와 __next__ 로 커스텀 이터레이터 만들기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🔄 __iter__ 와 __next__ 로 커스텀 이터레이터 만들기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">for문이 객체를 반복할 수 있는 건, 그 객체가 __iter__(반복을 시작할 때 자기 자신을 반환)와 __next__(다음 값을 하나씩 꺼내주고, 더 없으면 StopIteration을 발생) 메서드를 가지고 있기 때문이에요. 이 두 메서드를 직접 구현하면 \'짝수만 순서대로 꺼내주는\' 나만의 반복 가능한 객체를 만들 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class EvenIterator:\n    def __init__(self, start, end):\n        self.current = start if start % 2 == 0 else start + 1\n        self.end = end\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.current > self.end:\n            raise StopIteration\n        value = self.current\n        self.current += 2\n        return value\n\ns, e = map(int, input().split())\nfor v in EvenIterator(s, e):\n    print(v)</pre>\n</div>\n',
    },
    {
        "id": 450,
        "old": '<p>온도와 변환 방향(CtoF/FtoC)이 입력됩니다. Temperature 클래스의 클래스 메서드로 변환해 소수 둘째 자리로 출력하세요.</p>',
        "problem_text": '온도와 변환 방향(CtoF/FtoC)이 입력됩니다. Temperature 클래스의 클래스 메서드로 변환해 소수 둘째 자리로 출력하세요.',
        "marker": '@classmethod 와 @staticmethod 의 차이',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🏷️ @classmethod 와 @staticmethod 의 차이</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">@staticmethod는 클래스나 인스턴스 상태와 무관한, 그냥 클래스 안에 넣어둔 일반 함수예요. @classmethod는 첫 번째 인자로 클래스 자신(cls)을 받아서, 클래스 변수를 활용하거나 \'대안 생성자\'처럼 쓰여요. 온도 변환처럼 \'어떤 클래스에 속한 기능이지만 특정 인스턴스가 필요 없는\' 경우에 둘 다 적합하지만, cls를 써야 하면 classmethod를 선택해요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Temperature:\n    @classmethod\n    def c_to_f(cls, c):\n        return c * 9 / 5 + 32\n    @classmethod\n    def f_to_c(cls, f):\n        return (f - 32) * 5 / 9\n\nvalue, direction = input().split()\nvalue = float(value)\nif direction == \'CtoF\':\n    print(round(Temperature.c_to_f(value), 2))\nelse:\n    print(round(Temperature.f_to_c(value), 2))</pre>\n</div>\n',
    },
    {
        "id": 451,
        "old": '<p>이름이 입력됩니다. LogMixin 과 SaveMixin 을 상속한 Service 클래스를 구현해 process() 호출 시 [LOG] 처리: 이름, [SAVE] 저장: 이름 을 출력하세요.</p>',
        "problem_text": '이름이 입력됩니다. LogMixin 과 SaveMixin 을 상속한 Service 클래스를 구현해 process() 호출 시 [LOG] 처리: 이름, [SAVE] 저장: 이름 을 출력하세요.',
        "marker": '믹스인(mixin) 패턴으로 기능 조합하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🧵 믹스인(mixin) 패턴으로 기능 조합하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">믹스인은 \'단독으로 쓰이지 않고, 다른 클래스에 특정 기능 하나를 끼워 넣기 위한\' 작은 클래스예요. LogMixin은 로그 기능만, SaveMixin은 저장 기능만 담당하게 만들고, Service 클래스가 이 둘을 함께 상속하면 두 기능을 조합해서 쓸 수 있어요. 상속 하나로 거대한 클래스를 만드는 대신, 작은 기능 조각들을 레고처럼 조립하는 방식이에요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class LogMixin:\n    def log(self, name):\n        print(f"[LOG] 처리: {name}")\n\nclass SaveMixin:\n    def save(self, name):\n        print(f"[SAVE] 저장: {name}")\n\nclass Service(LogMixin, SaveMixin):\n    def process(self, name):\n        self.log(name)\n        self.save(name)\n\nname = input()\nService().process(name)</pre>\n</div>\n',
    },
    {
        "id": 452,
        "old": '<p>이름과 나이가 입력됩니다. __slots__ 를 사용한 Person 클래스로 이름: 이름, 나이: 나이 를 출력하세요.</p>',
        "problem_text": '이름과 나이가 입력됩니다. __slots__ 를 사용한 Person 클래스로 이름: 이름, 나이: 나이 를 출력하세요.',
        "marker": '__slots__ 로 메모리 절약하기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🪶 __slots__ 로 메모리 절약하기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">파이썬 객체는 기본적으로 속성을 담는 딕셔너리(__dict__)를 하나씩 가지고 있어서, 객체가 아주 많아지면 메모리를 꽤 많이 써요. 클래스에 __slots__ = [\'name\', \'age\']처럼 미리 쓸 속성 이름을 고정해두면, 딕셔너리 대신 더 가벼운 구조로 저장돼서 메모리를 아낄 수 있어요. 다만 __slots__에 적지 않은 새로운 속성은 추가할 수 없다는 제약이 생겨요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class Person:\n    __slots__ = [\'name\', \'age\']\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\nname, age = input().split()\np = Person(name, int(age))\nprint(f"이름: {p.name}, 나이: {p.age}")</pre>\n</div>\n',
    },
    {
        "id": 453,
        "old": '<p>파일명이 입력됩니다. __enter__와 __exit__가 구현된 FileManager 클래스를 with 문으로 사용해 열기: 파일명, 닫기: 파일명 을 출력하세요.</p>',
        "problem_text": '파일명이 입력됩니다. __enter__와 __exit__가 구현된 FileManager 클래스를 with 문으로 사용해 열기: 파일명, 닫기: 파일명 을 출력하세요.',
        "marker": '컨텍스트 매니저(with문) 클래스 만들기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">🚪 컨텍스트 매니저(with문) 클래스 만들기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">with 문을 쓰면 \'시작할 때 할 일\'과 \'끝날 때(에러가 나도!) 꼭 해야 할 일\'을 자동으로 보장할 수 있어요. 클래스에 __enter__(with 블록에 들어갈 때 실행, 보통 self 반환)와 __exit__(블록을 빠져나올 때 실행)를 구현하면 나만의 컨텍스트 매니저를 만들 수 있어요. 파일을 열고 닫는 작업을 흉내 내기 좋은 예시예요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">class FileManager:\n    def __init__(self, filename):\n        self.filename = filename\n    def __enter__(self):\n        print(f"열기: {self.filename}")\n        return self\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        print(f"닫기: {self.filename}")\n\nfilename = input()\nwith FileManager(filename):\n    pass</pre>\n</div>\n',
    },
    {
        "id": 454,
        "old": '<p>정수가 입력됩니다. 실행 시간을 측정하는 timer 데코레이터를 구현하고, 적용된 함수를 실행해 함수이름 실행완료 를 출력하세요.</p>',
        "problem_text": '정수가 입력됩니다. 실행 시간을 측정하는 timer 데코레이터를 구현하고, 적용된 함수를 실행해 함수이름 실행완료 를 출력하세요.',
        "marker": '데코레이터(decorator)로 함수 감싸기',
        "concept": '\n<div class="jz-card">\n<strong style="color:#fff;font-size:16px;">⏱️ 데코레이터(decorator)로 함수 감싸기</strong>\n<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">데코레이터는 \'어떤 함수를 실행하기 전/후에 공통된 동작을 끼워 넣는\' 함수예요. 원래 함수를 인자로 받아서, 그 함수를 호출하는 wrapper 함수를 새로 정의해 반환하는 구조예요. @timer를 함수 위에 붙이면 그 함수를 호출할 때마다 wrapper가 대신 실행되면서 추가 동작(예: 시간 측정, 메시지 출력)을 끼워 넣을 수 있어요.</p>\n<pre style="background:rgba(0,0,0,0.3);padding:10px 12px;border-radius:8px;color:#e5e7eb;font-size:14.5px;">def timer(func):\n    def wrapper(*args, **kwargs):\n        result = func(*args, **kwargs)\n        print(f"{func.__name__} 실행완료")\n        return result\n    return wrapper\n\n@timer\ndef compute(n):\n    return sum(range(n))\n\nn = int(input())\ncompute(n)</pre>\n</div>\n',
    },
]


class Command(BaseCommand):
    help = "COS Pro 1급 대비 고급 OOP 단원(44장) 문항 10건에 개념 설명 카드를 추가합니다."

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
