"""
Deterministic test-data factories for the Anshita Makeover regression suite.

Every factory returns the objects it creates so individual tests can compose
exactly the dataset they need.  ``build_full_dataset()`` seeds the complete
canonical dataset (the same dataset that is serialised into
``tests/fixtures/regression_dataset.json`` by ``generate_fixture.py`` and can
be loaded into a dev database via ``python manage.py seed_test_data``).

The data is intentionally realistic (Bhopal bridal-studio domain content) but
fully deterministic — no random values, no timestamps, no network access.
"""
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from core.models import (
    SiteSettings, Artist, AcademyCourse, CourseModule, MakeupPackage,
    GalleryImage, MediaItem, ServicePrice, EventPackage, ChatMessage,
    AdminProfile, CustomerReview, StudioService, LookGroup, LookMediaItem,
)

# ── Canonical credentials ────────────────────────────────────────────────
ADMIN_USERNAME = 'regadmin'
ADMIN_PASSWORD = 'RegTest@2026'
SUPERUSER_USERNAME = 'akshat'
SUPERUSER_PASSWORD = 'Anshita@2026'
CLIENT_USERNAME = 'client_user'
CLIENT_PASSWORD = 'Client@2026'


# ── Users ────────────────────────────────────────────────────────────────
def build_admin_user(username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
    """Staff superuser used for all admin-portal regression flows."""
    user, _ = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.email = f'{username}@anshitamakeover.test'
    user.save()
    AdminProfile.objects.get_or_create(user=user, defaults={'email': user.email})
    return user


def build_superuser(username=SUPERUSER_USERNAME, password=SUPERUSER_PASSWORD):
    user, _ = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.email = f'{username}@anshitamakeover.test'
    user.save()
    return user


def build_client_user(username=CLIENT_USERNAME, password=CLIENT_PASSWORD):
    """Non-staff user — must be rejected by every admin-only endpoint."""
    user, _ = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = False
    user.is_superuser = False
    user.is_active = True
    user.email = f'{username}@anshitamakeover.test'
    user.save()
    return user


# ── Site settings ────────────────────────────────────────────────────────
def build_site_settings(**overrides):
    """Singleton SiteSettings row (id=1) with canonical defaults."""
    defaults = dict(
        whatsapp_number='917879223442',
        instagram_url='https://www.instagram.com/anshitamakeover21/',
        coupon_active=True,
        coupon_code='GLAMOUR30',
        coupon_discount_percent=30,
        coupon_label='Seasonal Privilege Offer on Bridal Suites & Packages',
        coupon_auto_by_date=False,  # deterministic default for tests
        exit_coupon_active=True,
        exit_coupon_code='SECRET10',
        exit_coupon_discount_percent=10,
        exit_coupon_label='Exclusive Secret Privilege: Extra 10% Additional Discount',
        offer_bridal_free_sides=2,
        offer_next_sides_discounted_price=2500,
        offer_combo_discount_percent=15,
        offer_grand_combo_bundle_price=50000,
        offer_rules_active=True,
        travel_widget_active=True,
        travel_same_zone_km=100,
        travel_near_fee_min=8000,
        travel_near_fee_max=15000,
        travel_far_fee_min=20000,
        travel_far_fee_max=40000,
        default_auto_coupon_active=True,
        default_auto_coupon_code='TODAYVIP',
        default_auto_coupon_discount=15,
        default_auto_coupon_type='percent',
        ai_negotiation_enabled=True,
        ai_negotiation_min_floor_percent=75,
        ai_max_discount_percent=20,
        ai_negotiation_strategy='balanced',
        vip_generated_codes='[]',
    )
    defaults.update(overrides)
    site, _ = SiteSettings.objects.get_or_create(id=1)
    for key, value in defaults.items():
        setattr(site, key, value)
    site.save()
    return site


# ── Artists ──────────────────────────────────────────────────────────────
ARTIST_ROWS = [
    dict(name='Anshita', slug='anshita',
         bio='Founder & India Celebrated Bridal Couturier with 8+ years mastery and 500+ radiant brides.',
         specialities='makeup,hair,draping', order=0, is_active=True),
    dict(name='Tejal Sinha', slug='tejal-sinha',
         bio='Senior hair stylist specialising in bridal updos and vintage waves.',
         specialities='hair,beauty', order=1, is_active=True),
    dict(name='Shristee', slug='shristee',
         bio='Nail artist on sabbatical.',
         specialities='nails', order=2, is_active=False),
]


def build_artists():
    artists = []
    for row in ARTIST_ROWS:
        artist, _ = Artist.objects.update_or_create(
            slug=row['slug'], defaults={k: v for k, v in row.items() if k != 'slug'},
        )
        artists.append(artist)
    return artists


# ── Academy ──────────────────────────────────────────────────────────────
COURSE_MODULES = [
    (1, 'Makeup Foundations', 'Skin Prep, Face Shapes, Product Knowledge, Color Theory, Hygiene & Safety'),
    (2, 'Professional Makeup Techniques', 'Base Application, Contouring, Concealing, Eye Makeup, Lash Application, Lip Art'),
    (3, 'Bridal Makeup Training', 'HD Bridal, Engagement, Reception Looks, Luxury Finishing, Client Consultation'),
    (4, 'Advanced Makeup Looks', 'Soft Glam, Party Makeup, Smokey Eye, Dewy Skin, Nude & Contemporary Editorial Looks'),
    (5, 'Bridal Styling & Draping', 'Saree Draping, Dupatta Setting, Jewellery Placement & Bridal Styling'),
    (6, 'Social Media & Portfolio', 'Instagram Reels, Personal Branding, Portfolio Building, Viral Content Strategy'),
]


def build_courses():
    course, _ = AcademyCourse.objects.update_or_create(
        slug='professional-makeup-artist-program',
        defaults=dict(
            name='Professional Makeup Artist Program',
            tagline='Beginner to Professional Bridal Makeup Certification',
            duration_days=28, duration_label='4 Weeks', hours_per_day=3,
            total_hours=84, course_fee=30000, gst_percent=18,
            registration_fee=5000,
            batch_start_note='Last Batch of 2026 — Starts 27th July',
            is_active=True, is_featured=True, order=0,
        ),
    )

    for order, title, description in COURSE_MODULES:
        CourseModule.objects.update_or_create(
            course=course, order=order,
            defaults={'title': title, 'description': description},
        )

    hair_course, _ = AcademyCourse.objects.update_or_create(
        slug='bridal-hair-masterclass',
        defaults=dict(
            name='Bridal Hair Masterclass',
            tagline='Couture Updos, Waves & Traditional Buns',
            duration_days=7, duration_label='1 Week', hours_per_day=4,
            total_hours=28, course_fee=12000, gst_percent=18,
            registration_fee=2000, is_active=True, is_featured=False, order=1,
        ),
    )
    return [course, hair_course]


# ── Makeup packages ──────────────────────────────────────────────────────
PACKAGE_ROWS = [
    dict(name='Imperial Royal HD Bridal Suite', package_type='bridal', price=35000,
         tagline='The signature HD bridal transformation', is_featured=True, order=0,
         min_negotiated_price=26250, max_discount_percent=25, allow_ai_negotiation=True,
         features='High-definition luminous base\nCut-crease eye artistry\nDupatta & saree draping\n2 side makeups free'),
    dict(name='Master Airbrush Bridal Suite', package_type='bridal', price=45000,
         tagline='TEMPTU 24-hour cry-proof airbrush perfection', is_featured=True, order=1,
         min_negotiated_price=None, max_discount_percent=15, allow_ai_negotiation=True,
         features='TEMPTU airbrush base\n24-hr cry-proof finish\nVanity setup at venue\n2 side makeups free'),
    dict(name='Grand Royal Heritage Bundle', package_type='bridal', price=50000,
         tagline='Bridal + Engagement grand bundle', is_featured=True, order=2,
         features='Bridal suite\nEngagement suite\n2 side makeups free\nPriority date lock'),
    dict(name='Engagement & Roka Glam', package_type='engagement', price=18000,
         tagline='Glass-skin glow for your roka', is_featured=False, order=3,
         features='Glass-skin base\nHair styling\nSaree draping'),
    dict(name='Reception Radiance Suite', package_type='reception', price=22000,
         tagline='Evening glamour for the reception', is_featured=False, order=4,
         features='Contour-heavy evening look\nGown draping assistance'),
    dict(name='Side & Family Artistry', package_type='side_makeup', price=3500,
         tagline='Elegant glam for bridesmaids and family', is_featured=False, order=5,
         features='Soft glam base\nBasic hair styling'),
    dict(name='Party Festive Glam', package_type='party', price=8000,
         tagline='Festive shimmer for parties', is_featured=False, order=6,
         features='Shimmer party look\nLash application'),
    dict(name='Haute Hair Couture', package_type='hair', price=6000,
         tagline='Couture bridal hair artistry', is_featured=False, order=7,
         features='Bridal updo\nAccessory placement'),
    dict(name='Bridal Nail Extensions', package_type='nails', price=5500,
         tagline='Swarovski bridal nail art', is_featured=False, order=8,
         features='Gel extensions\nBridal nail art'),
    dict(name='Pre-Bridal Skin Ritual', package_type='beauty', price=9500,
         tagline='Hydra-glow pre-bridal prep', is_featured=False, order=9,
         features='Hydra facial\nBrightening ritual'),
    dict(name='Bespoke Custom Couture', package_type='custom', price=None,
         display_label='On Request', tagline='Tailored couture quote', is_featured=False, order=10,
         features='Consultation-led bespoke quote'),
    dict(name='Legacy Trial Package', package_type='party', price=4000,
         tagline='Deprecated trial package', is_featured=False, order=99, is_active=False,
         features='Should never appear on public pages'),
]


def build_packages():
    packages = []
    for row in PACKAGE_ROWS:
        row = dict(row)
        defaults = dict(row, features=row.get('features', ''))
        pkg, _ = MakeupPackage.objects.update_or_create(
            name=defaults.pop('name'), defaults=defaults,
        )
        packages.append(pkg)
    return packages


# ── Studio services ──────────────────────────────────────────────────────
STUDIO_SERVICE_ROWS = [
    dict(title='Imperial Bridal Couture & Airbrush',
         discipline='SIGNATURE DISCIPLINE 01 · SACRED WEDDING DAY',
         category='bridal', price=35000, discount_price=29750,
         bundle_note='Save 15% with Wedding Package',
         description='Full airbrush bridal couture with TEMPTU cry-proof base.',
         features='TEMPTU airbrush base\nCut-crease artistry\nDupatta draping',
         image_url='/static/core/images/curated/royal_crimson_bride_angle3.jpg',
         look_group_id='bengali_bride', min_negotiated_price=26250,
         max_discount_percent=25, allow_ai_negotiation=True, order=0, is_active=True),
    dict(title='Reception Cocktail Radiance',
         discipline='SIGNATURE DISCIPLINE 02 · EVENING SOIRÉE',
         category='reception', price=22000, discount_price=None,
         bundle_note='',
         description='Evening contour glam for receptions and cocktail events.',
         features='Contour-heavy base\nGown draping',
         image_url='/static/core/images/anshita_front.jpg',
         order=1, is_active=True),
    dict(title='Engagement Roka Glass-Skin',
         discipline='SIGNATURE DISCIPLINE 03 · RING CEREMONY',
         category='engagement', price=18000, discount_price=15300,
         bundle_note='Combo 15% off with Bridal',
         description='Dewy glass-skin engagement glam.',
         features='Glass-skin finish\nSoft waves',
         order=2, is_active=True),
    dict(title='Nail Couture Atelier',
         discipline='SIGNATURE DISCIPLINE 04 · NAIL COUTURE',
         category='nails', price=5500, discount_price=None,
         description='Swarovski bridal nail extensions and art.',
         features='Gel extensions\nSwarovski art',
         order=3, is_active=True, allow_ai_negotiation=False),
    dict(title='Retired Haldi Service',
         discipline='SIGNATURE DISCIPLINE 99 · RETIRED',
         category='sangeet', price=7000,
         description='Retired haldi service — must not render publicly.',
         order=99, is_active=False),
]


def build_studio_services():
    services = []
    for row in STUDIO_SERVICE_ROWS:
        row = dict(row)
        # price/description are NOT NULL — supply them as creation defaults.
        defaults = dict(row, price=row.get('price', 0),
                        description=row.get('description', ''))
        svc, _ = StudioService.objects.update_or_create(
            title=defaults.pop('title'), defaults=defaults,
        )
        services.append(svc)
    return services


# ── Service prices ───────────────────────────────────────────────────────
SERVICE_PRICE_ROWS = [
    ('makeup_basic', 15000, '', False),
    ('makeup_hd', 35000, '35,000 (Bridal HD Suite)', False),
    ('makeup_airbrush', 45000, '45,000 (Master Airbrush Bridal Suite)', False),
    ('hair_basic', 1500, 'Starting ₹1,500', False),
    ('hair_bridal', 3500, 'Starting 3,500', False),
    ('nails_basic', 1200, '', False),
    ('nails_art', 2500, '', False),
    ('nails_extension', 5500, '', False),
    ('beauty_facial', 2500, '', False),
    ('beauty_prebridal', 8000, 'Starting 8,000', False),
    ('tejal_makeup', 0, 'On Request', True),
    ('shristee_nails', 4500, '', False),
]


def build_service_prices():
    prices = []
    for service, price, label, on_request in SERVICE_PRICE_ROWS:
        sp, _ = ServicePrice.objects.update_or_create(
            service=service,
            defaults={'price': price, 'price_label': label,
                      'is_on_request': on_request, 'is_active': True},
        )
        prices.append(sp)
    return prices


# ── Event packages ───────────────────────────────────────────────────────
EVENT_PACKAGE_ROWS = [
    dict(name='Royal Premium Photography', category='photography',
         package_type='photography_premium', vendor_cost=90000, price=120000,
         description='Full-day cinematic coverage with drone aerials.',
         features='Candid + Traditional\nCinematic film\nDrone aerials\nPremium album',
         is_featured=True, order=0),
    dict(name='Standard Wedding Photography', category='photography',
         package_type='photography_standard', vendor_cost=70000, price=90000,
         description='Complete candid and traditional coverage.',
         features='Candid + Traditional\n300+ edited portraits',
         is_featured=False, order=1),
    dict(name='Full Wedding Management', category='full_event',
         package_type='full_event', vendor_cost=420000, price=500000,
         description='End-to-end royal wedding management.',
         features='Venue styling\nVendor orchestration\nDay-of coordination',
         is_featured=True, order=2),
    dict(name='Royal Stage Decor', category='decor', package_type='custom',
         vendor_cost=60000, price=None, price_label='On Request',
         description='Bespoke stage and mandap decor.',
         is_featured=False, order=3),
    dict(name='Retired DJ Package', category='dj', package_type='custom',
         vendor_cost=20000, price=30000, description='Inactive DJ package.',
         is_active=False, order=99),
]


def build_event_packages(user=None):
    packages = []
    for row in EVENT_PACKAGE_ROWS:
        row = dict(row)
        defaults = dict(row, description=row.get('description', ''),
                        features=row.get('features', ''))
        if user is not None:
            defaults['created_by'] = user
        pkg, _ = EventPackage.objects.update_or_create(
            name=defaults.pop('name'), defaults=defaults,
        )
        packages.append(pkg)
    return packages


# ── Reviews ──────────────────────────────────────────────────────────────
REVIEW_ROWS = [
    ('Priya Sharma', 'Royal Bride', 'Bhopal', 5,
     'Anshita transformed me into a queen. The airbrush base survived every happy tear!', 'Dec 2025', True),
    ('Meera Verma', 'Engagement Bride', 'Indore', 5,
     'Glass-skin glow that photographed like a dream. Highly recommended.', 'Jan 2026', True),
    ('Sneha Patel', 'Reception Bride', 'Bhopal', 5,
     'The team handled my entire family of 8 sides flawlessly.', 'Feb 2026', True),
    ('Ritika Jain', 'Party Glam', 'Jabalpur', 4,
     'Beautiful festive look, slight delay in start but worth it.', 'Mar 2026', True),
    ('Aishwarya Rao', 'Royal Bride', 'Nagpur', 5,
     'Destination wedding done perfectly — artist travelled with full kit.', 'Apr 2026', True),
    ('Kavya Nair', 'Royal Bride', 'Bhopal', 5,
     'Cry-proof indeed! 14 hours of flawless makeup.', 'May 2026', True),
    ('Divya Singh', 'Engagement Bride', 'Ujjain', 4,
     'Loved the soft glam. The VIP coupon saved us a good amount too.', 'Jun 2026', True),
    ('Pooja Malhotra', 'Academy Graduate', 'Bhopal', 5,
     'The masterclass changed my career. Hands-on training with real brides.', 'Jul 2026', True),
    ('Nisha Gupta', 'Royal Bride', 'Sehore', 5,
     'Every bride deserves this studio. Chandan art was authentic and gorgeous.', 'Aug 2026', True),
    ('Hidden Reviewer', 'Royal Bride', 'Bhopal', 1,
     'This review is moderated off and must never render publicly.', '', False),
]


def build_reviews():
    reviews = []
    for order, row in enumerate(REVIEW_ROWS):
        name, event_type, location, rating, text, wedding_date, is_active = row
        review, _ = CustomerReview.objects.get_or_create(client_name=name, review_text=text)
        review.event_type = event_type
        review.location = location
        review.rating = rating
        review.wedding_date = wedding_date
        review.is_verified = True
        review.is_active = is_active
        review.order = order
        review.save()
        reviews.append(review)
    return reviews


# ── Look groups & look media ─────────────────────────────────────────────
def build_look_groups():
    kuhu, _ = LookGroup.objects.update_or_create(
        name='Kuhu — Traditional Kolkata Banarasi & Chandan Art',
        defaults=dict(
            client_name='Kuhu', makeup_type='Traditional Bengali Mukut & Chandan',
            category='bridal',
            description='Authentic Bengali bridal with chandan art and shakha-pola.',
            cover_image_url='/static/core/images/authentic/bride_look1_portrait.jpg',
            order=0, is_active=True,
        ),
    )
    rajak, _ = LookGroup.objects.update_or_create(
        name='Miss Rajak — Mauve Shimmer Cut-Crease',
        defaults=dict(
            client_name='Miss Rajak', makeup_type='Mauve Shimmer Cut-Crease',
            category='reception',
            description='Soft mauve reception glam. Cover intentionally left empty for auto-cover tests.',
            cover_image_url='', order=1, is_active=True,
        ),
    )
    return [kuhu, rajak]


def build_look_media(groups=None):
    if groups is None:
        groups = build_look_groups()
    kuhu, rajak = groups[0], groups[1]
    items = []

    def add(group, **kwargs):
        defaults = dict(
            media_type='image', external_url='', embed_code='',
            thumbnail_url='', title='', caption='',
        )
        defaults.update(kwargs)
        item, _ = LookMediaItem.objects.update_or_create(
            group=group, title=kwargs.get('title', ''),
            caption=kwargs.get('caption', ''), defaults=defaults,
        )
        items.append(item)
        return item

    add(kuhu, media_type='image', title='Kuhu Front Portrait',
        caption='Chandan art close-up', thumbnail_url='/static/core/images/authentic/bride_look1_portrait.jpg', order=1)
    add(kuhu, media_type='instagram', title='Kuhu Reel — Shubho Drishti',
        external_url='https://www.instagram.com/reel/Dap4JkvKL1E/', embed_code='Dap4JkvKL1E',
        thumbnail_url='https://example.test/ig/kahu.jpg', order=2)
    add(kuhu, media_type='youtube', title='Kuhu Cinematic Film',
        external_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', embed_code='dQw4w9WgXcQ',
        order=3)
    add(rajak, media_type='image', title='Rajak Side Profile',
        caption='Mauve shimmer cut-crease', thumbnail_url='/static/core/images/authentic/bride_look1_side.jpg', order=1)
    add(rajak, media_type='youtube', title='Rajak Reel Film',
        external_url='https://youtu.be/aBcDeFgHiJk', embed_code='aBcDeFgHiJk', order=2)
    return items


# ── Media items (gallery / reels) ────────────────────────────────────────
MEDIA_ITEM_ROWS = [
    dict(title='Shubho Drishti — Bengali Bridal Reel', media_type='instagram',
         category='bridal', section='reels', caption='Traditional Bengali reveal',
         external_url='https://www.instagram.com/reel/Dap4JkvKL1E/', embed_code='Dap4JkvKL1E',
         thumbnail_url='https://example.test/ig/shubho.jpg', views_count='128.4K+ views',
         is_featured=True, order=0),
    dict(title='Royal Reception Walk — YouTube', media_type='youtube',
         category='reception', section='reels', caption='Cinematic reception entry',
         external_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', embed_code='dQw4w9WgXcQ',
         views_count='54.2K+ views', is_featured=True, order=1),
    dict(title='Chandan Art Detail', media_type='image', category='bridal',
         section='gallery', caption='Authentic chandan detail shot',
         thumbnail_url='/static/core/images/authentic/bride_look2_jewelry.jpg',
         views_count='25.4K+ views', is_featured=True, order=2),
    dict(title='Engagement Glass Skin', media_type='image', category='engagement',
         section='both', thumbnail_url='/static/core/images/authentic/bride_look3_candid.jpg',
         is_featured=False, order=3),
    dict(title='Retired Trial Reel', media_type='instagram', category='party',
         section='reels', external_url='https://www.instagram.com/p/DW0f_eHAecV/',
         embed_code='DW0f_eHAecV', is_featured=False, is_active=False, order=99),
]


def build_media_items():
    items = []
    for row in MEDIA_ITEM_ROWS:
        row = dict(row)
        defaults = dict(caption='', external_url='', embed_code='',
                        thumbnail_url='')
        defaults.update(row)
        item, _ = MediaItem.objects.update_or_create(
            title=defaults.pop('title'), defaults=defaults,
        )
        items.append(item)
    return items


# ── Gallery images (person/lookbook grouping) ────────────────────────────
GALLERY_ROWS = [
    dict(caption='Royal Bengali Bride — Front', category='bridal',
         look_group_id='bengali_bride', look_group_name='Royal Bengali Bride (4 Looks)',
         is_group_cover=True, is_active=True, order=0),
    dict(caption='Royal Bengali Bride — Side', category='bridal',
         look_group_id='bengali_bride', look_group_name='Royal Bengali Bride (4 Looks)',
         is_group_cover=False, is_active=True, order=1),
    dict(caption='Reception Glow Solo', category='reception',
         look_group_id='', look_group_name='', is_group_cover=True, is_active=True, order=2),
    dict(caption='Hidden Gallery Shot', category='bridal',
         look_group_id='', look_group_name='', is_group_cover=True, is_active=False, order=99),
]


def build_gallery_images(artist=None):
    images = []
    for row in GALLERY_ROWS:
        row = dict(row)
        caption = row.pop('caption')
        img, _ = GalleryImage.objects.get_or_create(caption=caption)
        for key, value in row.items():
            setattr(img, key, value)
        if artist is not None:
            img.artist = artist
        img.save()
        images.append(img)
    return images


# ── Chat history ─────────────────────────────────────────────────────────
def build_chat_messages(session_id='regression-session-0001', count=3):
    messages = []
    for i in range(count):
        messages.append(ChatMessage.objects.create(
            session_id=session_id,
            message=f'Regression probe question {i + 1}',
            response=f'Regression probe answer {i + 1}',
        ))
    return messages


# ── Full dataset ─────────────────────────────────────────────────────────
def build_full_dataset():
    """Seed the complete canonical dataset. Returns a model -> count map."""
    admin = build_admin_user()
    build_superuser()
    build_client_user()
    build_site_settings()
    artists = build_artists()
    build_courses()
    build_packages()
    build_studio_services()
    build_service_prices()
    build_event_packages(user=admin)
    build_reviews()
    groups = build_look_groups()
    build_look_media(groups)
    build_media_items()
    build_gallery_images(artist=artists[0])
    build_chat_messages()
    return {
        'User': User.objects.count(),
        'SiteSettings': SiteSettings.objects.count(),
        'Artist': Artist.objects.count(),
        'AcademyCourse': AcademyCourse.objects.count(),
        'CourseModule': CourseModule.objects.count(),
        'MakeupPackage': MakeupPackage.objects.count(),
        'StudioService': StudioService.objects.count(),
        'ServicePrice': ServicePrice.objects.count(),
        'EventPackage': EventPackage.objects.count(),
        'CustomerReview': CustomerReview.objects.count(),
        'LookGroup': LookGroup.objects.count(),
        'LookMediaItem': LookMediaItem.objects.count(),
        'MediaItem': MediaItem.objects.count(),
        'GalleryImage': GalleryImage.objects.count(),
        'ChatMessage': ChatMessage.objects.count(),
        'AdminProfile': AdminProfile.objects.count(),
    }
