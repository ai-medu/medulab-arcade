# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


class Command(BaseCommand):
    help = (
        "AICE Junior 'BMI 예측하기' 챕터의 데이터셋 칼럼 단위를 cm/kg에서 "
        "실제 배포되는 원본 데이터 단위인 Height(Inches)/Weight(Pounds)로 맞춥니다. "
        "(개인 BMI 계산기 등 일반 교육용 설명은 cm/kg을 그대로 유지합니다.)"
    )

    def handle(self, *args, **options):
        total_changed = 0
        total_skipped = 0

        # ---------- junior_05_02: 데이터 수집 ----------
        item = self._get(args, "junior_05_02")
        html = item.explain_html
        pairs = [
            (
                "※ 원래 데이터는 키가 인치, 몸무게가 파운드 단위인데, 우리가 쓰기 편하게 cm와 kg으로 바꿔서 사용해요.",
                "※ 이 데이터셋은 원래 단위인 키(인치)와 몸무게(파운드)를 그대로 사용해요.",
            ),
            (">몸무게 (70kg)</button>", ">몸무게 (154lbs)</button>"),
        ]
        changed, skipped = self._apply(html, pairs, item)
        total_changed += changed
        total_skipped += skipped

        # ---------- junior_05_03: 데이터 분석 및 가공 ----------
        item = self._get(args, "junior_05_03")
        html = item.explain_html
        pairs = [
            (
                "<strong>153cm ~ 191cm</strong> 사이이고, 평균(약 172cm) 근처 사람이 가장 많은 종 모양 분포예요. "
                "빈칸(결측값)이 <strong>19개</strong> 있어요.",
                "<strong>60.28in ~ 75.15in</strong> 사이이고, 평균(약 68.0in) 근처 사람이 가장 많은 종 모양 분포예요. "
                "빈칸(결측값)이 <strong>19개</strong> 있어요.",
            ),
            (
                "<strong>35kg ~ 78kg</strong> 사이이고, 빈칸이 <strong>16개</strong> 있어요.",
                "<strong>78.01lbs ~ 170.92lbs</strong> 사이이고, 빈칸이 <strong>16개</strong> 있어요.",
            ),
            (
                "Q5-4. '몸무게[Weight(kg)]' 칼럼에서 최솟값은 얼마인가요?",
                "Q5-4. '몸무게[Weight(Pounds)]' 칼럼에서 최솟값은 얼마인가요?",
            ),
            (
                'placeholder="숫자만 입력 (예: 35.39)"',
                'placeholder="숫자만 입력 (예: 78.01)"',
            ),
            (
                "checkJ0503Blank('j0504Answer','j0504Result',35.39,'junior_05_03')",
                "checkJ0503Blank('j0504Answer','j0504Result',78.01,'junior_05_03')",
            ),
            (
                "Q5-5. '키[Height(cm)]' 칼럼의 결측값은 몇 개인가요?",
                "Q5-5. '키[Height(Inches)]' 칼럼의 결측값은 몇 개인가요?",
            ),
        ]
        changed, skipped = self._apply(html, pairs, item)
        total_changed += changed
        total_skipped += skipped

        # ---------- junior_05_04: AI 모델 학습 ----------
        item = self._get(args, "junior_05_04")
        html = item.explain_html
        pairs = [
            (
                '"성별이 남자야? 몸무게가 60kg 이상이야?"처럼 <strong>스무고개 질문</strong>으로 그룹을 나누고, '
                "마지막 그룹의 평균으로 예측해요.",
                '"성별이 남자야? 몸무게가 130lbs 이상이야?"처럼 <strong>스무고개 질문</strong>으로 그룹을 나누고, '
                "마지막 그룹의 평균으로 예측해요.",
            ),
        ]
        changed, skipped = self._apply(html, pairs, item)
        total_changed += changed
        total_skipped += skipped

        self.stdout.write(self.style.SUCCESS(
            f"총 {total_changed}곳을 Inches/Pounds 단위로 변환했습니다. ({total_skipped}곳은 이미 적용되어 건너뜀)"
        ))

    def _get(self, args, key):
        try:
            return Item.objects.get(key=key)
        except Item.DoesNotExist:
            raise CommandError(f"key='{key}' 문항을 찾을 수 없습니다.")

    def _apply(self, html, pairs, item):
        changed = 0
        skipped = 0
        for old, new in pairs:
            if new in html:
                skipped += 1
                continue
            if old not in html:
                raise CommandError(
                    f"[{item.key}] '{old[:40]}...' 블록을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다."
                )
            html = html.replace(old, new, 1)
            changed += 1
        item.explain_html = html
        item.save(update_fields=["explain_html"])
        return changed, skipped
