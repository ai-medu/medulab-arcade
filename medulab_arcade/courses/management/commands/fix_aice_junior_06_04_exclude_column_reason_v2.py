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
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;"><strong>animal_name(이름)</strong>은 101마리가 전부 다른 텍스트라서 패턴이 없어 항상 제외하고, <strong>class_type(동물 분류)</strong>은 빼는 게 아니라 Output(맞힐 대상)으로 따로 지정해요.</p>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">나머지 16개 칼럼은 <strong>"class_type과의 상관계수 절댓값"</strong>을 기준으로 골랐어요. class_type의 1~7은 순서가 있는 숫자가 아니라 이름표지만, <strong>"이 칼럼 값이 바뀔 때 동물 분류도 자주 같이 바뀌는가"</strong>를 보는 상관계수 절댓값 자체는 여전히 쓸모 있는 신호예요. 상관계수 절댓값이 <strong>약 0.3 이하</strong>인 칼럼은 제외하고, <strong>0.3보다 큰</strong> 칼럼만 Input으로 남겼어요.</p>
<table class="jz-table" style="margin-top:8px;">
  <tr><th>칼럼</th><th>class_type과의 상관계수</th><th>처리</th></tr>
  <tr><td>backbone (등뼈)</td><td>-0.829</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>milk (젖먹이)</td><td>-0.724</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>eggs (난생)</td><td>0.662</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>tail (꼬리)</td><td>-0.632</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>hair (털)</td><td>-0.562</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>catsize (크기)</td><td>-0.521</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>breathes (호흡)</td><td>-0.519</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>toothed (이빨)</td><td>-0.472</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>aquatic (물 서식)</td><td>0.327</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr><td>venomous (독)</td><td>0.321</td><td style="color:#00ffb4;font-weight:700;">✅ Input</td></tr>
  <tr style="background:rgba(239,68,68,0.06);"><td>feathers (깃털)</td><td>-0.198</td><td style="color:#f87171;font-weight:700;">❌ 제외</td></tr>
  <tr style="background:rgba(239,68,68,0.06);"><td>domestic (토종)</td><td>-0.181</td><td style="color:#f87171;font-weight:700;">❌ 제외</td></tr>
  <tr style="background:rgba(239,68,68,0.06);"><td>legs / legs_MS (다리 개수)</td><td>0.132</td><td style="color:#f87171;font-weight:700;">❌ 제외</td></tr>
  <tr style="background:rgba(239,68,68,0.06);"><td>fins (지느러미)</td><td>0.099</td><td style="color:#f87171;font-weight:700;">❌ 제외</td></tr>
  <tr style="background:rgba(239,68,68,0.06);"><td>predator (육식)</td><td>0.061</td><td style="color:#f87171;font-weight:700;">❌ 제외</td></tr>
  <tr style="background:rgba(239,68,68,0.06);"><td>airborne (공중비행)</td><td>0.023</td><td style="color:#f87171;font-weight:700;">❌ 제외</td></tr>
</table>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 Input으로 남긴 칼럼은 전부 상관계수 절댓값 <strong>0.3 이상</strong>, 제외한 칼럼은 전부 <strong>0.2 이하</strong>로 깔끔하게 나뉘어요. 이 0.3이라는 기준 자체도 "보통 이 정도면 쓸 만하다"는 관행적인 기준이라, 다른 사람이 분석했다면 문턱값이 조금 달라졌을 수도 있어요.</p>
</div>
"""


class Command(BaseCommand):
    help = (
        "junior_06_04 문항의 'Input 제외 칼럼' 설명 카드를, 실제 히트맵의 class_type 상관계수 "
        "절댓값(약 0.3 기준)으로 정확히 교체합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "class_type과의 상관계수" in html:
            self.stdout.write(self.style.WARNING("이미 수정된 설명으로 교체되어 있습니다."))
            return

        if OLD_BLOCK not in html:
            raise CommandError("교체할 기존 카드를 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(OLD_BLOCK, NEW_BLOCK.strip(), 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS("Input 제외 칼럼 설명을 class_type 상관계수(0.3 기준)로 정확하게 교체했습니다."))
