import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'django'))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
django.setup()

from core.models import LookGroup, CustomerReview

print("Updating LookGroup and Reviews for Kuhu Khare & Instagram Clients...")

# 1. Update LookGroup for Kuhu Khare
g = LookGroup.objects.filter(slug__contains='kuhu').first()
if g:
    g.client_name = 'Kuhu Khare'
    g.name = 'Kuhu Khare — Traditional Kolkata Banarasi & Chandan Art (Competition Artistry)'
    g.description = 'Award-winning Bengali bridal artistry featuring authentic Mukut placement, hand-painted Chandan geometry, and cry-proof HD complexion sculpted for bridal competition participation.'
    g.save()
    print(f"Updated LookGroup: {g.name} (Client: {g.client_name})")

# 2. Add / Update Kuhu Khare in CustomerReview
reviews_data = [
    {
        'client_name': 'Kuhu Khare',
        'event_type': 'Bengali Bride (Artistry Competition)',
        'location': 'Jabalpur / Showcase Arena',
        'rating': 5,
        'review_text': "Anshita's Bengali bride artistry for my competition participation was breathtaking — the intricate hand-painted Chandan motifs, authentic Mukut placement, and radiant 18-hour cry-proof base won unanimous admiration under stage lights. Truly the gold standard of bridal couture!",
        'wedding_date': 'Competition Showcase 2026',
        'is_verified': True,
        'avatar_url': '/static/core/images/curated/bengali_bride_mukut_chandan.jpg',
        'order': 1
    },
    {
        'client_name': 'Thakur Shivani',
        'event_type': 'Royal Sangeet & Engagement Glam',
        'location': 'Jabalpur (@shiviiiiii24)',
        'rating': 5,
        'review_text': "The dewy glass-skin finish and royal jewel-tone eye makeup Anshita sculpted lasted through 6 hours of high-energy dancing! Not a smudge or crease in sight. The warmth and attention to detail made me feel like royalty.",
        'wedding_date': 'Winter Celebrations',
        'is_verified': True,
        'avatar_url': '/static/core/images/curated/ig_post_DSrKrDHiLNPGzQHnwZkcRe3YUoC5fCc24nWZjQ0.jpg',
        'order': 2
    },
    {
        'client_name': 'Miss Rajak',
        'event_type': 'Imperial Crimson Vivah',
        'location': 'Jabalpur Heritage',
        'rating': 5,
        'review_text': "From dual dupatta draping to the delicate floral hair bun and velvet base, every single element was immaculate. Anshita understands cultural vivah traditions with effortless mastery. 10/10 recommendation!",
        'wedding_date': 'Royal Vivah 2026',
        'is_verified': True,
        'avatar_url': '/static/core/images/curated/royal_crimson_bride_main.jpg',
        'order': 3
    },
    {
        'client_name': 'Dr. Ritu Saxena',
        'event_type': 'Cathedral Reception & Glass-Skin Glam',
        'location': 'Jabalpur',
        'rating': 5,
        'review_text': "The soft porcelain glass skin for my reception felt so lightweight yet photographed like a luxury magazine cover. Guests kept asking who did my makeup all evening. World-class luxury artistry!",
        'wedding_date': 'Cathedral Reception',
        'is_verified': True,
        'avatar_url': '/static/core/images/curated/reception_ivory_bride.jpg',
        'order': 4
    },
    {
        'client_name': 'Priya Sharma',
        'event_type': 'Royal Vivah & Pheras',
        'location': 'Bhopal Heritage Palace',
        'rating': 5,
        'review_text': "She transformed me into the bride I always dreamed of being. 18 hours later through emotional tears and non-stop celebrations, my makeup remained completely immaculate. Anshita is a true master.",
        'wedding_date': 'Royal Vivah',
        'is_verified': True,
        'avatar_url': '/static/core/images/curated/fuchsia_emerald_bride_hq.jpg',
        'order': 5
    }
]

for item in reviews_data:
    r, created = CustomerReview.objects.update_or_create(
        client_name=item['client_name'],
        defaults=item
    )
    status = "Created" if created else "Updated"
    print(f"[{status}] Review for {r.client_name} ({r.event_type})")

print("All reviews successfully synced to database!")
