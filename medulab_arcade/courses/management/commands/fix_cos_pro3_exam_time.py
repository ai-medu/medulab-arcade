from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Chapter, LearningProgram


COURSE_NAME = "COS Pro 파이썬 3급 대비"


class Command(BaseCommand):
    help = (
        "'COS Pro 파이썬 3급 대비' 과정의 설명/챕터 안내문에 남아있는 "
        "'40분' 시험 시간 표기를 실제 시험 시간인 '50분'으로 고칩니다. "
        "문제/챕터를 지우고 다시 만들지 않고 텍스트 필드만 수정하므로 학생 기록에 영향이 없습니다."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            program = LearningProgram.objects.get(name=COURSE_NAME)
        except LearningProgram.DoesNotExist:
            raise CommandError(f"'{COURSE_NAME}' 과정을 찾을 수 없습니다.")

        changed = 0

        if "40분" in program.description:
            program.description = program.description.replace("40분", "50분")
            program.save(update_fields=["description"])
            changed += 1
            self.stdout.write("과정 설명을 수정했습니다.")

        chapters = Chapter.objects.filter(program=program, content__icontains="40분")
        for chapter in chapters:
            chapter.content = chapter.content.replace("40분", "50분")
            chapter.save(update_fields=["content"])
            changed += 1
            self.stdout.write(f"챕터 '{chapter.title}' 안내문을 수정했습니다.")

        if changed:
            self.stdout.write(self.style.SUCCESS(f"총 {changed}곳을 50분으로 수정했습니다."))
        else:
            self.stdout.write(self.style.WARNING("'40분' 표기를 찾지 못했습니다. 이미 수정된 상태일 수 있습니다."))
