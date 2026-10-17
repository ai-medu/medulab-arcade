from html import escape

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Chapter, Item, LearningProgram


COURSE_NAME = "COS Pro 파이썬 3급 대비"
NEW_CHAPTER_TITLES = ["실전 모의고사 7", "실전 모의고사 8"]


def html_paragraphs(*lines):
    return "".join(f"<p>{escape(line)}</p>" for line in lines if line)


def problem(title, explain_lines, hint, answer_code, example_input="", expected_output=""):
    return {
        "title": title,
        "explain_html": html_paragraphs(*explain_lines),
        "hint": hint,
        "answer_code": answer_code.strip(),
        "example_input": example_input,
        "expected_output": expected_output,
    }


def build_extra_chapters():
    chapters = []

    # ── 실전 모의고사 7 (기출 변형 수준, Part 1) ────────────────────────────
    chapters.append({
        "title": "실전 모의고사 7",
        "content": "COS Pro 3급 공식 예제집 Part 1(기출 변형 수준) 10문제를 입력/출력 형식으로 재구성했습니다.",
        "items": [
            problem(
                "[모의7-1] 홀수 위치의 합",
                [
                    "숫자로 구성된 리스트가 한 줄에 공백으로 입력됩니다.",
                    "리스트의 원소 중 홀수 위치(위치는 0부터 셉니다)에 있는 숫자를 모두 더한 값을 출력하세요.",
                ],
                "range(1, len(arr), 2) 로 홀수 인덱스만 돌면서 더하세요.",
                "arr = list(map(int, input().split()))\ntotal = 0\nfor i in range(1, len(arr), 2):\n    total += arr[i]\nprint(total)",
                "1 3 2 6 8 10 22",
                "19",
            ),
            problem(
                "[모의7-2] 대문자 개수",
                ["문자열이 입력되면 그 안에 포함된 알파벳 대문자의 개수를 출력하세요."],
                "isupper() 메서드로 대문자 여부를 확인하세요.",
                "s = input()\ncnt = 0\nfor c in s:\n    if c.isupper():\n        cnt += 1\nprint(cnt)",
                "CodingHaru",
                "2",
            ),
            problem(
                "[모의7-3] 문자열 n번 반복",
                ["첫 줄에 문자열 s, 둘째 줄에 자연수 n이 입력됩니다. s를 n번 이어 붙여 출력하세요."],
                "문자열 * 정수 형태를 사용하면 간단합니다.",
                "s = input()\nn = int(input())\nprint(s * n)",
                "ab\n3",
                "ababab",
            ),
            problem(
                "[모의7-4] 줄어드는 부분 문자열",
                [
                    "문자열이 입력되면 전체 문자열부터 한 글자씩 줄여가며, 한 글자가 남을 때까지의 부분 문자열을 공백으로 구분해 출력하세요.",
                ],
                "range(len(s), 0, -1) 로 길이를 줄여가며 s[:i] 를 모으세요.",
                "s = input()\nresult = []\nfor i in range(len(s), 0, -1):\n    result.append(s[:i])\nprint(' '.join(result))",
                "IOT",
                "IOT IO I",
            ),
            problem(
                "[모의7-5] 5씩 줄어드는 수열",
                ["두 자연수 k, n이 한 줄씩 입력됩니다. k부터 5씩 줄어드는 수를 n개 공백으로 구분해 출력하세요."],
                "k - 5 * i 형태로 i를 0부터 n-1까지 반복하세요.",
                "k = int(input())\nn = int(input())\nresult = []\nfor i in range(n):\n    result.append(k - 5 * i)\nprint(*result)",
                "500\n5",
                "500 495 490 485 480",
            ),
            problem(
                "[모의7-6] 3 뒤에 있는 숫자의 개수",
                [
                    "숫자로 이루어진 리스트가 입력됩니다. 리스트에는 3이 정확히 한 번 들어있습니다.",
                    "3보다 뒤에 있는 숫자의 개수를 출력하세요.",
                ],
                "리스트의 index 메서드로 3의 위치를 찾은 뒤 뒤쪽 개수를 계산하세요.",
                "arr = list(map(int, input().split()))\nidx = arr.index(3)\nprint(len(arr) - idx - 1)",
                "8 12 3 9 15 20 4",
                "4",
            ),
            problem(
                "[모의7-7] 홀수·짝수 판별 (삼항연산자)",
                ["정수 하나가 입력되면 삼항연산자를 사용해 홀수이면 홀수, 짝수이면 짝수를 출력하세요."],
                "`A if 조건 else B` 형태의 삼항연산자를 사용하세요.",
                "num = int(input())\nprint('홀수' if num % 2 != 0 else '짝수')",
                "7",
                "홀수",
            ),
            problem(
                "[모의7-8] 별 삼각형",
                ["자연수 n이 입력되면 1번째 줄에 별 1개, 2번째 줄에 2개, ..., n번째 줄에 n개가 출력되도록 하세요."],
                "'*' * i 를 i가 1부터 n까지 증가하며 출력하세요.",
                "n = int(input())\nfor i in range(1, n + 1):\n    print('*' * i)",
                "4",
                "*\n**\n***\n****",
            ),
            problem(
                "[모의7-9] 몫과 나머지",
                ["두 정수 a, b가 한 줄씩 입력됩니다. a를 b로 나눈 몫과 나머지를 공백으로 구분해 출력하세요."],
                "// 는 몫, % 는 나머지를 구합니다.",
                "a = int(input())\nb = int(input())\nprint(a // b, a % b)",
                "17\n5",
                "3 2",
            ),
            problem(
                "[모의7-10] 문자열 뒤집기",
                ["문자열이 입력되면 거꾸로 뒤집어 출력하세요."],
                "슬라이싱 [::-1] 을 사용하면 간단합니다.",
                "s = input()\nresult = ''\nfor c in s:\n    result = c + result\nprint(result)",
                "hello",
                "olleh",
            ),
        ],
    })

    # ── 실전 모의고사 8 (난이도 10% 상향, Part 2) ────────────────────────────
    chapters.append({
        "title": "실전 모의고사 8",
        "content": "COS Pro 3급 공식 예제집 Part 2(난이도 약 10% 상향) 10문제를 입력/출력 형식으로 재구성했습니다.",
        "items": [
            problem(
                "[모의8-1] 홀수 위치의 짝수만 더하기",
                [
                    "숫자로 구성된 리스트가 입력됩니다. 홀수 위치(0부터 셉니다)에 있으면서 값이 짝수인 숫자만 모두 더해 출력하세요.",
                ],
                "홀수 인덱스를 돌면서 그 값이 짝수인지 추가로 확인하세요.",
                "arr = list(map(int, input().split()))\ntotal = 0\nfor i in range(1, len(arr), 2):\n    if arr[i] % 2 == 0:\n        total += arr[i]\nprint(total)",
                "1 3 2 6 8 10 22",
                "16",
            ),
            problem(
                "[모의8-2] 대문자와 소문자 개수",
                ["문자열이 입력되면 대문자 개수와 소문자 개수를 공백으로 구분해 순서대로 출력하세요."],
                "isupper() 가 참이면 대문자, 아니면 소문자로 처리하세요.",
                "s = input()\nup = 0\nlow = 0\nfor c in s:\n    if c.isupper():\n        up += 1\n    else:\n        low += 1\nprint(up, low)",
                "CodingHaru",
                "2 8",
            ),
            problem(
                "[모의8-3] 하이픈으로 이어 붙이기",
                ["첫 줄에 문자열 s, 둘째 줄에 자연수 n이 입력됩니다. s를 하이픈(-)으로 구분해 n번 이어 붙여 출력하세요."],
                "처음 s로 시작해서 n-1번 '-' + s 를 더하세요.",
                "s = input()\nn = int(input())\nresult = s\nfor i in range(n - 1):\n    result += '-' + s\nprint(result)",
                "ab\n3",
                "ab-ab-ab",
            ),
            problem(
                "[모의8-4] 늘었다 줄어드는 부분 문자열",
                [
                    "문자열이 입력되면 한 글자부터 전체 문자열까지 늘어난 뒤 다시 한 글자로 줄어드는 부분 문자열을 공백으로 구분해 출력하세요.",
                    "전체 문자열은 한 번만 출력합니다.",
                ],
                "늘어나는 구간과 줄어드는 구간을 각각 리스트에 모은 뒤 합치세요.",
                "s = input()\nparts = []\nfor i in range(1, len(s) + 1):\n    parts.append(s[:i])\nfor i in range(len(s) - 1, 0, -1):\n    parts.append(s[:i])\nprint(' '.join(parts))",
                "IOT",
                "I IO IOT IO I",
            ),
            problem(
                "[모의8-5] 증가폭이 커지는 수열",
                [
                    "두 자연수 k, n이 한 줄씩 입력됩니다. 첫 번째 수는 k이고, i번째 수는 바로 앞의 수에 i를 더한 값이 되도록 n개를 출력하세요.",
                ],
                "누적 변수를 두고 1부터 n-1까지 i를 더해 나가세요.",
                "k = int(input())\nn = int(input())\ncur = k\nresult = [k]\nfor i in range(1, n):\n    cur += i\n    result.append(cur)\nprint(*result)",
                "7\n5",
                "7 8 10 13 17",
            ),
            problem(
                "[모의8-6] 최댓값 앞의 짝수 개수",
                [
                    "숫자로 이루어진 리스트가 입력됩니다(가장 큰 수는 한 번만 등장).",
                    "가장 큰 수보다 앞에 있는 숫자 중 짝수의 개수를 출력하세요.",
                ],
                "max 와 index 로 최댓값의 위치를 찾은 뒤 그 앞부분만 확인하세요.",
                "arr = list(map(int, input().split()))\nidx = arr.index(max(arr))\ncnt = 0\nfor x in arr[:idx]:\n    if x % 2 == 0:\n        cnt += 1\nprint(cnt)",
                "8 12 3 9 15 20 4",
                "2",
            ),
            problem(
                "[모의8-7] 합에 따라 큰 수 또는 작은 수",
                [
                    "정수 두 개가 한 줄씩 입력됩니다. 두 수의 합이 짝수이면 더 큰 수를, 홀수이면 더 작은 수를 삼항연산자로 출력하세요.",
                ],
                "max(a, b)와 min(a, b)를 삼항연산자로 선택하세요.",
                "a = int(input())\nb = int(input())\nprint(max(a, b) if (a + b) % 2 == 0 else min(a, b))",
                "27\n64",
                "27",
            ),
            problem(
                "[모의8-8] 오른쪽 정렬 별 삼각형",
                [
                    "자연수 n이 입력되면 별(*)이 오른쪽 끝에 맞춰 한 줄씩 늘어나는 모양으로 출력하세요.",
                    "각 줄은 총 n칸이며, 별 앞의 빈 칸은 공백으로 채웁니다.",
                ],
                "각 줄에서 공백 개수는 n-i, 별 개수는 i입니다.",
                "n = int(input())\nfor i in range(1, n + 1):\n    print(' ' * (n - i) + '*' * i)",
                "4",
                "   *\n  **\n ***\n****",
            ),
            problem(
                "[모의8-9] 초를 시·분·초로 바꾸기",
                ["정수 n(초)이 입력되면 시, 분, 초를 공백으로 구분해 출력하세요."],
                "분을 구할 때는 전체 초를 3600으로 나눈 나머지를 다시 60으로 나누세요.",
                "n = int(input())\nh = n // 3600\nm = n % 3600 // 60\ns = n % 60\nprint(h, m, s)",
                "3725",
                "1 2 5",
            ),
            problem(
                "[모의8-10] 거꾸로 읽어도 같은 문자열",
                ["문자열이 입력되면 거꾸로 읽어도 같으면 YES, 다르면 NO를 출력하세요."],
                "s == s[::-1] 로 비교하세요.",
                "s = input()\nprint('YES' if s == s[::-1] else 'NO')",
                "level",
                "YES",
            ),
        ],
    })

    total_items = sum(len(chapter["items"]) for chapter in chapters)
    if total_items != 20:
        raise ValueError(f"추가 문항 수가 20개가 아닙니다: {total_items}")
    return chapters


