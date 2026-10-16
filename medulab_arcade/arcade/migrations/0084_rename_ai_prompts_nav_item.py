from django.db import migrations


def rename_forward(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(section='learning', url_name='ai_prompts').update(name='AI교육프로그램')


def rename_backward(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(section='learning', url_name='ai_prompts').update(name='AI 프롬프트 생성기')


class Migration(migrations.Migration):
    dependencies = [
        ('arcade', '0083_instagram_schedule_and_metrics'),
    ]

    operations = [
        migrations.RunPython(rename_forward, rename_backward),
    ]
