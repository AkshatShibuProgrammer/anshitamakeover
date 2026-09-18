import os
import json
import pytest
import django
from django.test import Client
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
django.setup()

from core.models import SiteSettings, Artist, CustomerReview, ServicePrice, EventPackage

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def admin_user():
    user, _ = User.objects.get_or_create(username='test_admin')
    user.set_password('AdminTest@123')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user

def test_home_page_status(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Anshita' in response.content

def test_academy_page_status(client):
    response = client.get('/academy/')
    assert response.status_code == 200

def test_sinha_logos_status(client):
    response = client.get('/sinha-logos/')
    assert response.status_code == 200

def test_language_switch_api(client):
    response = client.post('/set-language/', json.dumps({'language': 'hi'}), content_type='application/json')
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') == 'ok'

def test_coupon_api(client):
    response = client.get('/api/coupon/')
    assert response.status_code == 200
    data = response.json()
    assert 'coupon' in data or 'code' in data or data.get('status') in ['ok', 'active', True] or 'discount' in str(data)

def test_chatbot_api(client):
    response = client.post('/api/chatbot/', json.dumps({'message': 'What are your bridal prices?'}), content_type='application/json')
    assert response.status_code == 200
    data = response.json()
    assert 'reply' in data or 'response' in data or 'message' in data

def test_review_submission(client):
    payload = {
        'reviewer_name': 'Playwright Test Reviewer',
        'rating': 5,
        'comment': 'Exceptional makeup artistry and service!',
        'service_type': 'bridal'
    }
    response = client.post('/api/review/submit/', json.dumps(payload), content_type='application/json')
    assert response.status_code in [200, 201]

def test_admin_portal_login_and_access(client, admin_user):
    login_success = client.login(username='test_admin', password='AdminTest@123')
    assert login_success is True
    response = client.get('/admin-portal/')
    assert response.status_code == 200
