import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from features.public_ops.public_service import (
    compile_home_context,
    compile_academy_context,
    compile_travel_estimator_context,
    compile_cart_context,
    compile_chatbot_context
)

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

def home(request):
    """Orchestrator endpoint delegating homepage data compilation to public_ops"""
    lang = request.GET.get('lang') or request.COOKIES.get('lang', 'english')
    context = compile_home_context(lang)
    resp = render(request, 'core/home.html', context)
    if request.GET.get('lang'):
        resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

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
