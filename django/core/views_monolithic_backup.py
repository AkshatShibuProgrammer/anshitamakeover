import json
import os
import uuid
import re
import urllib.request
import urllib.parse
from pathlib import Path
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

from .models import (
    SiteSettings, Artist, AcademyCourse, MakeupPackage,
    GalleryImage, ServicePrice, EventPackage, ChatMessage, AdminProfile, CustomerReview,
    MediaItem, StudioService, LookGroup, LookMediaItem
)
from .translations import get_translation, TRANSLATIONS


def get_site_settings():
    s, _ = SiteSettings.objects.get_or_create(id=1)
    return s


def get_active_coupon(settings_obj):
    """Return active coupon dict based on settings or auto date logic"""
    if not settings_obj.coupon_active:
        return None
    if settings_obj.coupon_auto_by_date:
        from datetime import date
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


def home(request):
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

    # Calculate special offer pricing transparently
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
                p.offer_price = base_p
                p.saving = 0
                p.discount_percent = 0
        else:
            p.has_offer = False
            p.offer_price = None
            p.saving = 0
            p.discount_percent = 0

    packages = all_packages
    event_packages = EventPackage.objects.filter(is_active=True)
    service_prices = {sp.service: sp for sp in ServicePrice.objects.filter(is_active=True)}
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    t = get_translation(lang)

    # Artists by speciality
    makeup_artists = [a for a in artists if 'makeup' in a.get_specialities_list()]
    hair_artists   = [a for a in artists if 'hair'   in a.get_specialities_list()]
    nail_artists   = [a for a in artists if 'nails'  in a.get_specialities_list()]

    courses = AcademyCourse.objects.filter(is_active=True)
    reviews = CustomerReview.objects.filter(is_active=True)
    bridal_packages = [p for p in packages if p.package_type == 'bridal']
    side_packages = [p for p in packages if p.package_type == 'side_makeup']
    photo_premium = event_packages.filter(package_type='photography_premium').first()
    photo_standard = event_packages.filter(package_type='photography_standard').first()
    custom_events = [ep for ep in event_packages if ep.package_type in ['custom', 'full_event']]

    # Media items (Admin uploaded photos, Instagram Reels & YouTube Videos)
    media_reels = MediaItem.objects.filter(is_active=True, section__in=['reels', 'both'])
    media_gallery = MediaItem.objects.filter(is_active=True, section__in=['gallery', 'both'])
    services = StudioService.objects.filter(is_active=True).order_by('order', 'id')
    look_groups = LookGroup.objects.filter(is_active=True).prefetch_related('media_items').order_by('order', 'id')

    # Serialize LookGroups to JSON for client-side Lookbook Peek engine
    look_groups_dict = {}
    for lg in look_groups:
        items = []
        for itm in lg.media_items.all():
            items.append({
                'src': itm.display_thumb,
                'caption': f"{lg.name} · {itm.title or itm.caption or lg.makeup_type}",
                'category': lg.get_category_display(),
                'media_type': itm.media_type,
                'external_url': itm.external_url,
                'embed_code': itm.embed_code,
                'instagram': itm.external_url if itm.media_type == 'instagram' else '',
                'youtube': itm.external_url if itm.media_type == 'youtube' else ''
            })
        grp_data = {
            'id': lg.id,
            'title': lg.name,
            'client_name': lg.client_name,
            'makeup_type': lg.makeup_type,
            'category': lg.get_category_display(),
            'cover': lg.display_cover,
            'items': items
        }
        look_groups_dict[str(lg.id)] = grp_data
        # Also alias by common identifiers
        if lg.client_name:
            look_groups_dict[lg.client_name.lower().strip()] = grp_data
        if lg.category:
            if lg.category not in look_groups_dict:
                look_groups_dict[lg.category] = grp_data

    context = {
        'site': site,
        'coupon': coupon,
        'default_coupon': default_coupon,
        'exit_coupon': exit_coupon,
        'artists': artists,
        'makeup_artists': makeup_artists,
        'hair_artists': hair_artists,
        'nail_artists': nail_artists,
        'gallery': gallery,
        'services': services,
        'look_groups': look_groups,
        'look_groups_json': json.dumps(look_groups_dict),
        'media_gallery': media_gallery,
        'media_reels': media_reels,
        'packages': packages,
        'bridal_packages': bridal_packages,
        'side_packages': side_packages,
        'reviews': reviews,
        'event_packages': event_packages,
        'photo_premium': photo_premium,
        'photo_standard': photo_standard,
        'custom_events': custom_events,
        'service_prices': service_prices,
        'courses': courses,
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
        'whatsapp': site.whatsapp_number,
        'lang': lang,
        'current_lang': lang,
        't': t,
    }
    resp = render(request, 'core/home.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp


def academy(request):
    site = get_site_settings()
    coupon = get_active_coupon(site)
    exit_coupon = {
        'code': site.exit_coupon_code,
        'discount': site.exit_coupon_discount_percent,
        'label': site.exit_coupon_label,
        'active': site.exit_coupon_active,
    } if site.exit_coupon_active else None

    courses = list(AcademyCourse.objects.filter(is_active=True).prefetch_related('modules'))
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

    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    t = get_translation(lang)

    # Static fallback modules for when DB is empty
    modules_static = [
        ('Makeup Foundations', 'Skin Prep, Face Shapes, Product Knowledge, Color Theory, Hygiene & Safety'),
        ('Professional Makeup Techniques', 'Base Application, Contouring, Concealing, Eye Makeup, Lash Application, Lip Art'),
        ('Bridal Makeup Training', 'HD Bridal, Engagement, Reception Looks, Luxury Finishing, Client Consultation'),
        ('Advanced Makeup Looks', 'Soft Glam, Party Makeup, Smokey Eye, Dewy Skin, Nude & Contemporary Editorial Looks'),
        ('Bridal Styling & Draping', 'Saree Draping, Dupatta Setting, Jewellery Placement & Bridal Styling'),
        ('Social Media & Portfolio', 'Instagram Reels, Personal Branding, Portfolio Building, Viral Content Strategy'),
    ]

    # Fallback standard vs offer pricing for static presentation
    fallback_std_price = 35400
    fallback_offer_price = round(fallback_std_price * (100 - active_discount) / 100) if active_discount > 0 else fallback_std_price
    fallback_saving = fallback_std_price - fallback_offer_price

    context = {
        'site': site,
        'coupon': coupon,
        'exit_coupon': exit_coupon,
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
    resp = render(request, 'core/academy.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp


# ── API: Chatbot ──────────────────────────────────────────────
@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))

        if not user_msg:
            return JsonResponse({'reply': 'Greetings! How may I assist you with our bridal and beauty services today? ✨', 'session_id': session_id})

        # Load Gemini API key
        key_file = Path(settings.BASE_DIR) / 'gemini_api_key.txt'
        api_key = ''
        if key_file.exists():
            api_key = key_file.read_text().strip()

        if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
            reply = fallback_chatbot(user_msg)
        else:
            try:
                reply = gemini_chat(api_key, user_msg, session_id)
            except Exception as e:
                reply = fallback_chatbot(user_msg)

        ChatMessage.objects.create(session_id=session_id, message=user_msg, response=reply)
        return JsonResponse({'reply': reply, 'session_id': session_id})

    except Exception as e:
        return JsonResponse({'reply': 'We are temporarily unable to process your request. Please connect with us directly on WhatsApp at +91 78792 23442.', 'session_id': ''})


def gemini_chat(api_key, user_msg, session_id):
    """Client-facing AI Concierge using Google Gemini 2.5 Flash with live DB pricing, negotiation guardrails, and WhatsApp privilege hand-off"""
    import requests
    site = get_site_settings()
    free_sides = site.offer_bridal_free_sides
    disc_sides_rate = int(site.offer_next_sides_discounted_price)
    combo_disc = site.offer_combo_discount_percent
    combo_flat = int(site.offer_grand_combo_bundle_price)
    wa_number = site.whatsapp_number or "917879223442"
    today_code = site.default_auto_coupon_code if site.default_auto_coupon_active else "TODAYVIP"
    today_disc = site.default_auto_coupon_discount if site.default_auto_coupon_active else 15
    today_badge = site.default_auto_coupon_badge if site.default_auto_coupon_active else "Extra 15% VIP Privilege applied automatically today!"

    # Query active packages and services from database dynamically
    pkgs = list(MakeupPackage.objects.filter(is_active=True).order_by('order'))
    pkg_rules = []
    table_rows = []

    min_floor_pct = site.ai_negotiation_min_floor_percent or 75
    max_disc_pct = site.ai_max_discount_percent or 20

    for p in pkgs:
        std_val = float(p.price) if p.price else 0.0
        # Calculate offer price based on site coupon if active
        offer_val = round(std_val * (100 - today_disc) / 100) if site.default_auto_coupon_active else round(std_val * (100 - site.coupon_discount_percent) / 100) if site.coupon_active and site.coupon_discount_percent else std_val
        # Determine minimum negotiated floor price
        floor_val = float(p.min_negotiated_price) if p.min_negotiated_price else round(std_val * min_floor_pct / 100)
        
        feats = ", ".join(p.get_features_list()[:3])
        table_rows.append(f"| **{p.name}** | ₹{std_val:,.0f} | ₹{offer_val:,.0f} | {feats} |")
        pkg_rules.append(
            f"- {p.name}: Standard Rate ₹{std_val:,.0f}, Special Seasonal Rate ₹{offer_val:,.0f}. "
            f"ABSOLUTE MINIMUM NEGOTIATED FLOOR PRICE: ₹{floor_val:,.0f}. "
            f"Allowed to negotiate: {'YES' if (site.ai_negotiation_enabled and p.allow_ai_negotiation) else 'NO (Strict Fixed Rate)'}."
        )

    pkg_rules_text = "\n".join(pkg_rules)
    table_text = "\n".join(table_rows)

    system_prompt = f"""You are the Luxury Concierge AI for Anshita Makeover — India's premier bespoke bridal couture, hair, and beauty studio.
Respond in a warm, dignified, respectful, and sophisticated tone. Use clear English or respectful, elegant Hindi/Hinglish when addressed in Hindi.

TODAY'S DEFAULT EXCLUSIVE VIP PRIVILEGE:
- Default Auto Coupon: {today_code} ({today_disc}% Extra Discount)
- Announcement: {today_badge}

REAL-TIME DATABASE PACKAGES & PRICING RULES:
{pkg_rules_text}

Active Studio Booking Privileges:
- Bridal Booking: First {free_sides} Side Makeups are completely FREE (₹0).
- Subsidized Family Sides: Next 2 Side Makeups at ₹{disc_sides_rate:,} each.
- Bridal + Engagement Combo: Additional {combo_disc}% off.
- Grand Royal Bundle: Flat ₹{combo_flat:,}.

AI NEGOTIATION RANGE & GUARDRAIL SETTINGS:
- Negotiation Enabled: {'YES' if site.ai_negotiation_enabled else 'NO'}
- Strategy: {site.ai_negotiation_strategy.upper()}
- Max Negotiable Discount: {max_disc_pct}% off standard price
- Min Allowed Price Floor: {min_floor_pct}% of standard price
- Admin Directives: {site.ai_negotiation_instructions}

CRITICAL PRICING & NEGOTIATION RULES:
1. FACTUAL ACCURACY: You MUST quote exact rates from the database rules above. NEVER hallucinate or invent prices.
2. DISCOUNTS & BARGAINING:
   - When user asks to negotiate or gives a budget:
     * If user gives a budget >= Floor Price: You may warmly accept and grant a "Special Concierge Privilege Rate" matching or approaching their budget, and issue VIP code '{today_code}'.
     * If user gives a budget < Floor Price: State that due to 100% original international luxury products (TEMPTU, Charlotte Tilbury, MAC) and hygiene standards, our authorized minimum is ₹[Floor Price], but highlight that it includes {free_sides} FREE Side Makeups worth ₹7,000!
     * NEVER quote a price below the ABSOLUTE MINIMUM NEGOTIATED FLOOR PRICE.
3. WHATSAPP CONFIRMATION HAND-OFF:
   - When offering a negotiated rate, instruct the user that this special privilege is locked exclusively via WhatsApp.
   - WhatsApp link format: https://wa.me/{wa_number}?text=Namaste!%20AI%20Concierge%20has%20granted%20me%20a%20Special%20Privilege%20Rate%20of%20₹[Amount]%20with%20VIP%20code%20{today_code}.%20Please%20confirm%20my%20booking.

FORMATTING REQUIREMENTS:
- Structure package comparisons in clean markdown tables with bold highlights.
- Keep responses elegant, structured with bullet points (✦), concise, and never cut off mid-sentence!

Standard Pricing Reference Table:
| Service / Package | Standard Rate | Special Privilege Rate | Key Inclusions |
| :--- | :--- | :--- | :--- |
{table_text}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": user_msg}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.25, "maxOutputTokens": 800}
    }
    
    resp = requests.post(url, json=payload, timeout=6)
    if resp.status_code == 200:
        data = resp.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    raise RuntimeError(f"Gemini API error: {resp.status_code} - {resp.text[:200]}")


# ── API: Admin AI Co-Pilot (Intelligent Natural Language Website Manager) ──
@login_required
@require_POST
def admin_ai_command(request):
    """
    Admin AI Copilot: Translates natural language instructions into database actions:
    Examples:
    - 'Add a new package named Haldi Sunshine Glam for 8500 with features: Dewy yellow tones, flower jewellery setting'
    - 'Change coupon to SUMMER40 with 40% discount'
    - 'Embed instagram reel https://www.instagram.com/reel/Dap4JkvKL1E/ titled Shubho Drishti'
    - 'Embed youtube video https://www.youtube.com/watch?v=xxx titled Bridal Masterclass'
    - 'Update HD bridal price to 26000'
    """
    try:
        body = json.loads(request.body)
        prompt = body.get('prompt', '').strip()
        if not prompt:
            return JsonResponse({'ok': False, 'error': 'Please enter an instruction.'})

        key_file = Path(settings.BASE_DIR) / 'gemini_api_key.txt'
        api_key = key_file.read_text().strip() if key_file.exists() else ''
        if not api_key:
            return JsonResponse({'ok': False, 'error': 'Gemini API key not configured.'})

        # Ask Gemini to return structured JSON action
        system_instruction = """You are the Dedicated Admin AI Co-Pilot for Anshita Makeover website management and database validation.
Your role is to strictly validate and execute modifications to:
1. Packages, prices, and features
2. Booking offer rules: number of free side makeups (e.g. 2 free), subsidized side makeup rate (e.g. ₹2,500 to ₹3,000), combo bridal+engagement discount % (e.g. 10% to 20%), and Grand Royal Combo bundle flat rate (e.g. ₹50,000).
3. Coupons and exit privileges
4. Instagram reels and media embeds

Do NOT include conversational chatter or markdown fences. Return ONLY a single raw JSON object matching one of the schemas below.

Validation Rules:
- Discount percentages must be between 0% and 50% (Combo discount must not exceed 20%).
- Subsidized side makeup price must be between 2000 and 4500 (standard is 2500 - 3000).
- Free side makeup count must be an integer between 0 and 5 (default 2).

Supported Action Schemas:

1. Modify Booking Privileges & Offer Rules:
{
  "action": "modify_booking_offers",
  "free_sides": 2,
  "discounted_side_price": 2500,
  "combo_discount_percent": 15,
  "bundle_price": 50000,
  "active": true
}

2. Add or Update Service/Package:
{
  "action": "create_package",
  "name": "Package Name",
  "package_type": "bridal|side_makeup|engagement|reception|party|hair|nails|beauty|custom",
  "price": 50000,
  "price_label": "₹50,000",
  "tagline": "Short description",
  "features": "Feature 1\\nFeature 2\\nFeature 3",
  "is_featured": false
}

3. Update Existing Package Price:
{
  "action": "update_package",
  "package_id": 22,
  "name_query": "Grand Royal|HD Bridal|Airbrush",
  "price": 50000,
  "features": "Optional new features"
}

4. Update Coupon:
{
  "action": "update_coupon",
  "coupon_code": "SUMMER40",
  "discount_percent": 40,
  "label": "Summer Bridal Privilege",
  "active": true
}

5. Embed Media:
{
  "action": "add_media",
  "title": "Title",
  "media_type": "instagram|youtube",
  "url": "https://...",
  "category": "bridal|engagement|hair|nails|party",
  "section": "gallery|reels|both"
}

6. Update Service Price:
{
  "action": "update_price",
  "service": "makeup_hd|makeup_airbrush|nails_art|nails_extension|photo_premium|photo_standard",
  "price": 26000
}

7. Create or Configure Partner Add-on & Bundle (ROI & Commission):
{
  "action": "create_addon_bundle",
  "name": "Bespoke Royal Photography & Stage Decor",
  "category": "photography|decor|catering|salon|dj|full_event|custom",
  "vendor_cost": 50000,
  "client_quote": 68000,
  "features": "Cinematic 4K Wedding Film\\n2 Candid Photographers\\nRoyal Stage Floral Mandap",
  "description": "Curated partner addon"
}

8. Informational, ROI advisory, or validation warning:
{
  "action": "answer",
  "message": "Explanation, commission calculation, or bundle combo recommendation"
}
"""
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 600}
        }
        res = requests.post(url, json=payload, timeout=12)
        if res.status_code != 200:
            return JsonResponse({'ok': False, 'error': f"Gemini error: {res.status_code}"})

        raw_text = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        # Clean potential markdown formatting
        if raw_text.startswith('```'):
            raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
            raw_text = re.sub(r'\s*```$', '', raw_text)

        action_data = json.loads(raw_text)
        action_type = action_data.get('action')

        # Execute Actions
        if action_type == 'modify_booking_offers':
            site = get_site_settings()
            if 'free_sides' in action_data and action_data['free_sides'] is not None:
                site.offer_bridal_free_sides = max(0, min(5, int(action_data['free_sides'])))
            if 'discounted_side_price' in action_data and action_data['discounted_side_price'] is not None:
                rate = float(action_data['discounted_side_price'])
                site.offer_next_sides_discounted_price = max(1500.0, min(4500.0, rate))
            if 'combo_discount_percent' in action_data and action_data['combo_discount_percent'] is not None:
                disc = int(action_data['combo_discount_percent'])
                site.offer_combo_discount_percent = max(5, min(25, disc))
            if 'bundle_price' in action_data and action_data['bundle_price'] is not None:
                b_price = float(action_data['bundle_price'])
                site.offer_grand_combo_bundle_price = b_price
                # Also synchronize package 22 or bundle package price in DB
                MakeupPackage.objects.filter(name__icontains='Grand Royal Heritage').update(
                    price=b_price,
                    price_label=f"₹{int(b_price):,}"
                )
            if 'active' in action_data:
                site.offer_rules_active = bool(action_data['active'])
            site.save()
            return JsonResponse({
                'ok': True,
                'message': (
                    f"✨ Booking Offers Validated & Saved!\n"
                    f"• Bridal Free Sides: {site.offer_bridal_free_sides} Free\n"
                    f"• Next 2 Sides Special Rate: ₹{int(site.offer_next_sides_discounted_price):,}\n"
                    f"• Engagement Combo Privilege: {site.offer_combo_discount_percent}% OFF\n"
                    f"• Grand Heritage Bundle: ₹{int(site.offer_grand_combo_bundle_price):,}"
                ),
                'action_executed': action_data
            })

        elif action_type == 'update_package':
            query = action_data.get('name_query') or action_data.get('name', '')
            pkg_id = action_data.get('package_id')
            qs = MakeupPackage.objects.filter(id=pkg_id) if pkg_id else MakeupPackage.objects.filter(name__icontains=query)
            pkg = qs.first()
            if not pkg:
                return JsonResponse({'ok': False, 'error': f"Could not find package matching '{query}' to update."})
            if 'price' in action_data and action_data['price'] is not None:
                p_val = float(action_data['price'])
                pkg.price = p_val
                pkg.price_label = f"₹{int(p_val):,}"
            if action_data.get('features'):
                pkg.features = action_data['features']
            pkg.save()
            return JsonResponse({
                'ok': True,
                'message': f"✨ Package '{pkg.name}' updated! New price: {pkg.price_label}.",
                'action_executed': action_data
            })

        elif action_type == 'create_package':
            pkg = MakeupPackage.objects.create(
                name=action_data.get('name', 'Bespoke Package'),
                package_type=action_data.get('package_type', 'bridal'),
                tagline=action_data.get('tagline', ''),
                price=float(action_data['price']) if action_data.get('price') else None,
                price_label=action_data.get('price_label') or (f"₹{int(action_data['price']):,}" if action_data.get('price') else 'On Request'),
                features=action_data.get('features', ''),
                is_featured=bool(action_data.get('is_featured', False)),
                is_active=True
            )
            return JsonResponse({
                'ok': True,
                'message': f"✨ Package '{pkg.name}' created successfully with price {pkg.price_label}!",
                'action_executed': action_data
            })

        elif action_type == 'update_coupon':
            site = get_site_settings()
            site.coupon_code = action_data.get('coupon_code', site.coupon_code).upper()
            site.coupon_discount_percent = int(action_data.get('discount_percent', site.coupon_discount_percent))
            site.coupon_label = action_data.get('label', site.coupon_label)
            site.coupon_active = bool(action_data.get('active', True))
            site.coupon_auto_by_date = False
            site.save()
            return JsonResponse({
                'ok': True,
                'message': f"🏷️ Coupon updated to '{site.coupon_code}' ({site.coupon_discount_percent}% OFF)!",
                'action_executed': action_data
            })

        elif action_type == 'add_media':
            m_url = action_data.get('url', '')
            m_type = action_data.get('media_type', 'instagram')
            embed_code = ''
            thumb = ''

            if 'instagram.com' in m_url or m_type == 'instagram':
                m_type = 'instagram'
                match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', m_url)
                if match:
                    embed_code = match.group(1)
            elif 'youtube.com' in m_url or 'youtu.be' in m_url or m_type == 'youtube':
                m_type = 'youtube'
                match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})', m_url)
                if match:
                    embed_code = match.group(1)
                    thumb = f"https://img.youtube.com/vi/{embed_code}/hqdefault.jpg"

            item = MediaItem.objects.create(
                title=action_data.get('title', 'Featured Spotlight'),
                media_type=m_type,
                category=action_data.get('category', 'bridal'),
                section=action_data.get('section', 'both'),
                caption=action_data.get('caption', ''),
                external_url=m_url,
                embed_code=embed_code,
                thumbnail_url=thumb,
                views_count='24.5K+ views',
                is_active=True
            )
            return JsonResponse({
                'ok': True,
                'message': f"🎥 Media '{item.title}' ({item.get_media_type_display()}) successfully added and embedded on the website!",
                'action_executed': action_data
            })

        elif action_type == 'update_price':
            svc = action_data.get('service')
            pr = float(action_data.get('price', 0))
            if svc in ['photo_premium', 'photo_standard']:
                EventPackage.objects.filter(package_type=svc).update(price=pr, price_label=f"₹{int(pr):,}")
            else:
                sp, _ = ServicePrice.objects.get_or_create(service=svc)
                sp.price = pr
                sp.price_label = f"₹{int(pr):,}"
                sp.save()
            return JsonResponse({
                'ok': True,
                'message': f"💰 Price for '{svc}' successfully updated to ₹{int(pr):,}!",
                'action_executed': action_data
            })

        elif action_type == 'create_addon_bundle':
            name = action_data.get('name', 'Bespoke Add-on Bundle')
            cat = action_data.get('category', 'custom')
            v_cost = float(action_data.get('vendor_cost', 0) or 0)
            quote = float(action_data.get('client_quote', 0) or action_data.get('price', 0) or 0)
            feats = action_data.get('features', '')
            desc = action_data.get('description', '')
            
            pkg = EventPackage.objects.create(
                name=name,
                category=cat,
                package_type='custom',
                vendor_cost=v_cost,
                price=quote if quote > 0 else None,
                price_label=f"₹{int(quote):,}" if quote > 0 else "On Request",
                features=feats,
                description=desc,
                is_active=True,
                created_by=request.user
            )
            return JsonResponse({
                'ok': True,
                'message': (
                    f"🎁 Partner Add-on Bundle '{pkg.name}' Created!\n"
                    f"• Category: {pkg.get_category_display()}\n"
                    f"• Base Vendor Cost: ₹{int(pkg.vendor_cost):,}\n"
                    f"• Client Quote: {pkg.price_label}\n"
                    f"• Studio Margin: ₹{int(pkg.studio_commission):,} ({pkg.margin_percent}% margin | {pkg.roi_percent}% ROI)"
                ),
                'action_executed': action_data
            })

        else:
            return JsonResponse({
                'ok': True,
                'message': action_data.get('message', 'Processed instruction.'),
                'action_executed': action_data
            })

    except Exception as e:
        return JsonResponse({'ok': False, 'error': f"Failed to execute: {str(e)}"})


def fallback_chatbot(msg):
    msg_lower = msg.lower()
    site = get_site_settings()
    wa_number = site.whatsapp_number or "917879223442"
    today_code = site.default_auto_coupon_code if site.default_auto_coupon_active else "TODAYVIP"
    today_disc = site.default_auto_coupon_discount if site.default_auto_coupon_active else 15
    today_badge = site.default_auto_coupon_badge if site.default_auto_coupon_active else "Extra 15% VIP Privilege applied automatically today!"

    # ── 1. SMART AI PRICE NEGOTIATION & BUDGET MATCHING ──
    is_negotiation = any(k in msg_lower for k in [
        'negotiat', 'bargain', 'budget', 'kam karo', 'kam ho sakta', 'kam kijiye',
        'discount', 'sasta', 'too costly', 'expensive', 'mehenga', 'mehanga', 'concession',
        'best price', 'last price', 'final price', 'special price', 'vip code',
        '20000', '25000', '28000', '30000', '32000', '35000', '40000'
    ])

    if is_negotiation and site.ai_negotiation_enabled:
        # Extract potential budget amount from message (e.g. "28k", "₹28,000", "28000", "Rs. 25000")
        msg_clean = msg_lower.replace(',', '')
        budget = None
        m_k = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*k\b', msg_clean)
        if m_k:
            budget = float(m_k.group(1)) * 1000
        else:
            m_num = re.search(r'(?:₹|rs\.?|inr)?\s*(\d{4,6})\b', msg_clean)
            if m_num:
                budget = float(m_num.group(1))

        # Standard bridal package anchors
        hd_std = 35000.0
        air_std = 45000.0
        min_floor_pct = site.ai_negotiation_min_floor_percent or 75
        max_disc_pct = site.ai_max_discount_percent or 20

        hd_floor = round(hd_std * min_floor_pct / 100)   # e.g. ₹26,250
        air_floor = round(air_std * min_floor_pct / 100) # e.g. ₹33,750

        if budget:
            if budget >= hd_floor:
                # Accept and lock authorized concierge rate
                target_suite = "Master Airbrush Bridal" if budget >= air_floor else "Imperial Royal HD Bridal"
                std_ref = air_std if budget >= air_floor else hd_std
                savings = int(std_ref - budget)
                return f"""### ✨ Special AI Concierge Privilege Approved!

Namaste! 🙏 We truly appreciate you sharing your planned budget with us.
Because every bride deserves radiant perfection on her auspicious day, our studio management has **authorized your requested Special Rate of ₹{int(budget):,}** for the **{target_suite}**!

✦ **Authorized Privilege Rate**: **₹{int(budget):,}** *(Standard: ₹{int(std_ref):,} — You save ₹{savings:,}!)*
✦ **Complimentary VIP Privileges Included**:
  • **2 Family/Side Makeups completely FREE (₹0)** *(Direct Value: ₹7,000)*
  • TEMPTU 24-hr Cry-Proof Base & Cut-Crease Eye Artistry
  • Designer Dupatta & Sabyasachi/Banarasi Lehenga Draping
  • Premium Silk Eyelashes, Hair Accessories & Colored Lenses
✦ **Exclusive VIP Code**: **`{today_code}`** *(Assigned to your date)*

👉 **Lock This Negotiated Privilege on WhatsApp Before the Slot Closes**:
[Click to Lock ₹{int(budget):,} on WhatsApp](https://wa.me/{wa_number}?text=Namaste!%20AI%20Concierge%20has%20authorized%20a%20Special%20Rate%20of%20₹{int(budget):,}%20with%20VIP%20code%20{today_code}.%20Please%20reserve%20my%20wedding%20date.)"""
            else:
                # Below floor: politely defend luxury standard while offering authorized floor rate
                return f"""### ✦ Anshita Makeover Bespoke Concierge Advisory

Namaste! 🙏 We completely respect and honor your planned budget of ₹{int(budget):,}.
At Anshita Makeover, we exclusively utilize 100% original international luxury brands (TEMPTU USA Airbrush, Charlotte Tilbury, Huda Beauty, MAC, NARS) with dedicated single-bride attention and sterile medical-grade hygiene kits to guarantee a 24-hour cry-proof glow.

To support your dream wedding while maintaining our certified artistry:
✦ **Studio Authorized Best Floor Rate**: **₹{hd_floor:,}** for Imperial Royal HD Bridal *(Standard: ₹35,000)*
✦ **Complimentary Inclusions**: Includes **2 Family/Side Makeups completely FREE (₹0)** worth ₹7,000!
✦ **Today's Extra Privilege**: Apply VIP Code **`{today_code}`** today to lock this special concession.

👉 [Connect with Anshita on WhatsApp to Finalize Your Plan](https://wa.me/{wa_number}?text=Namaste%20Anshita!%20My%20budget%20is%20around%20₹{int(budget):,}.%20Can%20we%20customize%20a%20bridal%20suite%20for%20my%20date?)"""

        else:
            # General negotiation / discount question
            return f"""### ✦ AI Smart Concierge Negotiation & Exclusive Privileges

Namaste! ✨ Yes, under our current Studio Privilege Policy, our AI Concierge is authorized to provide flexible custom pricing and privileges:

✦ **⚡ Today's Default VIP Privilege**: Code **`{today_code}`** is active today, giving you an **extra {today_disc}% automatic savings** across all bridal suites!
✦ **👑 Complimentary Family Inclusions**: First **2 Side Makeups are 100% FREE (₹0)** with any Bridal booking *(Direct savings of ₹7,000!)*.
✦ **💍 Event Combo Savings**: Up to **20% OFF** when booking Engagement / Reception alongside Bridal.
✦ **🤝 Flexible Budget Negotiation**: What is your **Wedding Date** and **Planned Target Budget**? Share your number and I will calculate the best authorized concession for you right now!

Or lock your privileged booking directly with our bridal concierge on WhatsApp at **+91 {wa_number}**."""

    # ── 2. BRIDAL INQUIRIES ──
    if any(w in msg_lower for w in ['bridal', 'wedding', 'shaadi', 'bride', 'dulhan']):
        return f"""Namaste! ✨ We would be delighted to curate your dream bridal look.

### 👑 Signature Bridal Suites & Booking Privileges

| Package Suite | Investment | Special Inclusions |
| :--- | :--- | :--- |
| **Imperial Royal HD Suite** | ₹24,500 *(Offer)* | HD Base, Cut-Crease Eyes, Dupatta Draping, **2 Side Makeups FREE** |
| **Master Airbrush Suite** | ₹31,500 *(Offer)* | TEMPTU 24-hr Cry-Proof, Vanity Setup, **2 Side Makeups FREE** |
| **Grand Royal Heritage Suite** | ₹50,000 *(Bundle)* | **Bridal + Engagement Suite** + 2 Side Makeups FREE |

✦ **⚡ Today's Deal**: Auto code **`{today_code}`** applies for extra savings today!
✦ **VIP Booking Privilege**: First 2 Side Makeups are **FREE (₹0)**, and the next 2 at only **₹2,500 each**!
✦ **Combo Privilege**: Up to 20% discount on Engagement & Roka when booked together!

To reserve your auspicious date, please WhatsApp our bridal team at +91 {wa_number}."""

    # ── 3. PRICING INQUIRIES ──
    if any(w in msg_lower for w in ['price', 'rate', 'cost', 'kitna', 'fees', 'charges', 'package', 'packages']):
        return f"""### ✨ Anshita Makeover Curated Pricing Guide

| Service / Suite | Investment | Privilege Benefits |
| :--- | :--- | :--- |
| **Imperial Royal HD Bridal** | ₹24,500 / ₹35,000 | 2 Side Makeups FREE |
| **Master Airbrush Bridal** | ₹31,500 / ₹45,000 | TEMPTU 24-hr Cry-Proof, 2 FREE Sides |
| **Engagement & Roka Glam** | ₹12,600 / ₹18,000 | Glass-Skin Glow & Hair Styling |
| **Grand Royal Combo Suite** | ₹50,000 Flat | Bridal + Engagement + 2 Free Sides |
| **Side & Family Artistry** | ₹2,500 (Subsidized) | Professional Glam & Draping |
| **Academy Masterclass** | ₹35,400 | 4 Weeks Certified Hands-on Training |

✦ **Today's Auto Privilege**: Extra {today_disc}% off with code **`{today_code}`**!
✦ Connect with our concierge on WhatsApp at **+91 {wa_number}** for a tailored quote!"""

    if any(w in msg_lower for w in ['photo', 'photography', 'event', 'videography', 'camera']):
        return f"Through Anshita Signature Events & Photography, we offer complete royal wedding coverage: 📸\n✦ Standard Collection: ₹90,000 (Candid + Traditional, 300+ edited portraits)\n✦ Royal Premium Collection: ₹1,20,000 (Full-day cinematic video, Drone aerials, Pre-wedding & Premium album)\nFor complete event management inquiries, please connect with us at +91 {wa_number}."

    # ── 4. COUPON & CODE INQUIRIES ──
    if any(w in msg_lower for w in ['coupon', 'discount', 'offer', 'code', 'promo', 'vip']):
        return f"""🎉 **Anshita Makeover Active Offers & VIP Codes**!
✦ **Today's Auto Privilege**: Code **`{today_code}`** is active today for extra **{today_disc}% OFF**!
✦ **Announcement**: {today_badge}
✦ **VIP Booking Privilege**: First 2 Side Makeups are **100% FREE (₹0)** with any Bridal booking!
Please mention code **{today_code}** when booking on WhatsApp at +91 {wa_number}."""

    if any(w in msg_lower for w in ['location', 'address', 'kahan', 'studio', 'city']):
        return f"Anshita Makeover Studio is based in Jabalpur, Madhya Pradesh, catering to bridal appointments, destination weddings, and couture bookings nationwide. 📍\nTo reserve your date or book a consultation, please WhatsApp +91 {wa_number}."

    if any(w in msg_lower for w in ['hello', 'hi', 'namaste', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return f"Namaste and warm greetings from Anshita Makeover! 🙏✨\nWe are dedicated to crafting your most radiant and elegant moments across India — from royal bridal transformations to certified professional makeup education.\nToday's special privilege: Use code **`{today_code}`** for extra savings today!\nHow may we be at your service today? 💄"

    return f"Thank you for reaching out to Anshita Makeover. ✨ For immediate assistance, personalized packages, and appointment reservations across India, please WhatsApp our bridal concierge at +91 {wa_number}. We look forward to creating magic with you! 💍"


# ── API: Set Language ─────────────────────────────────────────
@csrf_exempt
def set_language(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            lang = body.get('language') or body.get('lang', 'hinglish')
        except Exception:
            lang = request.POST.get('language') or request.POST.get('lang', 'hinglish')
        
        is_json = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('accept', '') or
            request.content_type == 'application/json'
        )
        if is_json:
            res = JsonResponse({'status': 'ok', 'language': lang})
            res.set_cookie('lang', lang, max_age=365*24*3600)
            return res

    lang = request.GET.get('lang') or request.POST.get('lang', 'hinglish')
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('lang', lang, max_age=365*24*3600)
    return response



# ── Admin Login/Logout ────────────────────────────────────────
def admin_login(request):
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.headers.get('accept', '').startswith('application/json') or
        request.POST.get('ajax') == '1'
    )
    if request.user.is_authenticated and request.user.is_staff:
        if is_ajax:
            return JsonResponse({'ok': True, 'redirect': '/admin-portal/'})
        return redirect(request.GET.get('next', '/admin-portal/'))

    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next') or '/admin-portal/'
            if is_ajax:
                return JsonResponse({'ok': True, 'redirect': next_url})
            return redirect(next_url)
        else:
            error = 'Invalid credentials or account does not have admin privileges.'
            if is_ajax:
                return JsonResponse({'ok': False, 'error': error}, status=401)
    return render(request, 'core/admin_login.html', {'error': error})


def admin_logout_view(request):
    logout(request)
    return redirect('/')


def admin_portal(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin-login/?next=/admin-portal/')
    
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

    # Parse VIP generated codes JSON
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

    context = {
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
        'user': request.user,
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
    return render(request, 'core/admin_portal.html', context)



# ── API: Get Current Active & Exit Coupons ────────────────────
def get_coupon_api(request):
    site = get_site_settings()
    active_coupon = get_active_coupon(site)
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
    return JsonResponse({
        'ok': True,
        'coupon': active_coupon,
        'default_coupon': default_coupon,
        'exit_coupon': exit_coupon
    })


# ── API: Admin Coupon Control ─────────────────────────────────
@login_required
def admin_coupon_update(request):
    if request.method == 'POST':
        site = get_site_settings()
        action = request.POST.get('action') or ''

        # Support JSON payload
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                action = data.get('action', action)
            except Exception:
                data = {}
        else:
            data = request.POST

        # 1. VIP Code Generation
        if action == 'generate_vip':
            code = data.get('code', '').strip().upper()
            if not code:
                import random
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
            return JsonResponse({'ok': True, 'vip': new_vip, 'vip_list': vip_list})

        # 2. VIP Code Revoke / Deletion
        if action == 'delete_vip':
            target_id = data.get('id', '')
            target_code = data.get('code', '')
            try:
                vip_list = json.loads(site.vip_generated_codes or '[]')
                vip_list = [v for v in vip_list if v.get('id') != target_id and v.get('code') != target_code]
                site.vip_generated_codes = json.dumps(vip_list)
                site.save()
                return JsonResponse({'ok': True, 'vip_list': vip_list})
            except Exception as e:
                return JsonResponse({'ok': False, 'error': str(e)})

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
        return JsonResponse({
            'ok': True,
            'default_coupon_code': site.default_auto_coupon_code,
            'default_coupon_discount': site.default_auto_coupon_discount,
            'default_coupon_active': site.default_auto_coupon_active,
            'coupon_code': site.coupon_code,
            'exit_coupon_code': site.exit_coupon_code,
            'exit_coupon_discount': site.exit_coupon_discount_percent
        })
    return JsonResponse({'ok': False})


# ── API: Admin Price Update ───────────────────────────────────
@login_required
def admin_price_update(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        target_type = data.get('type')
        service = data.get('service')
        price = data.get('price')

        # 1. AI Negotiation Settings Update
        if target_type in ['ai_negotiation', 'negotiation_rules']:
            site = get_site_settings()
            if 'ai_negotiation_enabled' in data:
                site.ai_negotiation_enabled = bool(data['ai_negotiation_enabled'])
            if 'ai_negotiation_min_floor_percent' in data:
                site.ai_negotiation_min_floor_percent = max(40, min(95, int(data['ai_negotiation_min_floor_percent'])))
            if 'ai_max_discount_percent' in data:
                site.ai_max_discount_percent = max(5, min(50, int(data['ai_max_discount_percent'])))
            if 'ai_negotiation_strategy' in data:
                site.ai_negotiation_strategy = str(data['ai_negotiation_strategy'])
            if 'ai_negotiation_instructions' in data:
                site.ai_negotiation_instructions = str(data['ai_negotiation_instructions'])
            site.save()

            # Handle per-service floor price updates if provided
            if 'service_floors' in data and isinstance(data['service_floors'], list):
                for sf in data['service_floors']:
                    s_id = sf.get('id')
                    floor_pr = sf.get('min_negotiated_price')
                    allow_neg = sf.get('allow_ai_negotiation')
                    max_disc = sf.get('max_discount_percent')
                    if s_id:
                        svc_obj = StudioService.objects.filter(id=s_id).first()
                        if svc_obj:
                            if floor_pr is not None and str(floor_pr).strip():
                                svc_obj.min_negotiated_price = float(floor_pr)
                            elif floor_pr == '':
                                svc_obj.min_negotiated_price = None
                            if allow_neg is not None:
                                svc_obj.allow_ai_negotiation = bool(allow_neg)
                            if max_disc is not None and str(max_disc).strip():
                                svc_obj.max_discount_percent = int(max_disc)
                            svc_obj.save()

            return JsonResponse({
                'ok': True,
                'ai_negotiation_enabled': site.ai_negotiation_enabled,
                'ai_negotiation_min_floor_percent': site.ai_negotiation_min_floor_percent,
                'ai_max_discount_percent': site.ai_max_discount_percent,
                'ai_negotiation_strategy': site.ai_negotiation_strategy
            })

        # Course fee update
        if target_type == 'course' or 'course_id' in data:
            course_id = data.get('course_id') or data.get('id')
            if course_id and price is not None:
                AcademyCourse.objects.filter(id=course_id).update(course_fee=float(price))
                return JsonResponse({'ok': True})

        # Event Photography package price update
        if target_type == 'event' or service in ['photo_premium', 'photo_standard', 'premium', 'standard']:
            pkg_type = 'photography_premium' if (service in ['premium', 'photo_premium'] or data.get('package_type') == 'premium') else 'photography_standard'
            if price is not None:
                p_val = float(price)
                label = f"₹{p_val/100000:.1f} Lakh" if p_val >= 100000 else f"₹{int(p_val):,}"
                EventPackage.objects.filter(package_type=pkg_type).update(price=p_val, price_label=label)
                return JsonResponse({'ok': True})

        # Booking Privilege / Offer update
        if target_type in ['booking_offer', 'offer_rules']:
            site = get_site_settings()
            if 'free_sides' in data and data['free_sides'] is not None:
                site.offer_bridal_free_sides = max(0, min(5, int(data['free_sides'])))
            if 'discounted_side_price' in data and data['discounted_side_price'] is not None:
                site.offer_next_sides_discounted_price = float(data['discounted_side_price'])
            if 'combo_discount_percent' in data and data['combo_discount_percent'] is not None:
                site.offer_combo_discount_percent = max(0, min(30, int(data['combo_discount_percent'])))
            if 'bundle_price' in data and data['bundle_price'] is not None:
                b_pr = float(data['bundle_price'])
                site.offer_grand_combo_bundle_price = b_pr
                MakeupPackage.objects.filter(name__icontains='Grand Royal Heritage').update(price=b_pr, price_label=f"₹{int(b_pr):,}")
            if 'active' in data:
                site.offer_rules_active = bool(data['active'])
            site.save()
            return JsonResponse({
                'ok': True,
                'free_sides': site.offer_bridal_free_sides,
                'discounted_side_price': float(site.offer_next_sides_discounted_price),
                'combo_discount_percent': site.offer_combo_discount_percent,
                'bundle_price': float(site.offer_grand_combo_bundle_price)
            })

        # Travel / Outstation Fee Settings update
        if target_type == 'travel':
            site = get_site_settings()
            if 'travel_widget_active' in data:
                site.travel_widget_active = bool(data['travel_widget_active'])
            if 'travel_same_zone_km' in data and data['travel_same_zone_km'] is not None:
                site.travel_same_zone_km = int(data['travel_same_zone_km'])
            if 'travel_near_label' in data:
                site.travel_near_label = str(data['travel_near_label'])
            if 'travel_near_fee_min' in data and data['travel_near_fee_min'] is not None:
                site.travel_near_fee_min = float(data['travel_near_fee_min'])
            if 'travel_near_fee_max' in data and data['travel_near_fee_max'] is not None:
                site.travel_near_fee_max = float(data['travel_near_fee_max'])
            if 'travel_far_label' in data:
                site.travel_far_label = str(data['travel_far_label'])
            if 'travel_far_fee_min' in data and data['travel_far_fee_min'] is not None:
                site.travel_far_fee_min = float(data['travel_far_fee_min'])
            if 'travel_far_fee_max' in data and data['travel_far_fee_max'] is not None:
                site.travel_far_fee_max = float(data['travel_far_fee_max'])
            if 'travel_custom_note' in data:
                site.travel_custom_note = str(data['travel_custom_note'])
            site.save()
            return JsonResponse({'ok': True, 'message': 'Travel settings saved'})

        # Service price update
        is_on_request = data.get('is_on_request', False)
        sp, _ = ServicePrice.objects.get_or_create(service=service)
        if price is not None and str(price).strip():
            sp.price = float(price)
        sp.is_on_request = is_on_request
        sp.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


# ── API: Admin Event & Add-on Package CRUD (Commission & ROI) ─────────────────
@login_required
def admin_event_package(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pkg_id = data.get('id')
        if pkg_id:
            try:
                pkg = EventPackage.objects.get(id=pkg_id)
            except EventPackage.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Not found'})
        else:
            pkg = EventPackage(created_by=request.user)

        pkg.name = data.get('name', pkg.name if pkg_id else '')
        pkg.category = data.get('category', pkg.category if pkg_id else 'custom')
        pkg.package_type = data.get('package_type', 'custom')
        pkg.description = data.get('description', '')
        pkg.features = data.get('features', '')
        pkg.is_active = data.get('is_active', True)
        pkg.is_featured = data.get('is_featured', False)
        
        vendor_cost_str = data.get('vendor_cost', '')
        pkg.vendor_cost = float(vendor_cost_str) if vendor_cost_str not in [None, '', 'null'] else 0.0

        price_str = data.get('price', '')
        pkg.price = float(price_str) if price_str not in [None, '', 'null'] else None
        
        if pkg.price:
            pkg.price_label = f"₹{int(pkg.price):,}"
        else:
            pkg.price_label = data.get('price_label', 'On Request')
        pkg.save()
        return JsonResponse({
            'ok': True,
            'id': pkg.id,
            'commission': pkg.studio_commission,
            'margin_pct': pkg.margin_percent,
            'roi_pct': pkg.roi_percent
        })

    if request.method == 'DELETE':
        data = json.loads(request.body)
        EventPackage.objects.filter(id=data.get('id')).delete()
        return JsonResponse({'ok': True})

    # GET
    pkgs = []
    for p in EventPackage.objects.all():
        pkgs.append({
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'category_display': p.get_category_display(),
            'package_type': p.package_type,
            'description': p.description,
            'features': p.features,
            'vendor_cost': float(p.vendor_cost) if p.vendor_cost else 0.0,
            'price': float(p.price) if p.price else None,
            'price_label': p.price_label,
            'is_active': p.is_active,
            'is_featured': p.is_featured,
            'commission': p.studio_commission,
            'margin_pct': p.margin_percent,
            'roi_pct': p.roi_percent
        })
    return JsonResponse({'packages': pkgs})


# ── API: Admin Artist Management (CRUD) ─────────────────────────
@login_required
def admin_artist_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            artist_id = request.POST.get('id')
            Artist.objects.filter(id=artist_id).delete()
            return JsonResponse({'ok': True})

        artist_id = request.POST.get('id')
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'ok': False, 'error': 'Artist name is required.'})

        specialities = request.POST.get('specialities', 'makeup').strip()
        bio = request.POST.get('bio', '').strip()
        order_val = request.POST.get('order', 0)
        try:
            order = int(order_val)
        except (ValueError, TypeError):
            order = 0
        is_active = request.POST.get('is_active') != '0'

        if artist_id:
            try:
                artist = Artist.objects.get(id=artist_id)
                artist.name = name
                artist.specialities = specialities
                artist.bio = bio
                artist.order = order
                artist.is_active = is_active
            except Artist.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Artist not found.'})
        else:
            base_slug = slugify(name) or 'artist'
            slug = base_slug
            idx = 1
            while Artist.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{idx}"
                idx += 1
            artist = Artist(
                name=name,
                slug=slug,
                specialities=specialities,
                bio=bio,
                order=order,
                is_active=is_active
            )

        if 'photo' in request.FILES:
            artist.photo = request.FILES['photo']

        artist.save()
        return JsonResponse({
            'ok': True,
            'artist': {
                'id': artist.id,
                'name': artist.name,
                'specialities': artist.specialities,
                'bio': artist.bio,
                'photo_url': artist.photo.url if artist.photo else '',
                'order': artist.order,
                'is_active': artist.is_active
            }
        })

    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            artist_id = data.get('id')
            Artist.objects.filter(id=artist_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    # GET
    artists = []
    for a in Artist.objects.all():
        artists.append({
            'id': a.id,
            'name': a.name,
            'slug': a.slug,
            'bio': a.bio,
            'specialities': a.specialities,
            'photo_url': a.photo.url if a.photo else '',
            'order': a.order,
            'is_active': a.is_active
        })
    return JsonResponse({'artists': artists})


# ── API: Admin Service / Package Management (CRUD) ────────────
@login_required
def admin_service_manage(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        action = data.get('action')
        if action == 'delete':
            pkg_id = data.get('id')
            MakeupPackage.objects.filter(id=pkg_id).delete()
            return JsonResponse({'ok': True})

        pkg_id = data.get('id')
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'ok': False, 'error': 'Service name is required.'})

        package_type = data.get('package_type', 'bridal')
        tagline = data.get('tagline', '').strip()
        price_val = data.get('price')
        price = float(price_val) if price_val and str(price_val).strip() else None
        price_label = data.get('price_label', '').strip()
        if not price_label:
            price_label = f"₹{int(price):,}" if price else 'On Request'
        features = data.get('features', '').strip()
        is_featured = str(data.get('is_featured', '')).lower() in ['1', 'true', 'on']
        is_active = str(data.get('is_active', '1')).lower() not in ['0', 'false']

        if pkg_id:
            try:
                pkg = MakeupPackage.objects.get(id=pkg_id)
                pkg.name = name
                pkg.package_type = package_type
                pkg.tagline = tagline
                pkg.price = price
                pkg.price_label = price_label
                pkg.features = features
                pkg.is_featured = is_featured
                pkg.is_active = is_active
                pkg.save()
            except MakeupPackage.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Service package not found.'})
        else:
            pkg = MakeupPackage.objects.create(
                name=name,
                package_type=package_type,
                tagline=tagline,
                price=price,
                price_label=price_label,
                features=features,
                is_featured=is_featured,
                is_active=is_active
            )

        return JsonResponse({
            'ok': True,
            'package': {
                'id': pkg.id,
                'name': pkg.name,
                'package_type': pkg.package_type,
                'price': float(pkg.price) if pkg.price else None,
                'price_label': pkg.price_label,
                'features': pkg.features
            }
        })

    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            pkg_id = data.get('id')
            MakeupPackage.objects.filter(id=pkg_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    # GET
    pkgs = list(MakeupPackage.objects.all().values())
    return JsonResponse({'packages': pkgs})





# ── API: Customer Review Submission (Public) ──────────────────
@require_POST
def submit_review(request):
    try:
        data = json.loads(request.body)
        name = data.get('client_name', '').strip()
        review_text = data.get('review_text', '').strip()
        event_type = data.get('event_type', 'Bridal Makeover').strip()
        location = data.get('location', '').strip()
        rating = int(data.get('rating', 5))
        wedding_date = data.get('wedding_date', '').strip()

        if not name or not review_text:
            return JsonResponse({'ok': False, 'error': 'Name and review text are required.'})

        rating = max(1, min(5, rating))
        review = CustomerReview.objects.create(
            client_name=name,
            event_type=event_type or 'Royal Bride',
            location=location or 'India',
            rating=rating,
            review_text=review_text,
            wedding_date=wedding_date,
            is_verified=True,
            is_active=True,
            order=0
        )
        return JsonResponse({
            'ok': True,
            'message': 'Thank you! Your verified review has been submitted.',
            'review_id': review.id
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


# ── API: Admin Review Management (CRUD) ───────────────────────
@login_required
def admin_review_manage(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        rev_id = data.get('id')

        if action == 'delete' and rev_id:
            CustomerReview.objects.filter(id=rev_id).delete()
            return JsonResponse({'ok': True})

        if action == 'toggle_active' and rev_id:
            r = CustomerReview.objects.filter(id=rev_id).first()
            if r:
                r.is_active = not r.is_active
                r.save()
                return JsonResponse({'ok': True, 'is_active': r.is_active})

    reviews = list(CustomerReview.objects.all().values())
    return JsonResponse({'reviews': reviews})


# ── API: Admin Media Management (Upload Photos, Instagram Reels & YouTube) ──
@login_required
def admin_media_manage(request):
    """
    Handle:
    1. Photo uploads directly via file input
    2. Instagram Post/Reel URLs -> auto-detect shortcode and create embed/post reference
    3. YouTube Video URLs -> auto-extract video ID, fetch oEmbed metadata (title, thumbnail) and create player
    4. Delete & Toggle active
    """
    if request.method == 'POST':
        action = request.POST.get('action') or ''
        
        # Also support JSON body if sent as json
        if request.content_type == 'application/json':
            try:
                body_data = json.loads(request.body)
                action = body_data.get('action')
                if action == 'delete':
                    media_id = body_data.get('id')
                    MediaItem.objects.filter(id=media_id).delete()
                    return JsonResponse({'ok': True})
                if action == 'toggle_active':
                    media_id = body_data.get('id')
                    item = MediaItem.objects.filter(id=media_id).first()
                    if item:
                        item.is_active = not item.is_active
                        item.save()
                        return JsonResponse({'ok': True, 'is_active': item.is_active})
            except Exception as e:
                return JsonResponse({'ok': False, 'error': str(e)})

        if action == 'delete':
            media_id = request.POST.get('id')
            MediaItem.objects.filter(id=media_id).delete()
            return JsonResponse({'ok': True})

        title = request.POST.get('title', '').strip()
        media_type = request.POST.get('media_type', 'image')
        category = request.POST.get('category', 'bridal')
        section = request.POST.get('section', 'gallery')
        caption = request.POST.get('caption', '').strip()
        ext_url = request.POST.get('external_url', '').strip()
        views_count = request.POST.get('views_count', '25.4K+ views').strip()
        is_featured = request.POST.get('is_featured') in ['1', 'true', 'on']
        
        embed_code = ''
        thumb_url = ''

        # ── 1. INSTAGRAM AUTO EMBED ──
        if media_type == 'instagram' or 'instagram.com' in ext_url:
            media_type = 'instagram'
            if not title:
                title = 'Instagram Reel Showcase'
            
            # Extract shortcode e.g. /reel/Dap4JkvKL1E/ or /p/DW0f_eHAecV/
            shortcode_match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', ext_url)
            if shortcode_match:
                shortcode = shortcode_match.group(1)
                embed_code = shortcode
                # Fallback clean embed URL
                clean_url = f"https://www.instagram.com/p/{shortcode}/"
            else:
                clean_url = ext_url

            # Try oEmbed for Instagram metadata if available
            try:
                oembed_api = f"https://api.instagram.com/oembed/?url={urllib.parse.quote(clean_url)}"
                req = urllib.request.Request(oembed_api, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode())
                    if not caption and data.get('title'):
                        caption = data.get('title')
                    if data.get('thumbnail_url'):
                        thumb_url = data.get('thumbnail_url')
            except Exception:
                pass

        # ── 2. YOUTUBE AUTO EMBED ──
        elif media_type == 'youtube' or ('youtube.com' in ext_url or 'youtu.be' in ext_url):
            media_type = 'youtube'
            yt_id = ''
            # Extract video ID: youtu.be/ID or watch?v=ID or shorts/ID
            yt_match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})', ext_url)
            if yt_match:
                yt_id = yt_match.group(1)
                embed_code = yt_id
                thumb_url = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
            
            # Auto-fetch title from YouTube oEmbed
            try:
                yt_oembed = f"https://www.youtube.com/oembed?url={urllib.parse.quote(ext_url)}&format=json"
                req = urllib.request.Request(yt_oembed, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    yt_data = json.loads(resp.read().decode())
                    if not title or title == 'YouTube Video':
                        title = yt_data.get('title', 'YouTube Video')
                    if yt_data.get('thumbnail_url'):
                        thumb_url = yt_data.get('thumbnail_url')
            except Exception:
                if not title:
                    title = 'Bridal YouTube Feature'

        # ── 3. UPLOADED IMAGE ──
        elif media_type == 'image':
            if not title:
                title = 'Bridal Portfolio Look'

        # Create MediaItem
        media_item = MediaItem(
            title=title or 'Bridal Artistry Highlight',
            media_type=media_type,
            category=category,
            section=section,
            caption=caption,
            external_url=ext_url,
            embed_code=embed_code,
            thumbnail_url=thumb_url,
            views_count=views_count or '22.8K+ views',
            is_featured=is_featured,
            is_active=True
        )

        look_group_id = request.POST.get('look_group_id', '').strip()
        look_group_name = request.POST.get('look_group_name', '').strip()
        is_group_cover_raw = request.POST.get('is_group_cover')
        is_group_cover = (is_group_cover_raw in ['1', 'true', 'on']) if is_group_cover_raw is not None else (not look_group_id)

        if 'image_file' in request.FILES:
            media_item.image_file = request.FILES['image_file']
            # Also sync to GalleryImage if section is gallery or both
            if section in ['gallery', 'both']:
                GalleryImage.objects.create(
                    image=request.FILES['image_file'],
                    caption=title or caption or 'Bridal Couture Look',
                    category=category,
                    look_group_id=look_group_id,
                    look_group_name=look_group_name,
                    is_group_cover=is_group_cover,
                    is_active=True,
                    order=0
                )

        if 'video_file' in request.FILES:
            media_item.video_file = request.FILES['video_file']

        media_item.save()

        return JsonResponse({
            'ok': True,
            'item': {
                'id': media_item.id,
                'title': media_item.title,
                'media_type': media_item.media_type,
                'category': media_item.category,
                'section': media_item.section,
                'thumb': media_item.display_thumb,
                'embed_code': media_item.embed_code,
                'external_url': media_item.external_url,
            }
        })

    # GET request - return list
    items = []
    for m in MediaItem.objects.all():
        items.append({
            'id': m.id,
            'title': m.title,
            'media_type': m.media_type,
            'media_type_display': m.get_media_type_display(),
            'category': m.category,
            'section': m.section,
            'caption': m.caption,
            'external_url': m.external_url,
            'embed_code': m.embed_code,
            'thumb': m.display_thumb,
            'is_active': m.is_active,
            'is_featured': m.is_featured,
            'created_at': m.created_at.strftime('%d %b %Y'),
        })
    return JsonResponse({'media': items})


# ── API: Admin Studio Service Management (Add, Edit, Delete, Inclusions) ──
@login_required
def admin_studio_service_manage(request):
    """
    Full Admin CRUD for Studio Services:
    - Add new services
    - Edit title, discipline, pricing, discount, bundle note, description, image, look_group_id
    - Add, edit, remove feature inclusions
    - Delete services
    """
    if request.method == 'POST':
        action = request.POST.get('action') or ''
        
        # Support JSON payload as well
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                action = body.get('action')
                if action == 'delete':
                    svc_id = body.get('id')
                    StudioService.objects.filter(id=svc_id).delete()
                    return JsonResponse({'ok': True})
            except Exception as e:
                return JsonResponse({'ok': False, 'error': str(e)})

        if action == 'delete':
            svc_id = request.POST.get('id')
            StudioService.objects.filter(id=svc_id).delete()
            return JsonResponse({'ok': True})

        svc_id = request.POST.get('id')
        title = request.POST.get('title', '').strip()
        discipline = request.POST.get('discipline', '').strip()
        category = request.POST.get('category', 'bridal').strip()
        price_val = request.POST.get('price')
        discount_val = request.POST.get('discount_price')
        bundle_note = request.POST.get('bundle_note', '').strip()
        description = request.POST.get('description', '').strip()
        features = request.POST.get('features', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        look_group_id = request.POST.get('look_group_id', '').strip()
        order_val = request.POST.get('order', '0')
        is_active = request.POST.get('is_active') not in ['0', 'false', 'off']

        if not title:
            return JsonResponse({'ok': False, 'error': 'Service title is required.'})

        try:
            price = float(price_val) if price_val else 0.0
        except ValueError:
            price = 0.0

        try:
            discount_price = float(discount_val) if discount_val else None
        except ValueError:
            discount_price = None

        try:
            order = int(order_val)
        except ValueError:
            order = 0

        if svc_id:
            try:
                svc = StudioService.objects.get(id=svc_id)
            except StudioService.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Service not found.'})
            svc.title = title
            svc.discipline = discipline
            svc.category = category
            svc.price = price
            svc.discount_price = discount_price
            svc.bundle_note = bundle_note
            svc.description = description
            svc.features = features
            if image_url:
                svc.image_url = image_url
            if look_group_id:
                svc.look_group_id = look_group_id
            svc.order = order
            svc.is_active = is_active
        else:
            svc = StudioService(
                title=title,
                discipline=discipline or f"SIGNATURE DISCIPLINE 0{StudioService.objects.count()+1}",
                category=category,
                price=price,
                discount_price=discount_price,
                bundle_note=bundle_note,
                description=description,
                features=features,
                image_url=image_url,
                look_group_id=look_group_id,
                order=order,
                is_active=is_active
            )

        if 'image_file' in request.FILES:
            svc.image = request.FILES['image_file']

        svc.save()

        return JsonResponse({
            'ok': True,
            'service': {
                'id': svc.id,
                'title': svc.title,
                'discipline': svc.discipline,
                'category': svc.category,
                'price': float(svc.price),
                'discount_price': float(svc.discount_price) if svc.discount_price else None,
                'bundle_note': svc.bundle_note,
                'description': svc.description,
                'features': svc.features,
                'features_list': svc.get_features_list(),
                'display_image': svc.display_image,
                'look_group_id': svc.look_group_id,
                'order': svc.order,
                'is_active': svc.is_active,
            }
        })

    # GET: return list
    services = []
    for s in StudioService.objects.all():
        services.append({
            'id': s.id,
            'title': s.title,
            'discipline': s.discipline,
            'category': s.category,
            'price': float(s.price),
            'discount_price': float(s.discount_price) if s.discount_price else None,
            'bundle_note': s.bundle_note,
            'description': s.description,
            'features': s.features,
            'features_list': s.get_features_list(),
            'display_image': s.display_image,
            'look_group_id': s.look_group_id,
            'order': s.order,
            'is_active': s.is_active,
        })
    return JsonResponse({'services': services})


# ── API: Admin Look Groups (Folders by Person / Makeup Type) ──────────
@login_required
def admin_lookgroup_manage(request):
    """
    CRUD for Look Groups (Person / Client folders):
    - Name (e.g. Kuhu - Traditional Bengali Mukut & Chandan)
    - Client Name (e.g. Kuhu)
    - Makeup Type (e.g. Traditional Banarasi Chandan Art)
    - Category (bridal, reception, engagement, etc.)
    """
    if request.method == 'POST':
        action = request.POST.get('action') or ''
        
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                action = body.get('action')
                if action == 'delete':
                    grp_id = body.get('id')
                    LookGroup.objects.filter(id=grp_id).delete()
                    return JsonResponse({'ok': True})
            except Exception as e:
                return JsonResponse({'ok': False, 'error': str(e)})

        if action == 'delete':
            grp_id = request.POST.get('id')
            LookGroup.objects.filter(id=grp_id).delete()
            return JsonResponse({'ok': True})

        grp_id = request.POST.get('id')
        name = request.POST.get('name', '').strip()
        client_name = request.POST.get('client_name', '').strip()
        makeup_type = request.POST.get('makeup_type', '').strip()
        category = request.POST.get('category', 'bridal').strip()
        description = request.POST.get('description', '').strip()
        cover_image_url = request.POST.get('cover_image_url', '').strip()
        order_val = request.POST.get('order', '0')
        is_active = request.POST.get('is_active') not in ['0', 'false', 'off']

        if not name:
            if client_name and makeup_type:
                name = f"{client_name} — {makeup_type}"
            else:
                name = client_name or makeup_type or "Bespoke Bridal Look"

        try:
            order = int(order_val)
        except ValueError:
            order = 0

        if grp_id:
            try:
                grp = LookGroup.objects.get(id=grp_id)
            except LookGroup.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Look group not found.'})
            grp.name = name
            grp.client_name = client_name
            grp.makeup_type = makeup_type
            grp.category = category
            grp.description = description
            if cover_image_url:
                grp.cover_image_url = cover_image_url
            grp.order = order
            grp.is_active = is_active
        else:
            grp = LookGroup(
                name=name,
                client_name=client_name,
                makeup_type=makeup_type,
                category=category,
                description=description,
                cover_image_url=cover_image_url,
                order=order,
                is_active=is_active
            )

        if 'cover_file' in request.FILES:
            grp.cover_image = request.FILES['cover_file']

        grp.save()

        return JsonResponse({
            'ok': True,
            'group': {
                'id': grp.id,
                'name': grp.name,
                'client_name': grp.client_name,
                'makeup_type': grp.makeup_type,
                'category': grp.category,
                'description': grp.description,
                'display_cover': grp.display_cover,
                'order': grp.order,
                'is_active': grp.is_active,
                'media_count': grp.media_items.count()
            }
        })

    # GET: return list
    groups = []
    for g in LookGroup.objects.prefetch_related('media_items').all():
        media_list = []
        for itm in g.media_items.all():
            media_list.append({
                'id': itm.id,
                'media_type': itm.media_type,
                'title': itm.title,
                'caption': itm.caption,
                'external_url': itm.external_url,
                'embed_code': itm.embed_code,
                'thumb': itm.display_thumb,
                'order': itm.order
            })
        groups.append({
            'id': g.id,
            'name': g.name,
            'client_name': g.client_name,
            'makeup_type': g.makeup_type,
            'category': g.category,
            'description': g.description,
            'display_cover': g.display_cover,
            'order': g.order,
            'is_active': g.is_active,
            'media_items': media_list,
            'media_count': len(media_list)
        })
    return JsonResponse({'groups': groups})


# ── API: Admin Look Media (Add Photo, Video, Instagram, YouTube to Group) ──
@login_required
def admin_lookmedia_manage(request):
    """Add or remove photos, video files, Instagram URLs, or YouTube links inside a LookGroup"""
    if request.method == 'POST':
        action = request.POST.get('action') or ''

        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                action = body.get('action')
                if action == 'delete':
                    itm_id = body.get('id')
                    LookMediaItem.objects.filter(id=itm_id).delete()
                    return JsonResponse({'ok': True})
            except Exception as e:
                return JsonResponse({'ok': False, 'error': str(e)})

        if action == 'delete':
            itm_id = request.POST.get('id')
            LookMediaItem.objects.filter(id=itm_id).delete()
            return JsonResponse({'ok': True})

        group_id = request.POST.get('group_id')
        if not group_id:
            return JsonResponse({'ok': False, 'error': 'Look Group is required.'})

        try:
            group = LookGroup.objects.get(id=group_id)
        except LookGroup.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Look group not found.'})

        media_type = request.POST.get('media_type', 'image')
        ext_url = request.POST.get('external_url', '').strip()
        title = request.POST.get('title', '').strip()
        caption = request.POST.get('caption', '').strip()
        thumb_url = request.POST.get('thumbnail_url', '').strip()
        embed_code = ''

        # Auto-detect Instagram
        if media_type == 'instagram' or 'instagram.com' in ext_url:
            media_type = 'instagram'
            m = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', ext_url)
            if m:
                embed_code = m.group(1)
            # Try oEmbed for thumbnail
            try:
                clean_url = f"https://www.instagram.com/p/{embed_code}/" if embed_code else ext_url
                oembed_api = f"https://api.instagram.com/oembed/?url={urllib.parse.quote(clean_url)}"
                req = urllib.request.Request(oembed_api, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    odata = json.loads(resp.read().decode())
                    if odata.get('thumbnail_url'):
                        thumb_url = odata.get('thumbnail_url')
                    if not title and odata.get('title'):
                        title = odata.get('title')
            except Exception:
                pass

        # Auto-detect YouTube
        elif media_type == 'youtube' or ('youtube.com' in ext_url or 'youtu.be' in ext_url):
            media_type = 'youtube'
            yt_m = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})', ext_url)
            if yt_m:
                embed_code = yt_m.group(1)
                thumb_url = f"https://img.youtube.com/vi/{embed_code}/hqdefault.jpg"
            try:
                yt_oembed = f"https://www.youtube.com/oembed?url={urllib.parse.quote(ext_url)}&format=json"
                req = urllib.request.Request(yt_oembed, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    yt_data = json.loads(resp.read().decode())
                    if not title and yt_data.get('title'):
                        title = yt_data.get('title')
            except Exception:
                pass

        item = LookMediaItem(
            group=group,
            media_type=media_type,
            external_url=ext_url,
            embed_code=embed_code,
            thumbnail_url=thumb_url,
            title=title or f"{group.client_name or group.name} Highlight",
            caption=caption,
            order=group.media_items.count() + 1
        )

        if 'image_file' in request.FILES:
            item.image_file = request.FILES['image_file']
        if 'video_file' in request.FILES:
            item.video_file = request.FILES['video_file']

        item.save()

        # If group doesn't have a cover yet, set this item as cover
        if not group.cover_image and not group.cover_image_url:
            if item.image_file:
                group.cover_image = item.image_file
                group.save()
            elif item.thumbnail_url:
                group.cover_image_url = item.thumbnail_url
                group.save()

        return JsonResponse({
            'ok': True,
            'item': {
                'id': item.id,
                'media_type': item.media_type,
                'title': item.title,
                'caption': item.caption,
                'external_url': item.external_url,
                'embed_code': item.embed_code,
                'thumb': item.display_thumb,
                'order': item.order
            }
        })

    return JsonResponse({'ok': False, 'error': 'Invalid request method.'})


def sinha_logo_studio(request):
    """Visualizer page for The Sinha Family Group luxury branding and prompts"""
    return render(request, 'core/sinha_logo_studio.html')
