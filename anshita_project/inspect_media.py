import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
django.setup()

from core.models import LookGroup, LookMediaItem, GalleryImage, StudioService

print("--- LOOK GROUPS ---")
for lg in LookGroup.objects.all():
    print(f"ID: {lg.id} | Name: {lg.name} | Category: {lg.category} | Active: {lg.is_active} | Cover: {lg.cover_image or lg.cover_image_url}")
    for itm in lg.media_items.all():
        print(f"   [Media {itm.id}] Type: {itm.media_type} | File: {itm.image_file or itm.thumbnail_url} | Title: {itm.title}")

print("\n--- GALLERY IMAGES ---")
for gi in GalleryImage.objects.all():
    print(f"ID: {gi.id} | Title: {gi.title} | Cat: {gi.category} | Active: {gi.is_active} | Img: {gi.image or gi.image_url}")

print("\n--- STUDIO SERVICES ---")
for ss in StudioService.objects.all():
    print(f"ID: {ss.id} | Title: {ss.title} | Cat: {ss.category} | Active: {ss.is_active} | LookGroupID: {ss.look_group_id}")
