import json
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
from .common import admin_required
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


def get_gemini_api_key():
    """Load Gemini API key from environment variable first, then check candidate file paths."""
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        base_path = Path(settings.BASE_DIR)
        candidate_paths = [
            base_path / '.env',
            base_path.parent / '.env',
            base_path / 'gemini_api_key.txt',
            base_path.parent / 'anshita_project' / 'gemini_api_key.txt',
            base_path.parent / 'gemini_api_key.txt',
            base_path / 'anshita_project' / 'gemini_api_key.txt',
            # CFA / Learning tools fallback if present on machine
            Path(r"F:\Code by Akshat\learning tools\AIDocumentMergerCreator\.env"),
            Path(r"F:\Code by Akshat\learning tools\combined pdf\.env"),
        ]
        for p in candidate_paths:
            if p.exists():
                try:
                    if p.name == '.env':
                        for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
                            if line.strip().startswith('GEMINI_API_KEY='):
                                val = line.split('=', 1)[1].strip().strip('"\'')
                                if val and val != 'YOUR_GEMINI_API_KEY_HERE':
                                    api_key = val
                                    break
                    else:
                        val = p.read_text(encoding='utf-8', errors='ignore').strip()
                        if val and val != 'YOUR_GEMINI_API_KEY_HERE':
                            api_key = val
                    if api_key:
                        break
                except Exception:
                    continue
    if api_key == 'YOUR_GEMINI_API_KEY_HERE':
        return ''
    return api_key


# ── API: Chatbot ──────────────────────────────────────────────
@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        language = data.get('language', 'hindi').strip().lower()

        if not user_msg:
            return JsonResponse({'reply': 'Greetings! How may I assist you with our bridal and beauty services today? ✨', 'session_id': session_id})

        # Load Gemini API key (env var priority, candidate file fallback)
        api_key = get_gemini_api_key()

        if not api_key:
            reply = fallback_chatbot(user_msg, language=language)
        else:
            try:
                reply = gemini_chat(api_key, user_msg, session_id, language=language)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Gemini AI error (%s), activating fallback", e)
                reply = fallback_chatbot(user_msg, language=language)

        ChatMessage.objects.create(session_id=session_id, message=user_msg, response=reply)
        return JsonResponse({'reply': reply, 'session_id': session_id})

    except Exception as e:
        return JsonResponse({'reply': 'We are temporarily unable to process your request. Please connect with us directly on WhatsApp at +91 78792 23442.', 'session_id': ''})


# How many past exchanges are re-sent to Gemini as context (token budget!).
GEMINI_HISTORY_TURNS = int(os.environ.get('GEMINI_HISTORY_TURNS', '5'))
# Truncate each stored reply to this many chars when re-sending as context.
GEMINI_HISTORY_CHARS = 500
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-flash-latest')



# Headroom (github.com/headroomlabs-ai/headroom) compresses the chat history
# locally before it is billed by Gemini. Enable with CHATBOT_HEADROOM=1.
HEADROOM_ENABLED = os.environ.get('CHATBOT_HEADROOM', '0') == '1'


def headroom_compress_history(turns):
    """Compress Gemini-format history turns with Headroom.

    Returns the (possibly smaller) turns list. Any failure — Headroom not
    installed, compression error — degrades silently to the raw history so
    the concierge never breaks because of the optimiser.
    """
    if not turns or not HEADROOM_ENABLED:
        return turns
    try:
        from headroom import compress as headroom_compress
        to_openai = {'user': 'user', 'model': 'assistant'}
        messages = [{'role': to_openai[t['role']], 'content': t['parts'][0]['text']}
                    for t in turns]
        result = headroom_compress(messages, model=GEMINI_MODEL)
        compressed_msgs = getattr(result, 'messages', None)
        if not compressed_msgs:
            return turns
        from_openai = {'user': 'user', 'assistant': 'model'}
        compressed = [
            {'role': from_openai.get(m.get('role'), 'user'),
             'parts': [{'text': str(m.get('content') or '')}]}
            for m in compressed_msgs
        ]
        return compressed or turns
    except Exception:
        return turns


