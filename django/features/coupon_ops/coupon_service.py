import json
import uuid
import random
from datetime import date
from django.utils import timezone
from core.models import SiteSettings

def get_site_settings_instance():
    s, _ = SiteSettings.objects.get_or_create(id=1)
    return s

def calculate_active_coupon(settings_obj):
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

def fetch_active_and_exit_coupons():
    site = get_site_settings_instance()
    active_coupon = calculate_active_coupon(site)
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
    return {
        'ok': True,
        'coupon': active_coupon,
        'default_coupon': default_coupon,
        'exit_coupon': exit_coupon
    }

def update_or_generate_coupon(data, action):
    site = get_site_settings_instance()

    # 1. VIP Code Generation
    if action == 'generate_vip':
        code = data.get('code', '').strip().upper()
        if not code:
            code = f"VIP-{random.randint(100, 999)}-{random.randint(10, 99)}"
        discount = int(data.get('discount', 15) or 15)
        disc_type = data.get('discount_type', 'percent')
        client_name = data.get('client_name', '').strip()
        notes = data.get('notes', '').strip()
        
        try:
            vip_list = json.loads(site.vip_generated_codes or '[]')
        except Exception:
            vip_list = []

        new_vip = {
            'id': str(uuid.uuid4())[:8],
            'code': code,
            'discount': discount,
            'type': disc_type,
            'client_name': client_name or 'VIP Client',
            'notes': notes or 'Authorized concierge privilege',
            'created_at': timezone.now().strftime('%d %b %Y, %I:%M %p')
        }
        vip_list.insert(0, new_vip)
        site.vip_generated_codes = json.dumps(vip_list)
        site.save()
        return {'ok': True, 'vip': new_vip, 'vip_list': vip_list}

    # 2. VIP Code Revoke / Deletion
    if action == 'delete_vip':
        target_id = data.get('id', '')
        target_code = data.get('code', '')
        try:
            vip_list = json.loads(site.vip_generated_codes or '[]')
            vip_list = [v for v in vip_list if v.get('id') != target_id and v.get('code') != target_code]
            site.vip_generated_codes = json.dumps(vip_list)
            site.save()
            return {'ok': True, 'vip_list': vip_list}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    # 3. Default Today's Auto-Applied Coupon Settings
    if 'default_auto_coupon_active' in data:
        site.default_auto_coupon_active = data.get('default_auto_coupon_active') in ['1', True, 'true', 'on']
    if 'default_auto_coupon_code' in data:
        site.default_auto_coupon_code = str(data.get('default_auto_coupon_code', site.default_auto_coupon_code)).strip().upper()
    if 'default_auto_coupon_discount' in data:
        site.default_auto_coupon_discount = int(data.get('default_auto_coupon_discount', 15) or 15)
    if 'default_auto_coupon_type' in data:
        site.default_auto_coupon_type = data.get('default_auto_coupon_type', 'percent')
    if 'default_auto_coupon_badge' in data:
        site.default_auto_coupon_badge = str(data.get('default_auto_coupon_badge', site.default_auto_coupon_badge)).strip()

    # Regular Seasonal coupon settings
    if 'coupon_active' in data:
        site.coupon_active = data.get('coupon_active') in ['1', True, 'true', 'on']
    if 'coupon_auto_by_date' in data:
        site.coupon_auto_by_date = data.get('coupon_auto_by_date') in ['1', True, 'true', 'on']
    if 'coupon_code' in data:
        site.coupon_code = data.get('coupon_code', site.coupon_code)
    if 'coupon_discount_percent' in data:
        site.coupon_discount_percent = int(data.get('coupon_discount_percent', 0) or 0)
    if 'coupon_label' in data:
        site.coupon_label = data.get('coupon_label', site.coupon_label)
    
    # Exit-intent / Go-back coupon settings
    if 'exit_coupon_active' in data:
        site.exit_coupon_active = data.get('exit_coupon_active') in ['1', True, 'true', 'on']
    if 'exit_coupon_code' in data:
        site.exit_coupon_code = str(data.get('exit_coupon_code', site.exit_coupon_code)).strip().upper()
    if 'exit_coupon_discount_percent' in data:
        site.exit_coupon_discount_percent = int(data.get('exit_coupon_discount_percent', 10) or 10)
    if 'exit_coupon_label' in data:
        site.exit_coupon_label = str(data.get('exit_coupon_label', site.exit_coupon_label)).strip()

    site.save()
    return {
        'ok': True,
        'default_coupon_code': site.default_auto_coupon_code,
        'default_coupon_discount': site.default_auto_coupon_discount,
        'default_coupon_active': site.default_auto_coupon_active,
        'coupon_code': site.coupon_code,
        'exit_coupon_code': site.exit_coupon_code,
        'exit_coupon_discount': site.exit_coupon_discount_percent
    }
