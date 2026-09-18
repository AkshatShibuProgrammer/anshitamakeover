import os
from pathlib import Path

SRC = Path("core/views_monolithic_backup.py")
OUT_DIR = Path("core/views")
OUT_DIR.mkdir(exist_ok=True)

with open(SRC, "r", encoding="utf-8") as f:
    lines = f.readlines()

HEADER = """import json
import os
import uuid
import re
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import date
from django.utils.text import slugify

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from ..models import (
    SiteSettings, Artist, AcademyCourse, MakeupPackage,
    GalleryImage, ServicePrice, EventPackage, ChatMessage, AdminProfile, CustomerReview,
    MediaItem, StudioService, LookGroup, LookMediaItem
)
from ..translations import get_translation, TRANSLATIONS
from .common import get_site_settings, get_active_coupon
"""

COMMON_CONTENT = """from datetime import date
from ..models import SiteSettings

def get_site_settings():
    s, _ = SiteSettings.objects.get_or_create(id=1)
    return s

def get_active_coupon(settings_obj):
    \"\"\"Return active coupon dict based on settings or auto date logic\"\"\"
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
"""

with open(OUT_DIR / "common.py", "w", encoding="utf-8") as f:
    f.write(COMMON_CONTENT)

def write_module(filename, code_lines):
    full_code = HEADER + "\n\n" + "".join(code_lines)
    with open(OUT_DIR / filename, "w", encoding="utf-8") as f:
        f.write(full_code)

# public.py: home (54 to 200), academy (200 to 264), set_language (848 to 875), sinha_logo_studio (2112 to end)
write_module("public.py", lines[54:264] + lines[848:875] + lines[2112:])

# chatbot.py: chatbot_api, gemini_chat, admin_ai_command, fallback_chatbot (264 to 848)
write_module("chatbot.py", lines[264:848])

# auth.py: admin_login, admin_logout_view, admin_portal (875 to 972)
write_module("auth.py", lines[875:972])

# coupons.py: get_coupon_api, admin_coupon_update (972 to 1104)
write_module("coupons.py", lines[972:1104])

# services_pricing.py: admin_price_update, admin_event_package, admin_service_manage, admin_studio_service_manage
write_module("services_pricing.py", lines[1104:1300] + lines[1392:1478] + lines[1720:1864])

# artists.py: admin_artist_manage (1300 to 1392)
write_module("artists.py", lines[1300:1392])

# reviews.py: submit_review, admin_review_manage (1478 to 1537)
write_module("reviews.py", lines[1478:1537])

# media.py: admin_media_manage, admin_lookgroup_manage, admin_lookmedia_manage
write_module("media.py", lines[1537:1720] + lines[1864:2112])

# __init__.py
INIT_CONTENT = """from .common import get_site_settings, get_active_coupon
from .public import home, academy, set_language, sinha_logo_studio
from .chatbot import chatbot_api, gemini_chat, admin_ai_command, fallback_chatbot
from .auth import admin_login, admin_logout_view, admin_portal
from .coupons import get_coupon_api, admin_coupon_update
from .services_pricing import (
    admin_price_update, admin_event_package, admin_service_manage, admin_studio_service_manage
)
from .artists import admin_artist_manage
from .reviews import submit_review, admin_review_manage
from .media import admin_media_manage, admin_lookgroup_manage, admin_lookmedia_manage

__all__ = [
    'get_site_settings',
    'get_active_coupon',
    'home',
    'academy',
    'set_language',
    'sinha_logo_studio',
    'chatbot_api',
    'gemini_chat',
    'admin_ai_command',
    'fallback_chatbot',
    'admin_login',
    'admin_logout_view',
    'admin_portal',
    'get_coupon_api',
    'admin_coupon_update',
    'admin_price_update',
    'admin_event_package',
    'admin_service_manage',
    'admin_studio_service_manage',
    'admin_artist_manage',
    'submit_review',
    'admin_review_manage',
    'admin_media_manage',
    'admin_lookgroup_manage',
    'admin_lookmedia_manage',
]
"""
with open(OUT_DIR / "__init__.py", "w", encoding="utf-8") as f:
    f.write(INIT_CONTENT)

print("Modularization rewrite complete!")
