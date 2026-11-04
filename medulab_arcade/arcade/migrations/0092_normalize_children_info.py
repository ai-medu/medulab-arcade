import json

from django.db import migrations


def normalize(apps, schema_editor):
    """'[]' 처럼 문자열로 잘못 저장된 자녀 정보(children_info)를 실제 목록(없으면 None)으로 바로잡는다."""
    UserProfile = apps.get_model('arcade', 'UserProfile')
    for profile in UserProfile.objects.all():
        value = profile.children_info
        if not isinstance(value, str):
            continue
        for _ in range(3):
            if not isinstance(value, str):
                break
            try:
                value = json.loads(value)
            except ValueError:
                value = []
        value = [c for c in value if isinstance(c, dict)] if isinstance(value, list) else []
        profile.children_info = value or None
        profile.save(update_fields=['children_info'])


class Migration(migrations.Migration):

    dependencies = [
        ('arcade', '0091_parent_notify'),
    ]

    operations = [
        migrations.RunPython(normalize, migrations.RunPython.noop),
    ]
