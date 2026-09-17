"""
Seed data script for Anshita Makeover.
Run with: python manage.py shell < seed_data.py
Or: python seed_data.py (if DJANGO_SETTINGS_MODULE is set)
"""
import os
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from core.models import (
    SiteSettings, Artist, AcademyCourse, CourseModule,
    MakeupPackage, EventPackage, ServicePrice, CustomerReview, GalleryImage
)

print("[*] Seeding data for Anshita Makeover...")

# 1. Admin Users ('akshat' and 'admin')
for uname in ['akshat', 'admin']:
    u, created = User.objects.get_or_create(username=uname)
    u.set_password('Anshita@2026')
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.email = f"{uname}@anshitamakeover.com"
    u.save()
    print(f"[+] Superuser '{uname}' configured with password 'Anshita@2026'.")

# 2. Site Settings
site, _ = SiteSettings.objects.get_or_create(id=1)
site.whatsapp_number = '917879223442'
site.instagram_url = 'https://www.instagram.com/anshitamakeover21/'
site.coupon_auto_by_date = True
site.coupon_active = True
site.save()
print("[+] SiteSettings configured.")

# 3. Solo Artist Anshita (Active) & Others deactivated from public display
anshita_artist, _ = Artist.objects.get_or_create(slug='anshita')
anshita_artist.name = 'Anshita'
anshita_artist.bio = 'Founder & India Celebrated Bridal Couturier with 8+ years mastery and 500+ radiant brides.'
anshita_artist.specialities = 'makeup,hair,draping'
anshita_artist.order = 0
anshita_artist.is_active = True
anshita_artist.save()

# Deactivate secondary artists so they do not show in public roster
Artist.objects.exclude(slug='anshita').update(is_active=False)
print("[+] Solo brand Anshita configured as primary artist.")

# 4. Service Prices
prices_data = [
    ('makeup_hd', 35000.0, '35,000 (Bridal HD Suite)'),
    ('makeup_airbrush', 45000.0, '45,000 (Master Airbrush Bridal Suite)'),
    ('side_makeup_single', 6500.0, '6,500 (Single Side Makeup)'),
    ('side_makeup_group', 16500.0, '16,500 (Trio Bridesmaid Suite)'),
    ('hair_bridal', 3500.0, 'Starting 3,500'),
    ('beauty_prebridal', 8000.0, 'Starting 8,000'),
    ('outstation_day_fee', 18000.0, '18,000 / Day Surcharge'),
]

for svc, pr, lbl in prices_data:
    sp, _ = ServicePrice.objects.get_or_create(service=svc, defaults={'price': pr, 'price_label': lbl})
    sp.price = pr
    sp.price_label = lbl
    sp.save()
print(f"[+] {len(prices_data)} Service Prices seeded.")

# 5. Academy Course & Modules
course, _ = AcademyCourse.objects.get_or_create(
    slug='professional-makeup-artist-program',
    defaults={
        'name': 'Professional Makeup Artist Program',
        'tagline': 'Beginner to Professional Bridal Makeup Certification',
        'duration_days': 28,
        'duration_label': '4 Weeks',
        'hours_per_day': 3,
        'total_hours': 84,
        'course_fee': 30000.0,
        'gst_percent': 18,
        'registration_fee': 5000.0,
        'batch_start_note': 'Last Batch of 2026 — Starts 27th July',
        'is_featured': True,
        'is_active': True,
    }
)

modules_data = [
    ("Makeup Foundations", "Skin Prep, Face Shapes, Product Knowledge, Color Theory, Hygiene & Safety"),
    ("Professional Makeup Techniques", "Base Application, Contouring, Concealing, Eye Makeup, Lash Application, Lip Art"),
    ("Bridal Makeup Training", "HD Bridal, Engagement, Reception Looks, Luxury Finishing, Client Consultation"),
    ("Advanced Makeup Looks", "Soft Glam, Party Makeup, Smokey Eye, Dewy Skin, Nude & Contemporary Editorial Looks"),
    ("Bridal Styling & Draping", "Saree Draping, Dupatta Setting, Jewellery Placement & Bridal Styling"),
    ("Social Media & Portfolio", "Instagram Reels, Personal Branding, Portfolio Building, Viral Content Strategy"),
]

