# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "cos3_mock_12_04"

OLD_HTML = "<p>연도가 입력되면 is_leap(year) 함수로 윤년이면 윤년, 아니면 평년을 출력하세요.</p>"

NEW_HTML = """
<style>
.jz-card{background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:12px;padding:16px 18px;margin:14px 0;}
table.jz-table{width:100%;border-collapse:collapse;margin:12px 0;font-size:15px;}
table.jz-table th, table.jz-table td{border:1px solid var(--border);padding:8px 10px;text-align:left;color:#e5e7eb;}
table.jz-table th{background:rgba(255,255,255,0.06);color:#fff;}
</style>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">📅 윤년(leap year)이란?</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">1년은 보통 365일이지만, 지구가 태양을 도는 데 걸리는 시간은 정확히 365일이 아니라 <strong>약 365.2422일</strong>이에요. 이 오차를 보정하기 위해 몇 년에 한 번씩 2월을 29일까지 두는 해를 만드는데, 이 해를 <strong>윤년</strong>이라고 하고, 그렇지 않은 평범한 해(2월이 28일까지)를 <strong>평년</strong>이라고 해요.</p>
</div>
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🧮 윤년을 판단하는 규칙</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">연도(year)가 아래 조건 중 하나를 만족하면 윤년이에요.</p>
<table class="jz-table">
  <tr><th>조건</th><th>설명</th><th>예시</th></tr>
  <tr><td>4의 배수 <strong>이면서</strong> 100의 배수가 <strong>아님</strong></td><td>대부분의 윤년은 이 경우예요.</td><td>2024년(4의 배수, 100의 배수 아님) → 윤년</td></tr>
  <tr><td>400의 배수</td><td>100의 배수이면서 윤년인 특별한 경우예요.</td><td>2000년(400의 배수) → 윤년</td></tr>
</table>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">반대로 <strong>4의 배수가 아니거나</strong>, <strong>100의 배수이면서 400의 배수는 아닌 해</strong>는 평년이에요. (예: 2023년은 4의 배수가 아니라서 평년, 1900년은 100의 배수인데 400의 배수는 아니라서 평년)</p>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 파이썬 코드로 쓰면: <code>year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)</code> 이 참(True)이면 윤년이에요.</p>
</div>
<div class="jz-card" style="background:rgba(0,255,180,0.06);border-color:rgba(0,255,180,0.3);">
<strong style="color:#fff;font-size:16px;">📝 문제</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">연도가 입력되면 <code>is_leap(year)</code> 함수로 윤년이면 "윤년", 아니면 "평년"을 출력하세요.</p>
</div>
"""


class Command(BaseCommand):
    help = "COS Pro 3급 모의고사 '윤년/평년 판별' 문항(cos3_mock_12_04)에 윤년 규칙 설명을 추가합니다."

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        if item.explain_html.strip() != OLD_HTML:
            if "윤년(leap year)이란?" in item.explain_html:
                self.stdout.write(self.style.WARNING("이미 수정되어 있습니다."))
                return
            raise CommandError("기존 내용이 예상과 달라 안전하게 교체할 수 없습니다. 문항 내용을 확인해 주세요.")

        item.explain_html = NEW_HTML.strip()
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS("윤년/평년 설명을 추가했습니다."))
