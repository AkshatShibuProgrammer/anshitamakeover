from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0012_sitesettings_facebook_url_sitesettings_youtube_url")]
    operations = [
        migrations.AddField(model_name="lookgroup", name="is_featured", field=models.BooleanField(default=False, help_text="Display in top spatial 3D card fan")),
        migrations.AddField(model_name="lookgroup", name="show_external_link_button", field=models.BooleanField(default=True, help_text='Allow visitors to see "Watch on Instagram / YouTube" buttons for this album')),
        migrations.AddField(model_name="lookgroup", name="slug", field=models.SlugField(blank=True, max_length=220, unique=True)),
        migrations.AddField(model_name="lookgroup", name="is_published", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="lookgroup", name="seo_description", field=models.CharField(blank=True, max_length=320)),
        migrations.AddField(model_name="lookgroup", name="seo_title", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="lookmediaitem", name="show_platform_link", field=models.BooleanField(default=True, help_text='Show "Open in Instagram/YouTube" badge for this item')),
        migrations.AddField(model_name="lookmediaitem", name="alt_text", field=models.CharField(blank=True, max_length=300)),
        migrations.AddField(model_name="lookmediaitem", name="consent_status", field=models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=20)),
        migrations.AddField(model_name="lookmediaitem", name="duration_seconds", field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="lookmediaitem", name="is_published", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="lookmediaitem", name="provider", field=models.CharField(blank=True, help_text="youtube, instagram, or upload", max_length=20)),
    ]
