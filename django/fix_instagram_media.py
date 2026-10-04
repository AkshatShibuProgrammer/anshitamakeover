import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
django.setup()
from core.models import LookGroup, LookMediaItem

print("Fixing Instagram Media Items in Database...")

# 1. Update Bengali Bride (Kuhu)
kuhu_album = LookGroup.objects.filter(slug__contains='kuhu').first()
if kuhu_album:
    print(f"Found Kuhu Album: {kuhu_album.name}")
    # Ensure item 1 is purely an Instagram reel
    first_item = kuhu_album.media_items.first()
    if first_item:
        first_item.media_type = 'instagram'
        first_item.external_url = 'https://www.instagram.com/reel/Dap4JkvKL1E/'
        first_item.embed_code = 'Dap4JkvKL1E'
        first_item.title = 'Subho Drishti & Mukut Reveal Reel'
        first_item.video_file = None
        first_item.save()
        print("Updated Kuhu item 1 to Instagram Reel Dap4JkvKL1E")

# 2. Update any other items where external_url is Instagram to media_type='instagram'
updated_count = 0
for itm in LookMediaItem.objects.all():
    if itm.external_url and 'instagram.com' in itm.external_url:
        if itm.media_type == 'video_file':
            itm.media_type = 'instagram'
            itm.video_file = None
            itm.save()
            updated_count += 1
            print(f"Updated item {itm.id} ({itm.title}) to media_type='instagram'")

print(f"Total items converted to Instagram: {updated_count}")

# 3. Print verification
for g in LookGroup.objects.all():
    reels = g.media_items.filter(media_type='instagram')
    if reels.exists():
        print(f"Album: {g.name}")
        for r in reels:
            print(f"  -> [Instagram] {r.title} | {r.external_url}")
