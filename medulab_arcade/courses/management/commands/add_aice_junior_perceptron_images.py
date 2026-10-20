from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_03_02"
IMG_BASE = "/static/arcade/img/aice_junior/"

IMG_TAG_TEMPLATE = (
    '<img src="{src}" alt="{alt}" '
    'style="width:100%;max-width:480px;border-radius:10px;margin-top:10px;display:block;">'
)


class Command(BaseCommand):
    help = (
        "AICE Junior '딥러닝 모델의 이해' 문항에 퍼셉트론 구조도와 "
        "다층 퍼셉트론(입력층/은닉층/출력층) 구조도 이미지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0
        skipped = 0

        perceptron_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "perceptron_diagram.jpg", alt="퍼셉트론 구조도")
        perceptron_old = (
            '계산 결과를 보고 "통과!" 또는 "통과 못함"을 결정하는 문지기예요.</div></div>\n'
            '</div>'
        )
        if perceptron_img in html:
            skipped += 1
        elif perceptron_old in html:
            html = html.replace(perceptron_old, perceptron_old + "\n" + perceptron_img, 1)
            changed += 1
        else:
            raise CommandError("퍼셉트론 입력값 카드 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        mlp_img = IMG_TAG_TEMPLATE.format(src=IMG_BASE + "mlp_layers_diagram.jpg", alt="다층 퍼셉트론 구조도")
        mlp_descriptions = [
            "문제(데이터)가 처음 들어오는 곳이에요. 예) 공부시간, 게임시간처럼 입력값 개수만큼 노드가 있어요.",
            '입력층과 출력층 사이에 숨어서 계산하는 층이에요. 은닉층이 <strong>2개 이상</strong>이면 "딥러닝"이라고 불러요!',
            "최종 결과(예측값)를 내보내는 곳이에요. 합격/불합격처럼 두 가지 중 하나를 고르는 문제는 출력 노드가 1개, "
            "강아지/토끼/고양이처럼 3가지 중 고르는 문제는 출력 노드가 3개예요.",
        ]
        for desc in mlp_descriptions:
            old = f'<div style="font-size:15px;color:var(--text-secondary);">{desc}</div></div>'
            new = f'<div style="font-size:15px;color:var(--text-secondary);">{desc}</div>{mlp_img}</div>'
            if mlp_img in html and old not in html:
                skipped += 1
                continue
            if old not in html:
                raise CommandError(f"'{desc[:20]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
            html = html.replace(old, new, 1)
            changed += 1

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"{changed}곳에 이미지를 추가했습니다. ({skipped}곳은 이미 적용되어 건너뜀)"))
