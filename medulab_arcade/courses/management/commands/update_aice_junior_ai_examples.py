from django.core.management.base import BaseCommand, CommandError

from courses.models import Item


ITEM_KEY = "junior_01_01"

OLD_BLOCK = """<div style="display:flex;flex-direction:column;gap:14px;margin:16px 0;">
  <div style="display:flex;gap:10px;">
    <div style="font-size:20px;">🔊</div>
    <div>
      <div style="font-weight:700;color:#fff;">인공지능 스피커</div>
      <div style="font-size:15px;color:var(--text-secondary);margin-top:4px;">호텔 방의 AI 스피커는 시설 위치를 안내하고, 가정의 AI 스피커는 음성 명령으로 블라인드를 걷거나 로봇청소기를 가동합니다.</div>
    </div>
  </div>
  <div style="display:flex;gap:10px;">
    <div style="font-size:20px;">🤖</div>
    <div>
      <div style="font-weight:700;color:#fff;">인공지능 로봇</div>
      <div style="font-size:15px;color:var(--text-secondary);margin-top:4px;">호텔 배달 로봇은 스스로 엘리베이터를 타고 장애물을 피해 이동해 방 번호를 인식하고 물품을 전달합니다.</div>
    </div>
  </div>
  <div style="display:flex;gap:10px;">
    <div style="font-size:20px;">🛍️</div>
    <div>
      <div style="font-weight:700;color:#fff;">인공지능 추천 시스템</div>
      <div style="font-size:15px;color:var(--text-secondary);margin-top:4px;">사용자의 과거 행동과 선호를 분석해 영상·상품을 개인 맞춤형으로 추천합니다. (넷플릭스, 온라인 쇼핑몰 등)</div>
    </div>
  </div>
  <div style="display:flex;gap:10px;">
    <div style="font-size:20px;">🚗</div>
    <div>
      <div style="font-weight:700;color:#fff;">자율주행 자동차</div>
      <div style="font-size:15px;color:var(--text-secondary);margin-top:4px;">센서로 수집한 데이터를 학습해 주변 환경을 인식하고 위험을 예측하여 속도·방향·브레이크를 스스로 제어합니다.</div>
    </div>
  </div>
</div>"""


def youtube_embed(video_id):
    return (
        '<div style="position:relative;width:100%;padding-top:56.25%;margin-top:12px;border-radius:10px;overflow:hidden;">'
        f'<iframe src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" '
        'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
        'referrerpolicy="strict-origin-when-cross-origin" '
        'allowfullscreen loading="lazy"></iframe>'
        "</div>"
    )


