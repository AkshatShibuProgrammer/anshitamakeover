from datetime import date

from django.contrib.auth.decorators import user_passes_test

from ..models import SiteSettings


def admin_required(view_func):
    """Gate for admin-management APIs and artist portal.
    Permits authenticated staff members OR verified artist sessions.
    """
    from functools import wraps
    from django.http import JsonResponse, HttpResponseRedirect

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if (request.user.is_authenticated and request.user.is_staff) or request.session.get('artist_verified', False):
            return view_func(request, *args, **kwargs)
        # Preserve the established studio contract: all protected routes redirect
        # to the branded login page, including API calls. Frontend clients follow
        # the redirect and receive the login page rather than a leaked error shape.
        return HttpResponseRedirect('/admin-login/?next=' + request.path)
    return _wrapped

def get_site_settings():
    s, _ = SiteSettings.objects.get_or_create(id=1)
    return s

INDIAN_SEASONAL_COUPON_MAP = {
    1:  {'code': 'WINTER30', 'discount': 30, 'label': '❄️ Winter Wedding Peak Season — 30% Grand Bridal Privilege'},
    2:  {'code': 'WINTER30', 'discount': 30, 'label': '❄️ Auspicious Wedding Muhurtas — 30% Grand Bridal Privilege'},
    3:  {'code': 'SPRING15', 'discount': 15, 'label': '🌸 Spring Bridal Glow & Holi Festivities — 15% Off'},
    4:  {'code': 'SPRING15', 'discount': 15, 'label': '🌸 Vasant Panchami & Spring Nuptials — 15% Off'},
    5:  {'code': 'SUMMER10', 'discount': 10, 'label': '☀️ Early Summer Booking Privilege — 10% Off'},
    6:  {'code': 'MONSOON20', 'discount': 20, 'label': '🌧️ Monsoon Advance Makeover — Extra 20% Off Pre-Season Privilege'},
    7:  {'code': 'MONSOON20', 'discount': 20, 'label': '🌧️ Mid-Monsoon Early Booking — 20% Special Bridal Privilege'},
    8:  {'code': 'GLAM20', 'discount': 20, 'label': '✨ Pre-Season Bridal Privilege — 20% Off Advance Bookings'},
    9:  {'code': 'ROYAL25', 'discount': 25, 'label': '✨ Royal Autumn & Pre-Vivah Season Early-Bird — 25% Off Advance Bookings'},
    10: {'code': 'NAVRATRI15', 'discount': 15, 'label': '🪔 Navratri & Karwa Chauth Festive Glow — 15% Festive Privilege'},
    11: {'code': 'SHAADI30', 'discount': 30, 'label': '👑 Dev Uthani Ekadashi & Winter Vivah — 30% Grand Wedding Season Offer'},
    12: {'code': 'WINTER30', 'discount': 30, 'label': '❄️ Grand Winter Vivah Celebration — 30% Imperial Privilege'},
}

def get_active_coupon(settings_obj):
    """Return active coupon dict based on settings or Indian seasonal calendar logic"""
    if not settings_obj.coupon_active:
        return None
    if settings_obj.coupon_auto_by_date:
        # Day-of-month rotation is the canonical auto-coupon contract.
        # Seasonal campaigns are selected explicitly through manual mode so
        # they cannot silently change the public API during a month.
        day = date.today().day
        if day <= 10:
            return {'code': 'GLAMOUR30', 'discount': 30, 'label': 'Start of Month Special — Days 1–10'}
        elif day <= 20:
            return {'code': 'GLAM50', 'discount': 50, 'label': 'Mid-Month Dhamaka — Days 11–20'}
        else:
            return {'code': 'ANSHITA10', 'discount': 10, 'label': 'Month End Offer — Days 21–31'}
    if settings_obj.coupon_code:
        return {
            'code': settings_obj.coupon_code,
            'discount': settings_obj.coupon_discount_percent,
            'label': settings_obj.coupon_label,
        }
    return None
