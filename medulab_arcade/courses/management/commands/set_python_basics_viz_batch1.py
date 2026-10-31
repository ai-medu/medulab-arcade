# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

VIZ = {
    808: {
        "code": "print('내가 좋아하는 음식:')\nprint('초밥')\nprint('피자')\nprint('라면')",
        "steps": [
            {"line": 1, "desc": "첫 번째 print()로 안내 문구 \"내가 좋아하는 음식:\"을 출력해요.",
             "console_lines": ["내가 좋아하는 음식:"]},
            {"line": 2, "desc": "두 번째 print()로 \"초밥\"을 출력해요. print()를 쓸 때마다 한 줄씩 추가돼요.",
             "console_lines": ["내가 좋아하는 음식:", "초밥"]},
            {"line": 3, "desc": "세 번째 print()로 \"피자\"를 출력해요.",
             "console_lines": ["내가 좋아하는 음식:", "초밥", "피자"]},
            {"line": 4, "desc": "네 번째 print()로 \"라면\"을 출력해요. 이렇게 print()를 여러 번 쓰면 여러 줄을 출력할 수 있어요.",
             "console_lines": ["내가 좋아하는 음식:", "초밥", "피자", "라면"]},
        ],
    },
    809: {
        "code": "print('안녕하세요!')\nprint('저는 6학년입니다.')\nprint('파이썬을 배우는 중입니다.')",
        "steps": [
            {"line": 1, "desc": "첫 줄은 인사말 \"안녕하세요!\"를 출력해요.",
             "console_lines": ["안녕하세요!"]},
            {"line": 2, "desc": "두 번째 줄은 \"저는 6학년입니다.\"를 출력해요.",
             "console_lines": ["안녕하세요!", "저는 6학년입니다."]},
            {"line": 3, "desc": "세 번째 줄은 \"파이썬을 배우는 중입니다.\"를 출력해요. 코드는 위에서부터 한 줄씩 차례로 실행돼요.",
             "console_lines": ["안녕하세요!", "저는 6학년입니다.", "파이썬을 배우는 중입니다."]},
        ],
    },
    810: {
        "code": "print('철수: 뭐해?')\nprint('영희: 파이썬 공부해!')\nprint('철수: 오! 나도 배워볼래!')",
        "steps": [
            {"line": 1, "desc": "철수의 대화 \"철수: 뭐해?\"를 출력해요.",
             "console_lines": ["철수: 뭐해?"]},
            {"line": 2, "desc": "영희의 대답 \"영희: 파이썬 공부해!\"를 출력해요.",
             "console_lines": ["철수: 뭐해?", "영희: 파이썬 공부해!"]},
            {"line": 3, "desc": "철수의 마지막 말을 출력해요. print() 순서가 곧 화면에 보이는 순서예요.",
             "console_lines": ["철수: 뭐해?", "영희: 파이썬 공부해!", "철수: 오! 나도 배워볼래!"]},
        ],
    },
    820: {
        "code": "animal = input(\"좋아하는 동물: \")\nprint(animal)",
        "steps": [
            {"line": 1, "desc": "input()이 사용자가 입력한 글자를 그대로 가져와서 animal 변수에 저장해요. 예: \"강아지\"",
             "set_vars": [{"name": "animal", "value": "강아지", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "animal에 저장된 값을 그대로 출력해요.",
             "console_lines": ["강아지"]},
        ],
    },
    821: {
        "code": "name = input(\"이름: \")\nage = input(\"나이: \")\nprint(name, age + \"세\")",
        "steps": [
            {"line": 1, "desc": "입력받은 이름 \"홍길동\"을 name에 저장해요.",
             "set_vars": [{"name": "name", "value": "홍길동", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "input()은 항상 문자열(str)로 받아와요. 숫자처럼 보여도 age는 문자열 \"13\"이에요.",
             "set_vars": [{"name": "name", "value": "홍길동", "type": "str"}, {"name": "age", "value": "13", "type": "str"}],
             "console_lines": []},
            {"line": 3, "desc": "age가 문자열이니까 age + \"세\"는 글자를 이어붙여서 \"13세\"가 돼요. print(name, ...)는 둘을 공백으로 띄워서 출력해요.",
             "console_lines": ["홍길동 13세"]},
        ],
    },
    823: {
        "code": "word1 = input(\"단어1: \")\nword2 = input(\"단어2: \")\nprint(word1 + word2)",
        "steps": [
            {"line": 1, "desc": "첫 번째 단어 \"파이썬\"을 word1에 저장해요.",
             "set_vars": [{"name": "word1", "value": "파이썬", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "두 번째 단어 \"짱\"을 word2에 저장해요.",
             "set_vars": [{"name": "word1", "value": "파이썬", "type": "str"}, {"name": "word2", "value": "짱", "type": "str"}],
             "console_lines": []},
            {"line": 3, "desc": "문자열끼리 +로 더하면 사이에 공백 없이 이어붙여져요. \"파이썬\" + \"짱\" = \"파이썬짱\"",
             "console_lines": ["파이썬짱"]},
        ],
    },
    833: {
        "code": "animal = '고양이'\nprint(animal)",
        "steps": [
            {"line": 1, "desc": "'고양이'라는 문자열을 animal이라는 이름의 변수(상자)에 담아요.",
             "set_vars": [{"name": "animal", "value": "고양이", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "변수 이름을 쓰면 그 안에 담긴 값이 출력돼요.",
             "console_lines": ["고양이"]},
        ],
    },
    834: {
        "code": "food = '초밥'\ndrink = '콜라'\nprint('좋아하는 음식:', food)\nprint('좋아하는 음료:', drink)",
        "steps": [
            {"line": 1, "desc": "food 변수에 '초밥'을 저장해요.",
             "set_vars": [{"name": "food", "value": "초밥", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "drink 변수에 '콜라'를 저장해요. 변수는 여러 개 만들 수 있어요.",
             "set_vars": [{"name": "food", "value": "초밥", "type": "str"}, {"name": "drink", "value": "콜라", "type": "str"}],
             "console_lines": []},
            {"line": 3, "desc": "print()에 콤마(,)로 여러 값을 넣으면 공백으로 띄워서 한 줄에 출력해요.",
             "console_lines": ["좋아하는 음식: 초밥"]},
            {"line": 4, "desc": "drink 변수의 값도 같은 방식으로 출력해요.",
             "console_lines": ["좋아하는 음식: 초밥", "좋아하는 음료: 콜라"]},
        ],
    },
    835: {
        "code": "a = 10\nb = 3.14\nc = 'hello'\nprint(type(a))\nprint(type(b))\nprint(type(c))",
        "steps": [
            {"line": 1, "desc": "a에 정수 10을 저장해요. 소수점이 없는 숫자는 int(정수)예요.",
             "set_vars": [{"name": "a", "value": "10", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "b에 3.14를 저장해요. 소수점이 있는 숫자는 float(실수)예요.",
             "set_vars": [{"name": "a", "value": "10", "type": "int"}, {"name": "b", "value": "3.14", "type": "float"}],
             "console_lines": []},
            {"line": 3, "desc": "c에 'hello'를 저장해요. 따옴표로 감싼 글자는 str(문자열)이에요.",
             "set_vars": [{"name": "a", "value": "10", "type": "int"}, {"name": "b", "value": "3.14", "type": "float"},
                          {"name": "c", "value": "hello", "type": "str"}],
             "console_lines": []},
            {"line": 4, "desc": "type(a)는 a가 어떤 자료형인지 알려줘요. a는 정수니까 <class 'int'>가 출력돼요.",
             "console_lines": ["<class 'int'>"]},
            {"line": 5, "desc": "b는 실수니까 <class 'float'>가 출력돼요.",
             "console_lines": ["<class 'int'>", "<class 'float'>"]},
            {"line": 6, "desc": "c는 문자열이니까 <class 'str'>이 출력돼요.",
             "console_lines": ["<class 'int'>", "<class 'float'>", "<class 'str'>"]},
        ],
    },
    843: {
        "code": "a = 7\nb = 8\nprint(a + b)",
        "steps": [
            {"line": 1, "desc": "a에 숫자 7을 저장해요.",
             "set_vars": [{"name": "a", "value": "7", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "b에 숫자 8을 저장해요.",
             "set_vars": [{"name": "a", "value": "7", "type": "int"}, {"name": "b", "value": "8", "type": "int"}],
             "console_lines": []},
            {"line": 3, "desc": "a + b = 7 + 8 = 15를 계산해서 출력해요.",
             "console_lines": ["15"]},
        ],
    },
    844: {
        "code": "print(3 + 4 * 2)",
        "steps": [
            {"line": 1, "desc": "곱셈(*)은 더하기(+)보다 먼저 계산돼요. 그래서 먼저 4 * 2 = 8을 계산해요.",
             "console_lines": []},
            {"line": 1, "desc": "그다음 3 + 8 = 11을 계산해서 출력해요. 괄호 ()를 쓰면 순서를 바꿀 수 있어요.",
             "console_lines": ["11"]},
        ],
    },
    845: {
        "code": "def subtract(x, y):\n    return x - y\n\nprint(subtract(10, 3))",
        "steps": [
            {"line": 1, "desc": "def로 subtract(x, y)라는 함수를 미리 만들어둬요. 아직 실행은 안 돼요.",
             "console_lines": []},
            {"line": 4, "desc": "print(subtract(10, 3))에서 subtract 함수를 호출해요. 괄호 안의 10, 3이 함수로 전달돼요.",
             "console_lines": []},
            {"line": 1, "desc": "함수 안으로 들어가면 x에는 10, y에는 3이 전달돼요.",
             "set_vars": [{"name": "x", "value": "10", "type": "int"}, {"name": "y", "value": "3", "type": "int"}],
             "console_lines": []},
            {"line": 2, "desc": "return x - y는 10 - 3 = 7을 계산해서 함수 밖으로 '돌려줘요'.",
             "set_vars": [{"name": "x", "value": "10", "type": "int"}, {"name": "y", "value": "3", "type": "int"}],
             "console_lines": []},
            {"line": 4, "desc": "돌려받은 값 7이 print()로 출력돼요.",
             "clear_vars": ["x", "y"], "console_lines": ["7"]},
        ],
    },
    857: {
        "code": "name = input()\nprint(name.upper())",
        "steps": [
            {"line": 1, "desc": "입력받은 값 \"chulsoo\"를 name에 저장해요.",
             "set_vars": [{"name": "name", "value": "chulsoo", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "문자열에는 .upper()라는 메서드가 있어요. 모든 글자를 대문자로 바꿔줘요.",
             "console_lines": ["CHULSOO"]},
        ],
    },
}


class Command(BaseCommand):
    help = "파이썬기본과정 문항에 코드 실행 애니메이션(viz_data)을 추가합니다 (batch 1)."

    def handle(self, *args, **options):
        for item_id, data in VIZ.items():
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                raise CommandError(f"id={item_id} 문항을 찾을 수 없습니다.")
            item.viz_data = data
            item.save(update_fields=["viz_data"])
            self.stdout.write(self.style.SUCCESS(f"id={item_id} 애니메이션 데이터를 추가했습니다."))
