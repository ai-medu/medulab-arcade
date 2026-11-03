from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from arcade.models import NotificationLog, TuitionInvoice
from arcade.parent_notify import send_invoice_notice


class Command(BaseCommand):
    help = ("납부 기한이 임박했거나 지난 미납 청구서의 학부모에게 결제 링크가 담긴 미납 안내 알림톡을 보냅니다. "
            "같은 청구서에는 --every 일 간격으로만 다시 보냅니다. (매일 한 번 실행하도록 예약해 두세요)")

    def add_arguments(self, parser):
        parser.add_argument('--before', type=int, default=3, help='납부 기한 며칠 전부터 안내할지 (기본 3일)')
        parser.add_argument('--every', type=int, default=3, help='같은 청구서에 다시 보내는 최소 간격(일, 기본 3일)')

    def handle(self, *args, **options):
        today = timezone.localdate()
        invoices = TuitionInvoice.objects.filter(
            status=TuitionInvoice.STATUS_UNPAID,
            due_date__lte=today + timedelta(days=options['before']),
        ).select_related('student__profile', 'school_class')

        since = today - timedelta(days=options['every'] - 1)
        sent_total = 0
        for invoice in invoices:
            recently = NotificationLog.objects.filter(
                invoice=invoice, status=NotificationLog.STATUS_SENT,
                kind__in=[NotificationLog.KIND_INVOICE, NotificationLog.KIND_REMINDER],
                created_at__date__gte=since,
            ).exists()
            if recently:
                continue
            sent_total += send_invoice_notice(invoice, kind=NotificationLog.KIND_REMINDER)
        self.stdout.write(self.style.SUCCESS(f'미납 안내 알림톡 {sent_total}건 발송'))
