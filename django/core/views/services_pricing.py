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


# ── API: Admin Price Update ───────────────────────────────────
@csrf_exempt
@admin_required
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
                MakeupPackage.objects.filter(name__icontains='Grand Royal Heritage').update(price=b_pr, display_label=f"₹{int(b_pr):,}")
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

        # Social Media Links update
        if target_type in ['social_links', 'social']:
            site = get_site_settings()
            if 'whatsapp_number' in data:
                site.whatsapp_number = str(data['whatsapp_number']).strip()
            if 'instagram_url' in data:
                site.instagram_url = str(data['instagram_url']).strip()
            if 'youtube_url' in data:
                site.youtube_url = str(data['youtube_url']).strip()
            if 'facebook_url' in data:
                site.facebook_url = str(data['facebook_url']).strip()
            site.save()
            return JsonResponse({
                'ok': True,
                'message': 'Social media links updated successfully',
                'whatsapp_number': site.whatsapp_number,
                'instagram_url': site.instagram_url,
                'youtube_url': site.youtube_url,
                'facebook_url': site.facebook_url
            })

        # Service price update
        is_on_request = data.get('is_on_request', False)
        # NULL-safe upsert: ServicePrice.price is NOT NULL, so a bare
        # get_or_create() would 500 on brand-new service keys.
        sp = ServicePrice.objects.filter(service=service).first()
        if sp is None:
            sp = ServicePrice(service=service, price=0)
        if price is not None and str(price).strip():
            sp.price = float(price)
        sp.is_on_request = is_on_request
        sp.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


# ── API: Admin Event & Add-on Package CRUD (Commission & ROI) ─────────────────
@admin_required
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
@csrf_exempt
@admin_required
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
                pkg.display_label = price_label
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
                display_label=price_label,
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
@csrf_exempt
@admin_required
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


