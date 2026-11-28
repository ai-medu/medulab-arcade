"""올로AI 과정의 2단계 로봇 수업 내용과 2장 학습목표를 넣는다.

  python manage.py seed_ollo_lv2            # 2장 설명은 비어 있거나 처음에 넣은 기본 글일 때만 바꾼다
  python manage.py seed_ollo_lv2 --force    # 2장 설명도 다시 덮어쓴다
"""
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item, LearningProgram
from courses.robot_lessons.ollo_lv1 import CHAPTER_CONTENTS, PROGRAM_NAME_HINT
from courses.robot_lessons.ollo_lv2 import CHAPTER_CONTENT, LESSONS


class Command(BaseCommand):
    help = '올로AI 2단계 로봇 수업 내용 넣기'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        programs = LearningProgram.objects.filter(
            name__contains=PROGRAM_NAME_HINT, chapters__items__key='lv2_01').distinct()
        if programs.count() != 1:
            raise CommandError(f'올로AI 과정을 하나로 찾지 못했어요 ({programs.count()}개).')
        program = programs.get()
        chapter = program.chapters.get(number=2)

        items = {i.key: i for i in Item.objects.filter(chapter=chapter)}
        missing = [x['key'] for x in LESSONS if x['key'] not in items]
        if missing:
            raise CommandError(f'2장에 없는 항목: {missing}')
        for lesson in LESSONS:
            item = items[lesson['key']]
            item.robot_data = lesson
            item.requires_coding = True
            item.save(update_fields=['robot_data', 'requires_coding'])

        changed = options['force'] or (chapter.content or '').strip() in ('', CHAPTER_CONTENTS[2])
        if changed:
            chapter.content = CHAPTER_CONTENT
            chapter.save(update_fields=['content'])
        self.stdout.write(f'{program.name}: 2단계 수업 {len(LESSONS)}개' + (', 2장 설명 갱신' if changed else ''))
