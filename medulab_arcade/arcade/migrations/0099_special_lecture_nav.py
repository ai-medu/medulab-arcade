from django.db import migrations


def add_nav_item(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    if NavItem.objects.filter(url_name='special_lecture_list').exists():
        return
    # 러닝센터에서 '교육프로그램'(첫 번째) 바로 아래에 끼워 넣는다
    for item in NavItem.objects.filter(section='learning', order__gte=2):
        item.order += 1
        item.save(update_fields=['order'])
    NavItem.objects.create(section='learning', emoji='🎤', name='특강프로그램', url_name='special_lecture_list',
                           url_extra='', order=2, is_active=True, is_accent=False, new_tab=False)


def remove_nav_item(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(url_name='special_lecture_list').delete()
    for item in NavItem.objects.filter(section='learning', order__gte=3):
        item.order -= 1
        item.save(update_fields=['order'])


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0098_special_lecture'),
    ]

    operations = [
        migrations.RunPython(add_nav_item, remove_nav_item),
    ]
