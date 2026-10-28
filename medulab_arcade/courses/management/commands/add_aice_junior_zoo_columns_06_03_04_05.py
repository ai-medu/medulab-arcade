# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

PAIRS_BY_ITEM = {
    "junior_06_03": [
        ("cursor:pointer;\">물 서식</button>", "cursor:pointer;\">물 서식(aquatic)</button>"),
        ("cursor:pointer;\">육식</button>", "cursor:pointer;\">육식(predator)</button>"),
        ("cursor:pointer;\">이빨</button>", "cursor:pointer;\">이빨(toothed)</button>"),
        ("cursor:pointer;\">토종·크기</button>", "cursor:pointer;\">토종·크기(domestic·catsize)</button>"),
        ("cursor:pointer;\">동물 분류</button>", "cursor:pointer;\">동물 분류(class_type)</button>"),
        ("💧 물에 사는가?</div>", "💧 물에 사는가? (aquatic)</div>"),
        ("🍖 육식을 하는가?</div>", "🍖 육식을 하는가? (predator)</div>"),
        ("🦷 이빨이 있는가?</div>", "🦷 이빨이 있는가? (toothed)</div>"),
        ("📏 토종 / 크기</div>", "📏 토종(domestic) / 크기(catsize)</div>"),
        ("🏷️ 동물 분류별 개수</div>", "🏷️ 동물 분류(class_type)별 개수</div>"),
        (
            '<strong>"젖먹이"와 가장 관련이 깊은 특징은 "난생(알 낳음)"</strong>이고',
            '<strong>"젖먹이(milk)"와 가장 관련이 깊은 특징은 "난생(eggs, 알 낳음)"</strong>이고',
        ),
        (
            '예를 들어 등뼈 기준으로 보면',
            '예를 들어 등뼈(backbone) 기준으로 보면',
        ),
        (
            '<strong>"다리 개수"만 0~8까지 범위가 달라요.</strong>',
            '<strong>"다리 개수(legs)"만 0~8까지 범위가 달라요.</strong>',
        ),
        (
            'Q6-5. 동물 데이터에서 "젖먹이"와 "난생"의 상관계수가 -0.94라면',
            'Q6-5. 동물 데이터에서 "젖먹이(milk)"와 "난생(eggs)"의 상관계수가 -0.94라면',
        ),
        (
            'Q6-6. 다리 개수(0~8)를 0~1 사이 값으로',
            'Q6-6. 다리 개수(legs, 0~8)를 0~1 사이 값으로',
        ),
    ],
    "junior_06_04": [
        (
            'Output(맞힐 것)에는 <strong>"동물 분류"</strong>를 넣고, 이름 칼럼은 빼줘요.',
            'Output(맞힐 것)에는 <strong>"동물 분류(class_type)"</strong>를 넣고, 이름 칼럼(animal_name)은 빼줘요.',
        ),
    ],
    "junior_06_05": [
        ("<tr><td>꼬리</td><td>있다(1)</td></tr>", "<tr><td>꼬리(tail)</td><td>있다(1)</td></tr>"),
        ("<tr><td>등뼈</td><td>있다(1)</td></tr>", "<tr><td>등뼈(backbone)</td><td>있다(1)</td></tr>"),
        ("<tr><td>털</td><td>있다(1) · 깃털 모양</td></tr>", "<tr><td>털(hair)</td><td>있다(1) · 깃털 모양</td></tr>"),
        (
            "<tr><td>알을 낳는가(난생)</td><td>그렇다(1)</td></tr>",
            "<tr><td>알을 낳는가(eggs, 난생)</td><td>그렇다(1)</td></tr>",
        ),
        ("<tr><td>크기</td><td>고양이 이상(1)</td></tr>", "<tr><td>크기(catsize)</td><td>고양이 이상(1)</td></tr>"),
        (
            "<tr><td>폐로 숨 쉬는가(호흡)</td><td>그렇다(1)</td></tr>",
            "<tr><td>폐로 숨 쉬는가(breathes, 호흡)</td><td>그렇다(1)</td></tr>",
        ),
        (
            "<tr><td>젖을 먹이는가(젖먹이)</td><td>아니다(0)</td></tr>",
            "<tr><td>젖을 먹이는가(milk, 젖먹이)</td><td>아니다(0)</td></tr>",
        ),
        (
            "AIDU ez도 <strong>동물 분류 2(조류)</strong>로 예측했어요!",
            "AIDU ez도 <strong>동물 분류(class_type) 2(조류)</strong>로 예측했어요!",
        ),
    ],
}


class Command(BaseCommand):
    help = (
        "AICE Junior '동물 분류' 챕터의 데이터 분석/가공(06_03), AI 모델 학습(06_04), "
        "AI 모델 활용(06_05) 문항에서 한글로만 적힌 특징들을 실제 zoo.csv 영어 칼럼명과 함께 보여주도록 수정합니다."
    )

    def handle(self, *args, **options):
        total_items = 0
        total_changed = 0
        total_skipped = 0
        for key, pairs in PAIRS_BY_ITEM.items():
            try:
                item = Item.objects.get(key=key)
            except Item.DoesNotExist:
                raise CommandError(f"key='{key}' 문항을 찾을 수 없습니다.")

            html = item.explain_html
            changed = 0
            skipped = 0
            for old, new in pairs:
                if new in html:
                    skipped += 1
                    continue
                if old not in html:
                    raise CommandError(f"[{key}] '{old[:50]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
                html = html.replace(old, new, 1)
                changed += 1

            if changed:
                item.explain_html = html
                item.save(update_fields=["explain_html"])
                total_items += 1
            total_changed += changed
            total_skipped += skipped
            self.stdout.write(f"  - [{key}] {changed}곳 수정, {skipped}곳 이미 적용됨")

        self.stdout.write(self.style.SUCCESS(
            f"총 {total_items}개 문항에서 {total_changed}곳을 영어 칼럼명 병기로 수정했습니다. ({total_skipped}곳 건너뜀)"
        ))
