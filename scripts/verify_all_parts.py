import os
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'django')))

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import MakeupPackage

print("=" * 60)
print("VERIFYING ALL IMPLEMENTATION PARTS (BRANCH 20092026)")
print("=" * 60)

c = Client()

# Part 01 / Home Page / Part 06 (Preloader markup & animations)
r_home = c.get('/')
print(f"[TEST 1] GET / (Home Page): Status {r_home.status_code}")
assert r_home.status_code == 200, "Home page failed to render"
content = r_home.content.decode('utf-8')
assert 'id="preloader"' in content, "Preloader markup missing"
assert 'curtain-left' in content and 'curtain-right' in content, "Curtains missing"
assert 'floating-cart-pill' in content, "Floating cart button missing"
assert 'id="chatbot"' in content, "Chatbot container missing"
assert 'cartUpsellSection' in content, "Cart upsell section missing"
assert 'pkgQuickViewModal' in content, "Package Quick-View modal missing"
print("  -> Preloader, Curtains, Floating Cart, Chatbot, Quick-View Modal verified in Home Page!")

# Part 05: Seasonal Coupons
r_coupons = c.get('/api/coupon/')
print(f"[TEST 2] GET /api/coupon/: Status {r_coupons.status_code}")
assert r_coupons.status_code == 200, "Seasonal coupons endpoint failed"
coupon_data = r_coupons.json()
print(f"  -> Active seasonal coupon: {coupon_data.get('code')} ({coupon_data.get('discount')}% off: {coupon_data.get('description')})")

# Part 04: Security / Auth check on admin API
r_unauth = c.post('/api/admin/package/', json.dumps({"title": "Hack"}), content_type="application/json")
print(f"[TEST 3] Security Audit - Unauthenticated POST to /api/admin/package/: Status {r_unauth.status_code}")
assert r_unauth.status_code in [302, 401, 403], f"Unauthenticated access permitted: {r_unauth.status_code}"
print("  -> Unauthorized access strictly blocked!")

# Part 03: Admin Endpoints authenticated
u, _ = User.objects.get_or_create(username='verifier_admin', defaults={'is_staff': True})
u.is_staff = True
u.save()
c.force_login(u)

# Test package manage endpoint
pkg_payload = {
    "title": "Imperial Heritage Royale Test",
    "category": "bridal",
    "price": 49000,
    "original_price": 65000,
    "display_label": "Signature Couture",
    "features": ["3 Events included", "Airbrush HD", "2 Complimentary Sides"],
    "is_active": True
}
r_pkg = c.post('/api/admin/package/', json.dumps(pkg_payload), content_type="application/json")
print(f"[TEST 4] Admin POST /api/admin/package/: Status {r_pkg.status_code}")
assert r_pkg.status_code == 200, f"Package creation failed: {r_pkg.content}"
pkg_res = r_pkg.json()
print(f"  -> Package created successfully: ID {pkg_res.get('id')}, {pkg_res.get('title')}")

# Clean up created package and user
if 'id' in pkg_res:
    MakeupPackage.objects.filter(id=pkg_res['id']).delete()
u.delete()

print("=" * 60)
print("ALL VERIFICATION CHECKS PASSED PERFECTLY!")
print("=" * 60)
