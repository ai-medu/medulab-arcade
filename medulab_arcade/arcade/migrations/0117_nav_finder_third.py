from django.db import migrations


def update_nav(apps, schema_editor):
    """클래스 메뉴: '프로그램 찾기' → '내게 맞는 수업', 세 번째 자리로"""
    NavItem = apps.get_model('arcade', 'NavItem')
    items = list(NavItem.objects.filter(section='learning').order_by('order', 'id'))
    finder = [i for i in items if i.url_name == 'program_finder']
    if not finder:
        return
    for i in finder:
        i.name = '내게 맞는 수업'
    rest = [i for i in items if i not in finder]
    ordered = rest[:2] + finder + rest[2:]
    for order, item in enumerate(ordered, start=1):
        item.order = order
        item.save()


def revert_nav(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(section='learning', url_name='program_finder').update(name='프로그램 찾기')


class Migration(migrations.Migration):
    dependencies = [('arcade', '0116_move_works_gallery_to_play')]
    operations = [migrations.RunPython(update_nav, revert_nav)]
