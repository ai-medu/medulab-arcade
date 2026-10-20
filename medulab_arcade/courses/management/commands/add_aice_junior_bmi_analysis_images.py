from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_05_03"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;">'
)

# (anchor 끝 문장, 이미지 파일명, alt 텍스트)
TARGETS = [
    (
        "상자에서 너무 멀리 떨어진 값은 <strong>이상치</strong>로 표시돼요.",
        "boxplot_anatomy.jpg",
        "박스차트 해부도",
    ),
    (
        "<strong>0에 가까우면</strong> 서로 관계가 없어요.",
        "correlation_examples.jpg",
        "상관계수 예시 - 양의 상관/음의 상관/무관",
    ),
    (
        "글자(범주형) 데이터는 가장 많이 나온 값(최빈값)으로 채우는 게 보통이에요.",
        "missing_value_fill.jpg",
        "빈칸(결측값) 채우기 전후 비교",
    ),
]


class Command(BaseCommand):
    help = (
        "AICE Junior 'BMI 예측 - 데이터 분석 및 가공' 문항의 박스차트/상관관계/"
        "빈칸채우기 설명에 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        for anchor_end, filename, alt in TARGETS:
            img_tag = IMG_TAG_TEMPLATE.format(src=IMG_BASE + filename, alt=alt)
            old = f"{anchor_end}\n</div>"
            new = f"{anchor_end}\n{img_tag}</div>"

            if img_tag in html:
                skipped += 1
                continue
            if old not in html:
                raise CommandError(f"'{anchor_end[:20]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

            html = html.replace(old, new, 1)
            changed += 1

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"{changed}곳에 이미지를 추가했습니다. ({skipped}곳은 이미 적용되어 건너뜀)"))
