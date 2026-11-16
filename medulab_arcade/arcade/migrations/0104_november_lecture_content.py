from django.db import migrations

TITLE = 'AI 활용 나만의 머그컵 만들기'

CONTENT = (
    'AI 이미지 생성 도구로 나만의 그림과 문구를 디자인하고, 그 디자인을 머그컵에 담아 '
    '세상에 하나뿐인 머그컵을 완성하는 체험형 특강이에요.\n\n'
    '✔ AI에게 원하는 그림을 말로 설명(프롬프트)하는 방법 배우기\n'
    '✔ 마음에 드는 디자인을 고르고 다듬기\n'
    '✔ 디자인을 머그컵에 담아 나만의 머그컵 완성하기'
)


def fill_content(apps, schema_editor):
    """11월 특강의 수업 내용이 비어 있을 때만 초안을 넣는다 (관리자가 이미 적은 내용은 건드리지 않는다)"""
    SpecialLecture = apps.get_model('arcade', 'SpecialLecture')
    for lecture in SpecialLecture.objects.filter(title=TITLE, description=''):
        lecture.description = CONTENT
        lecture.save(update_fields=['description'])


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0103_special_notify'),
    ]

    operations = [
        migrations.RunPython(fill_content, migrations.RunPython.noop),
    ]
