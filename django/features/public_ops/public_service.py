import json
from core.models import (
    Artist, GalleryImage, MakeupPackage, StudioService,
    EventPackage, CustomerReview, MediaItem, LookGroup, AcademyCourse
)
from core.translations import get_translation
from core.views.common import get_site_settings, get_active_coupon

def compile_home_context(lang):
    """Compile and calculate all public pricing and showcases for the homepage"""
    site = get_site_settings()
    coupon = get_active_coupon(site)
    default_coupon = {
        'active': site.default_auto_coupon_active,
        'code': site.default_auto_coupon_code,
        'discount': site.default_auto_coupon_discount,
        'type': site.default_auto_coupon_type,
        'badge': site.default_auto_coupon_badge,
    } if site.default_auto_coupon_active else None
    exit_coupon = {
        'code': site.exit_coupon_code,
        'discount': site.exit_coupon_discount_percent,
        'label': site.exit_coupon_label,
        'active': site.exit_coupon_active,
    } if site.exit_coupon_active else None

    artists = Artist.objects.filter(is_active=True)
    gallery = GalleryImage.objects.filter(is_active=True, is_group_cover=True).order_by('order', 'id')
    all_packages = list(MakeupPackage.objects.filter(is_active=True))

    active_discount = coupon['discount'] if coupon else 0
    for p in all_packages:
        if p.price:
            base_p = float(p.price)
            if active_discount > 0:
                p.has_offer = True
                p.offer_price = round(base_p * (100 - active_discount) / 100)
                p.saving = base_p - p.offer_price
                p.discount_percent = active_discount
            else:
                p.has_offer = False
                p.offer_price = round(base_p)
                p.saving = 0
                p.discount_percent = 0

    packages_bridal = [p for p in all_packages if p.package_type == 'bridal']
    packages_other = [p for p in all_packages if p.package_type != 'bridal']

    studio_services = list(StudioService.objects.filter(is_active=True).order_by('order', 'id'))
    for s in studio_services:
        if s.price:
            base_p = float(s.price)
            if active_discount > 0:
                s.has_offer = True
                s.offer_price = round(base_p * (100 - active_discount) / 100)
                s.saving = base_p - s.offer_price
                s.discount_percent = active_discount
            else:
                s.has_offer = False
                s.offer_price = round(base_p)
                s.saving = 0
                s.discount_percent = 0

    event_packages = EventPackage.objects.filter(is_active=True).order_by('id')
    reviews = CustomerReview.objects.filter(is_active=True).order_by('-order', '-created_at')[:8]
    media_reels = MediaItem.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:6]
    look_groups = LookGroup.objects.filter(is_active=True).prefetch_related('media_items').order_by('order', 'id')

    # Build JSON map for lookbook modal
    look_groups_dict = {}
    for lg in look_groups:
        items = []
        for itm in lg.media_items.all().order_by('order', 'id'):
            thumb = itm.display_thumb
            if thumb and not thumb.startswith('http') and not thumb.startswith('/'):
                thumb = '/' + thumb
            items.append({
                'src': thumb,
                'caption': itm.caption or itm.title or lg.name,
                'category': lg.get_category_display(),
                'media_type': itm.media_type,
                'external_url': itm.external_url,
                'embed_code': itm.embed_code,
            })
        if not items and lg.display_cover:
            cov = lg.display_cover
            if cov and not cov.startswith('http') and not cov.startswith('/'):
                cov = '/' + cov
            items.append({
                'src': cov,
                'caption': lg.makeup_type or lg.name,
                'category': lg.get_category_display(),
                'media_type': 'image',
                'external_url': '',
                'embed_code': '',
            })
        group_data = {
            'id': lg.id,
            'title': lg.name,
            'category': lg.get_category_display(),
            'items': items,
        }
        # Key by numeric ID as string and integer
        look_groups_dict[str(lg.id)] = group_data

    look_groups_json = json.dumps(look_groups_dict)

    t = get_translation(lang)
    return {
        'site': site,
        'coupon': coupon,
        'default_coupon': default_coupon,
        'exit_coupon': exit_coupon,
        'artists': artists,
        'gallery': gallery,
        'packages_bridal': packages_bridal,
        'packages_other': packages_other,
        'studio_services': studio_services,
        'services': studio_services,
        'event_packages': event_packages,
        'reviews': reviews,
        'media_reels': media_reels,
        'look_groups': look_groups,
        'look_groups_json': look_groups_json,
        'whatsapp': site.whatsapp_number,
        'lang': lang,
        'current_lang': lang,
        't': t,
    }

