from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_02_03"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:480px;border-radius:10px;margin-top:10px;display:block;">'
)

# (고유하게 매칭되는 설명 문장, 이미지 파일명, alt 텍스트)
CHARTS = [
    (
        "점을 콕콕 찍어서 두 값 사이의 관계를 보여줘요. 예) 기온이 오를수록 입장객이 느는지 주는지",
        "chart_scatter.png",
        "산점도 예시 - 기온과 놀이공원 입장객수",
    ),
    (
        "색깔의 진하기로 두 값이 얼마나 관련 있는지 보여줘요. 진할수록 관련이 커요.",
        "chart_heatmap.png",
        "히트맵 예시 - 변수 간 상관관계",
    ),
    (
        "데이터가 어디에 몰려있는지, 유난히 튀는 값(이상치)이 있는지 한눈에 보여줘요.",
        "chart_boxplot.png",
        "박스차트 예시 - 요일별 입장객수 분포",
    ),
]


class Command(BaseCommand):
    help = (
        "AICE Junior '데이터 분석 및 가공' 문항의 '그래프로 살펴보기' 아코디언에 "
        "산점도/히트맵/박스차트 예시 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        for description, filename, alt in CHARTS:
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

        self.stdout.write(self.style.SUCCESS(f"{changed}개 그래프에 이미지를 추가했습니다. ({skipped}개는 이미 적용되어 건너뜀)"))
