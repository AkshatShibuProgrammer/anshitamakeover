"""
API contract regression suite — exercises the real HTTP stack.

Mirrors the Karate feature files one-to-one (see ``karate/``): every test
here has a Karate scenario twin with the same TC-API id, so the same
contract is validated by two independent frameworks.

Run (usually via the master program ``python testing/run_all.py --suite api``)::

    python -m pytest testing/api -v
"""
import json
import uuid

import pytest
import requests

pytestmark = [pytest.mark.public]


# ── Public endpoints ─────────────────────────────────────────────────────

def test_api_001_home_page(live_base_url):
    """TC-API-001: homepage serves 200 with brand content."""
    r = requests.get(live_base_url + '/', timeout=30)
    assert r.status_code == 200
    assert 'Anshita' in r.text


def test_api_002_academy_page(live_base_url):
    """TC-API-002: academy page serves 200."""
    r = requests.get(live_base_url + '/academy/', timeout=30)
    assert r.status_code == 200


def test_api_003_sinha_studio_page(live_base_url):
    """TC-API-003: sinha logo studio page serves 200."""
    r = requests.get(live_base_url + '/sinha-logos/', timeout=30)
    assert r.status_code == 200


def test_api_004_coupon_contract(live_base_url):
    """TC-API-004: /api/coupon/ contract — seasonal/default/exit layers."""
    r = requests.get(live_base_url + '/api/coupon/', timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data['ok'] is True
    assert set(data) >= {'ok', 'coupon', 'default_coupon', 'exit_coupon'}
    assert data['default_coupon']['code'] == 'TODAYVIP'


def test_api_005_cors_header(live_base_url):
    """TC-API-005: public API responses carry CORS allow-origin."""
    r = requests.get(live_base_url + '/api/coupon/', timeout=10)
    assert r.headers.get('Access-Control-Allow-Origin') == '*'


def test_api_006_language_switch_json(live_base_url):
    """TC-API-006: /set-language/ JSON switch sets lang cookie."""
    r = requests.post(live_base_url + '/set-language/',
                      json={'language': 'hindi'}, timeout=10)
    assert r.status_code == 200
    assert r.json()['language'] == 'hindi'
    assert r.cookies.get('lang') == 'hindi'


def test_api_007_chatbot_fallback_reply(live_base_url):
    """TC-API-007: chatbot answers without a Gemini key (fallback engine)."""
    r = requests.post(live_base_url + '/api/chatbot/',
                      json={'message': 'What are your bridal packages?',
                            'session_id': str(uuid.uuid4())}, timeout=30)
    assert r.status_code == 200
    body = r.json()
    assert body['reply']
    assert body['session_id']


def test_api_008_chatbot_negotiation_floor(live_base_url):
    """TC-API-008: budget below floor never undercuts the floor price."""
    r = requests.post(live_base_url + '/api/chatbot/',
                      json={'message': 'I can only pay 20000'}, timeout=30)
    assert '₹26,250' in r.json()['reply']


def test_api_009_review_submit_validation(anon_session):
    """TC-API-009: review submission validates required fields."""
    r = anon_session.post(anon_session.base_url + '/api/review/submit/',
                          json={'review_text': 'missing name'},
                          headers={'Content-Type': 'application/json'})
    assert r.status_code == 200
    assert r.json()['ok'] is False


def test_api_010_review_submit_roundtrip(anon_session):
    """TC-API-010: valid review submission persists."""
    r = anon_session.post(anon_session.base_url + '/api/review/submit/',
                          json={'client_name': f'API Probe {uuid.uuid4().hex[:6]}',
                                'review_text': 'Contract probe review', 'rating': 5},
                          headers={'Content-Type': 'application/json'})
    assert r.json()['ok'] is True


# ── Auth boundary ────────────────────────────────────────────────────────

ADMIN_PATHS = [
    '/admin-portal/', '/api/admin/coupon/', '/api/admin/artist/',
    '/api/admin/review/', '/api/admin/media/', '/api/admin/studio-service/',
    '/api/admin/lookgroup/', '/api/admin/service/', '/api/admin/event-package/',
]


@pytest.mark.parametrize('path', ADMIN_PATHS)
def test_api_011_admin_endpoints_require_login(live_base_url, path):
    """TC-API-011: anonymous requests to admin APIs bounce to login."""
    r = requests.get(live_base_url + path, allow_redirects=False, timeout=10)
    assert r.status_code == 302
    assert '/admin-login/' in r.headers['Location']


def test_api_012_login_page_renders(live_base_url):
    """TC-API-012: branded admin login page is public."""
    r = requests.get(live_base_url + '/admin-login/', timeout=10)
    assert r.status_code == 200


# ── Admin endpoints (staff session) ──────────────────────────────────────

@pytest.mark.admin
def test_api_013_admin_portal_loads(admin_session):
    """TC-API-013: staff session opens the admin portal dashboard."""
    r = admin_session.get(admin_session.base_url + '/admin-portal/', timeout=30)
    assert r.status_code == 200


@pytest.mark.admin
def test_api_014_artist_crud_roundtrip(admin_session):
    """TC-API-014: artist create → list → delete round trip."""
    name = f'API Artist {uuid.uuid4().hex[:6]}'
    r = admin_session.post(admin_session.base_url + '/api/admin/artist/',
                           data={'name': name, 'specialities': 'makeup'}, timeout=15)
    assert r.json()['ok'] is True
    artist_id = r.json()['artist']['id']

    r = admin_session.get(admin_session.base_url + '/api/admin/artist/', timeout=15)
    assert any(a['id'] == artist_id for a in r.json()['artists'])

    r = admin_session.post(admin_session.base_url + '/api/admin/artist/',
                           data={'action': 'delete', 'id': artist_id}, timeout=15)
    assert r.json()['ok'] is True


@pytest.mark.admin
def test_api_015_package_crud_roundtrip(admin_session):
    """TC-API-015: package create → update → delete round trip."""
    name = f'API Suite {uuid.uuid4().hex[:6]}'
    r = admin_session.api_post('/api/admin/service/', {
        'name': name, 'package_type': 'party', 'price': '7000',
        'features': 'Probe feature',
    })
    assert r.json()['ok'] is True
    pkg_id = r.json()['package']['id']
    assert r.json()['package']['price_label'] == '₹7,000'

    r = admin_session.api_post('/api/admin/service/', {
        'id': pkg_id, 'name': name + ' v2', 'price': '8000',
    })
    assert r.json()['ok'] is True

    r = admin_session.api_post('/api/admin/service/', {'action': 'delete', 'id': pkg_id})
    assert r.json()['ok'] is True


@pytest.mark.admin
def test_api_016_event_package_margin_math(admin_session):
    """TC-API-016: event package create returns commission/margin/ROI."""
    r = admin_session.api_post('/api/admin/event-package/', {
        'name': f'API Bundle {uuid.uuid4().hex[:6]}', 'category': 'photography',
        'package_type': 'custom', 'vendor_cost': '50000', 'price': '68000',
    })
    data = r.json()
    assert data['ok'] is True
    assert data['commission'] == 18000.0
    assert data['roi_pct'] == 36.0
    # cleanup
    admin_session.api_delete('/api/admin/event-package/', {'id': data['id']})


@pytest.mark.admin
def test_api_017_coupon_update_roundtrip(admin_session):
    """TC-API-017: seasonal coupon update + VIP generate/revoke."""
    r = admin_session.api_post('/api/admin/coupon/', {
        'coupon_active': '1', 'coupon_auto_by_date': '0',
        'coupon_code': 'APIPROBE', 'coupon_discount_percent': '22',
    })
    assert r.json()['ok'] is True

    vip_code = f'APIVIP{uuid.uuid4().hex[:4].upper()}'
    r = admin_session.api_post('/api/admin/coupon/', {
        'action': 'generate_vip', 'code': vip_code, 'discount': 20,
    })
    assert r.json()['ok'] is True
    r = admin_session.api_post('/api/admin/coupon/', {
        'action': 'delete_vip', 'code': vip_code,
    })
    assert r.json()['ok'] is True
    assert all(v['code'] != vip_code for v in r.json()['vip_list'])

    # restore canonical seasonal coupon for re-runs
    admin_session.api_post('/api/admin/coupon/', {
        'coupon_active': '1', 'coupon_auto_by_date': '0',
        'coupon_code': 'GLAMOUR30', 'coupon_discount_percent': '30',
    })


@pytest.mark.admin
def test_api_018_price_and_guardrail_updates(admin_session):
    """TC-API-018: price update + AI negotiation clamp boundaries."""
    r = admin_session.api_post('/api/admin/price/', {
        'service': 'nails_art', 'price': 2750,
    })
    assert r.json()['ok'] is True

    r = admin_session.api_post('/api/admin/price/', {
        'type': 'ai_negotiation', 'ai_negotiation_min_floor_percent': 1,
        'ai_max_discount_percent': 99,
    })
    data = r.json()
    assert data['ok'] is True
    assert data['ai_negotiation_min_floor_percent'] == 40   # clamped
    assert data['ai_max_discount_percent'] == 50            # clamped

    # restore canonical guardrails for re-runs
    admin_session.api_post('/api/admin/price/', {
        'type': 'ai_negotiation', 'ai_negotiation_min_floor_percent': 75,
        'ai_max_discount_percent': 20,
    })


@pytest.mark.admin
def test_api_019_studio_service_crud(admin_session):
    """TC-API-019: studio service create → delete."""
    title = f'API Discipline {uuid.uuid4().hex[:6]}'
    r = admin_session.post(admin_session.base_url + '/api/admin/studio-service/',
                           data={'title': title, 'price': '9000',
                                 'description': 'probe', 'features': 'a\nb'},
                           timeout=15)
    assert r.json()['ok'] is True
    svc_id = r.json()['service']['id']
    assert r.json()['service']['features_list'] == ['a', 'b']

    r = admin_session.post(admin_session.base_url + '/api/admin/studio-service/',
                           data={'action': 'delete', 'id': svc_id}, timeout=15)
    assert r.json()['ok'] is True


@pytest.mark.admin
def test_api_020_lookgroup_and_media(admin_session):
    """TC-API-020: look group create + media attach + teardown."""
    name = f'API Group {uuid.uuid4().hex[:6]}'
    r = admin_session.post(admin_session.base_url + '/api/admin/lookgroup/',
                           data={'name': name, 'client_name': 'Probe',
                                 'makeup_type': 'Test Look', 'category': 'bridal'},
                           timeout=15)
    assert r.json()['ok'] is True
    grp_id = r.json()['group']['id']

    r = admin_session.post(admin_session.base_url + '/api/admin/lookgroup/media/',
                           data={'group_id': grp_id, 'media_type': 'youtube',
                                 'external_url': 'https://youtu.be/abcdefghijk'},
                           timeout=15)
    assert r.json()['ok'] is True
    assert r.json()['item']['embed_code'] == 'abcdefghijk'

    r = admin_session.post(admin_session.base_url + '/api/admin/lookgroup/',
                           data={'action': 'delete', 'id': grp_id}, timeout=15)
    assert r.json()['ok'] is True
