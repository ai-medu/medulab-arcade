# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from courses.models import Item

ITEM_KEY = "junior_05_05"

OLD_TABLE_ROWS = (
    "  <tr><td>키</td><td>170cm</td></tr>\n"
    "  <tr><td>몸무게</td><td>70kg</td></tr>\n"
)

NEW_TABLE_ROWS = (
    "  <tr><td>키</td><td>170cm "
    "<button type=\"button\" class=\"jz-copy-badge\" onclick=\"jzCopyVal(this,'66.93in')\">66.93in 복사</button></td></tr>\n"
    "  <tr><td>몸무게</td><td>70kg "
    "<button type=\"button\" class=\"jz-copy-badge\" onclick=\"jzCopyVal(this,'154.32lbs')\">154.32lbs 복사</button></td></tr>\n"
)

STYLE_MARK = ".jz-copy-badge{"
STYLE_BLOCK = (
    "\n.jz-copy-badge{display:inline-block;margin-left:8px;border:1px solid rgba(0,255,180,0.4);"
    "background:rgba(0,255,180,0.08);color:#00ffb4;border-radius:999px;padding:3px 10px;"
    "font-size:12.5px;font-weight:700;cursor:pointer;}\n"
    ".jz-copy-badge:hover{background:rgba(0,255,180,0.18);}\n"
)
STYLE_ANCHOR = "table.jz-table th{background:rgba(255,255,255,0.06);color:#fff;}\n</style>"

SCRIPT_MARK = "function jzCopyVal("
SCRIPT_BLOCK = """
<script>
function jzCopyVal(btn, text){
  var original = btn.textContent;
  function done(ok){
    btn.textContent = ok ? '✅ 복사됨!' : '복사 실패';
    setTimeout(function(){ btn.textContent = original; }, 1200);
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function(){ done(true); }).catch(function(){ done(false); });
  } else {
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(true); } catch (e) { done(false); }
    document.body.removeChild(ta);
  }
}
</script>
"""


class Command(BaseCommand):
    help = (
        "AICE Junior 'AI 모델 활용' 문항의 입력정보 표(키 170cm, 몸무게 70kg) 옆에 "
        "인치/파운드 값을 누르면 복사되는 배지를 추가합니다."
    )

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(key=ITEM_KEY)
        except Item.DoesNotExist:
            raise CommandError(f"key='{ITEM_KEY}' 문항을 찾을 수 없습니다.")

        html = item.explain_html

        if "jz-copy-badge" in html:
            self.stdout.write(self.style.WARNING("이미 복사 배지가 추가되어 있습니다."))
            return

        if STYLE_ANCHOR not in html:
            raise CommandError("스타일 블록 끝 지점을 찾지 못했습니다.")
        html = html.replace(STYLE_ANCHOR, STYLE_BLOCK.rstrip("\n") + "\n" + STYLE_ANCHOR, 1)

        if OLD_TABLE_ROWS not in html:
            raise CommandError("키/몸무게 표 행을 찾지 못했습니다. 문항 내용이 변경되었을 수 있습니다.")
        html = html.replace(OLD_TABLE_ROWS, NEW_TABLE_ROWS, 1)

        html = html + SCRIPT_BLOCK

        item.explain_html = html
        item.save(update_fields=["explain_html"])

        self.stdout.write(self.style.SUCCESS("키/몸무게 옆 인치/파운드 복사 배지를 추가했습니다."))
