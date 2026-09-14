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
    MediaItem
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
    exit_coupon = {
        'code': site.exit_coupon_code,
        'discount': site.exit_coupon_discount_percent,
        'label': site.exit_coupon_label,
        'active': site.exit_coupon_active,
    } if site.exit_coupon_active else None

    artists = Artist.objects.filter(is_active=True)
    gallery = GalleryImage.objects.filter(is_active=True)[:12]
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

    context = {
        'site': site,
        'coupon': coupon,
        'exit_coupon': exit_coupon,
        'artists': artists,
        'makeup_artists': makeup_artists,
        'hair_artists': hair_artists,
        'nail_artists': nail_artists,
        'gallery': gallery,
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
            # Fallback rule-based chatbot
            reply = fallback_chatbot(user_msg)
        else:
            reply = gemini_chat(api_key, user_msg, session_id)

        ChatMessage.objects.create(session_id=session_id, message=user_msg, response=reply)
        return JsonResponse({'reply': reply, 'session_id': session_id})

    except Exception as e:
        return JsonResponse({'reply': 'We are temporarily unable to process your request. Please connect with us directly on WhatsApp at +91 78792 23442.', 'session_id': ''})


def gemini_chat(api_key, user_msg, session_id):
    """Client-facing AI Concierge using Google Gemini 2.5 Flash"""
    import requests
    system_prompt = """You are the luxury concierge AI for Anshita Makeover — India's premier bespoke bridal couture, hair, and beauty studio.
Respond in a warm, dignified, respectful, and sophisticated tone. Use clear English or respectful, elegant Hindi/Hinglish when addressed in Hindi.
Polite guidelines: 'We would be delighted to assist you', 'Aapka hardik swagat hai', 'Please connect with our bridal team on WhatsApp at +91 78792 23442'.

Key Studio Highlights:
- Founder & Master Artist: Anshita (Master Bridal Couturier & Specialist with 8+ years experience, 500+ brides styled across India)
- Studio Presence: Flagship studio in Jabalpur, traveling for destination weddings across Rajasthan, Goa, Mumbai, Delhi, and Pan-India
- Direct WhatsApp Concierge: +91 78792 23442 | Instagram: @anshitamakeover21
- Signature Services: Master Airbrush Bridal (TEMPTU 24-hr cry-proof), Imperial Royal HD Bridal, Engagement & Roka Glam, Haute Hair Architecture, Gel Nail Art & Extensions, Pre-Bridal Hydra Rituals
- Pricing:
  * Imperial Royal HD Bridal: ₹24,500 (Special Offer) / ₹35,000 Standard
  * Master Airbrush Suite: ₹31,500 (Special Offer) / ₹45,000 Standard
  * Engagement / Roka Glam: ₹12,600 (Special Offer) / ₹18,000 Standard
  * Side & Bridesmaids: ₹4,550/person (Special Offer) / ₹6,500 Standard
- Academy Masterclass: ₹35,400 (incl 18% GST), 4 Weeks hands-on master training, ₹5,000 registration.
- Event Photography: Standard ₹90,000 | Royal Premium ₹1,20,000.
Conclude each answer elegantly with an invitation to book or connect via WhatsApp (+91 78792 23442)."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": user_msg}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
    }
    
    resp = requests.post(url, json=payload, timeout=12)
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
        system_instruction = """You are the Admin Assistant AI for Anshita Makeover website.
Your job is to parse the admin's natural language instruction and return a STRICT JSON object representing the action to execute.
Do NOT include markdown backticks or any conversational text. Return ONLY valid raw JSON.

Supported Action Schemas:

1. Add/Update Service or Package:
{
  "action": "create_package",
  "name": "Package Name",
  "package_type": "bridal|side_makeup|engagement|reception|party|hair|nails|beauty|custom",
  "price": 8500,
  "price_label": "₹8,500",
  "tagline": "Short description",
  "features": "Feature 1\\nFeature 2\\nFeature 3",
  "is_featured": false
}

2. Update Coupon:
{
  "action": "update_coupon",
  "coupon_code": "SUMMER40",
  "discount_percent": 40,
  "label": "Summer Bridal Privilege",
  "active": true
}

3. Embed Instagram or YouTube Video:
{
  "action": "add_media",
  "title": "Title of media",
  "media_type": "instagram|youtube",
  "url": "https://...",
  "category": "bridal|engagement|hair|nails|beauty|party",
  "section": "gallery|reels|both",
  "caption": "Brief description"
}

4. Update Service Price:
{
  "action": "update_price",
  "service": "makeup_hd|makeup_airbrush|nails_art|nails_extension|photo_premium|photo_standard",
  "price": 26000
}

5. General / Informational answer (if not a direct db modification):
{
  "action": "answer",
  "message": "Informational response or explanation"
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
        if action_type == 'create_package':
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
    if any(w in msg_lower for w in ['bridal', 'wedding', 'shaadi', 'bride', 'dulhan']):
        return "Namaste! ✨ We would be delighted to curate your dream bridal look. Our signature packages include:\n✦ Senior Master Bridal (Anshita / Shristee / Priya): ₹35,000\n✦ Master Airbrush Bridal Suite (Tejal): ₹45,000\nEvery package includes bespoke HD/Airbrush makeup, skin prep, couture hair styling & royal dupatta setting.\nTo reserve your auspicious date, please WhatsApp our bridal team at +91 78792 23442."
    if any(w in msg_lower for w in ['nail', 'nails', 'manicure', 'pedicure']):
        return "For luxury nail aesthetics, our senior nail artist Shristee crafts exquisite gel extensions, Swarovski bridal nail art, and French ombré manicures. 💅\nKindly reach us at +91 78792 23442 to reserve your slot."
    if any(w in msg_lower for w in ['hair', 'baal', 'styling', 'draping']):
        return "Our master hair stylists craft couture bridal updos, romantic textured waves, and authentic saree/lehenga draping. 💇\nPlease contact our studio concierge at +91 78792 23442 for consultations."
    if any(w in msg_lower for w in ['course', 'academy', 'learn', 'sikho', 'sikhna', 'admission', 'batch']):
        return "Welcome to Anshita Academy! 🎓\nOur flagship Professional Makeup Artist Masterclass:\n✦ Duration: 4 Weeks (3 Hours/Day)\n✦ Investment: ₹35,400 (Inclusive of 18% GST)\n✦ Registration: ₹5,000 to reserve your seat\n✦ Complete curriculum: HD bridal, airbrush, skin prep, portfolio & client management.\nFor the syllabus and upcoming batch dates, WhatsApp us at +91 78792 23442."
    if any(w in msg_lower for w in ['price', 'rate', 'cost', 'kitna', 'fees', 'charges']):
        return "Our curated service investments:\n💄 Signature Bridal: ₹35,000 – ₹45,000\n🎓 Professional Makeup Masterclass: ₹35,400\n📸 Event Photography & Cinematography: ₹90,000 – ₹1,20,000\nFor a personalized bespoke quotation tailored to your requirements, please WhatsApp +91 78792 23442."
    if any(w in msg_lower for w in ['photo', 'photography', 'event', 'videography', 'camera']):
        return "Through Anshita Signature Events & Photography, we offer complete royal wedding coverage: 📸\n✦ Standard Collection: ₹90,000 (Candid + Traditional, 300+ edited portraits)\n✦ Royal Premium Collection: ₹1,20,000 (Full-day cinematic video, Drone aerials, Pre-wedding & Premium album)\nFor complete event management inquiries, please connect with us at +91 78792 23442."
    if any(w in msg_lower for w in ['coupon', 'discount', 'offer', 'code']):
        from datetime import date
        day = date.today().day
        if day <= 10:
            return "🎉 Welcome Privilege Offer!\nUse code: GLAMOUR30 for a 30% savings privilege on our Professional Academy Masterclass.\nPlease mention this code when connecting at +91 78792 23442."
        elif day <= 20:
            return "🔥 Mid-Month Royal Celebration!\nUse code: GLAM50 for a 50% exclusive privilege on Academy admissions.\nKindly reach our concierge at +91 78792 23442 to apply."
        else:
            return "✨ Season Special Privilege!\nUse code: ANSHITA10 for a 10% complimentary privilege.\nWhatsApp our team at +91 78792 23442 for details."
    if any(w in msg_lower for w in ['location', 'address', 'kahan', 'studio', 'city']):
        return "Anshita Makeover Studio is based in India, catering to bridal appointments, destination weddings, and couture bookings nationwide. 📍\nTo reserve your date or book a consultation, please WhatsApp +91 78792 23442."
    if any(w in msg_lower for w in ['hello', 'hi', 'namaste', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Namaste and warm greetings from Anshita Makeover! 🙏✨\nWe are dedicated to crafting your most radiant and elegant moments across India — from royal bridal transformations to certified professional makeup education.\nHow may we be at your service today? 💄"
    return "Thank you for reaching out to Anshita Makeover. ✨ For immediate assistance, personalized packages, and appointment reservations across India, please WhatsApp our bridal concierge at +91 78792 23442. We look forward to creating magic with you! 💍"


# ── API: Set Language ─────────────────────────────────────────
def set_language(request):
    lang = request.GET.get('lang', 'hinglish')
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('lang', lang, max_age=365*24*3600)
    return response


# ── Admin Login/Logout ────────────────────────────────────────
def admin_login(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', '/'))
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next') or '/'
            return redirect(next_url)
        else:
            error = 'Invalid credentials or not an admin.'
    return render(request, 'core/admin_login.html', {'error': error})


def admin_logout_view(request):
    logout(request)
    return redirect('/')


# ── API: Get Current Active & Exit Coupons ────────────────────
def get_coupon_api(request):
    site = get_site_settings()
    active_coupon = get_active_coupon(site)
    exit_coupon = {
        'code': site.exit_coupon_code,
        'discount': site.exit_coupon_discount_percent,
        'label': site.exit_coupon_label,
        'active': site.exit_coupon_active,
    } if site.exit_coupon_active else None
    return JsonResponse({
        'ok': True,
        'coupon': active_coupon,
        'exit_coupon': exit_coupon
    })


# ── API: Admin Coupon Control ─────────────────────────────────
@login_required
def admin_coupon_update(request):
    if request.method == 'POST':
        site = get_site_settings()
        if 'coupon_active' in request.POST:
            site.coupon_active = request.POST.get('coupon_active') == '1'
        if 'coupon_auto_by_date' in request.POST:
            site.coupon_auto_by_date = request.POST.get('coupon_auto_by_date') == '1'
        if 'coupon_code' in request.POST:
            site.coupon_code = request.POST.get('coupon_code', site.coupon_code)
        if 'coupon_discount_percent' in request.POST:
            site.coupon_discount_percent = int(request.POST.get('coupon_discount_percent', 0) or 0)
        if 'coupon_label' in request.POST:
            site.coupon_label = request.POST.get('coupon_label', site.coupon_label)
        
        # Exit-intent / Go-back coupon settings
        if 'exit_coupon_active' in request.POST:
            site.exit_coupon_active = request.POST.get('exit_coupon_active') == '1'
        if 'exit_coupon_code' in request.POST:
            site.exit_coupon_code = request.POST.get('exit_coupon_code', site.exit_coupon_code).strip().upper()
        if 'exit_coupon_discount_percent' in request.POST:
            site.exit_coupon_discount_percent = int(request.POST.get('exit_coupon_discount_percent', 10) or 10)
        if 'exit_coupon_label' in request.POST:
            site.exit_coupon_label = request.POST.get('exit_coupon_label', site.exit_coupon_label).strip()

        site.save()
        return JsonResponse({
            'ok': True,
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

        # Service price update
        is_on_request = data.get('is_on_request', False)
        sp, _ = ServicePrice.objects.get_or_create(service=service)
        if price is not None and str(price).strip():
            sp.price = float(price)
        sp.is_on_request = is_on_request
        sp.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


# ── API: Admin Event Package CRUD ────────────────────────────
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
        pkg.package_type = data.get('package_type', 'custom')
        pkg.description = data.get('description', '')
        pkg.features = data.get('features', '')
        pkg.is_active = data.get('is_active', True)
        pkg.is_featured = data.get('is_featured', False)
        price_str = data.get('price', '')
        pkg.price = float(price_str) if price_str else None
        pkg.price_label = data.get('price_label', 'On Request')
        pkg.save()
        return JsonResponse({'ok': True, 'id': pkg.id})

    if request.method == 'DELETE':
        data = json.loads(request.body)
        EventPackage.objects.filter(id=data.get('id')).delete()
        return JsonResponse({'ok': True})

    # GET
    pkgs = list(EventPackage.objects.all().values())
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


# ── API: Get current coupon (for frontend) ────────────────────
def get_coupon_api(request):
    site = get_site_settings()
    coupon = get_active_coupon(site)
    exit_coupon = {
        'code': site.exit_coupon_code,
        'discount': site.exit_coupon_discount_percent,
        'label': site.exit_coupon_label,
        'active': site.exit_coupon_active,
    } if site.exit_coupon_active else None
    return JsonResponse({
        'ok': True,
        'coupon': coupon,
        'exit_coupon': exit_coupon
    })


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

        if 'image_file' in request.FILES:
            media_item.image_file = request.FILES['image_file']
            # Also sync to GalleryImage if section is gallery or both
            if section in ['gallery', 'both']:
                GalleryImage.objects.create(
                    image=request.FILES['image_file'],
                    caption=title or caption or 'Bridal Couture Look',
                    category=category,
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