NEW_BLOCK = (
    '<p style="color:var(--text-secondary);font-size:15px;">아래 사례를 하나씩 눌러서 설명과 영상을 확인해 보세요.</p>\n'
    '<div id="j0100Cases" style="margin:14px 0;">\n'
    '  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">\n'
    '    <button type="button" class="jz-step-btn" data-step="0" onclick="jzAccordionShow(\'j0100Cases\',0)" '
    'style="flex:1;min-width:110px;border:1px solid var(--border);background:rgba(255,255,255,0.04);color:#e5e7eb;'
    'border-radius:8px;padding:10px 8px;font-weight:700;font-size:14px;cursor:pointer;">🔊 AI 스피커</button>\n'
    '    <button type="button" class="jz-step-btn" data-step="1" onclick="jzAccordionShow(\'j0100Cases\',1)" '
    'style="flex:1;min-width:110px;border:1px solid var(--border);background:rgba(255,255,255,0.04);color:#e5e7eb;'
    'border-radius:8px;padding:10px 8px;font-weight:700;font-size:14px;cursor:pointer;">🤖 AI 로봇</button>\n'
    '    <button type="button" class="jz-step-btn" data-step="2" onclick="jzAccordionShow(\'j0100Cases\',2)" '
    'style="flex:1;min-width:110px;border:1px solid var(--border);background:rgba(255,255,255,0.04);color:#e5e7eb;'
    'border-radius:8px;padding:10px 8px;font-weight:700;font-size:14px;cursor:pointer;">🛍️ 추천 시스템</button>\n'
    '    <button type="button" class="jz-step-btn" data-step="3" onclick="jzAccordionShow(\'j0100Cases\',3)" '
    'style="flex:1;min-width:110px;border:1px solid var(--border);background:rgba(255,255,255,0.04);color:#e5e7eb;'
    'border-radius:8px;padding:10px 8px;font-weight:700;font-size:14px;cursor:pointer;">🚗 자율주행차</button>\n'
    '  </div>\n'
    '  <div class="jz-card" style="margin:0;">\n'
    '    <div class="jz-step-body" style="">\n'
    '      <div style="font-weight:700;color:#fff;font-size:16px;margin-bottom:6px;">🔊 인공지능 스피커</div>\n'
    '      <div style="font-size:15px;color:var(--text-secondary);">호텔 방의 AI 스피커는 시설 위치를 안내하고, '
    '가정의 AI 스피커는 음성 명령으로 블라인드를 걷거나 로봇청소기를 가동합니다.</div>\n'
    f'      {youtube_embed("mvtyBXAsuwY")}\n'
    '    </div>\n'
    '    <div class="jz-step-body" style="display:none;">\n'
    '      <div style="font-weight:700;color:#fff;font-size:16px;margin-bottom:6px;">🤖 인공지능 로봇</div>\n'
    '      <div style="font-size:15px;color:var(--text-secondary);">호텔 배달 로봇은 스스로 엘리베이터를 타고 '
    '장애물을 피해 이동해 방 번호를 인식하고 물품을 전달합니다.</div>\n'
    f'      {youtube_embed("Bbir5cG9Tc8")}\n'
    '    </div>\n'
    '    <div class="jz-step-body" style="display:none;">\n'
    '      <div style="font-weight:700;color:#fff;font-size:16px;margin-bottom:6px;">🛍️ 인공지능 추천 시스템</div>\n'
    '      <div style="font-size:15px;color:var(--text-secondary);">사용자의 과거 행동과 선호를 분석해 영상·상품을 '
    '개인 맞춤형으로 추천합니다. (넷플릭스, 온라인 쇼핑몰 등)</div>\n'
    '    </div>\n'
    '    <div class="jz-step-body" style="display:none;">\n'
    '      <div style="font-weight:700;color:#fff;font-size:16px;margin-bottom:6px;">🚗 자율주행 자동차</div>\n'
    '      <div style="font-size:15px;color:var(--text-secondary);">센서로 수집한 데이터를 학습해 주변 환경을 '
    '인식하고 위험을 예측하여 속도·방향·브레이크를 스스로 제어합니다.</div>\n'
    f'      {youtube_embed("brRRnmKzKNA")}\n'
    '    </div>\n'
    '  </div>\n'
    '</div>'
)


class Command(BaseCommand):
    help = (
        "AICE Junior '인공지능 개념과 특성' 문항의 4가지 사례를 "
        "하나씩 눌러 설명과 영상을 볼 수 있는 아코디언 형태로 교체합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")
        except Item.MultipleObjectsReturned:
            raise CommandError(f"key='{ITEM_KEY}' 문항이 여러 개 있습니다. 수동으로 확인해 주세요.")

        if NEW_BLOCK in item.explain_html:
            self.stdout.write(self.style.WARNING("이미 아코디언 형태로 수정되어 있습니다."))
            return

        if OLD_BLOCK not in item.explain_html:
            raise CommandError("기존 사례 블록을 찾지 못했습니다. 문항 내용이 이미 변경되었을 수 있습니다.")

        item.explain_html = item.explain_html.replace(OLD_BLOCK, NEW_BLOCK, 1)
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS(f"'{item.title}' 문항의 사례 영역을 아코디언+영상 형태로 교체했습니다."))
