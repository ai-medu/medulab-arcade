from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_03_04"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:480px;border-radius:10px;margin-top:10px;display:block;">'
)

TARGETS = [
    (
        "둘 중 하나를 고르는 문제(예: 합격/불합격)는 출력값을 0~1 사이로 바꿔주는 시그모이드를 사용해요. "
        "0.5 이상이면 1, 미만이면 0으로 판단해요.",
        "output_binary.jpg",
        "이진분류 시그모이드 예시",
    ),
    (
        "3개 이상 중 하나를 고르는 문제(예: 강아지/토끼/고양이)는 소프트맥스를 사용해요. 각 종류일 확률을 다 더하면 "
        "1이 되도록 계산해줘요. (예: 강아지 70%, 토끼 20%, 고양이 10%)",
        "output_multiclass.jpg",
        "다중분류 소프트맥스 예시",
    ),
    (
        "숫자를 그대로 맞히는 회귀 문제는 보통 출력층에 활성함수를 쓰지 않아요. (예측값이 항상 양수라면 렐루를 쓰기도 해요.)",
        "output_regression.jpg",
        "회귀 출력 예시",
    ),
]


class Command(BaseCommand):
    help = (
        "AICE Junior '활성함수' 문항의 '문제 유형에 따라 정해진 출력층 활성함수' 아코디언"
        "(이진분류/다중분류/회귀)에 각각 예시 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        for description, filename, alt in TARGETS:
            img_tag = IMG_TAG_TEMPLATE.format(src=IMG_BASE + filename, alt=alt)
            old = f'<div style="font-size:15px;color:var(--text-secondary);">{description}</div></div>'
            new = f'<div style="font-size:15px;color:var(--text-secondary);">{description}</div>{img_tag}</div>'

            if img_tag in html:
                skipped += 1
                continue
            if old not in html:
                raise CommandError(f"'{description[:20]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

            html = html.replace(old, new, 1)
            changed += 1

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"{changed}곳에 이미지를 추가했습니다. ({skipped}곳은 이미 적용되어 건너뜀)"))
