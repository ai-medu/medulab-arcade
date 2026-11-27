from django.core.management.base import BaseCommand
from django.utils import timezone

from arcade.models import NotificationLog, TuitionInvoice
from arcade.parent_notify import send_invoice_notice

# 발송이 계속 안 되는 청구서(번호 오류, 학부모 없음 등)를 매일 되풀이하지 않도록 이 일수만 시도한다
MAX_FAILED_DAYS = 3


class Command(BaseCommand):
    help = ("청구 안내를 보낸 뒤에도 미납인 청구서의 학부모에게 결제 링크가 담긴 미납 안내 알림톡을 보냅니다. "
            "마지막 안내에서 --every 일이 지나면 보내고, 청구서마다 --max 번까지만 보냅니다. "
            "(매일 한 번 실행하도록 예약해 두세요)")

    def add_arguments(self, parser):
        parser.add_argument('--every', type=int, default=10, help='마지막 안내 후 며칠 뒤에 보낼지 (기본 10일)')
        parser.add_argument('--max', type=int, default=2, help='청구서마다 미납 안내 최대 횟수 (기본 2번)')
        parser.add_argument('--dry-run', action='store_true', help='보내지 않고 대상만 확인')

    def handle(self, *args, **options):
        today = timezone.localdate()
        invoices = TuitionInvoice.objects.filter(
            status=TuitionInvoice.STATUS_UNPAID,
        ).select_related('student__profile', 'school_class').order_by('id')

        targets = sent_total = 0
        for invoice in invoices:
            if not self._due_for_reminder(invoice, today, options['every'], options['max']):
                continue
            targets += 1
            if options['dry_run']:
                self.stdout.write(f'대상: 청구서 {invoice.pk} (납부 기한 {invoice.due_date})')
                continue
            sent_total += send_invoice_notice(invoice, kind=NotificationLog.KIND_REMINDER)
        if options['dry_run']:
            self.stdout.write(f'{today} 미납 안내 대상 {targets}건 (발송하지 않음)')
        else:
            self.stdout.write(self.style.SUCCESS(f'{today} 미납 안내 알림톡 {sent_total}건 발송'))

    def _due_for_reminder(self, invoice, today, every, max_count):
        logs = NotificationLog.objects.filter(
            invoice=invoice, kind__in=[NotificationLog.KIND_INVOICE, NotificationLog.KIND_REMINDER])
        sent = logs.filter(status=NotificationLog.STATUS_SENT)
        last = sent.order_by('-created_at').first()
        if not last:
            return False   # 청구서 안내를 아직 보내지 않은 청구서는 대상이 아니다
        # 학부모가 여러 명이어도 하루 발송은 1번으로 센다 (직접 보낸 미납 안내도 횟수에 포함)
        reminder_days = sent.filter(kind=NotificationLog.KIND_REMINDER).values_list('target_date', flat=True)
        if len(set(reminder_days)) >= max_count:
            return False
        if (today - timezone.localtime(last.created_at).date()).days < every:
            return False
        failed_days = logs.exclude(status=NotificationLog.STATUS_SENT).filter(
            created_at__gt=last.created_at).values_list('target_date', flat=True)
        return len(set(failed_days)) < MAX_FAILED_DAYS
