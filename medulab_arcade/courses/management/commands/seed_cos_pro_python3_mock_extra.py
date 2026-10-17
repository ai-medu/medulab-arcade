from html import escape

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Chapter, Item, LearningProgram


COURSE_NAME = "COS Pro 파이썬 3급 대비"
NEW_CHAPTER_TITLES = ["실전 모의고사 4", "실전 모의고사 5", "실전 모의고사 6"]


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

    # ── 실전 모의고사 4 ──────────────────────────────────────────────────────
    chapters.append({
        "title": "실전 모의고사 4",
        "content": "COS Pro 3급 출제 유형을 반영한 네 번째 모의고사입니다. 10문제를 50분 안에 풀어보세요.",
        "items": [
            problem(
                "[모의4-1] 두 수 중 큰 값",
                ["정수 두 개가 한 줄에 입력됩니다. 둘 중 더 큰 값을 출력하세요."],
                "if-else로 두 값을 비교하세요.",
                "a, b = map(int, input().split())\nif a > b:\n    print(a)\nelse:\n    print(b)",
                "7 3",
                "7",
            ),
            problem(
                "[모의4-2] 문자열 뒤집기",
                ["문자열이 입력되면 거꾸로 뒤집어 출력하세요."],
                "슬라이싱 [::-1] 을 사용하세요.",
                "s = input().strip()\nprint(s[::-1])",
                "python",
                "nohtyp",
            ),
            problem(
                "[모의4-3] 특정 단 구구단 출력",
                ["정수 n이 입력되면 n단을 1부터 9까지 출력하세요. 형식: 단x배수=결과"],
                "for i in range(1, 10) 을 사용하세요.",
                "n = int(input())\nfor i in range(1, 10):\n    print(f'{n}x{i}={n*i}')",
                "7",
                "7x1=7\n7x2=14\n7x3=21\n7x4=28\n7x5=35\n7x6=42\n7x7=49\n7x8=56\n7x9=63",
            ),
            problem(
                "[모의4-4] 리스트 최솟값",
                ["한 줄에 정수 다섯 개가 입력됩니다. 최솟값을 출력하세요."],
                "min 함수를 사용하세요.",
                "nums = list(map(int, input().split()))\nprint(min(nums))",
                "9 2 7 4 5",
                "2",
            ),
            problem(
                "[모의4-5] 문자열 포함 여부",
                ["두 줄에 걸쳐 문자열과 찾을 문자열이 입력됩니다. 포함되어 있으면 YES, 아니면 NO를 출력하세요."],
                "in 연산자로 포함 여부를 확인하세요.",
                "s = input().strip()\nt = input().strip()\nif t in s:\n    print('YES')\nelse:\n    print('NO')",
                "apple\nppl",
                "YES",
            ),
            problem(
                "[모의4-6] 피보나치 수열 n번째 항",
                ["정수 n(2 이상)이 입력되면 피보나치 수열(1, 1, 2, 3, 5, ...)의 n번째 항을 출력하세요."],
                "두 변수를 번갈아 갱신하며 n-2번 반복하세요.",
                "n = int(input())\na, b = 1, 1\nfor _ in range(n - 2):\n    a, b = b, a + b\nprint(b)",
                "7",
                "13",
            ),
            problem(
                "[모의4-7] BMI 계산 함수",
                ["몸무게(kg)와 키(cm)가 한 줄에 입력됩니다. bmi(weight, height_cm) 함수로 BMI를 소수 첫째 자리까지 출력하세요."],
                "키를 미터로 바꾼 뒤 weight / (h*h) 로 계산하고 round 를 사용하세요.",
                "def bmi(weight, height_cm):\n    h = height_cm / 100\n    return round(weight / (h * h), 1)\n\nw, h = map(int, input().split())\nprint(bmi(w, h))",
                "70 175",
                "22.9",
            ),
            problem(
                "[모의4-8] 두 문자열 합치기",
                ["두 줄에 문자열이 각각 입력됩니다. 두 문자열을 이어 붙인 결과와 그 길이를 차례로 출력하세요."],
                "문자열 더하기 후 len 을 사용하세요.",
                "a = input().strip()\nb = input().strip()\nmerged = a + b\nprint(merged)\nprint(len(merged))",
                "Hello\nWorld",
                "HelloWorld\n10",
            ),
            problem(
                "[모의4-9] 3 또는 5의 배수 합",
                ["정수 n이 입력되면 1부터 n까지 수 중 3의 배수 또는 5의 배수의 합을 출력하세요."],
                "or 연산자로 두 조건을 연결하세요.",
                "n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    if i % 3 == 0 or i % 5 == 0:\n        total += i\nprint(total)",
                "15",
                "60",
            ),
            problem(
                "[모의4-10] 중복 제거 후 개수",
                ["한 줄에 정수 여러 개가 입력됩니다. 중복을 제거했을 때 남는 값의 개수를 출력하세요."],
                "set 자료형을 사용하면 중복이 자동으로 제거됩니다.",
                "nums = list(map(int, input().split()))\nunique = set(nums)\nprint(len(unique))",
                "1 2 2 3 4 4 4 5",
                "5",
            ),
        ],
    })

    # ── 실전 모의고사 5 ──────────────────────────────────────────────────────
    chapters.append({
        "title": "실전 모의고사 5",
        "content": "조금 더 응용된 다섯 번째 모의고사입니다. 실제 시험처럼 풀어보세요.",
        "items": [
            problem(
                "[모의5-1] 세 수의 중간값",
                ["정수 세 개가 입력되면 크기순으로 가운데 값을 출력하세요."],
                "sorted 로 정렬한 뒤 가운데 인덱스를 출력하세요.",
                "a, b, c = map(int, input().split())\nnums = sorted([a, b, c])\nprint(nums[1])",
                "5 9 2",
                "5",
            ),
            problem(
                "[모의5-2] 문자 치환",
                ["첫 줄에 문자열, 둘째 줄에 '원래문자 바꿀문자'가 공백으로 입력됩니다. 치환한 결과를 출력하세요."],
                "replace 메서드를 사용하세요.",
                "s = input()\nold, new = input().split()\nprint(s.replace(old, new))",
                "banana\na *",
                "b*n*n*",
            ),
            problem(
                "[모의5-3] 평균과 최고점",
                ["한 줄에 정수 다섯 개(점수)가 입력됩니다. 평균을 첫째 줄에, 최고점을 둘째 줄에 출력하세요."],
                "sum/len 으로 평균을, max 로 최고점을 구하세요.",
                "scores = list(map(int, input().split()))\navg = sum(scores) / len(scores)\nprint(avg)\nprint(max(scores))",
                "80 90 70 60 100",
                "80.0\n100",
            ),
            problem(
                "[모의5-4] 윤년 판별 함수",
                ["연도가 입력되면 is_leap(year) 함수로 윤년이면 윤년, 아니면 평년을 출력하세요."],
                "4의 배수이면서 100의 배수가 아니거나, 400의 배수이면 윤년입니다.",
                "def is_leap(year):\n    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):\n        return True\n    return False\n\ny = int(input())\nif is_leap(y):\n    print('윤년')\nelse:\n    print('평년')",
                "2024",
                "윤년",
            ),
            problem(
                "[모의5-5] 홀수 번째 인덱스 값만 출력",
                ["한 줄에 정수 여러 개가 입력됩니다. 인덱스가 홀수(1, 3, 5, ...)인 값만 한 줄에 하나씩 출력하세요."],
                "반복문 안에서 i % 2 == 1 조건을 확인하세요.",
                "nums = list(map(int, input().split()))\nfor i in range(len(nums)):\n    if i % 2 == 1:\n        print(nums[i])",
                "10 20 30 40 50 60",
                "20\n40\n60",
            ),
            problem(
                "[모의5-6] 가운데 글자 추출",
                ["길이가 홀수인 문자열이 입력되면 정가운데 글자 하나를 출력하세요."],
                "len(s) // 2 가 가운데 인덱스입니다.",
                "s = input().strip()\nmid = len(s) // 2\nprint(s[mid])",
                "level",
                "v",
            ),
            problem(
                "[모의5-7] 재귀함수로 팩토리얼",
                ["정수 n이 입력되면 재귀함수 factorial(n)으로 n!을 출력하세요."],
                "n이 1 이하면 1을 반환하고, 그 외에는 n * factorial(n-1)을 반환하세요.",
                "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nn = int(input())\nprint(factorial(n))",
                "5",
                "120",
            ),
            problem(
                "[모의5-8] 대문자 변환과 공백 제거",
                ["문장이 입력되면 모두 대문자로 바꾸고 공백을 제거해 출력하세요."],
                "upper() 와 replace(' ', '') 를 함께 사용하세요.",
                "s = input()\nresult = s.upper().replace(' ', '')\nprint(result)",
                "hello world",
                "HELLOWORLD",
            ),
            problem(
                "[모의5-9] 두 집합의 교집합 개수",
                ["두 줄에 걸쳐 정수 다섯 개씩 입력됩니다. 두 줄에 공통으로 들어있는 수의 개수를 출력하세요."],
                "set 으로 바꾼 뒤 & 연산자로 교집합을 구하세요.",
                "a = set(map(int, input().split()))\nb = set(map(int, input().split()))\nprint(len(a & b))",
                "1 2 3 4 5\n3 4 5 6 7",
                "3",
            ),
            problem(
                "[모의5-10] 증가하는 별 삼각형",
                ["정수 n이 입력되면 1개부터 n개까지 한 줄씩 늘어나는 별 삼각형을 출력하세요."],
                "'*' * i 를 i가 1부터 n까지 증가하며 출력하세요.",
                "n = int(input())\nfor i in range(1, n + 1):\n    print('*' * i)",
                "4",
                "*\n**\n***\n****",
            ),
        ],
    })

    # ── 실전 모의고사 6 ──────────────────────────────────────────────────────
    chapters.append({
        "title": "실전 모의고사 6",
        "content": "기출 유형을 종합한 여섯 번째 모의고사입니다. 실제 시험 환경처럼 50분 안에 도전하세요.",
        "items": [
            problem(
                "[모의6-1] 섭씨를 화씨로 변환하는 함수",
                ["섭씨 온도가 입력되면 c_to_f(c) 함수로 화씨 온도를 출력하세요."],
                "화씨 = 섭씨 * 9 / 5 + 32 입니다.",
                "def c_to_f(c):\n    return c * 9 / 5 + 32\n\nc = float(input())\nprint(c_to_f(c))",
                "25",
                "77.0",
            ),
            problem(
                "[모의6-2] 리스트 오름차순 정렬",
                ["한 줄에 정수 여러 개가 입력됩니다. 오름차순으로 정렬해 공백으로 구분해 출력하세요."],
                "sort 메서드와 print(*리스트) 를 사용하세요.",
                "nums = list(map(int, input().split()))\nnums.sort()\nprint(*nums)",
                "5 2 8 1 9",
                "1 2 5 8 9",
            ),
            problem(
                "[모의6-3] 모음 개수 세기",
                ["영문 문자열이 입력되면 모음(a, e, i, o, u)의 개수를 출력하세요."],
                "문자가 'aeiou'에 포함되는지 확인하세요.",
                "s = input().strip()\nvowels = 'aeiou'\ncount = 0\nfor ch in s:\n    if ch in vowels:\n        count += 1\nprint(count)",
                "programming",
                "3",
            ),
            problem(
                "[모의6-4] 행렬 전체 합",
                ["두 줄에 걸쳐 정수 세 개씩 입력됩니다(2행 3열). 모든 값의 합을 출력하세요."],
                "두 줄을 각각 리스트로 받아 sum을 더하세요.",
                "row1 = list(map(int, input().split()))\nrow2 = list(map(int, input().split()))\nprint(sum(row1) + sum(row2))",
                "1 2 3\n4 5 6",
                "21",
            ),
            problem(
                "[모의6-5] 소수 판별 함수",
                ["정수 n이 입력되면 is_prime(n) 함수로 소수이면 소수, 아니면 합성수를 출력하세요."],
                "2부터 n-1까지 나누어떨어지는 수가 있는지 확인하세요.",
                "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, n):\n        if n % i == 0:\n            return False\n    return True\n\nn = int(input())\nif is_prime(n):\n    print('소수')\nelse:\n    print('합성수')",
                "17",
                "소수",
            ),
            problem(
                "[모의6-6] 단어 빈도수 세기",
                ["단어 여러 개가 공백으로 입력됩니다. apple 이라는 단어가 몇 번 나오는지 출력하세요."],
                "딕셔너리에 단어별 등장 횟수를 누적하세요.",
                "words = input().split()\ncount = {}\nfor w in words:\n    count[w] = count.get(w, 0) + 1\nprint(count.get('apple', 0))",
                "apple banana apple orange apple banana",
                "3",
            ),
            problem(
                "[모의6-7] 리스트 뒤집기",
                ["한 줄에 정수 여러 개가 입력됩니다. 순서를 뒤집어 출력하세요."],
                "reverse 메서드와 print(*리스트) 를 사용하세요.",
                "nums = list(map(int, input().split()))\nnums.reverse()\nprint(*nums)",
                "1 2 3 4 5",
                "5 4 3 2 1",
            ),
            problem(
                "[모의6-8] 최대공약수(GCD)",
                ["정수 두 개가 입력되면 유클리드 호제법으로 최대공약수를 출력하세요."],
                "b가 0이 될 때까지 a, b = b, a % b 를 반복하세요.",
                "a, b = map(int, input().split())\nwhile b != 0:\n    a, b = b, a % b\nprint(a)",
                "48 18",
                "6",
            ),
            problem(
                "[모의6-9] 간단한 문자 암호화",
                ["영소문자로만 이루어진 문자열이 입력되면 각 글자를 알파벳 순서상 바로 다음 글자로 바꿔 출력하세요. (z는 고려하지 않습니다)"],
                "ord 로 코드값을 구한 뒤 1을 더하고 chr 로 다시 문자로 바꾸세요.",
                "s = input().strip()\nresult = ''\nfor ch in s:\n    result += chr(ord(ch) + 1)\nprint(result)",
                "abc",
                "bcd",
            ),
            problem(
                "[모의6-10] 평균 이상인 학생 수",
                ["한 줄에 학생들의 점수가 입력됩니다. 평균 점수 이상을 받은 학생 수를 출력하세요."],
                "평균을 구한 뒤 각 점수와 비교하며 세어보세요.",
                "scores = list(map(int, input().split()))\navg = sum(scores) / len(scores)\ncount = 0\nfor s in scores:\n    if s >= avg:\n        count += 1\nprint(count)",
                "70 85 90 60 75 95",
                "3",
            ),
        ],
    })

    total_items = sum(len(chapter["items"]) for chapter in chapters)
    if total_items != 30:
        raise ValueError(f"추가 문항 수가 30개가 아닙니다: {total_items}")
    return chapters


class Command(BaseCommand):
    help = "기존 'COS Pro 파이썬 3급 대비' 과정에 실전 모의고사 4~6 (30문제)을 추가합니다. 기존 챕터/학생 기록은 건드리지 않습니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="실전 모의고사 4~6 챕터가 이미 있으면 그 3개 챕터만 지우고 다시 생성합니다. 기존 1~10장은 영향받지 않습니다.",
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
                    "실전 모의고사 4~6 챕터가 이미 있습니다. 다시 넣으려면 --replace 옵션을 사용하세요."
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

        if "모의고사 3세트" in program.description:
            program.description = program.description.replace("모의고사 3세트", "모의고사 6세트")
            program.save(update_fields=["description"])

        self.stdout.write(self.style.SUCCESS(
            f"'{COURSE_NAME}'에 실전 모의고사 4~6 챕터를 추가했습니다. (총 {item_total}문제 추가)"
        ))
