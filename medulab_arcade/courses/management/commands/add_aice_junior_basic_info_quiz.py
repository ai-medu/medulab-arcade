from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_05_03"

ANCHOR = "jzAccordionShow('j0503Look',0);</script>"

QUIZ_BLOCK = """
<h3>배운 내용 확인하기 - 기초 정보</h3>
<div class="jz-card">
  <div class="jz-quiz-title">Q5-4. '몸무게[Weight(kg)]' 칼럼에서 최솟값은 얼마인가요?</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
    <input type="text" id="j0504Answer" placeholder="숫자만 입력 (예: 35.39)" style="flex:1;min-width:140px;padding:10px 14px;border-radius:8px;border:1px solid var(--border);background:rgba(255,255,255,0.05);color:#fff;font-size:15.5px;outline:none;">
    <button type="button" onclick="checkJ0503Blank('j0504Answer','j0504Result',35.39,'junior_05_03')" style="border:none;border-radius:8px;padding:10px 20px;background:var(--accent-green);color:#03140e;font-weight:800;font-size:15.5px;cursor:pointer;white-space:nowrap;">✅ 채점하기</button>
  </div>
  <div id="j0504Result" class="jz-result"></div>
</div>

<div class="jz-card">
  <div class="jz-quiz-title">Q5-5. '키[Height(cm)]' 칼럼의 결측값은 몇 개인가요?</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
    <input type="text" id="j0505Answer" placeholder="숫자만 입력" style="flex:1;min-width:140px;padding:10px 14px;border-radius:8px;border:1px solid var(--border);background:rgba(255,255,255,0.05);color:#fff;font-size:15.5px;outline:none;">
    <button type="button" onclick="checkJ0503Blank('j0505Answer','j0505Result',19,'junior_05_03')" style="border:none;border-radius:8px;padding:10px 20px;background:var(--accent-green);color:#03140e;font-weight:800;font-size:15.5px;cursor:pointer;white-space:nowrap;">✅ 채점하기</button>
  </div>
  <div id="j0505Result" class="jz-result"></div>
</div>

<script>
function checkJ0503Blank(inputId, resultId, correct, itemId){
  var input = document.getElementById(inputId);
  var resultEl = document.getElementById(resultId);
  var val = parseFloat((input.value || '').trim());
  if (!isNaN(val) && Math.abs(val - correct) < 0.01) {
    input.style.borderColor = '#00ffb4';
    resultEl.textContent = '🎉 정답입니다! ' + correct + ' 입니다!';
    resultEl.style.color = '#00ffb4';
    var panel = document.getElementById('aicePanel');
    var csrfInput = document.querySelector('#aiceCsrfForm [name=csrfmiddlewaretoken]');
    if (panel && csrfInput) {
      fetch('/courses/api/grade/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfInput.value },
        body: 'item_id=' + encodeURIComponent(itemId) + '&selected_option=OK'
      }).catch(function(){});
    }
  } else {
    input.style.borderColor = '#ef4444';
    resultEl.textContent = '❌ 다시 한 번 생각해 보세요!';
    resultEl.style.color = '#f87171';
  }
}
</script>
"""


class Command(BaseCommand):
    help = (
        "AICE Junior 교재의 Q5-4(몸무게 최솟값), Q5-5(키 결측값 개수) 확인 문제가 "
        "'BMI 예측 - 데이터 분석 및 가공' 문항에 빠져 있어 '1) 데이터 살펴보기' 바로 뒤에 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "checkJ0503Blank" in html:
            self.stdout.write(self.style.WARNING("이미 Q5-4/Q5-5 문제가 추가되어 있습니다."))
            return

        if ANCHOR not in html:
            raise CommandError("'1) 데이터 살펴보기' 아코디언 끝 지점을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(ANCHOR, ANCHOR + QUIZ_BLOCK, 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS("Q5-4, Q5-5 확인 문제를 추가했습니다."))
