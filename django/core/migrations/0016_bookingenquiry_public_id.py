"""BookingEnquiry.public_id — opaque public reference (IDOR remediation, audit §7.1).

Written by hand (instead of ``makemigrations``) because adding a unique field
with a callable default to a populated table requires a three-step deploy:
add nullable → backfill a distinct UUID per row → enforce unique + default.
"""
import uuid

from django.db import migrations, models


def backfill_public_ids(apps, schema_editor):
    BookingEnquiry = apps.get_model('core', 'BookingEnquiry')
    for row in BookingEnquiry.objects.filter(public_id__isnull=True).iterator():
        row.public_id = uuid.uuid4()
        row.save(update_fields=['public_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_lookgroup_is_featured_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingenquiry',
            name='public_id',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(backfill_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='bookingenquiry',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
