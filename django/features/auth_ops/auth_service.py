import json
from django.contrib.auth import authenticate, login, logout
from core.models import (
    StudioService, LookGroup, MediaItem, MakeupPackage,
    CustomerReview, EventPackage, AcademyCourse, ServicePrice, Artist
)
from core.views.common import get_site_settings, get_active_coupon

def authenticate_admin_user(request, username, password):
    """Authenticate staff credentials and log in"""
    user = authenticate(request, username=username, password=password)
    if user and user.is_staff:
        login(request, user)
        return {'success': True, 'user': user}
    return {'success': False, 'error': 'Invalid credentials or account does not have admin privileges.'}

def logout_admin_user(request):
    """Log out authenticated user session"""
    logout(request)
    return True

def compile_admin_portal_data(user):
    """Fetch and structure all data required for the admin dashboard"""
    site = get_site_settings()
    coupon = get_active_coupon(site)
    services = StudioService.objects.all().order_by('order', 'id')
    look_groups = LookGroup.objects.all().prefetch_related('media_items').order_by('order', 'id')
    media_items = MediaItem.objects.all().order_by('-created_at')
    packages = MakeupPackage.objects.all().order_by('package_type', 'price')
    reviews = CustomerReview.objects.all().order_by('-created_at')
    event_packages = EventPackage.objects.all().order_by('id')
    courses = AcademyCourse.objects.all()
    service_prices = {sp.service: sp for sp in ServicePrice.objects.all()}
    artists = Artist.objects.all().order_by('order', 'id')

    try:
        vip_codes = json.loads(site.vip_generated_codes or '[]')
    except Exception:
        vip_codes = []

    default_coupon = {
        'active': site.default_auto_coupon_active,
        'code': site.default_auto_coupon_code,
        'discount': site.default_auto_coupon_discount,
        'type': site.default_auto_coupon_type,
        'badge': site.default_auto_coupon_badge,
    }

    return {
        'site': site,
        'coupon': coupon,
        'default_coupon': default_coupon,
        'vip_codes': vip_codes,
        'services': services,
        'look_groups': look_groups,
        'media_items': media_items,
        'packages': packages,
        'reviews': reviews,
        'event_packages': event_packages,
        'courses': courses,
        'service_prices': service_prices,
        'artists': artists,
        'user': user,
        'whatsapp': site.whatsapp_number,
        'travel_settings': {
            'active': site.travel_widget_active,
            'same_zone_km': site.travel_same_zone_km,
            'near_label': site.travel_near_label,
            'near_fee_min': site.travel_near_fee_min,
            'near_fee_max': site.travel_near_fee_max,
            'far_label': site.travel_far_label,
            'far_fee_min': site.travel_far_fee_min,
            'far_fee_max': site.travel_far_fee_max,
            'custom_note': site.travel_custom_note,
        },
    }