for idx, (title, desc) in enumerate(modules_data):
    CourseModule.objects.get_or_create(
        course=course,
        title=title,
        defaults={'description': desc, 'order': idx}
    )
print("[+] Academy Course & 6 Modules verified.")

# 6. Makeup Packages (Including Side Makeup)
# Clear old packages to refresh cleanly
MakeupPackage.objects.all().delete()

makeup_pkgs = [
    {
        'name': 'The Grand Royal Vivah Celebration (Complete 3-Event Bridal Suite)',
        'package_type': 'bridal',
        'tagline': 'Full Wedding Journey · Sacred Pheras, Evening Reception & Pre-Wedding Glam + 2 Free Side Makeups',
        'price': 58000.0,
        'price_label': '₹58,000',
        'features': "Event 1: Imperial Royal HD/Airbrush Bridal Makeover (Main Wedding & Sacred Pheras)\nEvent 2: Reception & Cocktail High-Glam Evening Makeover\nEvent 3: Engagement Ceremony or Sangeet Night Glamour\nVIP Family Bonus: 2 Complimentary Side Makeups for Mother & Sister (Value ₹13,000)\nLuxury International Kits (Dior, Charlotte Tilbury, Huda Beauty, TEMPTU Airbrush)\nCouture Hair Architecture & Floral Gajra Art for All 3 Functions\nDouble Dupatta Setting & Saree/Lehenga Precision Draping\nComplimentary Deluxe Touchup Kit with Custom Lip Decants\nStandalone A La Carte Value: ₹85,000 · You Save ₹27,000 (32% Off)",
        'is_featured': True,
        'order': 1,
    },
    {
        'name': 'Sacred Vivah & Reception Duo (2-Event Signature Package)',
        'package_type': 'bridal',
        'tagline': 'The Essential Two Major Milestones · Pheras Day & Evening Reception',
        'price': 45000.0,
        'price_label': '₹45,000',
        'features': "Event 1: Imperial Royal HD/Airbrush Bridal Suite for Sacred Pheras\nEvent 2: Reception & Cocktail Evening Glamour (Luminous Glass Skin)\n2 Distinct Couture Hairstyles (Royal Floral Bun + Hollywood Glam Waves)\nDouble Bridal Dupatta Pinning + Evening Gown/Saree Pleating\nCry-Proof & Sweat-Resistant Formulation (18+ Hours Longevity)\nComplimentary Touchup Decants & Oil-Blotting Sheets\nStandalone A La Carte Value: ₹60,000 · You Save ₹15,000 (25% Off)",
        'is_featured': True,
        'order': 2,
    },
    {
        'name': 'Pre-Wedding Rites & Festivities Trio (Haldi, Mehendi & Sangeet)',
        'package_type': 'engagement',
        'tagline': 'Complete Celebration Glam for Pre-Wedding Rituals & Ring Ceremony',
        'price': 34000.0,
        'price_label': '₹34,000',
        'features': "Event 1: Sangeet Night High-Energy Glam (Dance-Resistant Base)\nEvent 2: Engagement / Roka Ceremonial Glow (Dewy Glass Skin)\nEvent 3: Artisanal Gel Nail Extensions & Swarovski Crystal Set\n3 Signature Thermal Hairstyles (Textured Waves, Floral Braid, Half-Up)\nLehenga / Anarkali / Gown Draping & Dupatta Pinning for All 3 Events\nStandalone A La Carte Value: ₹47,500 · You Save ₹13,500 (~28% Off)",
        'is_featured': False,
        'order': 3,
    },
    {
        'name': 'Royal Family & Bridesmaids Ensemble (4-Person Group Suite)',
        'package_type': 'side_makeup',
        'tagline': 'Coordinated Bridal Entourage · Mothers, Sisters & Bridesmaids (Buy 3, 4th Free!)',
        'price': 19500.0,
        'price_label': '₹19,500',
        'features': "4 Complete Makeovers for Mother, Sisters & Bridesmaids (₹4,875 / Person)\nCamera-Ready Long-Wear HD Base Tailored to Face Shapes\n4 Customized Hairstyles (Textured Waves, Sleek Buns, Floral Accents)\nDupatta Setting, Saree Draping & Jewellery Alignment for All 4 Guests\nSynchronized Studio Team Execution (Zero Delays on Wedding Morning)\nStandalone A La Carte Value: ₹26,000 · You Save ₹6,500 (25% Off)",
        'is_featured': True,
        'order': 4,
    },
]

