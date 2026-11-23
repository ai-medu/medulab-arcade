"""관리자 알림을 텔레그램으로도 보낸다. 토큰/채팅 ID 가 설정되지 않으면 아무 일도 하지 않는다.
보내다 실패해도 원래 하던 일(접수, 결제 등)을 막지 않도록 백그라운드로 보내고 예외는 삼킨다."""
import json
import logging
import threading
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def _send(token, chat_ids, text):
    for chat_id in chat_ids:
        try:
            req = urllib.request.Request(
                f'https://api.telegram.org/bot{token}/sendMessage',
                data=json.dumps({'chat_id': chat_id, 'text': text, 'disable_web_page_preview': True}).encode(),
                headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=10).read()
        except Exception:
            logger.warning('텔레그램 알림 발송 실패 (chat_id=%s)', chat_id)


def send_telegram(text, url=''):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_ids = [c.strip() for c in getattr(settings, 'TELEGRAM_CHAT_IDS', '').split(',') if c.strip()]
    if not token or not chat_ids:
        return
    if url:
        text += f'\nhttps://medulab.kr{url}' if url.startswith('/') else f'\n{url}'
    threading.Thread(target=_send, args=(token, chat_ids, text), daemon=True).start()
