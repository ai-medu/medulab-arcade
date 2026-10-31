# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

VIZ = {
    858: {
        "code": "name = input()\ngrade = input()\nprint(f\"{name}은 {grade}학년입니다\")",
        "steps": [
            {"line": 1, "desc": "입력받은 이름 \"철수\"를 name에 저장해요.",
             "set_vars": [{"name": "name", "value": "철수", "type": "str"}], "console_lines": []},
            {"line": 2, "desc": "입력받은 학년 \"6\"을 grade에 저장해요.",
             "set_vars": [{"name": "name", "value": "철수", "type": "str"}, {"name": "grade", "value": "6", "type": "str"}],
             "console_lines": []},
            {"line": 3, "desc": "f\"...\"는 f-string이에요. {name}, {grade} 자리에 변수 값이 바로 들어가서 \"철수은 6학년입니다\"가 완성돼요.",
             "console_lines": ["철수은 6학년입니다"]},
        ],
    },
    869: {
        "code": "nums = [1,2,3]\nprint(nums)",
        "steps": [
            {"line": 1, "desc": "[1,2,3]처럼 대괄호 안에 값을 콤마로 나열하면 리스트가 만들어져요. 리스트는 여러 값을 순서대로 담는 상자예요.",
             "collections": [{"label": "nums", "items": [1, 2, 3]}], "console_lines": []},
            {"line": 2, "desc": "리스트를 그대로 출력하면 [1, 2, 3] 형태로 보여줘요.",
             "collections": [{"label": "nums", "items": [1, 2, 3]}], "console_lines": ["[1, 2, 3]"]},
        ],
    },
    871: {
        "code": "info = {\"이름\":\"영희\", \"학교\":\"초등학교\"}\nprint(info)",
        "steps": [
            {"line": 1, "desc": "딕셔너리는 {key:value} 짝으로 값을 저장해요. \"이름\"의 값은 \"영희\", \"학교\"의 값은 \"초등학교\"예요.",
             "collections": [{"label": "info", "items": ["이름:영희", "학교:초등학교"], "index_labels": ["0", "1"]}],
             "console_lines": []},
            {"line": 2, "desc": "딕셔너리를 출력하면 {'이름': '영희', '학교': '초등학교'} 형태로 모든 key:value가 보여요.",
             "collections": [{"label": "info", "items": ["이름:영희", "학교:초등학교"], "index_labels": ["0", "1"]}],
             "console_lines": ["{'이름': '영희', '학교': '초등학교'}"]},
        ],
    },
    872: {
        "code": "info = {\"이름\":\"민수\", \"나이\":12}\nprint(info[\"나이\"])",
        "steps": [
            {"line": 1, "desc": "info 딕셔너리에 \"이름\":\"민수\", \"나이\":12 두 짝을 저장해요.",
             "collections": [{"label": "info", "items": ["이름:민수", "나이:12"], "index_labels": ["0", "1"]}],
             "console_lines": []},
            {"line": 2, "desc": "info[\"나이\"]처럼 key를 대괄호에 넣으면 그 key의 value만 꺼낼 수 있어요. \"나이\"의 value는 12예요.",
             "collections": [{"label": "info", "items": ["이름:민수", "나이:12"], "index_labels": ["0", "1"], "hit_idx": 1, "dim_idx": [0]}],
             "console_lines": ["12"]},
        ],
    },
    882: {
        "code": "score = int(input())\nif score >= 60:\n    print(\"합격\")\nelse:\n    print(\"불합격\")",
        "steps": [
            {"line": 1, "desc": "입력받은 값을 숫자로 바꿔서 score에 저장해요. 예: 85",
             "set_vars": [{"name": "score", "value": "85", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "score >= 60 조건을 검사해요. 85 >= 60은 True(참)니까 if 블록으로 들어가요.",
             "set_vars": [{"name": "score", "value": "85", "type": "int"}], "console_lines": []},
            {"line": 3, "desc": "조건이 참이었으니 \"합격\"이 출력돼요. else는 실행되지 않아요.",
             "console_lines": ["합격"]},
        ],
    },
    883: {
        "code": "grade = int(input())\nif grade <= 3:\n    print(\"저학년\")\nelse:\n    print(\"고학년\")",
        "steps": [
            {"line": 1, "desc": "입력받은 학년을 숫자로 바꿔서 grade에 저장해요. 예: 5",
             "set_vars": [{"name": "grade", "value": "5", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "grade <= 3 조건을 검사해요. 5 <= 3은 False(거짓)라서 if 블록은 건너뛰고 else로 가요.",
             "set_vars": [{"name": "grade", "value": "5", "type": "int"}], "console_lines": []},
            {"line": 4, "desc": "조건이 거짓이었으니 else 블록의 \"고학년\"이 출력돼요.",
             "console_lines": ["고학년"]},
        ],
    },
    895: {
        "code": "fruits = [\"사과\",\"바나나\",\"딸기\"]\nfor f in fruits:\n    print(f)",
        "steps": [
            {"line": 1, "desc": "fruits 리스트에 \"사과\", \"바나나\", \"딸기\" 세 값을 담아요.",
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"]}], "console_lines": []},
            {"line": 2, "desc": "for f in fruits는 리스트의 값을 하나씩 꺼내서 f에 넣어요. 첫 번째로 \"사과\"가 들어와요.",
             "set_vars": [{"name": "f", "value": "사과", "type": "str"}],
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"], "cmp_idx": 0}], "console_lines": []},
            {"line": 3, "desc": "f를 출력해요 → \"사과\"",
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"], "cmp_idx": 0}], "console_lines": ["사과"]},
            {"line": 2, "desc": "반복문이 다시 돌아가서 f에 \"바나나\"가 들어와요.",
             "set_vars": [{"name": "f", "value": "바나나", "type": "str"}],
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"], "cmp_idx": 1, "dim_idx": [0]}],
             "console_lines": ["사과"]},
            {"line": 3, "desc": "f를 출력해요 → \"바나나\"",
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"], "cmp_idx": 1, "dim_idx": [0]}],
             "console_lines": ["사과", "바나나"]},
            {"line": 2, "desc": "마지막으로 f에 \"딸기\"가 들어와요.",
             "set_vars": [{"name": "f", "value": "딸기", "type": "str"}],
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"], "cmp_idx": 2, "dim_idx": [0, 1]}],
             "console_lines": ["사과", "바나나"]},
            {"line": 3, "desc": "f를 출력해요 → \"딸기\". 리스트의 모든 값을 다 꺼냈으니 반복이 끝나요.",
             "collections": [{"label": "fruits", "items": ["사과", "바나나", "딸기"], "cmp_idx": 2, "dim_idx": [0, 1]}],
             "console_lines": ["사과", "바나나", "딸기"]},
        ],
    },
    896: {
        "code": "i = 1\nwhile i <= 3:\n    print(i)\n    i += 1",
        "steps": [
            {"line": 1, "desc": "i를 1로 시작해요.",
             "set_vars": [{"name": "i", "value": "1", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "while은 조건이 참인 동안 계속 반복해요. i <= 3 → 1 <= 3은 True라서 블록을 실행해요.",
             "set_vars": [{"name": "i", "value": "1", "type": "int"}], "console_lines": []},
            {"line": 3, "desc": "i를 출력해요 → 1",
             "console_lines": ["1"]},
            {"line": 4, "desc": "i += 1로 i를 1만큼 늘려요. i가 2가 돼요. (안 늘리면 무한 반복에 걸려요!)",
             "set_vars": [{"name": "i", "value": "2", "type": "int"}], "console_lines": ["1"]},
            {"line": 2, "desc": "다시 조건을 검사해요. 2 <= 3은 True라서 또 반복해요.",
             "set_vars": [{"name": "i", "value": "2", "type": "int"}], "console_lines": ["1"]},
            {"line": 3, "desc": "i를 출력해요 → 2",
             "console_lines": ["1", "2"]},
            {"line": 4, "desc": "i가 3이 돼요.",
             "set_vars": [{"name": "i", "value": "3", "type": "int"}], "console_lines": ["1", "2"]},
            {"line": 2, "desc": "3 <= 3은 True라서 한 번 더 반복해요.",
             "set_vars": [{"name": "i", "value": "3", "type": "int"}], "console_lines": ["1", "2"]},
            {"line": 3, "desc": "i를 출력해요 → 3",
             "console_lines": ["1", "2", "3"]},
            {"line": 4, "desc": "i가 4가 돼요.",
             "set_vars": [{"name": "i", "value": "4", "type": "int"}], "console_lines": ["1", "2", "3"]},
            {"line": 2, "desc": "4 <= 3은 False라서 조건이 거짓이 되고, while 반복이 끝나요.",
             "set_vars": [{"name": "i", "value": "4", "type": "int"}], "console_lines": ["1", "2", "3"]},
        ],
    },
    907: {
        "code": "def hello():\n    print(\"안녕하세요\")\n\nhello()",
        "steps": [
            {"line": 1, "desc": "def로 hello()라는 함수를 미리 만들어둬요. 이 줄에서는 아직 실행되지 않아요.",
             "console_lines": []},
            {"line": 4, "desc": "hello()라고 쓰면 그 이름의 함수를 '호출'해서 실행시켜요.",
             "console_lines": []},
            {"line": 2, "desc": "함수 안의 코드인 print(\"안녕하세요\")가 실행돼요.",
             "console_lines": ["안녕하세요"]},
        ],
    },
    908: {
        "code": "def add(a, b):\n    return a + b\n\nprint(add(3, 4))",
        "steps": [
            {"line": 1, "desc": "add(a, b)라는 함수를 만들어둬요.",
             "console_lines": []},
            {"line": 4, "desc": "print(add(3, 4))에서 add 함수를 3, 4와 함께 호출해요.",
             "console_lines": []},
            {"line": 1, "desc": "함수 안에서 a에는 3, b에는 4가 전달돼요.",
             "set_vars": [{"name": "a", "value": "3", "type": "int"}, {"name": "b", "value": "4", "type": "int"}],
             "console_lines": []},
            {"line": 2, "desc": "return a + b는 3 + 4 = 7을 계산해서 함수 밖으로 돌려줘요.",
             "set_vars": [{"name": "a", "value": "3", "type": "int"}, {"name": "b", "value": "4", "type": "int"}],
             "console_lines": []},
            {"line": 4, "desc": "돌려받은 값 7이 print()로 출력돼요.",
             "clear_vars": ["a", "b"], "console_lines": ["7"]},
        ],
    },
    909: {
        "code": "def is_even(n):\n    return n % 2 == 0\n\nprint(is_even(4))",
        "steps": [
            {"line": 1, "desc": "숫자가 짝수인지 확인하는 is_even(n) 함수를 만들어둬요.",
             "console_lines": []},
            {"line": 4, "desc": "print(is_even(4))에서 is_even 함수를 4와 함께 호출해요.",
             "console_lines": []},
            {"line": 1, "desc": "함수 안에서 n에 4가 전달돼요.",
             "set_vars": [{"name": "n", "value": "4", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "n % 2 == 0은 '2로 나눈 나머지가 0인가?'를 물어봐요. 4 % 2 = 0이고 0 == 0은 True예요. 이 True가 함수 밖으로 돌아가요.",
             "set_vars": [{"name": "n", "value": "4", "type": "int"}], "console_lines": []},
            {"line": 4, "desc": "돌려받은 값 True가 그대로 출력돼요.",
             "clear_vars": ["n"], "console_lines": ["True"]},
        ],
    },
    920: {
        "code": "num = int(input())\nif num % 2 == 0:\n    print(\"성공\")\nelse:\n    print(\"실패\")",
        "steps": [
            {"line": 1, "desc": "입력받은 값을 숫자로 바꿔서 num에 저장해요. 예: 4",
             "set_vars": [{"name": "num", "value": "4", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "num % 2 == 0 조건을 검사해요. 4 % 2 = 0이고 0 == 0은 True라서 if 블록으로 들어가요.",
             "set_vars": [{"name": "num", "value": "4", "type": "int"}], "console_lines": []},
            {"line": 3, "desc": "조건이 참이었으니 \"성공\"이 출력돼요.",
             "console_lines": ["성공"]},
        ],
    },
    921: {
        "code": "for i in range(3):\n    print(\"안녕하세요\")",
        "steps": [
            {"line": 1, "desc": "range(3)은 0, 1, 2를 순서대로 꺼내줘요(3은 포함 안 돼요). 그래서 블록이 총 3번 반복돼요.",
             "set_vars": [{"name": "i", "value": "0", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "i 값과 상관없이 \"안녕하세요\"를 출력해요. (1번째 반복)",
             "console_lines": ["안녕하세요"]},
            {"line": 1, "desc": "반복문이 다시 돌아가서 i가 1이 돼요. (2번째 반복)",
             "set_vars": [{"name": "i", "value": "1", "type": "int"}], "console_lines": ["안녕하세요"]},
            {"line": 2, "desc": "\"안녕하세요\"를 또 출력해요.",
             "console_lines": ["안녕하세요", "안녕하세요"]},
            {"line": 1, "desc": "i가 2가 돼요. (3번째 반복)",
             "set_vars": [{"name": "i", "value": "2", "type": "int"}], "console_lines": ["안녕하세요", "안녕하세요"]},
            {"line": 2, "desc": "\"안녕하세요\"를 세 번째로 출력해요. i가 3이 되면 range(3) 밖이라 반복이 끝나요.",
             "console_lines": ["안녕하세요", "안녕하세요", "안녕하세요"]},
        ],
    },
}


class Command(BaseCommand):
    help = "파이썬기본과정 문항에 코드 실행 애니메이션(viz_data)을 추가합니다 (batch 2)."

    def handle(self, *args, **options):
        for item_id, data in VIZ.items():
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                raise CommandError(f"id={item_id} 문항을 찾을 수 없습니다.")
            item.viz_data = data
            item.save(update_fields=["viz_data"])
            self.stdout.write(self.style.SUCCESS(f"id={item_id} 애니메이션 데이터를 추가했습니다."))
