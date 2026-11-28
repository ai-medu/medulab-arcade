from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses import coding_missions as content
from courses.models import Chapter, Item, LearningProgram


class Command(BaseCommand):
    help = "'코딩기초' 과정에 메듀코드 블록코딩 미션을 넣거나 새 내용으로 고칩니다. 학생 기록은 지우지 않습니다."

    @transaction.atomic
    def handle(self, *args, **options):
        program = LearningProgram.objects.filter(name=content.PROGRAM_NAME).first()
        if not program:
            raise CommandError(f"'{content.PROGRAM_NAME}' 과정이 없어요. 먼저 과정을 만들어 주세요.")
        program.description = content.DESCRIPTION
        program.save(update_fields=['description'])

        total = 0
        for number, data in enumerate(content.CHAPTERS, 1):
            chapter = Chapter.objects.filter(program=program, number=number).first() or Chapter(program=program, number=number)
            chapter.title = data['title']
            chapter.content = content.chapter_content(data)
            chapter.save()
            for item_number, mission in enumerate(data['missions'], 1):
                key = content.item_key(number, item_number)
                # 예전 미로 항목은 같은 키를 그대로 써서 번호(주소)와 학생 기록이 남게 한다
                item = Item.objects.filter(chapter__program=program, key=key).first() or Item(key=key)
                item.chapter = chapter
                item.number = item_number
                item.title = mission['title']
                item.item_type = 'block_coding'
                item.requires_coding = True
                item.explain_html = f"<p>{mission['story']}</p>"
                item.hint = '\n'.join(mission['hints'])
                item.answer_code = ''
                item.example_input = ''
                item.mission_data = content.mission_data(number, item_number)
                item.save()
                total += 1
        self.stdout.write(self.style.SUCCESS(f'{len(content.CHAPTERS)}개 단원, 미션 {total}개를 넣었습니다.'))
