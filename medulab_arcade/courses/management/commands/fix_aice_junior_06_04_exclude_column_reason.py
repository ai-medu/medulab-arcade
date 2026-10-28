# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "junior_06_04"

OLD_BLOCK = (
    '<div class="jz-card">\n'
    '<strong style="color:#fff;font-size:16px;">🚫 Input에서 빼야 할 칼럼은 무엇일까요?</strong>\n'
    '<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">모델을 학습시킬 때 18개 칼럼을 전부 다 넣는 게 아니에요. 아래 기준으로 Input(참고 정보)에서 뺄 칼럼을 정해요.</p>\n'
    '<table class="jz-table" style="margin-top:8px;">\n'
    '  <tr><th>칼럼</th><th>처리</th><th>이유</th></tr>\n'
    '  <tr><td>animal_name (동물 이름)</td><td style="color:#f87171;font-weight:700;">❌ Input 제외</td><td>101마리 전부 이름이 달라서(텍스트), 분류를 예측하는 데 쓸 수 있는 "패턴"이 없어요. 오히려 이름 하나하나를 그대로 외워버려(과적합) 처음 보는 동물은 잘 못 맞히게 돼요.</td></tr>\n'
    '  <tr><td style="color:#00ffb4;font-weight:700;">class_type (동물 분류)</td><td style="color:#00ffb4;font-weight:700;">🎯 Output으로 지정</td><td>빼는 게 아니라 <strong>맞힐 대상(Output)</strong>으로 따로 지정해요. Input에 같이 두면 "정답을 보고 정답을 맞히는" 셈이 되어버려요.</td></tr>\n'
    '  <tr><td>나머지 16개 칼럼<br>(hair, feathers, eggs, milk, airborne, aquatic, predator, toothed, backbone, breathes, venomous, fins, legs, tail, domestic, catsize)</td><td style="color:#00ffb4;font-weight:700;">✅ Input 사용</td><td>동물의 실제 생김새·생활 방식을 나타내는 특징이라서, 분류를 예측하는 데 쓸모 있는 패턴이 들어 있어요.</td></tr>\n'
    '</table>\n'
    '<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 정리: <strong>animal_name은 제외, class_type은 Output, 나머지 16개는 Input</strong>으로 사용해요. 일반적으로 "이름"이나 "ID"처럼 하나하나 다 다른 텍스트 칼럼은 거의 항상 Input에서 빼야 해요.</p>\n'
    '</div>'
)

NEW_BLOCK = """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🚫 Input에서 빼야 할 칼럼은 무엇일까요?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">모델을 학습시킬 때 18개 칼럼을 전부 다 넣는 게 아니에요. <strong>animal_name(이름)</strong>은 101마리가 전부 다른 텍스트라서 패턴이 없어 항상 제외하고, <strong>class_type(동물 분류)</strong>은 빼는 게 아니라 Output(맞힐 대상)으로 따로 지정해요.</p>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">그런데 <strong>class_type의 숫자 1~7은 크기가 아니라 그냥 이름표라서</strong>, "class_type과 다른 칼럼의 상관관계"를 보는 건 의미가 없어요. 그래서 나머지 칼럼을 정할 때는 <strong>16개 입력 칼럼끼리의 히트맵(전체 상관관계)</strong>을 보고, 서로 비슷한 정보를 담고 있거나 다른 칼럼과도 관계가 약한 칼럼을 골라서 뺐어요.</p>
<table class="jz-table" style="margin-top:8px;">
  <tr><th>제외한 칼럼</th><th>히트맵에서 보이는 이유</th></tr>
  <tr><td>predator (육식)</td><td>다른 모든 칼럼과 상관계수가 대부분 ±0.3 이하로 전반적으로 약해요. 어떤 특징과도 뚜렷한 관계가 없어요.</td></tr>
  <tr><td>domestic (토종)</td><td>마찬가지로 다른 칼럼들과 상관계수가 대체로 낮아서(대부분 ±0.3 이하), 분류에 쓸 만한 정보가 적어요.</td></tr>
  <tr><td>feathers (깃털)</td><td>airborne(공중비행)과 0.657로 강하게 겹쳐요. 게다가 eggs(0.419)·toothed(-0.614)·hair(-0.428) 같은, <strong>이미 Input으로 남겨둔 칼럼들과 정보가 많이 겹쳐서</strong> 굳이 따로 넣지 않아도 돼요.</td></tr>
  <tr><td>airborne (공중비행)</td><td>feathers와 0.657로 강하게 겹치고, toothed와도 -0.594로 겹쳐요. feathers와 묶여서 "새 특징"을 중복으로 알려주는 칼럼이라 같이 뺐어요.</td></tr>
  <tr><td>fins (지느러미)</td><td>aquatic(물 서식)과 0.604, breathes(호흡)와 -0.617로 강하게 겹쳐요. <strong>aquatic과 breathes는 Input으로 남아 있어서</strong> 같은 정보를 fins로 또 알려줄 필요가 없어요.</td></tr>
  <tr><td>legs / legs_MS (다리 개수)</td><td>fins(-0.606, 같이 제외됨)와 backbone(-0.433, Input으로 남음)과 겹치는 정도가 있고, 그 외에는 대부분 약해요. 원본(legs)과 스케일 조정한 버전(legs_MS)은 같은 정보라서 같이 뺐어요.</td></tr>
</table>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 즉, <strong>① 아무 칼럼과도 관계가 약하거나, ② 이미 남겨둔 다른 칼럼과 거의 같은 정보를 주는(중복되는) 칼럼</strong>을 히트맵에서 찾아 제외하는 거예요. "상관계수가 몇 이상이면 남긴다"는 딱 떨어지는 공식은 없고, 히트맵 전체를 보고 사람이 판단해요.</p>
</div>
"""


class Command(BaseCommand):
    help = (
        "junior_06_04 문항의 'Input 제외 칼럼' 설명 카드를, 실제 전체 히트맵(16개 입력 칼럼 간 "
        "상관관계) 기준의 정확한 설명으로 교체합니다. (기존 카드는 '젖먹이와의 상관계수'만으로 "
        "설명해 실제 책의 선택과 맞지 않는 부분이 있었습니다.)"
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "히트맵에서 보이는 이유" in html:
            self.stdout.write(self.style.WARNING("이미 수정된 설명으로 교체되어 있습니다."))
            return

        if OLD_BLOCK not in html:
            raise CommandError("교체할 기존 카드를 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(OLD_BLOCK, NEW_BLOCK.strip(), 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS("Input 제외 칼럼 설명을 실제 히트맵 기준으로 정확하게 교체했습니다."))
