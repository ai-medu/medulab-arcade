from django.db import migrations


def remove_from_class_menu(apps, schema_editor):
    """'학생 작품 갤러리'는 플레이 메뉴(작품 전시관)로 옮겼으므로 클래스 메뉴에서 뺀다"""
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(section='learning', url_name='works_gallery').delete()


def restore(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    if not NavItem.objects.filter(section='learning', url_name='works_gallery').exists():
        NavItem.objects.create(section='learning', emoji='🎨', name='학생 작품 갤러리', url_name='works_gallery',
                               url_extra='', order=99)


class Migration(migrations.Migration):
    dependencies = [('arcade', '0115_nav_curriculum_roadmap_aice')]
    operations = [migrations.RunPython(remove_from_class_menu, restore)]
