# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "junior_05_05"

PAIRS = [
    ("jzCopyVal(this,'66.93in')", "jzCopyVal(this,'66.93')"),
    ("jzCopyVal(this,'154.32lbs')", "jzCopyVal(this,'154.32')"),
]


class Command(BaseCommand):
    help = (
        "AI 모델 활용 문항의 키/몸무게 복사 배지가 단위(in/lbs)까지 함께 복사되던 것을 "
        "숫자만 복사되도록 고칩니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        for old, new in PAIRS:
            if new in html:
                continue
            if old not in html:
                raise CommandError(f"'{old}' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
            html = html.replace(old, new, 1)
            changed += 1

        if changed == 0:
            self.stdout.write(self.style.WARNING("이미 숫자만 복사되도록 적용되어 있습니다."))
            return

        item.explain_html = html
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS(f"{changed}곳을 숫자만 복사되도록 수정했습니다."))