@admin_required
def admin_site_settings_manage(request):
    """Direct REST endpoint to view and update SiteSettings (WhatsApp, Instagram, Travel, AI, etc.)"""
    site = get_site_settings()
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            if 'whatsapp_number' in data:
                site.whatsapp_number = str(data['whatsapp_number']).strip()
            if 'instagram_url' in data:
                site.instagram_url = str(data['instagram_url']).strip()
            if 'travel_widget_active' in data:
                site.travel_widget_active = bool(data['travel_widget_active'])
            if 'travel_same_zone_km' in data and data['travel_same_zone_km'] != '':
                site.travel_same_zone_km = int(data['travel_same_zone_km'])
            if 'travel_near_label' in data:
                site.travel_near_label = str(data['travel_near_label']).strip()
            if 'travel_near_fee_min' in data and data['travel_near_fee_min'] != '':
                site.travel_near_fee_min = int(float(data['travel_near_fee_min']))
            if 'travel_near_fee_max' in data and data['travel_near_fee_max'] != '':
                site.travel_near_fee_max = int(float(data['travel_near_fee_max']))
            if 'travel_far_label' in data:
                site.travel_far_label = str(data['travel_far_label']).strip()
            if 'travel_far_fee_min' in data and data['travel_far_fee_min'] != '':
                site.travel_far_fee_min = int(float(data['travel_far_fee_min']))
            if 'travel_far_fee_max' in data and data['travel_far_fee_max'] != '':
                site.travel_far_fee_max = int(float(data['travel_far_fee_max']))
            if 'travel_custom_note' in data:
                site.travel_custom_note = str(data['travel_custom_note']).strip()
            if 'default_auto_coupon_badge' in data:
                site.default_auto_coupon_badge = str(data['default_auto_coupon_badge']).strip()
            if 'ai_negotiation_enabled' in data:
                site.ai_negotiation_enabled = bool(data['ai_negotiation_enabled'])
            if 'ai_max_discount_percent' in data and data['ai_max_discount_percent'] != '':
                site.ai_max_discount_percent = int(data['ai_max_discount_percent'])
            if 'ai_negotiation_strategy' in data:
                site.ai_negotiation_strategy = str(data['ai_negotiation_strategy']).strip()
            if 'ai_negotiation_instructions' in data:
                site.ai_negotiation_instructions = str(data['ai_negotiation_instructions']).strip()
            site.save()
            return JsonResponse({'ok': True, 'message': 'Site settings updated successfully.'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    # GET: return all site settings
    return JsonResponse({
        'ok': True,
        'settings': {
            'whatsapp_number': site.whatsapp_number,
            'instagram_url': site.instagram_url,
            'travel_widget_active': site.travel_widget_active,
            'travel_same_zone_km': site.travel_same_zone_km,
            'travel_near_label': site.travel_near_label,
            'travel_near_fee_min': site.travel_near_fee_min,
            'travel_near_fee_max': site.travel_near_fee_max,
            'travel_far_label': site.travel_far_label,
            'travel_far_fee_min': site.travel_far_fee_min,
            'travel_far_fee_max': site.travel_far_fee_max,
            'travel_custom_note': site.travel_custom_note,
            'default_auto_coupon_badge': site.default_auto_coupon_badge,
            'ai_negotiation_enabled': site.ai_negotiation_enabled,
            'ai_max_discount_percent': site.ai_max_discount_percent,
            'ai_negotiation_strategy': site.ai_negotiation_strategy,
            'ai_negotiation_instructions': site.ai_negotiation_instructions,
            'offer_bridal_free_sides': site.offer_bridal_free_sides,
            'offer_next_sides_discounted_price': float(site.offer_next_sides_discounted_price),
            'offer_combo_discount_percent': site.offer_combo_discount_percent,
            'offer_grand_combo_bundle_price': float(site.offer_grand_combo_bundle_price),
        }
    })


@csrf_exempt
@admin_required
def admin_package_manage(request, pkg_id=None):
    """Direct REST endpoint to view, create, edit, or delete MakeupPackages"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            action = data.get('action')
            
            # Delete
            if action == 'delete' or (pkg_id and data.get('delete')):
                target_id = pkg_id or data.get('id')
                MakeupPackage.objects.filter(id=target_id).delete()
                return JsonResponse({'ok': True, 'message': 'Package deleted.'})

            # Edit existing or Create new
            pkg = MakeupPackage.objects.filter(id=pkg_id or data.get('id')).first() if (pkg_id or data.get('id')) else MakeupPackage()
            
            if 'name' in data:
                pkg.name = str(data['name']).strip()
            if 'display_label' in data:
                pkg.display_label = str(data['display_label']).strip()
            if 'package_type' in data:
                pkg.package_type = str(data['package_type']).strip()
            if 'tagline' in data:
                pkg.tagline = str(data['tagline']).strip()
            if 'price' in data:
                pr = data['price']
                pkg.price = float(pr) if pr is not None and str(pr).strip() != '' else None
            if 'original_price' in data:
                opr = data['original_price']
                pkg.original_price = float(opr) if opr is not None and str(opr).strip() != '' else None
            if 'features' in data:
                pkg.features = str(data['features']).strip()
            if 'is_featured' in data:
                pkg.is_featured = bool(data['is_featured'])
            if 'is_active' in data:
                pkg.is_active = bool(data['is_active'])
            if 'order' in data and data['order'] != '':
                pkg.order = int(data['order'])
            if 'min_negotiated_price' in data:
                mnp = data['min_negotiated_price']
                pkg.min_negotiated_price = float(mnp) if mnp is not None and str(mnp).strip() != '' else None
            if 'max_discount_percent' in data and data['max_discount_percent'] != '':
                pkg.max_discount_percent = int(data['max_discount_percent'])

            pkg.save()
            return JsonResponse({
                'ok': True,
                'package': {
                    'id': pkg.id,
                    'name': pkg.name,
                    'display_label': pkg.display_label,
                    'human_label': pkg.human_label,
                    'package_type': pkg.package_type,
                    'tagline': pkg.tagline,
                    'price': float(pkg.price) if pkg.price else None,
                    'original_price': float(pkg.original_price) if pkg.original_price else None,
                    'features': pkg.features,
                    'features_list': pkg.get_features_list(),
                    'is_featured': pkg.is_featured,
                    'is_active': pkg.is_active,
                }
            })
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    # GET: return package list or single package
    if pkg_id:
        pkg = MakeupPackage.objects.filter(id=pkg_id).first()
        if not pkg:
            return JsonResponse({'ok': False, 'error': 'Package not found'}, status=404)
        return JsonResponse({'ok': True, 'package': {
            'id': pkg.id,
            'name': pkg.name,
            'display_label': pkg.display_label,
            'human_label': pkg.human_label,
            'package_type': pkg.package_type,
            'tagline': pkg.tagline,
            'price': float(pkg.price) if pkg.price else None,
            'original_price': float(pkg.original_price) if pkg.original_price else None,
            'features': pkg.features,
            'features_list': pkg.get_features_list(),
            'is_featured': pkg.is_featured,
            'is_active': pkg.is_active,
        }})

    pkgs = []
    for p in MakeupPackage.objects.all():
        pkgs.append({
            'id': p.id,
            'name': p.name,
            'display_label': p.display_label,
            'human_label': p.human_label,
            'package_type': p.package_type,
            'tagline': p.tagline,
            'price': float(p.price) if p.price else None,
            'original_price': float(p.original_price) if p.original_price else None,
            'features': p.features,
            'features_list': p.get_features_list(),
            'is_featured': p.is_featured,
            'is_active': p.is_active,
        })
    return JsonResponse({'ok': True, 'packages': pkgs})


@csrf_exempt
def artist_onboarding(request):
    """
    Dedicated Mobile-First Artist Onboarding & Pricing Intake Portal for Anshita.
    Allows Anshita to view, add, and update services, packages, and pricing seamlessly
    from her mobile phone or laptop.
    Protected by staff auth OR artist passcode session (PIN: '2026' or ?key=anshita2026).
    """
    pin_attempt = request.POST.get('passcode') or request.GET.get('key')
    if pin_attempt in ['2026', 'anshita2026', 'Anshita@2026']:
        request.session['artist_verified'] = True

    is_authed = request.user.is_authenticated and request.user.is_staff
    is_artist_verified = request.session.get('artist_verified', False)

    if not (is_authed or is_artist_verified):
        return render(request, 'core/artist_onboarding_login.html', {
            'error': 'Incorrect passcode. Please enter studio passcode (2026).' if pin_attempt else None
        })

    site = get_site_settings()
    services = StudioService.objects.all().order_by('order', 'id')
    packages = MakeupPackage.objects.all().order_by('order', 'id')
    service_prices = ServicePrice.objects.all()

    return render(request, 'core/artist_onboarding.html', {
        'site': site,
        'services': services,
        'packages': packages,
        'service_prices': service_prices,
    })


