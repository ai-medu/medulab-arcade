# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "junior_06_02"

OLD_TABLE = (
    '<table class="jz-table">\n'
    '  <tr><th>종류</th><th>칼럼</th></tr>\n'
    '  <tr><td>이름</td><td>동물 이름</td></tr>\n'
    '  <tr><td>있다(1) / 없다(0)로 적은 특징</td><td>털, 깃털, 난생(알 낳음), 젖먹이, 공중비행, 물 서식, 육식, 이빨, 등뼈, 호흡(폐), 독, 지느러미, 꼬리, 토종, 크기(고양이 이상)</td></tr>\n'
    '  <tr><td>숫자로 적은 특징</td><td>다리 개수 (0, 2, 4, 6, 8)</td></tr>\n'
    '  <tr><td style="color:#00ffb4;font-weight:700;">🎯 맞힐 것</td><td style="color:#00ffb4;font-weight:700;">동물 분류 (1~7)</td></tr>\n'
    '</table>'
)

NEW_TABLE = (
    '<p style="font-size:14.5px;color:var(--text-secondary);margin:4px 0 10px;">※ 책에는 한글로 설명돼 있지만, 실제 <strong>zoo.csv</strong> 파일의 칼럼 이름은 영어예요. 아래 표에서 영어 칼럼명과 뜻을 같이 확인해 보세요.</p>'
    '<table class="jz-table">\n'
    '  <tr><th>칼럼명 (zoo.csv)</th><th>번역(뜻)</th><th>값</th></tr>\n'
    '  <tr><td>animal_name</td><td>동물 이름</td><td>글자(텍스트)</td></tr>\n'
    '  <tr><td>hair</td><td>털이 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>feathers</td><td>깃털이 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>eggs</td><td>알을 낳나요? (난생)</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>milk</td><td>젖을 먹여 키우나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>airborne</td><td>하늘을 나나요? (공중비행)</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>aquatic</td><td>물속에서 사나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>predator</td><td>다른 동물을 사냥하나요? (육식)</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>toothed</td><td>이빨이 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>backbone</td><td>등뼈가 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>breathes</td><td>폐로 숨을 쉬나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>venomous</td><td>독이 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>fins</td><td>지느러미가 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>legs</td><td>다리가 몇 개인가요?</td><td>숫자 (0, 2, 4, 6, 8)</td></tr>\n'
    '  <tr><td>tail</td><td>꼬리가 있나요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>domestic</td><td>사람이 기르는 동물인가요? (가축화)</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td>catsize</td><td>고양이만 하거나 더 큰가요?</td><td>있음(1) / 없음(0)</td></tr>\n'
    '  <tr><td style="color:#00ffb4;font-weight:700;">🎯 class_type</td><td style="color:#00ffb4;font-weight:700;">동물 분류 (맞힐 대상)</td><td style="color:#00ffb4;font-weight:700;">숫자 1~7</td></tr>\n'
    '</table>'
)


class Command(BaseCommand):
    help = (
        "AICE Junior '동물 데이터 수집' 문항(junior_06_02)의 칼럼 설명 표를 교재의 한글 설명 대신 "
        "실제 zoo.csv 파일의 영어 칼럼명 + 한글 번역을 함께 보여주도록 교체합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "animal_name</td><td>동물 이름" in html:
            self.stdout.write(self.style.WARNING("이미 영어 칼럼명 표로 수정되어 있습니다."))
            return

        if OLD_TABLE not in html:
            raise CommandError("기존 칼럼 설명 표를 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")

        html = html.replace(OLD_TABLE, NEW_TABLE, 1)
        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS("칼럼 설명 표를 zoo.csv 실제 영어 칼럼명 + 번역으로 교체했습니다."))
