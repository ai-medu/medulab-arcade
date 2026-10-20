from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_03_03"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:480px;border-radius:10px;margin-top:10px;display:block;">'
)


class Command(BaseCommand):
    help = (
        "AICE Junior '딥러닝은 어떻게 학습할까' 문항에 경사하강법 그림과 "
        "조기종료(학습곡선) 그래프 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        gd_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "gradient_descent.jpg", alt="경사하강법 - 산에서 골짜기 내려가기")
        gd_old = "그래서 적당한 보폭을 정하는 게 중요합니다.\n</div>"
        if gd_img in html:
            skipped += 1
        elif gd_old in html:
            html = html.replace(gd_old, gd_old + "\n" + gd_img, 1)
            changed += 1
        else:
            raise CommandError("최적화(경사하강법) 설명 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        es_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "overfitting_curve.jpg", alt="조기 종료 - 학습/검증 오차 곡선")
        es_desc = "한 번도 안 본 문제(검증 데이터)의 점수가 더 이상 좋아지지 않는 시점에 공부를 멈추는 방법이에요."
        es_old = f'<div style="font-size:15px;color:var(--text-secondary);">{es_desc}</div></div>'
        es_new = f'<div style="font-size:15px;color:var(--text-secondary);">{es_desc}</div>{es_img}</div>'
        if es_img in html:
            skipped += 1
        elif es_old in html:
            html = html.replace(es_old, es_new, 1)
            changed += 1
        else:
            raise CommandError("조기종료 설명 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"{changed}곳에 이미지를 추가했습니다. ({skipped}곳은 이미 적용되어 건너뜀)"))
