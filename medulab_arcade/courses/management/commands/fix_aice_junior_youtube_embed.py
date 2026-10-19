from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_01_01"

OLD_IFRAME_OPEN = (
    'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
    'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
    'allowfullscreen loading="lazy">'
)

NEW_IFRAME_OPEN = (
    'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
    'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
    'referrerpolicy="strict-origin-when-cross-origin" '
    'allowfullscreen loading="lazy">'
)


class Command(BaseCommand):
    help = (
        "AICE Junior '인공지능 개념과 특성' 문항의 유튜브 iframe에 "
        "referrerpolicy 속성을 추가해 '동영상 플레이어 구성 오류(153)'를 해결합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        count = item.explain_html.count(OLD_IFRAME_OPEN)
        if count == 0:
            if NEW_IFRAME_OPEN in item.explain_html:
                self.stdout.write(self.style.WARNING("이미 referrerpolicy가 적용되어 있습니다."))
            else:
                raise CommandError("수정할 iframe 패턴을 찾지 못했습니다. 문항 내용을 확인해 주세요.")
            return

        item.explain_html = item.explain_html.replace(OLD_IFRAME_OPEN, NEW_IFRAME_OPEN)
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"iframe {count}개에 referrerpolicy를 추가했습니다."))
