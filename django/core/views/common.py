from datetime import date
from ..models import SiteSettings

def get_site_settings():
    s, _ = SiteSettings.objects.get_or_create(id=1)
    return s

def get_active_coupon(settings_obj):
    """Return active coupon dict based on settings or auto date logic"""
    if not settings_obj.coupon_active:
        return None
    if settings_obj.coupon_auto_by_date:
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
