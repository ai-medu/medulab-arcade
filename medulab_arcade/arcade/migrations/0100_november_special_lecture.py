import datetime
from zoneinfo import ZoneInfo

from django.db import migrations

TITLE = 'AI 활용 나만의 머그컵 만들기'


def add_lecture(apps, schema_editor):
    SpecialLecture = apps.get_model('arcade', 'SpecialLecture')
    if SpecialLecture.objects.filter(title=TITLE).exists():
        return
    SpecialLecture.objects.create(
        title=TITLE,
        summary='11월 특강 · AI로 디자인하고 나만의 머그컵을 만들어요',
        description=(
            '📅 일시: 11월 21일(토) 13:00~14:30\n\n'
            '📍 장소: 메듀랩 AI로봇코딩학원\n'
            '광주 서구 화개중앙로 51, 5층 (화개초 앞)'
        ),
        lecture_at=datetime.datetime(2026, 11, 21, 13, 0, tzinfo=ZoneInfo('Asia/Seoul')),
        location='메듀랩 AI로봇코딩학원 (광주 서구 화개중앙로 51, 5층 · 화개초 앞)',
        capacity=0, base_price=20000, friend_discount=10000, registration_open=True, is_active=True,
    )


def remove_lecture(apps, schema_editor):
    apps.get_model('arcade', 'SpecialLecture').objects.filter(title=TITLE, reservations__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0099_special_lecture_nav'),
    ]

    operations = [
        migrations.RunPython(add_lecture, remove_lecture),
    ]