class Command(BaseCommand):
    help = (
        "기존 'COS Pro 파이썬 3급 대비' 과정에 공식 예제집 기반 실전 모의고사 7~8 (20문제)을 추가합니다. "
        "기존 챕터/학생 기록은 건드리지 않습니다."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="실전 모의고사 7~8 챕터가 이미 있으면 그 2개 챕터만 지우고 다시 생성합니다. 다른 장은 영향받지 않습니다.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            program = LearningProgram.objects.get(name=COURSE_NAME)
        except LearningProgram.DoesNotExist:
            raise CommandError(
                f"'{COURSE_NAME}' 과정을 찾을 수 없습니다. 먼저 seed_cos_pro_python3 를 실행해 주세요."
            )

        existing_extra = Chapter.objects.filter(program=program, title__in=NEW_CHAPTER_TITLES)
        if existing_extra.exists():
            if not options["replace"]:
                self.stdout.write(self.style.WARNING(
                    "실전 모의고사 7~8 챕터가 이미 있습니다. 다시 넣으려면 --replace 옵션을 사용하세요."
                ))
                return
            existing_extra.delete()

        last_number = Chapter.objects.filter(program=program).order_by("-number").first()
        next_number = (last_number.number if last_number else 0) + 1

        chapters = build_extra_chapters()
        item_total = 0

        for offset, chapter_data in enumerate(chapters):
            chapter_number = next_number + offset
            chapter = Chapter.objects.create(
                program=program,
                number=chapter_number,
                title=chapter_data["title"],
                content=chapter_data["content"],
            )

            for item_index, item_data in enumerate(chapter_data["items"], start=1):
                item_total += 1
                Item.objects.create(
                    chapter=chapter,
                    number=item_index,
                    key=f"cos3_mock_{chapter_number:02d}_{item_index:02d}",
                    title=item_data["title"],
                    item_type="problem",
                    explain_html=item_data["explain_html"],
                    hint=item_data["hint"],
                    answer_code=item_data["answer_code"],
                    example_input=item_data["example_input"],
                    expected_output=item_data["expected_output"],
                )

        if "모의고사 6세트" in program.description:
            program.description = program.description.replace("모의고사 6세트", "모의고사 8세트")
            program.save(update_fields=["description"])

        self.stdout.write(self.style.SUCCESS(
            f"'{COURSE_NAME}'에 실전 모의고사 7~8 챕터를 추가했습니다. (총 {item_total}문제 추가)"
        ))
