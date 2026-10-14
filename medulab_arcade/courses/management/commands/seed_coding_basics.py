import json

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Chapter, Item, LearningProgram, ProgramType


COURSE_NAME = "코딩기초"
PROGRAM_TYPE_NAME = "블록코딩"


def level(title, explain, hint, solution, grid, start_dir="E"):
    return {
        "title": title,
        "explain_html": f"<p>{explain}</p>",
        "hint": hint,
        "answer_code": solution,
        "maze": {"grid": grid, "start_dir": start_dir},
    }


def build_course_data():
    chapters = []

    # --- 1장: 블록으로 앞으로 이동하기 ---
    chapters.append({
        "title": "블록코딩 처음 만나기",
        "content": "블록을 하나씩 연결해서 로봇을 목표 지점까지 이동시켜 봅니다.",
        "items": [
            level(
                "한 칸 이동하기",
                "로봇을 오른쪽으로 한 칸 이동시켜 깃발까지 도착시키세요.",
                "'앞으로 이동' 블록 1개면 충분해요.",
                "앞으로 이동 × 1",
                ["####", "#SG#", "####"],
            ),
            level(
                "세 칸 이동하기",
                "'앞으로 이동' 블록을 여러 개 연결해서 깃발까지 이동시키세요.",
                "같은 블록을 필요한 만큼 이어 붙이면 됩니다.",
                "앞으로 이동 × 3",
                ["######", "#S..G#", "######"],
            ),
            level(
                "꺾인 길 지나가기",
                "오른쪽으로 이동하다가 아래로 꺾어서 깃발까지 가 보세요.",
                "먼저 앞으로 이동한 다음, 오른쪽으로 돌고 다시 이동하세요.",
                "앞으로 이동 → 오른쪽으로 돌기 → 앞으로 이동 × 2",
                [
                    "######",
                    "#S...#",
                    "####.#",
                    "####G#",
                    "######",
                ],
            ),
        ],
    })

    # --- 2장: 방향 바꾸기 ---
    chapters.append({
        "title": "방향 바꾸기",
        "content": "왼쪽/오른쪽으로 도는 블록을 활용해 복잡한 길을 통과합니다.",
        "items": [
            level(
                "왼쪽으로 돌아가기",
                "왼쪽으로 돈 다음 이동해서 깃발까지 가 보세요.",
                "'왼쪽으로 돌기' 블록을 먼저 사용해보세요.",
                "왼쪽으로 돌기 → 앞으로 이동 × 2",
                [
                    "#####",
                    "#..G#",
                    "#.###",
                    "#S###",
                    "#####",
                ],
                start_dir="N",
            ),
            level(
                "지그재그 길",
                "오른쪽, 왼쪽을 번갈아 돌면서 깃발까지 이동하세요.",
                "꺾이는 지점마다 방향 전환 블록을 추가하세요.",
                "앞으로 이동 → 오른쪽으로 돌기 → 앞으로 이동 → 왼쪽으로 돌기 → 앞으로 이동 × 2",
                [
                    "######",
                    "#S#..#",
                    "#.#.##",
                    "#...G#",
                    "######",
                ],
            ),
            level(
                "미로 탈출",
                "여러 번 꺾어야 도착할 수 있는 미로입니다. 길을 잘 살펴보세요.",
                "막다른 길로 가지 않도록 미로를 먼저 눈으로 따라가 보세요.",
                "앞으로 이동 → 오른쪽으로 돌기 → 앞으로 이동 × 2 → 왼쪽으로 돌기 → 앞으로 이동 × 2",
                [
                    "#######",
                    "#S....#",
                    "#.###.#",
                    "#...#.#",
                    "###.#.#",
                    "#G..#.#",
                    "#######",
                ],
            ),
        ],
    })

    # --- 3장: 반복 블록으로 더 똑똑하게 ---
    chapters.append({
        "title": "반복 블록 활용하기",
        "content": "'N번 반복하기' 블록으로 같은 동작을 간단하게 반복합니다.",
        "items": [
            level(
                "반복으로 길게 이동하기",
                "긴 직선 길을 '번 반복하기' 블록 하나로 통과해보세요.",
                "'5번 반복하기' 블록 안에 '앞으로 이동' 블록을 넣어보세요.",
                "5번 반복하기 { 앞으로 이동 }",
                ["########", "#S....G#", "########"],
            ),
            level(
                "네모를 그리며 이동",
                "반복 블록 안에 이동과 회전을 함께 넣어 네모 모양 길을 통과하세요.",
                "'앞으로 이동 → 오른쪽으로 돌기'를 반복 블록 안에 넣어보세요.",
                "4번 반복하기 { 앞으로 이동 × 2 → 오른쪽으로 돌기 }",
                [
                    "######",
                    "#S...#",
                    "#.##.#",
                    "#....#",
                    "#.##.#",
                    "#...G#",
                    "######",
                ],
            ),
            level(
                "최종 미로 도전",
                "지금까지 배운 이동, 회전, 반복 블록을 모두 활용해서 깃발까지 도착하세요!",
                "먼저 머릿속으로 경로를 그려본 다음 블록을 하나씩 쌓아보세요.",
                "앞으로 이동 × 2 → 오른쪽으로 돌기 → 3번 반복하기 { 앞으로 이동 } → 왼쪽으로 돌기 → 앞으로 이동 × 2",
                [
                    "########",
                    "#S.....#",
                    "######.#",
                    "#......#",
                    "#.######",
                    "#.#....#",
                    "#.#.##.#",
                    "#...#G.#",
                    "########",
                ],
            ),
        ],
    })

    return chapters


