from django.db import migrations


def rename_forward(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(url_name='board_contest', name='추천 공모전').update(name='대회 및 공모전')


def rename_backward(apps, schema_editor):
    NavItem = apps.get_model('arcade', 'NavItem')
    NavItem.objects.filter(url_name='board_contest', name='대회 및 공모전').update(name='추천 공모전')


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0096_signup_source_reason'),
    ]

    operations = [
        migrations.RunPython(rename_forward, rename_backward),
    ]
