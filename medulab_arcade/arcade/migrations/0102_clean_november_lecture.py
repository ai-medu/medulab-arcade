import datetime

from django.db import migrations

TITLE = 'AI 활용 나만의 머그컵 만들기'


def clean_lecture(apps, schema_editor):
    """11월 특강: 일시·장소가 상세 안내에 중복으로 적혀 있던 것을 지우고, 종료 시각과 썸네일 이모지를 채운다"""
    SpecialLecture = apps.get_model('arcade', 'SpecialLecture')
    for lecture in SpecialLecture.objects.filter(title=TITLE):
        if '일시: 11월 21일(토) 13:00~14:30' in (lecture.description or ''):
            lecture.description = ''
        if lecture.end_time is None:
            lecture.end_time = datetime.time(14, 30)
        if lecture.thumb_emoji == '🎤':
            lecture.thumb_emoji = '☕'
        lecture.save()


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0101_special_lecture_fields'),
    ]

    operations = [
        migrations.RunPython(clean_lecture, migrations.RunPython.noop),
    ]
