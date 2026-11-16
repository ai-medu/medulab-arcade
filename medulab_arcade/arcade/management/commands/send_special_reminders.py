"""특강 하루 전 안내 알림톡 발송.

내일 열리는 특강의 확정된 예약자에게 안내 알림톡을 보낸다 (이미 안내한 예약은 건너뜀).
매일 저녁에 한 번 실행되도록 서버 스케줄(cron 등)에 등록해 두면 자동으로 나간다.
관리자 화면의 '참가 안내 알림 보내기' 버튼으로 수동 발송도 가능하다.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from arcade.models import SpecialLecture
from arcade.special_lecture import send_reminders


class Command(BaseCommand):
    help = '내일 열리는 특강의 확정 예약자에게 하루 전 안내 알림톡을 보냅니다.'

    def handle(self, *args, **options):
        tomorrow = timezone.localdate() + timedelta(days=1)
        lectures = [l for l in SpecialLecture.objects.filter(is_active=True) if timezone.localtime(l.lecture_at).date() == tomorrow]
        if not lectures:
            self.stdout.write('내일 열리는 특강이 없습니다.')
            return
        for lecture in lectures:
            sent, failed, reasons = send_reminders(lecture)
            self.stdout.write(f'{lecture.title}: 발송 {sent}건, 실패 {failed}건 {" / ".join(reasons)}')