def conversation_history(session_id, limit=GEMINI_HISTORY_TURNS):
    """Load the last `limit` exchanges for this session as Gemini `contents`.

    Long past replies are truncated so context never blows up the token bill.
    """
    past = list(
        ChatMessage.objects.filter(session_id=session_id)
        .order_by('-created_at')[:limit]
    )
    turns = []
    for row in reversed(past):
        turns.append({'role': 'user', 'parts': [{'text': row.message}]})
        prev_reply = (row.response or '').strip()[:GEMINI_HISTORY_CHARS]
        if prev_reply:
            turns.append({'role': 'model', 'parts': [{'text': prev_reply}]})
    return turns


def gemini_chat(api_key, user_msg, session_id, language='hindi'):
    """Client-facing AI Concierge — Gemini with conversation memory, live DB
    pricing, standalone bridal vs package distinction, negotiation guardrails and a strict concise/plain-text style."""
    import requests
    site = get_site_settings()
    free_sides = site.offer_bridal_free_sides
    disc_sides_rate = int(site.offer_next_sides_discounted_price)
    combo_disc = site.offer_combo_discount_percent
    combo_flat = int(site.offer_grand_combo_bundle_price)
    wa_number = site.whatsapp_number or "917879223442"
    today_code = site.default_auto_coupon_code if site.default_auto_coupon_active else "TODAYVIP"
    today_disc = site.default_auto_coupon_discount if site.default_auto_coupon_active else 15

    services = list(StudioService.objects.filter(is_active=True).order_by('order'))
    pkgs = list(MakeupPackage.objects.filter(is_active=True).order_by('order'))
    min_floor_pct = site.ai_negotiation_min_floor_percent or 75
    max_disc_pct = site.ai_max_discount_percent or 20

    # 1. Standalone single-day bridal looks (NOT packages)
    standalone_bridal = [s for s in services if s.category == 'bridal']
    if not standalone_bridal:
        standalone_bridal = services[:3]

    standalone_rules = []
    for s_ in standalone_bridal:
        s_std = float(s_.price) if s_.price else 35000.0
        s_off = round(s_std * (100 - today_disc) / 100) if site.default_auto_coupon_active else s_std
        s_floor = float(s_.min_negotiated_price) if s_.min_negotiated_price else round(s_std * min_floor_pct / 100)
        note = s_.bundle_note or (s_.features[:60] if s_.features else "Single-day luxury bridal makeover")
        standalone_rules.append(
            f"- {s_.title}: std ₹{s_std:,.0f}, today's VIP offer ₹{s_off:,.0f}. "
            f"Authorized floor: ₹{s_floor:,.0f}. Inclusions: {note}"
        )
    standalone_text = "\n".join(standalone_rules)

    # 2. Multi-event celebration packages (bundles)
    pkg_rules = []
    for p_ in pkgs:
        std_val = float(p_.price) if p_.price else 0.0
        offer_val = round(std_val * (100 - today_disc) / 100) if site.default_auto_coupon_active else round(std_val * (100 - site.coupon_discount_percent) / 100) if site.coupon_active and site.coupon_discount_percent else std_val
        floor_val = float(p_.min_negotiated_price) if p_.min_negotiated_price else round(std_val * min_floor_pct / 100)
        feats = ", ".join(p_.get_features_list()[:3])
        pkg_rules.append(
            f"- {p_.name}: std ₹{std_val:,.0f}, today's VIP offer ₹{offer_val:,.0f}, "
            f"includes: {feats}. "
            f"Authorized floor: ₹{floor_val:,.0f}."
        )
    pkg_rules_text = "\n".join(pkg_rules) or "- No active packages."

    lang_instruction = f"User has selected preferred language: {language.upper()}."
    if language == 'bundelkhandi':
        lang_instruction += " Speak in authentic, affectionate Bundelkhandi (बुंदेलखंडी - eg. 'हओ', 'किए का सिंगार', 'का हाल चाल')."
    elif language == 'baghelkhandi':
        lang_instruction += " Speak in natural Baghelkhandi (बघेलखंडी - eg. 'कइसन बाटे', 'का भाव परि', 'लगन सिंगार')."
    elif language == 'bhojpuri':
        lang_instruction += " Speak in sweet, respectful Bhojpuri (भोजपुरी - eg. 'राउर स्वागत बा', 'कवन सिंगार चाहीं')."
    elif language == 'marathi':
        lang_instruction += " Speak in elegant, welcoming Marathi (मराठी)."
    elif language == 'english':
        lang_instruction += " Speak in sophisticated luxury English."
    else:
        lang_instruction += " Speak in warm conversational Hindi/Hinglish."

    system_prompt = f"""You are Anshita Makeover's Luxury Concierge AI (bridal, hair, nails, academy).

PRIMARY LANGUAGE PREFERENCE:
- {lang_instruction}

CONVERSATION CONTEXT:
- This is an ongoing conversation: you can see earlier messages above. Continue naturally.
- NEVER repeat welcome greetings or re-introduce the studio if this is a follow-up message.
- Answer the user's specific question or objection directly in your FIRST sentence.
- Mirror user's language: If user writes in Hindi, Hinglish, Bundelkhandi, Baghelkhandi, Bhojpuri, Marathi, or English, reply naturally in that language!

CATALOG & PRICING (live from database — quote ONLY these, never invent prices):

✦ STANDALONE SINGLE-DAY BRIDAL MAKEUP (NOT PACKAGES):
{standalone_text}

✦ MULTI-EVENT CELEBRATION PACKAGES (BUNDLES FOR 2-3 EVENTS):
{pkg_rules_text}

BOOKING PRIVILEGES:
- First {free_sides} side makeups (sisters/family) are completely FREE (₹0, worth ₹7,000) with any bridal booking!
- Next 2 side makeups at ₹{disc_sides_rate:,} each; bridal+engagement combo extra {combo_disc}% off.
- Today's VIP Privilege Code: {today_code} gives extra {today_disc}% savings.

CRITICAL INSTRUCTIONS:
1. STANDALONE BRIDAL VS MULTI-EVENT PACKAGES:
- If user says "only bridal makeup", "sirf bridal", "not package", "package nahi", "package nahi chahiye", "single day", "ek din ka", "bas bridal", or asks specifically for bridal makeup without packages:
  YOU MUST NEVER PITCH PACKAGES! NEVER mention Sacred Vivah Duo or Grand Royal Vivah!
  Quote ONLY the Standalone Single-Day Bridal options above (e.g. Royal Bridal Couture HD/Airbrush ₹35,000 / today ₹{round(35000 * (100 - today_disc) / 100):,}, or Traditional Banarasi ₹25,000 / today ₹{round(25000 * (100 - today_disc) / 100):,}).
- Only pitch multi-event packages if the user explicitly asks for packages, bundles, or multi-day celebrations.

2. PRICE OBJECTIONS & NEGOTIATION ("yeh toh bahut mehnga h", "expensive", "too costly", "budget kam h", "discount", "kam karo"):
- Reply warmly in Hinglish/Hindi: "Hum bilkul samajhte hain! Hamari priority hai ki aap apne wedding par sabse khoobsurat lagein."
- Explain the premium value gently: 100% original international luxury brands (TEMPTU, Charlotte Tilbury, MAC) + medical-grade hygiene.
- Standalone bridal negotiation: Offer the special privilege rate down towards authorized floor (e.g. ₹20,000 - ₹24,500 for Royal Bridal HD/Airbrush, or ₹18,000 for Traditional Banarasi) using VIP code {today_code}.
- Highlight the bonus perk: Remind them that 2 family side makeups are completely FREE (saving ₹7,000), making the overall package extremely economical.
- Direct to WhatsApp: https://wa.me/{wa_number}?text=Namaste!%20AI%20Concierge%20granted%20me%20a%20Special%20Privilege%20Rate%20with%20VIP%20code%20{today_code}.

3. ABSOLUTELY NO TRUNCATION:
- Keep the response clean, concise (under 100 words), and complete.
- NEVER stop mid-sentence.
- Use ✦ bullet points. Plain text only (no markdown tables, no HTML <br>).
"""

    history = headroom_compress_history(conversation_history(session_id))
    contents = history + [{'role': 'user', 'parts': [{'text': user_msg}]}]

    candidate_models = []
    for m in [GEMINI_MODEL, 'gemini-flash-latest', 'gemini-2.5-flash', 'gemini-2.0-flash']:
        if m and m not in candidate_models:
            candidate_models.append(m)

    last_error = None
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        gen_config = {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
            "thinkingConfig": {"thinkingBudget": 0}
        }
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": gen_config,
        }

        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    parts = candidates[0]['content'].get('parts', [])
                    for part in parts:
                        if 'text' in part and part['text'].strip():
                            return part['text'].strip()
            elif resp.status_code == 400 and 'thinkingConfig' in resp.text:
                # Retry this model without thinkingConfig if unsupported
                payload["generationConfig"] = {
                    "temperature": 0.4,
                    "maxOutputTokens": 2048,
                }
                resp2 = requests.post(url, json=payload, timeout=15)
                if resp2.status_code == 200:
                    data2 = resp2.json()
                    candidates2 = data2.get('candidates', [])
                    if candidates2 and 'content' in candidates2[0]:
                        parts2 = candidates2[0]['content'].get('parts', [])
                        for part in parts2:
                            if 'text' in part and part['text'].strip():
                                return part['text'].strip()
            last_error = f"{model_name}: {resp.status_code} - {resp.text[:150]}"
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


