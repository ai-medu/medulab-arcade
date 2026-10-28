# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ANCHOR = (
    'Output(맞힐 것)에는 <strong>"동물 분류(class_type)"</strong>를 넣고, 이름 칼럼(animal_name)은 빼줘요.\n'
    '</div>'
)

BLOCK = """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚫 Input에서 빼야 할 칼럼은 무엇일까요?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">모델을 학습시킬 때 18개 칼럼을 전부 다 넣는 게 아니에요. 아래 기준으로 Input(참고 정보)에서 뺄 칼럼을 정해요.</p>
<table class="jz-table" style="margin-top:8px;">
  <tr><th>칼럼</th><th>처리</th><th>이유</th></tr>
  <tr><td>animal_name (동물 이름)</td><td style="color:#f87171;font-weight:700;">❌ Input 제외</td><td>101마리 전부 이름이 달라서(텍스트), 분류를 예측하는 데 쓸 수 있는 "패턴"이 없어요. 오히려 이름 하나하나를 그대로 외워버려(과적합) 처음 보는 동물은 잘 못 맞히게 돼요.</td></tr>
  <tr><td style="color:#00ffb4;font-weight:700;">class_type (동물 분류)</td><td style="color:#00ffb4;font-weight:700;">🎯 Output으로 지정</td><td>빼는 게 아니라 <strong>맞힐 대상(Output)</strong>으로 따로 지정해요. Input에 같이 두면 "정답을 보고 정답을 맞히는" 셈이 되어버려요.</td></tr>
  <tr><td>나머지 16개 칼럼<br>(hair, feathers, eggs, milk, airborne, aquatic, predator, toothed, backbone, breathes, venomous, fins, legs, tail, domestic, catsize)</td><td style="color:#00ffb4;font-weight:700;">✅ Input 사용</td><td>동물의 실제 생김새·생활 방식을 나타내는 특징이라서, 분류를 예측하는 데 쓸모 있는 패턴이 들어 있어요.</td></tr>
</table>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 정리: <strong>animal_name은 제외, class_type은 Output, 나머지 16개는 Input</strong>으로 사용해요. 일반적으로 "이름"이나 "ID"처럼 하나하나 다 다른 텍스트 칼럼은 거의 항상 Input에서 빼야 해요.</p>
</div>
"""


class Command(BaseCommand):
    help = (
        "AICE Junior 'AI 모델 학습'(junior_06_04) 문항에 Input에서 제외할 칼럼(animal_name)과 "
        "Output으로 지정할 칼럼(class_type)에 대한 상세 설명 카드를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key="junior_06_04")
        except Item.DoesNotExist:
            raise CommandError("key='junior_06_04' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "Input에서 빼야 할 칼럼은 무엇일까요?" in html:
            self.stdout.write(self.style.WARNING("이미 예외 칼럼 설명 카드가 추가되어 있습니다."))
            return

        if ANCHOR not in html:
            raise CommandError("기준이 되는 안내 문구를 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(ANCHOR, ANCHOR + BLOCK, 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS("Input 제외 칼럼(animal_name)/Output 칼럼(class_type) 설명 카드를 추가했습니다."))
