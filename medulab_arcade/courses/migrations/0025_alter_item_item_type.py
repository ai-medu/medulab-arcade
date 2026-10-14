# Generated manually to add '블록코딩 미로' item_type choice

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0024_item_requires_coding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_type',
            field=models.CharField(choices=[('example', '예제'), ('objective', '객관식'), ('problem', '실습문제'), ('project', '프로젝트'), ('homework', '과제'), ('olympiad', '사고력 올림피아드'), ('block_coding', '블록코딩 미로')], default='example', max_length=50, verbose_name='유형'),
        ),
    ]
