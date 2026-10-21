# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from courses.models import Item

OLD = "body: 'item_id=' + encodeURIComponent(itemId) + '&selected_option=OK'"
NEW = "body: 'item_id=' + encodeURIComponent(panel.dataset.itemId) + '&selected_option=OK'"


class Command(BaseCommand):
    help = (
        "AICE Junior 등 인라인 퀴즈 스크립트가 fetch로 진도를 저장할 때, 문항의 실제 PK 대신 "
        "문자열 key(예: 'junior_05_04')를 item_id로 보내던 버그를 고칩니다. "
        "grade_code 뷰는 Item.id(숫자)만 조회할 수 있어, 문자열 key가 전달되면 404로 실패하고 "
        "fetch의 .catch가 이를 조용히 무시해 진도 체크가 저장되지 않았습니다. "
        "panel의 data-item-id(실제 PK)를 사용하도록 고칩니다."
    )

    def handle(self, *args, **options):
        total_items = 0
        total_occurrences = 0
        for item in Item.objects.all():
            html = item.explain_html or ""
            count = html.count(OLD)
            if count == 0:
                continue
            html = html.replace(OLD, NEW)
            item.explain_html = html
            item.save(update_fields=["explain_html"])
            total_items += 1
            total_occurrences += count
            self.stdout.write(f"  - [{item.key or item.id}] {count}곳 수정")

        self.stdout.write(self.style.SUCCESS(
            f"총 {total_items}개 문항에서 {total_occurrences}곳의 item_id 버그를 수정했습니다."
        ))