def compile_academy_context(lang):
    """Compile masterclass courses and curriculum for the academy page"""
    site = get_site_settings()
    coupon = get_active_coupon(site)
    courses = list(AcademyCourse.objects.filter(is_active=True).order_by('order', 'id'))
    active_discount = coupon['discount'] if coupon else 0

    for c in courses:
        total = float(c.total_payable)
        if active_discount > 0:
            c.has_offer = True
            c.offer_price = round(total * (100 - active_discount) / 100)
            c.saving = round(total - c.offer_price)
            c.discount_percent = active_discount
        else:
            c.has_offer = False
            c.offer_price = round(total)
            c.saving = 0
            c.discount_percent = 0

    modules_static = [
        ('Makeup Foundations', 'Skin Prep, Face Shapes, Product Knowledge, Color Theory, Hygiene & Safety'),
        ('Professional Makeup Techniques', 'Base Application, Contouring, Concealing, Eye Makeup, Lash Application, Lip Art'),
        ('Bridal Makeup Training', 'HD Bridal, Engagement, Reception Looks, Luxury Finishing, Client Consultation'),
        ('Advanced Makeup Looks', 'Soft Glam, Party Makeup, Smokey Eye, Dewy Skin, Nude & Contemporary Editorial Looks'),
        ('Bridal Styling & Draping', 'Saree Draping, Dupatta Setting, Jewellery Placement & Bridal Styling'),
        ('Social Media & Portfolio', 'Instagram Reels, Personal Branding, Portfolio Building, Viral Content Strategy'),
    ]

    fallback_std_price = 35400
    fallback_offer_price = round(fallback_std_price * (100 - active_discount) / 100) if active_discount > 0 else fallback_std_price
    fallback_saving = fallback_std_price - fallback_offer_price
    t = get_translation(lang)

    return {
        'site': site,
        'coupon': coupon,
        'courses': courses,
        'modules_static': modules_static,
        'fallback_std_price': fallback_std_price,
        'fallback_offer_price': fallback_offer_price,
        'fallback_saving': fallback_saving,
        'whatsapp': site.whatsapp_number,
        'lang': lang,
        'current_lang': lang,
        't': t,
    }

def compile_travel_estimator_context(lang):
    """Compile context for standalone Pan-India Travel & Outstation Distance Estimator tool page"""
    site = get_site_settings()
    coupon = get_active_coupon(site)
    t = get_translation(lang)
    return {
        'site': site,
        'coupon': coupon,
        'whatsapp': site.whatsapp_number,
        'lang': lang,
        'current_lang': lang,
        't': t,
    }

def compile_cart_context(lang):
    """Compile context for the dedicated Bridal Trousseau / Cart booking page"""
    site = get_site_settings()
    coupon = get_active_coupon(site)
    studio_services = list(StudioService.objects.filter(is_active=True).order_by('order', 'id'))
    all_packages = list(MakeupPackage.objects.filter(is_active=True).order_by('order', 'id'))
    t = get_translation(lang)
    return {
        'site': site,
        'coupon': coupon,
        'studio_services': studio_services,
        'packages': all_packages,
        'whatsapp': site.whatsapp_number,
        'lang': lang,
        'current_lang': lang,
        't': t,
    }

def compile_chatbot_context(lang):
    """Compile context for standalone full-screen AI Concierge chat page"""
    site = get_site_settings()
    coupon = get_active_coupon(site)
    t = get_translation(lang)
    return {
        'site': site,
        'coupon': coupon,
        'whatsapp': site.whatsapp_number,
        'lang': lang,
        'current_lang': lang,
        't': t,
    }


