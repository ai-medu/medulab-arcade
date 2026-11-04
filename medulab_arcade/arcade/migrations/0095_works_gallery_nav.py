from django.db import migrations


def point_to_gallery_page(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(url_name='home', url_extra='#works').update(url_name='works_gallery', url_extra='')


def point_back_to_home(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(url_name='works_gallery', url_extra='').update(url_name='home', url_extra='#works')


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0094_invoice_absence_prededucted'),
    ]

    operations = [
        migrations.RunPython(point_to_gallery_page, point_back_to_home),
    ]
