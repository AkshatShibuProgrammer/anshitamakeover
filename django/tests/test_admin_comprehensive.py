import os
import json
import pytest
from django.test import Client
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
import django
django.setup()

from core.models import (
    SiteSettings, Artist, MakeupPackage, CustomerReview,
    EventPackage, StudioService, LookGroup, LookMediaItem, MediaItem
)

@pytest.fixture
def auth_client():
    client = Client()
    user, _ = User.objects.get_or_create(username='admin_test_tester')
    user.set_password('AdminSec@2026')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    client.login(username='admin_test_tester', password='AdminSec@2026')
    return client

def test_admin_portal_page_get(auth_client):
    res = auth_client.get('/admin-portal/')
    assert res.status_code == 200
    assert b'Admin' in res.content or b'Portal' in res.content or b'Dashboard' in res.content

def test_admin_coupon_generate_and_delete_vip(auth_client):
    # 1. Generate VIP coupon
    payload = {
        'action': 'generate_vip',
        'code': 'VIPTEST100',
        'discount': 25,
        'discount_type': 'percent',
        'client_name': 'Royal VIP Bride',
        'notes': 'Test privilege'
    }
    res = auth_client.post('/api/admin/coupon/', json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    assert data.get('vip', {}).get('code') == 'VIPTEST100'

    # 2. Delete VIP coupon
    del_payload = {
        'action': 'delete_vip',
        'code': 'VIPTEST100'
    }
    res_del = auth_client.post('/api/admin/coupon/', json.dumps(del_payload), content_type='application/json')
    assert res_del.status_code == 200
    assert res_del.json().get('ok') is True

def test_admin_price_and_ai_negotiation_update(auth_client):
    payload = {
        'type': 'ai_negotiation',
        'ai_negotiation_enabled': True,
        'ai_negotiation_min_floor_percent': 70,
        'ai_max_discount_percent': 20,
        'ai_negotiation_strategy': 'concierge_balanced'
    }
    res = auth_client.post('/api/admin/price/', json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    assert data.get('ai_negotiation_enabled') is True
    assert data.get('ai_max_discount_percent') == 20

def test_admin_artist_crud(auth_client):
    # Create / Update Artist
    res = auth_client.post('/api/admin/artist/', {
        'name': 'Test Senior Stylist',
        'specialities': 'Bridal Hair & Saree Draping',
        'bio': 'Over 7 years of editorial experience',
        'order': 2,
        'is_active': '1'
    })
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    artist_id = data.get('artist', {}).get('id')

    # Get Artists
    res_list = auth_client.get('/api/admin/artist/')
    assert res_list.status_code == 200
    artists = res_list.json().get('artists', [])
    assert any(a['name'] == 'Test Senior Stylist' for a in artists)

    # Delete Artist via DELETE request
    res_del = auth_client.delete('/api/admin/artist/', json.dumps({'id': artist_id}), content_type='application/json')
    assert res_del.status_code == 200
    assert res_del.json().get('ok') is True

def test_admin_service_crud(auth_client):
    # Create Makeup Package
    payload = {
        'name': 'Royal Mughal Airbrush Package',
        'package_type': 'bridal',
        'tagline': 'Bespoke HD Mughal Radiance',
        'price': 48000.0,
        'price_label': '₹48,000',
        'features': 'Airbrush base, 3D lashes, floral draping',
        'is_active': True,
        'is_featured': True
    }
    res = auth_client.post('/api/admin/service/', json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    pkg_id = data.get('package', {}).get('id')

    # Read
    res_list = auth_client.get('/api/admin/service/')
    assert res_list.status_code == 200
    pkgs = res_list.json().get('packages', [])
    assert any(p['name'] == 'Royal Mughal Airbrush Package' for p in pkgs)

    # Delete
    del_payload = {'id': pkg_id}
    res_del = auth_client.delete('/api/admin/service/', json.dumps(del_payload), content_type='application/json')
    assert res_del.status_code == 200
    assert res_del.json().get('ok') is True

def test_admin_event_package_crud(auth_client):
    # Create / Update
    payload = {
        'name': 'Grand Luxury Sangeet & Reception Package',
        'category': 'wedding',
        'package_type': 'signature',
        'price': 75000,
        'vendor_cost': 45000,
        'description': 'Full bride + 5 family glam suite',
        'features': 'Bridal HD + 5 Party Makeups'
    }
    res = auth_client.post('/api/admin/event-package/', json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    pkg_id = data.get('id')

    # Read
    res_list = auth_client.get('/api/admin/event-package/')
    assert res_list.status_code == 200
    assert any(p['id'] == pkg_id for p in res_list.json().get('packages', []))

    # Delete
    res_del = auth_client.delete('/api/admin/event-package/', json.dumps({'id': pkg_id}), content_type='application/json')
    assert res_del.status_code == 200
    assert res_del.json().get('ok') is True

def test_admin_review_management(auth_client):
    review = CustomerReview.objects.create(
        client_name='Pooja Sharma',
        rating=5,
        review_text='Most amazing bridal transformation!',
        event_type='Bridal HD',
        is_active=True
    )
    # Toggle active
    res = auth_client.post('/api/admin/review/', json.dumps({'action': 'toggle_active', 'id': review.id}), content_type='application/json')
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    review.refresh_from_db()
    assert review.is_active is False

    # Delete
    res_del = auth_client.post('/api/admin/review/', json.dumps({'action': 'delete', 'id': review.id}), content_type='application/json')
    assert res_del.status_code == 200
    assert CustomerReview.objects.filter(id=review.id).exists() is False

def test_admin_studio_service_crud(auth_client):
    # Create Studio Service
    res = auth_client.post('/api/admin/studio-service/', {
        'title': 'Couture Saree Draping & Dupatta Setting',
        'category': 'draping',
        'price': 3500.0,
        'discount_price': 3000.0,
        'description': 'Pleating and can-can setting',
        'features': 'Precision pleats, luxury safety pins included'
    })
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    svc_id = data.get('service', {}).get('id')

    # Read
    res_list = auth_client.get('/api/admin/studio-service/')
    assert res_list.status_code == 200
    assert any(s['id'] == svc_id for s in res_list.json().get('services', []))

    # Delete
    res_del = auth_client.post('/api/admin/studio-service/', json.dumps({'action': 'delete', 'id': svc_id}), content_type='application/json')
    assert res_del.status_code == 200
    assert res_del.json().get('ok') is True

def test_admin_lookgroup_crud(auth_client):
    # Create Look Group
    res = auth_client.post('/api/admin/lookgroup/', {
        'name': 'Pastel Royal Rajputi Bride Look',
        'client_name': 'Rhea Rathore',
        'makeup_type': 'Airbrush Pastel Bridal',
        'category': 'bridal',
        'description': 'Soft peach-pink tones with regal emerald contrasts'
    })
    assert res.status_code == 200
    data = res.json()
    assert data.get('ok') is True
    grp_id = data.get('group', {}).get('id')

    # Read
    res_list = auth_client.get('/api/admin/lookgroup/')
    assert res_list.status_code == 200
    assert any(g['id'] == grp_id for g in res_list.json().get('groups', []))

    # Delete
    res_del = auth_client.post('/api/admin/lookgroup/', json.dumps({'action': 'delete', 'id': grp_id}), content_type='application/json')
    assert res_del.status_code == 200
    assert res_del.json().get('ok') is True
