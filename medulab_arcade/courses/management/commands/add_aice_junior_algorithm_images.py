from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:480px;border-radius:10px;margin-top:10px;display:block;">'
)

# item_key -> [(description, image filename, alt text), ...]
TARGETS = {
    "junior_05_04": [  # 회귀 (BMI 예측)
        (
            "데이터를 가장 잘 지나가는 <strong>직선 하나</strong>를 찾아서 예측해요. 점들과 가장 가까운 선일수록 잘 맞는 선이에요.",
            "regression_line.jpg",
            "선형 회귀 예시",
        ),
        (
            "예측할 데이터와 <strong>가장 비슷한 이웃 K개</strong>를 찾아서, 그 이웃들의 값을 평균 내어 예측해요.",
            "knn_scatter.jpg",
            "K-최근접 이웃 예시",
        ),
        (
            '"성별이 남자야? 몸무게가 60kg 이상이야?"처럼 <strong>스무고개 질문</strong>으로 그룹을 나누고, 마지막 그룹의 평균으로 예측해요.',
            "decision_tree.jpg",
            "의사결정트리 예시",
        ),
        (
            "의사결정트리를 <strong>여러 그루(숲)</strong> 만들어서 각자 예측하게 한 뒤, 그 <strong>평균</strong>을 최종 예측으로 삼아요.",
            "random_forest.jpg",
            "랜덤 포레스트 예시",
        ),
    ],
    "junior_06_04": [  # 분류 (동물 분류)
        (
            '이름에 "회귀"가 들어 있지만 <strong>분류하는 알고리즘</strong>이에요. 어떤 종류일 <strong>확률(0~1)</strong>을 계산해서, 0.5보다 크면 "맞다", 작으면 "아니다"로 나눠요.',
            "classification_boundary.jpg",
            "로지스틱 회귀 예시",
        ),
        (
            "예측할 동물과 <strong>가장 비슷한 이웃 K마리</strong>를 찾아서, 그 이웃들 중 <strong>가장 많은 종류</strong>로 분류해요. (친구 따라 강남 가는 방식!)",
            "knn_scatter.jpg",
            "K-최근접 이웃 예시",
        ),
        (
            '"털이 있어? 알을 낳아?"처럼 <strong>스무고개 질문</strong>을 따라 내려가서 마지막에 도착한 그룹으로 분류해요.',
            "decision_tree.jpg",
            "의사결정트리 예시",
        ),
        (
            "의사결정트리를 <strong>여러 그루(숲)</strong> 만들어서 각자 분류하게 한 뒤, <strong>가장 많이 나온 답</strong>(다수결)으로 최종 분류해요.",
            "random_forest.jpg",
            "랜덤 포레스트 예시",
        ),
    ],
}


class Command(BaseCommand):
    help = (
        "AICE Junior 회귀/분류 프로젝트의 알고리즘 5종 비교 아코디언(선형회귀·K-최근접·"
        "의사결정트리·랜덤포레스트)에 설명 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        total_changed = 0
        total_skipped = 0

        for item_key, targets in TARGETS.items():
            try:
                item = Item.objects.get(key=item_key)
            except Item.DoesNotExist:
                raise CommandError(f"key='{item_key}' 문항을 찾을 수 없습니다.")

            html = item.explain_html
            changed = 0
            skipped = 0

            for description, filename, alt in targets:
                img_tag = IMG_TAG_TEMPLATE.format(src=IMG_BASE + filename, alt=alt)
                old = f'<div style="font-size:15px;color:var(--text-secondary);">{description}</div></div>'
                new = f'<div style="font-size:15px;color:var(--text-secondary);">{description}</div>{img_tag}</div>'

                if img_tag in html:
                    skipped += 1
                    continue
                if old not in html:
                    raise CommandError(
                        f"[{item_key}] '{description[:20]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다."
                    )
                html = html.replace(old, new, 1)
                changed += 1

            item.explain_html = html
            item.save(update_fields=["explain_html"])
            self.stdout.write(f"[{item_key}] {changed}곳 추가, {skipped}곳 건너뜀")
            total_changed += changed
            total_skipped += skipped

        self.stdout.write(self.style.SUCCESS(f"총 {total_changed}곳에 이미지를 추가했습니다. ({total_skipped}곳은 이미 적용됨)"))
