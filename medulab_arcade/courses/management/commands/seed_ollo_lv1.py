"""올로AI 과정의 1단계 로봇 수업 내용과 레벨(챕터)별 학습목표를 넣는다.

  python manage.py seed_ollo_lv1            # 챕터 설명은 비어 있는 곳만 채운다
  python manage.py seed_ollo_lv1 --force    # 챕터 설명도 다시 덮어쓴다
"""
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item, LearningProgram
from courses.robot_lessons.ollo_lv1 import CHAPTER_CONTENTS, LESSONS, PROGRAM_NAME_HINT


class Command(BaseCommand):
    help = '올로AI 1단계 로봇 수업 내용 넣기'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        programs = LearningProgram.objects.filter(
            name__contains=PROGRAM_NAME_HINT, chapters__items__key='lv1_01').distinct()
        if programs.count() != 1:
            raise CommandError(f'올로AI 과정을 하나로 찾지 못했어요 ({programs.count()}개).')
        program = programs.get()
        chapters = {c.number: c for c in program.chapters.all()}

        items = {i.key: i for i in Item.objects.filter(chapter=chapters[1])}
        missing = [x['key'] for x in LESSONS if x['key'] not in items]
        if missing:
            raise CommandError(f'1장에 없는 항목: {missing}')
        for lesson in LESSONS:
            item = items[lesson['key']]
            item.robot_data = lesson
            item.requires_coding = True
            item.save(update_fields=['robot_data', 'requires_coding'])

        filled = 0
        for number, text in CHAPTER_CONTENTS.items():
            chapter = chapters.get(number)
            if chapter and (options['force'] or not (chapter.content or '').strip()):
                chapter.content = text
                chapter.save(update_fields=['content'])
                filled += 1
        self.stdout.write(f'{program.name}: 수업 {len(LESSONS)}개, 챕터 설명 {filled}개')