class Command(BaseCommand):
    help = "메듀랩 '코딩기초' 블록코딩 미로 과정을 생성합니다 (code.org 코딩기초 벤치마킹)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="같은 이름의 기존 과정이 있으면 챕터를 모두 지우고 다시 생성합니다.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        program_type, _ = ProgramType.objects.get_or_create(
            name=PROGRAM_TYPE_NAME,
            defaults={"order": 15},
        )

        description = (
            "code.org 코딩기초를 벤치마킹한 메듀랩 자체 제작 블록코딩 과정입니다. "
            "마우스로 블록을 조립해 캐릭터를 미로 끝까지 이동시키며 순차, 방향 전환, 반복 개념을 익힙니다."
        )

        program, created = LearningProgram.objects.get_or_create(
            name=COURSE_NAME,
            defaults={
                "description": description,
                "program_type": program_type,
                "is_active": True,
            },
        )

        if not created and not options["replace"] and program.chapters.exists():
            self.stdout.write(self.style.WARNING("이미 같은 이름의 과정이 있습니다. 다시 넣으려면 --replace 옵션을 사용하세요."))
            return

        program.description = description
        program.program_type = program_type
        program.is_active = True
        program.save()

        program.chapters.all().delete()

        chapters = build_course_data()
        item_total = 0

        for chapter_index, chapter_data in enumerate(chapters, start=1):
            chapter = Chapter.objects.create(
                program=program,
                number=chapter_index,
                title=chapter_data["title"],
                content=chapter_data["content"],
            )

            for item_index, item_data in enumerate(chapter_data["items"], start=1):
                item_total += 1
                Item.objects.create(
                    chapter=chapter,
                    number=item_index,
                    key=f"codingbasics_{chapter_index:02d}_{item_index:02d}",
                    title=item_data["title"],
                    item_type="block_coding",
                    requires_coding=True,
                    explain_html=item_data["explain_html"],
                    hint=item_data["hint"],
                    answer_code=item_data["answer_code"],
                    example_input=json.dumps(item_data["maze"], ensure_ascii=False),
                )

        self.stdout.write(self.style.SUCCESS(f"'{COURSE_NAME}' 과정이 생성되었습니다."))
        self.stdout.write(self.style.SUCCESS(f"총 {len(chapters)}개 챕터, {item_total}개 미로를 등록했습니다."))
