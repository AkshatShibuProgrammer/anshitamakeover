import json
from django.shortcuts import render, redirect, get_object_or_404
from ..models import StudioService, MakeupPackage, BookingEnquiry
from .common import admin_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from features.public_ops.public_service import (
    compile_home_context,
    compile_academy_context,
    compile_travel_estimator_context,
    compile_cart_context,
    compile_chatbot_context
)

@csrf_exempt
def booking_enquiry(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body or '{}')
        name, phone = str(data.get('name', '')).strip(), str(data.get('phone', '')).strip()
        if not name or not phone:
            return JsonResponse({'ok': False, 'error': 'Name and phone are required.'}, status=400)
        items = data.get('items') if isinstance(data.get('items'), list) else []
        # Recalculate from current published database prices; never trust a browser total.
        verified_total = 0.0
        for item in items:
            item_id = str(item.get('id', ''))
            qty = max(1, min(20, int(item.get('qty', 1) or 1)))
            obj = None
            if item_id.startswith('service-'):
                obj = StudioService.objects.filter(id=item_id.removeprefix('service-'), is_active=True).first()
            elif item_id.startswith('package-'):
                obj = MakeupPackage.objects.filter(id=item_id.removeprefix('package-'), is_active=True).first()
            if obj and obj.price:
                verified_total += float(obj.price) * qty
        if not verified_total and not items:
            return JsonResponse({'ok': False, 'error': 'Please select at least one published service.'}, status=400)
        enquiry = BookingEnquiry.objects.create(name=name, phone=phone, email=str(data.get('email', '')).strip(), city=str(data.get('city', '')).strip(), notes=str(data.get('notes', '')).strip(), event_date=data.get('event_date') or None, cart_items=items, estimated_total=verified_total)
        return JsonResponse({'ok': True, 'id': enquiry.id, 'message': 'Your availability request has been received.'}, status=201)
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'Please check the booking details.'}, status=400)

def package_builder(request):
    """Public package recommender page; recommendations remain server-guarded."""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    return render(request, 'core/package_builder.html', context)

@csrf_exempt
def package_builder_api(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body or '{}')
        categories = data.get('categories') if isinstance(data.get('categories'), list) else []
        budget = float(data.get('budget') or 0)
        services = list(StudioService.objects.filter(is_active=True, category__in=categories).order_by('order', 'id')) if categories else list(StudioService.objects.filter(is_active=True).order_by('order', 'id')[:3])
        selected, total = [], 0.0
        for service in services:
            if service.price and (not budget or total + float(service.price) <= budget):
                selected.append({'id': service.id, 'title': service.title, 'price': float(service.price), 'category': service.category})
                total += float(service.price)
        max_discount = max(0, min(50, int(data.get('max_discount') or 0)))
        discount = round(total * max_discount / 100) if max_discount else 0
        return JsonResponse({'ok': True, 'items': selected, 'subtotal': total, 'discount': discount, 'total': total - discount, 'guardrails': {'max_discount_percent': max_discount}})
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'Please provide valid package preferences.'}, status=400)

@admin_required
def admin_booking_enquiries(request):
    if request.method == 'POST':
        payload = json.loads(request.body or '{}') if request.content_type == 'application/json' else request.POST
        enquiry = get_object_or_404(BookingEnquiry, id=payload.get('id'))
        if payload.get('action') == 'delete':
            enquiry.delete()
            return JsonResponse({'ok': True})
        if payload.get('status') in dict(BookingEnquiry.STATUS_CHOICES):
            enquiry.status = payload.get('status')
            enquiry.save(update_fields=['status'])
        return JsonResponse({'ok': True, 'status': enquiry.status})
    return render(request, 'core/admin_enquiries.html', {'enquiries': BookingEnquiry.objects.all()})

def chatbot_page(request):
    """Dedicated standalone full-screen AI Concierge page (for Open in New Tab)"""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_chatbot_context(lang)
    resp = render(request, 'core/chatbot_page.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

def cart_page(request):
    """Dedicated page for Bridal Trousseau / Cart booking, package customization, and combo checkout"""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_cart_context(lang)
    resp = render(request, 'core/cart.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

def animation_lab(request):
    """Preserved animation showcase route; public motion remains reduced-motion aware."""
    return render(request, 'core/animation_lab.html')

def home(request):
    """Orchestrator endpoint delegating homepage data compilation to public_ops"""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    resp = render(request, 'core/home.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

def services_page(request):
    """Public service catalogue with filterable, admin-managed offerings."""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    context['selected_category'] = request.GET.get('category', 'all')
    return render(request, 'core/services.html', context)

def gallery_page(request):
    """Dedicated data-driven lookbook catalogue."""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    context['gallery_category'] = request.GET.get('category', 'all')
    return render(request, 'core/gallery.html', context)

def service_detail(request, slug):
    """Dedicated service detail page; slug currently resolves by stable service id slug."""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    service = get_object_or_404(StudioService, id=slug, is_active=True)
    context['service_detail'] = service
    context['related_services'] = StudioService.objects.filter(is_active=True, category=service.category).exclude(pk=service.pk)[:4]
    return render(request, 'core/service_detail.html', context)

def packages_page(request):
    """Public package catalogue using the same admin-controlled pricing data."""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    context['package_filter'] = request.GET.get('category', 'all')
    return render(request, 'core/packages.html', context)

def package_detail(request, pkg_id):
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    context['package_detail'] = get_object_or_404(MakeupPackage, id=pkg_id, is_active=True)
    return render(request, 'core/package_detail.html', context)

def academy(request):
    """Orchestrator endpoint delegating academy curriculum compilation to public_ops"""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_academy_context(lang)
    resp = render(request, 'core/academy.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

def travel_estimator(request):
    """Dedicated page for Pan-India Travel & Outstation Distance Estimator Tool"""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_travel_estimator_context(lang)
    resp = render(request, 'core/travel_estimator.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

@csrf_exempt
def set_language(request):
    """Orchestrator endpoint handling language preference switching"""
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

def sinha_logo_studio(request):
    """Orchestrator endpoint for Sinha luxury branding visualizer"""
    return render(request, 'core/sinha_logo_studio.html')