for mp in makeup_pkgs:
    MakeupPackage.objects.create(
        name=mp['name'],
        package_type=mp['package_type'],
        tagline=mp['tagline'],
        price=mp['price'],
        price_label=mp['price_label'],
        features=mp['features'],
        is_featured=mp['is_featured'],
        order=mp['order'],
        is_active=True
    )
print(f"[+] {len(makeup_pkgs)} Signature Packages (including Side Makeup) seeded.")

# 7. Customer Reviews
CustomerReview.objects.all().delete()
reviews_data = [
    {
        'client_name': 'Isha Dugar',
        'event_type': 'Traditional Bengali Bride',
        'location': 'Jabalpur / Kolkata',
        'rating': 5,
        'review_text': 'Anshita did my Bengali wedding look with the most intricate chandan artwork on my forehead. My makeup stayed pristine from the morning rituals till the midnight vidai without a single crease. She also styled my mother and two sisters beautifully. Highly recommend her for every bride!',
        'wedding_date': 'December 2025',
        'order': 1,
    },
    {
        'client_name': 'Dr. Neha Kapoor',
        'event_type': 'Destination Wedding Bride',
        'location': 'Udaipur / Outstation',
        'rating': 5,
        'review_text': 'We booked Anshita for our 3-day destination wedding in Udaipur. She and her assistant arrived right on schedule, managed my mehendi, sangeet, and royal bridal look effortlessly, plus 4 side makeups for my bridal party. Her calm demeanour and international products made me feel like royalty.',
        'wedding_date': 'January 2026',
        'order': 2,
    },
    {
        'client_name': 'Sanya Malhotra',
        'event_type': 'Engagement & Cocktail Glam',
        'location': 'Bhopal',
        'rating': 5,
        'review_text': 'The dewy glass skin base Anshita created for my engagement was out of this world! It photographed so naturally under halogen and flash lights. Even after 6 hours of dancing at the sangeet, not a hint of oil or cakeiness. Anshita di is a true artist.',
        'wedding_date': 'November 2025',
        'order': 3,
    },
    {
        'client_name': 'Riya Sen',
        'event_type': 'Royal Velvet Lehenga Bride',
        'location': 'Jabalpur',
        'rating': 5,
        'review_text': 'I wanted a deep maroon velvet bridal aesthetic with royal nath and bold eye art. Anshita understood my vision instantly and brought it to life. The saree and heavy dupatta draping were so secure that I could move freely all evening. Love her work!',
        'wedding_date': 'February 2026',
        'order': 4,
    },
    {
        'client_name': 'Ananya & Preeti Patel',
        'event_type': 'Bridal Suite & Bridesmaids Group',
        'location': 'Indore',
        'rating': 5,
        'review_text': 'We booked the full bridal suite along with the bridesmaid trio package for myself and my two sisters. We all received personalized looks matching our lehengas. None of us felt overdone — just enhanced, radiant, and elegant. 5 stars all the way!',
        'wedding_date': 'January 2026',
        'order': 5,
    },
]

for r in reviews_data:
    CustomerReview.objects.create(
        client_name=r['client_name'],
        event_type=r['event_type'],
        location=r['location'],
        rating=r['rating'],
        review_text=r['review_text'],
        wedding_date=r['wedding_date'],
        is_verified=True,
        is_active=True,
        order=r['order']
    )
print(f"[+] {len(reviews_data)} Customer Reviews seeded.")

# 8. Event Packages (Photography & Combos)
event_pkgs = [
    {
        'name': 'Photography — Royal Premium',
        'package_type': 'photography_premium',
        'description': 'Full wedding celebration coverage across India · All luxury inclusions',
        'price': 120000.0,
        'price_label': '1.2 Lakh',
        'features': "2 Senior Candid Photographers + 1 Traditional\n12+ Hours Comprehensive Day Coverage\nFull HD & 4K Video Cinematography\nDrone Aerial Perspectives & Cinematic Teaser\nPre-Wedding Couple Shoot\n500+ Retouched High-Res Photographs\nSame-Day Instagram Preview Reel\nPremium Velvet Hardbound Photobook\nOnline Private Gallery & Cloud Delivery\n7-Day Express Delivery Guarantee",
        'is_featured': True,
        'order': 1,
    },
    {
        'name': 'Photography — Standard Signature',
        'package_type': 'photography_standard',
        'description': 'Essential high-quality wedding coverage · Exceptional value',
        'price': 90000.0,
        'price_label': '90,000',
        'features': "1 Candid Photographer + 1 HD Videographer\n8 Hours Event Coverage\nCandid & Traditional Family Portraits\nFull HD Wedding Highlight Reel\n300+ Retouched Photographs\nStandard Hardcover Photo Album\nOnline Gallery Delivery",
        'is_featured': False,
        'order': 2,
    },
]

