# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

STATS_TABLE = """
<h3 style="margin-top:20px;">18개 칼럼 전체 통계로 한눈에 보기</h3>
<p style="color:var(--text-secondary);font-size:15px;">위에서는 몇 가지만 살펴봤으니, 이번엔 <strong>18개 칼럼 전부</strong>를 실제 데이터 기준으로 한 번에 정리해 볼게요. (동물 101종 기준)</p>
<table class="jz-table">
  <tr><th>칼럼명</th><th>번역</th><th>있음(1)</th><th>없음(0)</th><th>비율(있음)</th></tr>
  <tr><td>hair</td><td>털이 있나요?</td><td>43종</td><td>58종</td><td>43%</td></tr>
  <tr><td>feathers</td><td>깃털이 있나요?</td><td>20종</td><td>81종</td><td>20%</td></tr>
  <tr><td>eggs</td><td>알을 낳나요?(난생)</td><td>59종</td><td>42종</td><td>58%</td></tr>
  <tr><td>milk</td><td>젖을 먹이나요?(젖먹이)</td><td>41종</td><td>60종</td><td>41%</td></tr>
  <tr><td>airborne</td><td>하늘을 나나요?(공중비행)</td><td>24종</td><td>77종</td><td>24%</td></tr>
  <tr><td>aquatic</td><td>물속에 사나요?</td><td>36종</td><td>65종</td><td>36%</td></tr>
  <tr><td>predator</td><td>사냥을 하나요?(육식)</td><td>56종</td><td>45종</td><td>55%</td></tr>
  <tr><td>toothed</td><td>이빨이 있나요?</td><td>61종</td><td>40종</td><td>60%</td></tr>
  <tr><td>backbone</td><td>등뼈가 있나요?</td><td>83종</td><td>18종</td><td>82%</td></tr>
  <tr><td>breathes</td><td>폐로 숨 쉬나요?(호흡)</td><td>80종</td><td>21종</td><td>79%</td></tr>
  <tr><td>venomous</td><td>독이 있나요?</td><td>8종</td><td>93종</td><td>8%</td></tr>
  <tr><td>fins</td><td>지느러미가 있나요?</td><td>17종</td><td>84종</td><td>17%</td></tr>
  <tr><td>tail</td><td>꼬리가 있나요?</td><td>75종</td><td>26종</td><td>74%</td></tr>
  <tr><td>domestic</td><td>가축화된 동물인가요?(토종)</td><td>13종</td><td>88종</td><td>13%</td></tr>
  <tr><td>catsize</td><td>고양이 크기 이상인가요?</td><td>44종</td><td>57종</td><td>44%</td></tr>
</table>
<table class="jz-table">
  <tr><th>칼럼명</th><th>번역</th><th>값(숫자/텍스트)</th><th>설명</th></tr>
  <tr><td>legs</td><td>다리 개수</td><td>0, 2, 4, 6, 8</td><td>0개 23종, 2개 27종, 4개 38종, 6개 10종, 8개 2종 (대부분 4개)</td></tr>
  <tr><td>animal_name</td><td>동물 이름</td><td>텍스트 (101종 모두 다름)</td><td>그냥 이름표라서 통계로 의미가 없어요. AI 모델 Input에서는 제외해요.</td></tr>
  <tr><td style="color:#00ffb4;font-weight:700;">class_type</td><td style="color:#00ffb4;font-weight:700;">동물 분류(1~7)</td><td>숫자 1~7</td><td>포유류41·조류20·파충류5·어류13·양서류4·곤충류8·기타무척추10종. 🎯 Input이 아니라 Output(맞힐 대상)이에요.</td></tr>
</table>
"""

HEATMAP_WHY = """
<div class="jz-card" style="background:rgba(94,234,212,0.06);border-color:rgba(94,234,212,0.3);">
🤔 <strong>히트맵을 왜 쓸까요?</strong><br>
동물 데이터는 특징(칼럼)이 17개나 돼요. 이렇게 많으면 "어떤 특징끼리 서로 관련 있는지"를 하나하나 눈으로 비교하기 어려워요. <strong>히트맵은 모든 특징 쌍의 상관계수를 색깔 하나로 한 번에 보여주는 그래프</strong>예요. 색이 진할수록(특히 진한 빨강·진한 파랑) 관련이 깊고, 연할수록 관련이 적어요. 히트맵을 보면 <strong>"비슷한 정보를 담은 중복 특징"</strong>이나 <strong>"정답(동물 분류)과 특히 관련 깊은 특징"</strong>을 그래프 한 장으로 빠르게 찾을 수 있어요.
</div>
"""


class Command(BaseCommand):
    help = (
        "AICE Junior '동물 데이터 분석 및 가공'(junior_06_03) 문항에 18개 칼럼 전체 통계표와 "
        "히트맵을 쓰는 이유 설명을 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key="junior_06_03")
        except Item.DoesNotExist:
            raise CommandError("key='junior_06_03' 문항을 찾을 수 없습니다.")

        html = item.explain_html
        changed = 0

        if "18개 칼럼 전체 통계로 한눈에 보기" not in html:
            anchor = "<script>jzAccordionShow('j0603Look',0);</script>\n<h3>2) 그래프로 살펴보기</h3>"
            if anchor not in html:
                raise CommandError("'1) 데이터 살펴보기' 종료 지점을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
            html = html.replace(
                anchor,
                "<script>jzAccordionShow('j0603Look',0);</script>\n" + STATS_TABLE + "\n<h3>2) 그래프로 살펴보기</h3>",
                1,
            )
            changed += 1

        if "히트맵을 왜 쓸까요?" not in html:
            anchor2 = '<h3>2) 그래프로 살펴보기</h3>\n<p style="color:var(--text-secondary);font-size:15px;">아래 번호를 하나씩 눌러서 확인해 보세요.</p>'
            if anchor2 not in html:
                raise CommandError("'2) 그래프로 살펴보기' 안내 문구를 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
            html = html.replace(
                anchor2,
                '<h3>2) 그래프로 살펴보기</h3>' + HEATMAP_WHY + '\n<p style="color:var(--text-secondary);font-size:15px;">아래 번호를 하나씩 눌러서 확인해 보세요.</p>',
                1,
            )
            changed += 1

        if changed == 0:
            self.stdout.write(self.style.WARNING("이미 전체 통계표와 히트맵 설명이 추가되어 있습니다."))
            return

        item.explain_html = html
        item.save(update_fields=["explain_html"])
        self.stdout.write(self.style.SUCCESS(f"{changed}곳을 추가했습니다. (18개 칼럼 전체 통계표 / 히트맵 사용 이유)"))
