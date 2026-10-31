# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

VIZ = {
    822: {
        "code": "a = int(input(\"a: \"))\nb = int(input(\"b: \"))\nprint(a + b)",
        "steps": [
            {"line": 1, "desc": "input()으로 받은 글자 \"7\"을 int()로 진짜 숫자로 바꿔서 a에 저장해요.",
             "set_vars": [{"name": "a", "value": "7", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "같은 방식으로 b에도 숫자 8을 저장해요.",
             "set_vars": [{"name": "b", "value": "8", "type": "int"}], "console_lines": []},
            {"line": 3, "desc": "a + b = 7 + 8 = 15를 계산해서 화면에 출력해요.",
             "console_lines": ["15"]},
        ],
    },
    870: {
        "code": "arr = []\narr.append(5)\nprint(arr)",
        "steps": [
            {"line": 1, "desc": "arr이라는 빈 리스트(상자)를 만들어요. 아직 아무것도 안 들어있어요.",
             "collections": [{"label": "arr", "items": []}], "console_lines": []},
            {"line": 2, "desc": "append(5)는 리스트 맨 뒤에 5를 '추가'해요.",
             "collections": [{"label": "arr", "items": [5], "hit_idx": 0}], "console_lines": []},
            {"line": 3, "desc": "리스트를 출력하면 [5]가 나와요.",
             "collections": [{"label": "arr", "items": [5], "hit_idx": 0}], "console_lines": ["[5]"]},
        ],
    },
    894: {
        "code": "for i in range(1,6):\n    print(i)",
        "steps": [
            {"line": 1, "desc": "range(1,6)은 1,2,3,4,5를 순서대로 꺼내줘요(6은 포함 안 돼요).",
             "set_vars": [{"name": "i", "value": "1", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "i가 1일 때 print(i) → 1을 출력해요.", "console_lines": ["1"]},
            {"line": 1, "desc": "반복문이 다시 돌아가서 i가 2가 돼요.",
             "set_vars": [{"name": "i", "value": "2", "type": "int"}], "console_lines": ["1"]},
            {"line": 2, "desc": "i가 2일 때 print(i) → 2를 출력해요.", "console_lines": ["1", "2"]},
            {"line": 1, "desc": "i가 3이 돼요.", "set_vars": [{"name": "i", "value": "3", "type": "int"}],
             "console_lines": ["1", "2"]},
            {"line": 2, "desc": "3을 출력해요.", "console_lines": ["1", "2", "3"]},
            {"line": 1, "desc": "i가 4가 돼요.", "set_vars": [{"name": "i", "value": "4", "type": "int"}],
             "console_lines": ["1", "2", "3"]},
            {"line": 2, "desc": "4를 출력해요.", "console_lines": ["1", "2", "3", "4"]},
            {"line": 1, "desc": "i가 5가 돼요.", "set_vars": [{"name": "i", "value": "5", "type": "int"}],
             "console_lines": ["1", "2", "3", "4"]},
            {"line": 2, "desc": "5를 출력해요. 이제 i가 6이 되면 range(1,6) 밖이라 반복이 끝나요.",
             "console_lines": ["1", "2", "3", "4", "5"]},
        ],
    },
    856: {
        "code": "word = \"PythonStudy\"\nprint(word[6:])",
        "steps": [
            {"line": 1, "desc": "문자열은 글자마다 번호(인덱스)가 있어요. word[0]='P', word[1]='y'... 이렇게 0부터 시작해요.",
             "collections": [{"label": "word", "items": list("PythonStudy")}], "console_lines": []},
            {"line": 2, "desc": "word[6:]는 '인덱스 6부터 끝까지'를 잘라내는 슬라이싱이에요. 6번은 'S'예요.",
             "collections": [{"label": "word", "items": list("PythonStudy"), "hit_idx": [6, 7, 8, 9, 10], "dim_idx": [0, 1, 2, 3, 4, 5]}],
             "console_lines": []},
            {"line": 2, "desc": "그래서 'Study'가 잘려 나와서 출력돼요.",
             "collections": [{"label": "word", "items": list("PythonStudy"), "hit_idx": [6, 7, 8, 9, 10], "dim_idx": [0, 1, 2, 3, 4, 5]}],
             "console_lines": ["Study"]},
        ],
    },
    881: {
        "code": "num = int(input())\nif num % 2 == 0:\n    print(\"짝수\")\nelse:\n    print(\"홀수\")",
        "steps": [
            {"line": 1, "desc": "입력받은 값을 숫자로 바꿔서 num에 저장해요. 예: 4",
             "set_vars": [{"name": "num", "value": "4", "type": "int"}], "console_lines": []},
            {"line": 2, "desc": "num % 2 는 4를 2로 나눈 나머지예요. 4 % 2 = 0 이고, 0 == 0은 True(참)예요. 그래서 if 블록으로 들어가요.",
             "set_vars": [{"name": "num", "value": "4", "type": "int"}], "console_lines": []},
            {"line": 3, "desc": "조건이 참이었으니까 \"짝수\"가 출력돼요. (else는 실행되지 않아요)",
             "console_lines": ["짝수"]},
        ],
    },
}


class Command(BaseCommand):
    help = "파이썬기본과정 샘플 5개 문항에 코드 실행 애니메이션(viz_data)을 추가합니다 (검증용)."

    def handle(self, *args, **options):
        for item_id, data in VIZ.items():
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                raise CommandError(f"id={item_id} 문항을 찾을 수 없습니다.")
            item.viz_data = data
            item.save(update_fields=["viz_data"])
            self.stdout.write(self.style.SUCCESS(f"id={item_id} 애니메이션 데이터를 추가했습니다."))
