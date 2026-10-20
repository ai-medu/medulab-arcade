from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_03_04"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:560px;border-radius:10px;margin-top:10px;display:block;">'
)


class Command(BaseCommand):
    help = "AICE Junior '활성함수' 문항에 시그모이드/렐루 곡선 비교 그래프 이미지를 추가합니다."

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "activation_functions.jpg", alt="시그모이드 vs 렐루 곡선 비교")
        old = "오늘날 은닉층에서 가장 많이 쓰여요.</div></div>\n</div>"

        if img in html:
            self.stdout.write(self.style.WARNING("이미 이미지가 적용되어 있습니다."))
            return
        if old not in html:
            raise CommandError("시그모이드/렐루 카드 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(old, old + "\n" + img, 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS("활성함수 그래프 이미지를 추가했습니다."))
