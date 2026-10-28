# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "junior_06_01"

ANCHOR = "jzAccordionShow('j0601Class',0);</script>"

BLOCK = """
<div class="jz-card">
<strong style="color:#fff;font-size:16px;">🤔 분류 기준에 딱 안 맞는 예외도 있어요</strong>
<p style="font-size:15px;color:var(--text-secondary);margin-top:8px;">겉모습이나 사는 곳만 보고 판단하면 헷갈리는 동물들이 있어요. 진짜 분류 기준은 <strong>새끼를 낳고 젖을 먹여 키우는지(포유류 여부)</strong>예요.</p>
<table class="jz-table" style="margin-top:10px;">
  <tr><th>동물</th><th>헷갈리는 점</th><th>진짜 분류</th></tr>
  <tr><td>🐋 고래</td><td>바다에 살고 물고기처럼 생겼어요</td><td>어류가 아니라 <strong style="color:#00ffb4;">포유류</strong> (새끼를 낳고 젖을 먹여요)</td></tr>
  <tr><td>🦇 박쥐</td><td>하늘을 날아다녀요</td><td>조류가 아니라 <strong style="color:#00ffb4;">포유류</strong> (깃털이 아니라 털이 있고, 새끼를 낳아요)</td></tr>
  <tr><td>🐧 펭귄</td><td>하늘을 날지 못해요</td><td>깃털이 있고 알을 낳는 <strong style="color:#00ffb4;">조류</strong> (날지 못해도 조류예요)</td></tr>
  <tr><td>🦆 오리너구리</td><td>포유류인데 알을 낳아요(난생)</td><td>젖을 먹여 키우는 <strong style="color:#00ffb4;">포유류</strong> (아주 드문 예외예요)</td></tr>
</table>
<p style="font-size:14.5px;color:var(--text-secondary);margin-top:8px;margin-bottom:0;">💡 "물에 살면 어류", "날면 조류"처럼 겉모습만으로 단정하지 말고, 새끼를 낳고 젖을 먹이는지를 먼저 확인하는 습관을 가져 보세요.</p>
</div>
"""


class Command(BaseCommand):
    help = (
        "AICE Junior '동물 분류' 문항(junior_06_01)에 겉모습만으로는 헷갈리는 포유류 예외 "
        "(고래, 박쥐, 펭귄, 오리너구리) 설명 카드를 '분류할 동물 7가지' 아코디언 뒤에 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "분류 기준에 딱 안 맞는 예외" in html:
            self.stdout.write(self.style.WARNING("이미 예외 설명 카드가 추가되어 있습니다."))
            return

        if ANCHOR not in html:
            raise CommandError("'동물 분류 7가지' 아코디언 끝 지점을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(ANCHOR, ANCHOR + BLOCK, 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS("포유류 예외(고래/박쥐/펭귄/오리너구리) 설명 카드를 추가했습니다."))