# ── API: Admin AI Co-Pilot (Intelligent Natural Language Website Manager) ──
@admin_required
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

        api_key = get_gemini_api_key()
        if not api_key:
            return JsonResponse({'ok': False, 'error': 'Gemini API key not configured. Set GEMINI_API_KEY environment variable or create django/gemini_api_key.txt.'})

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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
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


@admin_required
def admin_ai_status(request):
    """Return status of Gemini AI integration for Admin Dashboard."""
    api_key = get_gemini_api_key()
    source = 'none'
    live = False
    if api_key:
        live = True
        if os.environ.get('GEMINI_API_KEY', '').strip():
            source = 'env'
        else:
            source = 'file'

    return JsonResponse({
        'ok': True,
        'live': live,
        'source': source,
        'model': GEMINI_MODEL,
        'status_text': f"Live ({source.upper()})" if live else "Offline (Smart Fallback Active)"
    })


def fallback_chatbot(msg, language='hindi'):
    """Deterministic concierge (no Gemini key / Gemini down).

    Style mirrors the AI rules: short bullet lines, NO markdown tables,
    NO html — the chat widget renders plain text with ✦ bullets.
    Enriched with live DB packages, active pricing, and WhatsApp settings.
    """
    msg_lower = msg.lower()
    site = get_site_settings()
    wa_number = site.whatsapp_number or "917879223442"
    today_code = site.default_auto_coupon_code if site.default_auto_coupon_active else "TODAYVIP"
    today_disc = site.default_auto_coupon_discount if site.default_auto_coupon_active else 15
    free_sides = site.offer_bridal_free_sides
    disc_sides_rate = int(site.offer_next_sides_discounted_price)
    combo_disc = site.offer_combo_discount_percent
    combo_flat = int(site.offer_grand_combo_bundle_price)

    pkgs = list(MakeupPackage.objects.filter(is_active=True).order_by('order'))
    min_floor_pct = site.ai_negotiation_min_floor_percent or 75

    hd_pkg = next((p for p in pkgs if 'hd' in p.name.lower()), pkgs[0] if pkgs else None)
    air_pkg = next((p for p in pkgs if 'airbrush' in p.name.lower()), (pkgs[1] if len(pkgs) > 1 else pkgs[0]) if pkgs else None)

    hd_std = float(hd_pkg.price) if hd_pkg and hd_pkg.price else 35000.0
    air_std = float(air_pkg.price) if air_pkg and air_pkg.price else 45000.0
    hd_name = hd_pkg.name if hd_pkg else "Imperial Royal HD Bridal"
    air_name = air_pkg.name if air_pkg else "Master Airbrush Bridal"

    hd_floor = float(hd_pkg.min_negotiated_price) if (hd_pkg and hd_pkg.min_negotiated_price) else round(hd_std * min_floor_pct / 100)
    air_floor = float(air_pkg.min_negotiated_price) if (air_pkg and air_pkg.min_negotiated_price) else round(air_std * min_floor_pct / 100)

    # ── 1. STANDALONE SINGLE-DAY BRIDAL INQUIRIES (NOT PACKAGES) ──
    is_only_bridal = any(k in msg_lower for k in [
        'only bridal', 'not package', 'package nahi', 'sirf bridal', 'single day', 'ek din',
        'naki package', 'package bas nahi', 'only makeup', 'single bridal', 'bas bridal',
        'package nahi chahiye', 'no package', 'without package', 'not a package', 'single-day',
        'naki bridal', 'bridal makeup bas', 'makeup bas', 'package bas', 'sirf makeup',
        'package h naki', 'package hai naki', 'only single', 'sirf ek'
    ])

    if is_only_bridal:
        lines = [
            "Namaste! 🙏✨ Here are our Standalone Single-Day Bridal options (Not Packages):",
            f"✦ Royal Bridal Couture (HD & Airbrush Artistry) — ₹35,000 (today's VIP rate: ₹{round(35000 * (100 - today_disc) / 100):,})",
            f"✦ Traditional Banarasi & Mukut Artistry — ₹25,000 (today's VIP rate: ₹{round(25000 * (100 - today_disc) / 100):,})",
            f"✦ Imperial Fuchsia Palace Suite — ₹32,000 (today's VIP rate: ₹{round(32000 * (100 - today_disc) / 100):,})",
            f"✦ Master Airbrush Cry-Proof Suite — ₹45,000 (today's VIP rate: ₹{round(45000 * (100 - today_disc) / 100):,})",
            f"✦ Privilege: First {free_sides} side makeups for family are completely FREE (₹0, worth ₹7,000)!",
            f"✦ Today's VIP code {today_code} gives extra {today_disc}% savings.",
            f"WhatsApp Anshita directly: https://wa.me/{wa_number}?text="
            + urllib.parse.quote(f"Namaste Anshita! I want single-day standalone bridal makeup with VIP code {today_code}.")
        ]
        return "\n".join(lines)

    # ── 2. SMART AI PRICE NEGOTIATION & BUDGET MATCHING ──
    is_negotiation = any(k in msg_lower for k in [
        'negotiat', 'bargain', 'budget', 'kam karo', 'kam ho sakta', 'kam kijiye', 'kam h', 'kam hai',
        'discount', 'sasta', 'too costly', 'expensive', 'mehenga', 'mehanga', 'mehnga', 'concession',
        'best price', 'last price', 'final price', 'special price', 'vip code',
        'bahut mehnga', 'bohot mehnga', 'jyada hai', 'zyada hai', 'zyada h', 'jyada h',
        '20000', '25000', '28000', '30000', '32000', '35000', '40000'
    ])

    if is_negotiation and site.ai_negotiation_enabled:
        msg_clean = msg_lower.replace(',', '')
        budget = None
        m_k = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*k\b', msg_clean)
        if m_k:
            budget = float(m_k.group(1)) * 1000
        else:
            m_num = re.search(r'(?:₹|rs\.?|inr)?\s*(\d{4,6})\b', msg_clean)
            if m_num:
                budget = float(m_num.group(1))

        if budget:
            if budget >= hd_floor:
                target_suite = air_name if budget >= air_floor else hd_name
                std_ref = air_std if budget >= air_floor else hd_std
                savings = int(std_ref - budget)
                wa_text = (f"Namaste! AI Concierge has authorized a Special Rate of "
                           f"₹{int(budget):,} with VIP code {today_code}. Please reserve my wedding date.")
                return (
                    f"✨ Special AI Concierge Privilege Approved! 🙏\n"
                    f"✦ Your authorized rate: ₹{int(budget):,} for the {target_suite} (standard ₹{int(std_ref):,} — you save ₹{savings:,})\n"
                    f"✦ Included FREE: {free_sides} side makeups worth ₹7,000\n"
                    f"✦ VIP code for your date: {today_code}\n"
                    f"👉 Lock this rate before the slot closes: https://wa.me/{wa_number}?text={urllib.parse.quote(wa_text)}"
                )
            return (
                f"Namaste 🙏 We truly respect your budget of ₹{int(budget):,}.\n"
                f"✦ Our authorized floor rate: ₹{hd_floor:,.0f} for {hd_name} (standard ₹{hd_std:,.0f})\n"
                f"✦ Why this floor: 100% original luxury products (TEMPTU, Charlotte Tilbury, MAC) + medical-grade hygiene\n"
                f"✦ Included FREE: {free_sides} side makeups worth ₹7,000\n"
                f"✦ Use code {today_code} today for extra savings\n"
                f"👉 Plan together on WhatsApp: https://wa.me/{wa_number}?text="
                + urllib.parse.quote(f"Namaste Anshita! My budget is around ₹{int(budget):,}. Can we customize a bridal suite for my date?")
            )
        return (
            f"Hum bilkul samajhte hain! 🙏 Hamari priority hai ki aap apne wedding day par sabse khoobsurat lagein.\n"
            f"✦ Hamare bridal makeovers mein 100% original luxury brands (TEMPTU, Charlotte Tilbury, MAC) aur hospital-grade hygiene use hoti hai.\n"
            f"✦ Special AI Privilege Offer: Standalone Royal Bridal HD ₹22,000 - ₹24,500 tak (Traditional Banarasi ₹18,500 tak) possible hai with code {today_code}.\n"
            f"✦ PLUS: {free_sides} family side makeups bilkul FREE (₹7,000 value included)!\n"
            f"Aapka wedding date aur target budget kya hai? Anshita ji se direct best deal confirm karein:\n"
            f"👉 WhatsApp: https://wa.me/{wa_number}?text="
            + urllib.parse.quote(f"Namaste Anshita! AI Concierge offered a special rate with VIP code {today_code}. Let's discuss my wedding date.")
        )

    # ── 3. GENERAL BRIDAL INQUIRIES ──
    if any(w in msg_lower for w in ['bridal', 'wedding', 'shaadi', 'bride', 'dulhan']):
        lines = ["Namaste! ✨ Here are our signature Bridal Suites:"]
        if pkgs:
            for p in pkgs[:3]:
                std_p = float(p.price) if p.price else 0.0
                off_p = round(std_p * (100 - today_disc) / 100)
                feats = ", ".join(p.get_features_list()[:2]) or "luxury bridal finish"
                lines.append(f"✦ {p.name} — ₹{std_p:,.0f} (today ₹{off_p:,.0f}): {feats}")
            if combo_flat:
                lines.append(f"✦ Grand Royal Heritage Suite — ₹{combo_flat:,.0f} flat: bridal + engagement bundle")
        else:
            lines.extend([
                "✦ Imperial Royal HD Suite — ₹35,000 (offer ₹24,500): HD base, cut-crease eyes, draping",
                "✦ Master Airbrush Suite — ₹45,000 (offer ₹31,500): TEMPTU 24-hr cry-proof base",
                f"✦ Grand Royal Heritage Suite — ₹{combo_flat:,.0f} flat: bridal + engagement bundle"
            ])
        lines.append(f"✦ Privilege: first {free_sides} side makeups completely FREE (₹0), next 2 at ₹{disc_sides_rate:,} each")
        lines.append(f"✦ Today's code {today_code} gives extra {today_disc}% savings")
        lines.append(f"To reserve your date, WhatsApp +91 {wa_number} 💍")
        return "\n".join(lines)

    # ── 3. PRICING INQUIRIES ──
    if any(w in msg_lower for w in ['price', 'rate', 'cost', 'kitna', 'fees', 'charges', 'package', 'packages']):
        lines = ["✨ Anshita Makeover Pricing Guide (standard / today's offer):"]
        if pkgs:
            for p in pkgs[:4]:
                std_p = float(p.price) if p.price else 0.0
                off_p = round(std_p * (100 - today_disc) / 100)
                lines.append(f"✦ {p.name} — ₹{std_p:,.0f} / ₹{off_p:,.0f}")
        else:
            lines.extend([
                "✦ Imperial Royal HD Bridal — ₹35,000 / ₹24,500",
                "✦ Master Airbrush Bridal — ₹45,000 / ₹31,500",
                "✦ Engagement & Roka Glam — ₹18,000 / ₹12,600"
            ])
        if combo_flat:
            lines.append(f"✦ Grand Royal Combo (bridal + engagement) — ₹{combo_flat:,.0f} flat")
        lines.append(f"✦ Side & family makeup — ₹{disc_sides_rate:,} subsidized · Academy Masterclass — ₹35,400")
        lines.append(f"✦ Extra {today_disc}% off today with code {today_code}")
        lines.append(f"Want a tailored quote? WhatsApp +91 {wa_number}")
        return "\n".join(lines)

    if any(w in msg_lower for w in ['photo', 'photography', 'event', 'videography', 'camera']):
        return (f"📸 Anshita Signature Events & Photography:\n"
                f"✦ Standard Collection — ₹90,000 (candid + traditional, 300+ edited portraits)\n"
                f"✦ Royal Premium Collection — ₹1,20,000 (cinematic video, drone, pre-wedding, premium album)\n"
                f"For event management, WhatsApp +91 {wa_number}.")

    # ── 4. COUPON & CODE INQUIRIES ──
    if any(w in msg_lower for w in ['coupon', 'discount', 'offer', 'code', 'promo', 'vip']):
        return (
            f"🎉 Active offers at Anshita Makeover:\n"
            f"✦ Today's auto code {today_code}: extra {today_disc}% off\n"
            f"✦ First {free_sides} side makeups 100% FREE with any bridal booking\n"
            f"Mention {today_code} when booking on WhatsApp +91 {wa_number} ✨"
        )

    if any(w in msg_lower for w in ['location', 'address', 'kahan', 'studio', 'city']):
        return (f"Anshita Makeover Studio is based in Jabalpur, Madhya Pradesh 📍 — serving bridal, destination weddings and couture bookings nationwide.\n"
                f"To reserve your date, WhatsApp +91 {wa_number}.")

    if any(w in msg_lower for w in ['hello', 'hi', 'namaste', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return (f"Namaste from Anshita Makeover! 🙏✨ Bridal transformations, hair, nails & certified academy training.\n"
                f"✦ Today's privilege: code {today_code} for extra savings\n"
                f"How may I help you — packages, pricing or booking? 💄")

    return f"Thank you for reaching out to Anshita Makeover ✨ For personalized help or bookings, WhatsApp our bridal concierge at +91 {wa_number}. We look forward to creating magic with you! 💍"

