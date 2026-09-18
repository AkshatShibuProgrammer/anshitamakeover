from .common import get_site_settings, get_active_coupon
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
