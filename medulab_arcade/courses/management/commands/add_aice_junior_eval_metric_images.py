from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_05_04"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;">'
)

ACRONYM_NOTE = (
    "<br><br><strong>MAE</strong> = Mean Absolute Error(평균 절대 오차), "
    "<strong>MSE</strong> = Mean Squared Error(평균 제곱 오차), "
    "<strong>RMSE</strong> = Root Mean Squared Error(MSE에 제곱근을 씌운 값)의 줄임말이에요."
)


class Command(BaseCommand):
    help = (
        "AICE Junior 회귀 프로젝트 'AI 모델 학습' 문항의 '공부가 잘 됐는지 확인하는 방법' "
        "아코디언(교차검증/MAE·MSE·RMSE/R²)에 이미지와 약자 설명을 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        # 1) 교차검증 (K-fold)
        cv_desc = (
            "데이터를 K조각으로 나눠서, <strong>한 조각은 시험용, 나머지는 공부용</strong>으로 번갈아 "
            "바꿔가며 K번 시험을 봐요. 그 점수들의 평균으로 실력을 확인해요."
        )
        cv_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "k_fold_cv.jpg", alt="K-fold 교차검증 예시")
        cv_old = f'<div style="font-size:15px;color:var(--text-secondary);">{cv_desc}</div></div>'
        cv_new = f'<div style="font-size:15px;color:var(--text-secondary);">{cv_desc}</div>{cv_img}</div>'
        if cv_img in html:
            skipped += 1
        elif cv_old in html:
            html = html.replace(cv_old, cv_new, 1)
            changed += 1
        else:
            raise CommandError("교차검증 설명 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        # 2) MAE·MSE·RMSE (이미지 + 약자 설명 추가)
        err_desc = (
            "예측값과 실제값이 <strong>얼마나 차이 나는지</strong>를 재는 점수예요. "
            "숫자가 <strong>작을수록 좋은 모델</strong>이에요."
        )
        err_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "error_metrics.jpg", alt="오차 지표(MAE·MSE·RMSE) 예시")
        err_old = f'<div style="font-size:15px;color:var(--text-secondary);">{err_desc}</div></div>'
        err_new = (
            f'<div style="font-size:15px;color:var(--text-secondary);">{err_desc}{ACRONYM_NOTE}</div>'
            f'{err_img}</div>'
        )
        if err_img in html or ACRONYM_NOTE in html:
            skipped += 1
        elif err_old in html:
            html = html.replace(err_old, err_new, 1)
            changed += 1
        else:
            raise CommandError("MAE·MSE·RMSE 설명 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        # 3) R² (결정계수)
        r2_desc = (
            "0~1 사이의 숫자로, 모델이 데이터를 얼마나 잘 설명하는지 나타내요. "
            "<strong>1에 가까울수록 좋은 모델</strong>이에요. (0.97이 0.65보다 훨씬 잘 설명해요.)"
        )
        r2_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "r_squared_comparison.jpg", alt="R²(결정계수) 비교 예시")
        r2_old = f'<div style="font-size:15px;color:var(--text-secondary);">{r2_desc}</div></div>'
        r2_new = f'<div style="font-size:15px;color:var(--text-secondary);">{r2_desc}</div>{r2_img}</div>'
        if r2_img in html:
            skipped += 1
        elif r2_old in html:
            html = html.replace(r2_old, r2_new, 1)
            changed += 1
        else:
            raise CommandError("R²(결정계수) 설명 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"{changed}곳에 이미지/설명을 추가했습니다. ({skipped}곳은 이미 적용되어 건너뜀)"))
