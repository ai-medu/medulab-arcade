# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "junior_05_03"

PAIRS = [
    (
        '<input type="text" id="j0505Answer" placeholder="숫자만 입력"',
        '<input type="text" id="j0505BAnswer" placeholder="숫자만 입력"',
    ),
    (
        "checkJ0503Blank('j0505Answer','j0505Result',19,'junior_05_03')",
        "checkJ0503Blank('j0505BAnswer','j0505BResult',19,'junior_05_03')",
    ),
    (
        '<div id="j0505Result" class="jz-result"></div>\n</div>\n\n<script>\nfunction checkJ0503Blank',
        '<div id="j0505BResult" class="jz-result"></div>\n</div>\n\n<script>\nfunction checkJ0503Blank',
    ),
]


class Command(BaseCommand):
    help = (
        "'BMI 예측 - 데이터 분석 및 가공' 문항에서 Q5-5(결측값 빈칸 채우기)와 "
        "Q5-5(박스차트 객관식)가 같은 id='j0505Result'를 공유해 박스차트 정답 체크 결과가 "
        "엉뚱한 곳에 표시되던 문제를 id 분리로 수정합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "j0505BResult" in html:
            self.stdout.write(self.style.WARNING("이미 id 충돌이 수정되어 있습니다."))
            return

        changed = 0
        for old, new in PAIRS:
            if old not in html:
                raise CommandError(f"'{old[:50]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
            html = html.replace(old, new, 1)
            changed += 1

        item.explain_html = html
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS(f"{changed}곳의 id 충돌을 수정했습니다."))
