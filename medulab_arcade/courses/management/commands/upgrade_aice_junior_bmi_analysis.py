from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_05_03"
IMG_BASE = "/static/arcade/img/aice_junior/"

MARKER = "<!-- scatter-section-v1 -->"

SCATTER_IMG = (
    f'<img src="{IMG_BASE}bmi_scatter_compare.jpg" alt="BMI 산점도 - 나이/키/몸무게 비교" '
    'style="width:100%;max-width:640px;border-radius:10px;margin-top:10px;display:block;">'
)
BOXPLOT_REAL_IMG = (
    f'<img src="{IMG_BASE}bmi_boxplot_real.jpg" alt="BMI 박스차트 실제 수치" '
    'style="width:100%;max-width:420px;border-radius:10px;margin-top:10px;display:block;">'
)
CORR_BAR_IMG = (
    f'<img src="{IMG_BASE}bmi_correlation_bar.jpg" alt="BMI 상관계수 실제 값" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;">'
)

NEW_SCATTER_SECTION = (
    f"{MARKER}\n"
    "<h3>2) 그래프로 살펴보기 - 산점도</h3>\n"
    '<p>BMI와 다른 칼럼들이 서로 어떤 관계가 있는지 산점도(점 그래프)로 먼저 확인해볼까요?</p>\n'
    '<div class="jz-card">\n'
    "<strong>나이 - BMI</strong>: 나이는 18~35세에 골고루 퍼져 있어서, 나이가 많다고 BMI가 커지거나 "
    "작아지는 뚜렷한 경향이 보이지 않아요.<br><br>\n"
    "<strong>키 - BMI</strong>: 점들이 넓게 퍼져 있어서 키와 BMI가 크게 관련 있어 보이지 않아요.<br><br>\n"
    "<strong>몸무게 - BMI</strong>: 몸무게가 늘어날수록 BMI도 함께 올라가는 뚜렷한 경향(직선에 가까운 모양)이 "
    "보여요. 셋 중에서 가장 뚜렷한 관계예요!\n"
    f"{SCATTER_IMG}</div>\n\n"
)

OLD_BOXPLOT_TAIL = (
    '<img src="/static/arcade/img/aice_junior/boxplot_anatomy.jpg" alt="박스차트 해부도" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;"></div>'
)
NEW_BOXPLOT_TAIL = (
    '<img src="/static/arcade/img/aice_junior/boxplot_anatomy.jpg" alt="박스차트 해부도" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;">'
    "<br>실제 BMI 데이터로 그려보면 Q1=18.28, 중앙값=19.30, Q3=20.36이고, 최솟값은 13.07, 최댓값은 "
    "26.02예요. 상자 밖 기준선(울타리)은 아래 15.16, 위 23.48인데, 이 기준을 벗어난 값은 이상치로 볼 "
    "수 있어요. 하지만 <strong>BMI가 15 이하인 건 저체중일 뿐 잘못된 데이터가 아니라서 지우지 않아요.</strong> "
    "참고로 이 데이터에는 BMI 30 이상인 비만 데이터가 아예 없어요."
    f"{BOXPLOT_REAL_IMG}</div>"
)

OLD_CORR_TAIL = (
    '<img src="/static/arcade/img/aice_junior/correlation_examples.jpg" '
    'alt="상관계수 예시 - 양의 상관/음의 상관/무관" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;"></div>'
)
NEW_CORR_TAIL = (
    '<img src="/static/arcade/img/aice_junior/correlation_examples.jpg" '
    'alt="상관계수 예시 - 양의 상관/음의 상관/무관" '
    'style="width:100%;max-width:520px;border-radius:10px;margin-top:10px;display:block;">'
    "<br>실제로 히트맵으로 확인해보면 BMI와 각 칼럼의 상관계수는 이래요.<br>"
    "• BMI - 나이: -0.0033 (거의 관계 없음)<br>"
    "• BMI - 키: -0.1212 (아주 약한 관계)<br>"
    "• BMI - 몸무게: 0.7956 (아주 강한 관계)<br><br>"
    "그래서 BMI와 가장 관련 높은 건 <strong>몸무게 &gt; 키 &gt; 나이</strong> 순이에요. 보통은 상관관계가 높은 "
    "칼럼을 우선 쓰지만, 칼럼 수가 많지 않기 때문에 몸무게·키·나이·성별을 모두 독립변수로 사용할 거예요."
    f"{CORR_BAR_IMG}</div>"
)

OLD_H3_BOX = "<h3>2) 그래프로 살펴보기 - 박스차트</h3>"
NEW_H3_BOX = "<h3>3) 그래프로 살펴보기 - 박스차트</h3>"
OLD_H3_CORR = "<h3>3) 두 값이 얼마나 관련 있을까? - 상관관계</h3>"
NEW_H3_CORR = "<h3>4) 두 값이 얼마나 관련 있을까? - 상관관계</h3>"
OLD_H3_FILL = "<h3>4) 빈칸(결측값) 채우기</h3>"
NEW_H3_FILL = "<h3>5) 빈칸(결측값) 채우기</h3>"


class Command(BaseCommand):
    help = (
        "AICE Junior 교재(179~192p)와 비교해 'BMI 예측 - 데이터 분석 및 가공' 문항에 빠져있던 "
        "산점도 분석, 박스차트/상관관계 실제 수치를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        if MARKER in html:
            skipped += 1
        else:
            if OLD_H3_BOX not in html:
                raise CommandError("박스차트 h3 제목을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
            html = html.replace(OLD_H3_BOX, NEW_SCATTER_SECTION + NEW_H3_BOX, 1)
            changed += 1

        if OLD_H3_CORR not in html and NEW_H3_CORR not in html:
            raise CommandError("상관관계 h3 제목을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
        if OLD_H3_CORR in html:
            html = html.replace(OLD_H3_CORR, NEW_H3_CORR, 1)
            changed += 1
        else:
            skipped += 1

        if OLD_H3_FILL not in html and NEW_H3_FILL not in html:
            raise CommandError("빈칸채우기 h3 제목을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
        if OLD_H3_FILL in html:
            html = html.replace(OLD_H3_FILL, NEW_H3_FILL, 1)
            changed += 1
        else:
            skipped += 1

        if BOXPLOT_REAL_IMG in html:
            skipped += 1
        elif OLD_BOXPLOT_TAIL in html:
            html = html.replace(OLD_BOXPLOT_TAIL, NEW_BOXPLOT_TAIL, 1)
            changed += 1
        else:
            raise CommandError("박스차트 이미지 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        if CORR_BAR_IMG in html:
            skipped += 1
        elif OLD_CORR_TAIL in html:
            html = html.replace(OLD_CORR_TAIL, NEW_CORR_TAIL, 1)
            changed += 1
        else:
            raise CommandError("상관관계 이미지 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"{changed}곳을 업그레이드했습니다. ({skipped}곳은 이미 적용되어 건너뜀)"))
