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


# ── API: Admin Media Management (Upload Photos, Instagram Reels & YouTube) ──
@admin_required
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

        # File security validations (CWE-434 mitigation)
        ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        ALLOWED_VIDEO_EXTS = {'.mp4', '.webm', '.mov'}
        MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

        if 'image_file' in request.FILES:
            f = request.FILES['image_file']
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTS:
                return JsonResponse({'ok': False, 'error': f"Invalid image file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTS))}"}, status=400)
            if f.size > MAX_FILE_SIZE:
                return JsonResponse({'ok': False, 'error': "Image file exceeds maximum limit of 25MB."}, status=400)

            media_item.image_file = f
            # Also sync to GalleryImage if section is gallery or both
            if section in ['gallery', 'both']:
                GalleryImage.objects.create(
                    image=f,
                    caption=title or caption or 'Bridal Couture Look',
                    category=category,
                    look_group_id=look_group_id,
                    look_group_name=look_group_name,
                    is_group_cover=is_group_cover,
                    is_active=True,
                    order=0
                )

        if 'video_file' in request.FILES:
            vf = request.FILES['video_file']
            vext = os.path.splitext(vf.name)[1].lower()
            if vext not in ALLOWED_VIDEO_EXTS:
                return JsonResponse({'ok': False, 'error': f"Invalid video file type: {vext}. Allowed: {', '.join(sorted(ALLOWED_VIDEO_EXTS))}"}, status=400)
            if vf.size > MAX_FILE_SIZE:
                return JsonResponse({'ok': False, 'error': "Video file exceeds maximum limit of 25MB."}, status=400)

            media_item.video_file = vf

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


# ── API: Admin Look Groups (Folders by Person / Makeup Type) ──────────
@admin_required
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
        is_featured = request.POST.get('is_featured') in ['1', 'true', 'on']
        show_ext_btn = request.POST.get('show_external_link_button') not in ['0', 'false', 'off']

        if not name:
            if client_name and makeup_type:
                name = f"{client_name} — {makeup_type}"
            else:
                name = client_name or makeup_type or "Bespoke Bridal Look"

        try:
            order = int(order_val)
        except ValueError:
            order = 0

        slug_val = slugify(name)[:140]

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
            grp.slug = slug_val
            grp.is_featured = is_featured
            grp.show_external_link_button = show_ext_btn
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
                slug=slug_val,
                cover_image_url=cover_image_url,
                is_featured=is_featured,
                show_external_link_button=show_ext_btn,
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
                'is_featured': grp.is_featured,
                'show_external_link_button': grp.show_external_link_button,
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
                'show_platform_link': itm.show_platform_link,
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
            'is_featured': g.is_featured,
            'show_external_link_button': g.show_external_link_button,
            'order': g.order,
            'is_active': g.is_active,
            'media_items': media_list,
            'media_count': len(media_list)
        })
    return JsonResponse({'groups': groups})


# ── API: Admin Look Media (Add Photo, Video, Instagram, YouTube to Group) ──
@admin_required
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
        show_platform_link = request.POST.get('show_platform_link') not in ['0', 'false', 'off']
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
            show_platform_link=show_platform_link,
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