for ep in event_pkgs:
    pkg, _ = EventPackage.objects.get_or_create(name=ep['name'])
    pkg.package_type = ep['package_type']
    pkg.description = ep['description']
    pkg.price = ep['price']
    pkg.price_label = ep['price_label']
    pkg.features = ep['features']
    pkg.is_featured = ep['is_featured']
    pkg.order = ep['order']
    pkg.is_active = True
    pkg.save()
print("[+] Event Packages verified.")

# 9. Gallery Images (Curated Authentic Looks)
gallery_items = [
    {
        'file': 'bengali_bride_subho_drishti.jpg',
        'caption': 'Royal Bengali Bride — Subho Drishti Ritual with Hand-Painted Paan Leaf',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 1
    },
    {
        'file': 'bengali_bride_mukut_chandan.jpg',
        'caption': 'Sacred Chandan Artistry & Mukut Adornment — Haute Bridal Glow',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 2
    },
    {
        'file': 'bengali_bride_regal_portrait.jpg',
        'caption': 'Regal Heritage Portrait — Traditional Bengali Bridal Splendour',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 3
    },
    {
        'file': 'bengali_bride_paan_alta.jpg',
        'caption': 'Paan Leaf Adornment & Alta Hand Artistry — Timeless Indian Grace',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 4
    },
    {
        'file': 'bengali_bride_traditional_grace.jpg',
        'caption': 'Traditional Grace — Authentic Handcrafted Bridal Draping & Jewellery',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 5
    },
    {
        'file': 'bengali_bride_smiles.jpg',
        'caption': 'Joyful Radiance — Long-Lasting HD Base for All-Day Auspicious Rituals',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 6
    },
    {
        'file': 'bengali_bride_side_profile.jpg',
        'caption': 'Sculpted Profile & Winged Liner — Bespoke Royal Jewellery Setting',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 7
    },
    {
        'file': 'anshita_artistry_brush_action.jpg',
        'caption': 'Anshita in Studio Action — Master Stroke Bridal Transformation',
        'category': 'hair',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 8
    },
    {
        'file': 'anshita_masterclass_session.jpg',
        'caption': 'Live Couture Masterclass — Anshita Academy Hands-On Training',
        'category': 'academy',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 9
    },
    {
        'file': 'bride_reel_motion_glow.jpg',
        'caption': 'Cinematic Video Reel Glow — Photographed Flawlessly Under All Lights',
        'category': 'reception',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 10
    },
    {
        'file': 'engagement_lilac_glam.jpg',
        'caption': 'Modern Lilac Glass-Skin Engagement & Cocktail Radiance',
        'category': 'engagement',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 11
    },
    {
        'file': 'royal_maroon_bride.jpg',
        'caption': 'Imperial Deep Maroon Velvet Lehenga Bridal Look',
        'category': 'bridal',
        'ig_url': 'https://www.instagram.com/anshitamakeover21/',
        'order': 12
    },
]

media_gal = os.path.join(settings.MEDIA_ROOT, 'gallery')
os.makedirs(media_gal, exist_ok=True)
curated_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'images', 'curated')
static_img_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'images')

GalleryImage.objects.all().delete()
gal_count = 0
for item in gallery_items:
    fn = item['file']
    src = os.path.join(curated_dir, fn)
    if not os.path.exists(src):
        src = os.path.join(static_img_dir, fn)
    if os.path.exists(src):
        dst = os.path.join(media_gal, fn)
        shutil.copy2(src, dst)
        GalleryImage.objects.create(
            image='gallery/' + fn,
            caption=item['caption'],
            category=item['category'],
            instagram_url=item['ig_url'],
            order=item['order'],
            is_active=True
        )
        gal_count += 1
print(f"[+] {gal_count} Gallery Images seeded.")

print("\n[*] Database seeding completed successfully!")

