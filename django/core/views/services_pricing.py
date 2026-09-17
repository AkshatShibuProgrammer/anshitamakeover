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


