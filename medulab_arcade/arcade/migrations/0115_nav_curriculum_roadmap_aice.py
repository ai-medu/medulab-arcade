from django.db import migrations


def update_nav(apps, schema_editor):
    """클래스 메뉴: '프로그램 로드맵' → '커리큘럼 로드맵'으로 이름 변경해 맨 위로, 두 번째에 'AICE 과정 안내' 추가"""
    NavItem = apps.get_model('arcade', 'NavItem')
    items = list(NavItem.objects.filter(section='learning').order_by('order', 'id'))
    roadmap = [i for i in items if i.url_name == 'program_roadmap']
    for i in roadmap:
        i.name = '커리큘럼 로드맵'
    aice = [i for i in items if i.url_name == 'aice_info']
    if not aice:
        aice = [NavItem(section='learning', emoji='🎓', name='AICE 과정 안내', url_name='aice_info',
                        url_extra='', is_accent=False, new_tab=False, order=0)]
    rest = [i for i in items if i not in roadmap and i not in aice]
    for order, item in enumerate(roadmap + aice + rest, start=1):
        item.order = order
        item.save()


def revert_nav(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(section='learning', url_name='aice_info').delete()
    NavItem.objects.filter(section='learning', url_name='program_roadmap').update(name='프로그램 로드맵')


class Migration(migrations.Migration):
    dependencies = [('arcade', '0114_adminnotification')]
    operations = [migrations.RunPython(update_nav, revert_nav)]
