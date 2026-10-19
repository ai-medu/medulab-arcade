from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_01_01"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:360px;border-radius:10px;margin-top:10px;display:block;">'
)

# (고유하게 매칭되는 설명 문장, 이미지 파일명, alt 텍스트)
TRAITS = [
    (
        "센서와 카메라로 주변 환경(장애물, 건물 등)을 인식하고 이해합니다.",
        "trait_0_situational.jpg",
        "상황 인식 및 이해 예시",
    ),
    (
        "사람의 직접 조종 없이 스스로 경로를 계획하고 목표까지 도달합니다.",
        "trait_1_autonomy.jpg",
        "자율성 예시",
    ),
    (
        "다양한 데이터를 학습해 새로운 환경에 적응하고 이전의 오류를 개선합니다.",
        "trait_2_learning.jpg",
        "학습 예시",
    ),
    (
        "여러 경로 중 가장 효율적이고 안전한 경로(결정)를 선택합니다.",
        "trait_3_optimization.jpg",
        "최적화 예시",
    ),
    (
        "환경을 분석해 앞으로 어떤 행동을 해야 할지, 예상 결과가 어떨지 예측합니다.",
        "trait_4_prediction.jpg",
        "예측 예시",
    ),
]


class Command(BaseCommand):
    help = (
        "AICE Junior '인공지능 개념과 특성' 문항의 '인공지능의 5가지 특성' 아코디언에 "
        "각 특성을 보여주는 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        for description, filename, alt in TRAITS:
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

        self.stdout.write(self.style.SUCCESS(f"{changed}개 특성에 이미지를 추가했습니다. ({skipped}개는 이미 적용되어 건너뜀)"))
