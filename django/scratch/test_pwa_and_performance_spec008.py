"""
Automated Verification Suite for SPEC-008: Performance, PWA & Lighthouse 90+
"""
import os
import sys
import json
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')

import django
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import GalleryImage, Artist
from io import BytesIO
from PIL import Image

def test_pwa_manifest():
    print("--- 1. Testing Manifest Endpoint (/manifest.json) ---")
    client = Client()
    resp = client.get('/manifest.json')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert 'application/manifest+json' in resp['Content-Type'], f"Wrong Content-Type: {resp['Content-Type']}"
    manifest = json.loads(resp.content.decode('utf-8'))
    assert 'name' in manifest, "Missing 'name' in manifest"
    assert manifest.get('start_url') == '/', "Invalid start_url"
    assert len(manifest.get('icons', [])) >= 2, "Missing PWA icons in manifest"
    print("[PASS] PWA Manifest verified:", manifest['name'], "Icons:", len(manifest['icons']))

def test_service_worker_endpoint():
    print("\n--- 2. Testing Service Worker Endpoint (/sw.js) ---")
    client = Client()
    resp = client.get('/sw.js')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert resp.get('Service-Worker-Allowed') == '/', f"Missing Service-Worker-Allowed header: {resp.headers}"
    content = resp.content.decode('utf-8')
    assert 'CACHE_NAME' in content, "Missing cache definition in sw.js"
    assert 'addEventListener' in content, "Missing event listeners in sw.js"
    assert '/offline/' in content, "Missing /offline/ fallback in sw.js"
    print("[PASS] Service Worker verified with root scope header (Service-Worker-Allowed: /)")

def test_offline_fallback():
    print("\n--- 3. Testing Offline Fallback Page (/offline/) ---")
    client = Client()
    resp = client.get('/offline/')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    content = resp.content.decode('utf-8')
    assert 'You Are Currently Offline' in content, "Missing offline headline"
    assert 'Retry Connection' in content, "Missing retry button"
    print("[PASS] Offline fallback page rendered successfully")

def test_base_metadata_and_schema():
    print("\n--- 4. Testing Base Metadata, PWA Tags, and JSON-LD ---")
    client = Client()
    resp = client.get('/')
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    
    # PWA & Apple tags
    assert '<link rel="manifest" href="/manifest.json">' in content, "Missing manifest link"
    assert 'apple-mobile-web-app-capable' in content, "Missing apple mobile capable meta"
    assert '<link rel="apple-touch-icon" href="/static/core/images/icons/icon-192.png">' in content, "Missing apple-touch-icon"
    
    # Hero preload & LCP
    assert 'rel="preload" as="image"' in content, "Missing hero preload"
    assert 'fetchpriority="high"' in content, "Missing fetchpriority=high on hero LCP image"
    assert 'id="hero-portrait-img"' in content, "Missing #hero-portrait-img"
    
    # Open Graph cover
    assert 'og:image' in content and 'og-cover.jpg' in content, "Missing og-cover.jpg in og:image"
    assert 'twitter:image' in content and 'og-cover.jpg' in content, "Missing og-cover.jpg in twitter:image"
    
    # JSON-LD Schema
    assert '+91-7879223442' in content, "Incorrect studio contact phone in JSON-LD"
    assert 'aggregateRating' in content, "Missing aggregateRating in JSON-LD"
    assert '"ratingValue": "4.98"' in content, "Missing ratingValue in JSON-LD"
    
    # Service worker registration
    assert 'navigator.serviceWorker.register(\'/sw.js\'' in content, "Missing service worker registration script"
    print("[PASS] Base HTML PWA meta, Open Graph, LCP preload, and Schema verified")

def test_breadcrumbs():
    print("\n--- 5. Testing BreadcrumbList JSON-LD on Gallery & Packages ---")
    client = Client()
    g_resp = client.get('/gallery/')
    assert g_resp.status_code == 200
    assert 'BreadcrumbList' in g_resp.content.decode('utf-8'), "Missing BreadcrumbList in /gallery/"
    
    p_resp = client.get('/packages/')
    assert p_resp.status_code == 200
    assert 'BreadcrumbList' in p_resp.content.decode('utf-8'), "Missing BreadcrumbList in /packages/"
    print("[PASS] BreadcrumbList Schema verified on Gallery & Packages pages")

def test_whitenoise_compression():
    print("\n--- 6. Testing WhiteNoise Compression (.gz assets) ---")
    gz_sw = os.path.join('staticfiles', 'sw.js.gz')
    assert os.path.exists(gz_sw), "staticfiles/sw.js.gz does not exist"
    print(f"[PASS] WhiteNoise compressed sw.js.gz verified ({os.path.getsize(gz_sw)} bytes)")

def test_webp_conversion_on_model_save():
    print("\n--- 7. Testing Gallery Image WebP Conversion On Save ---")
    img_io = BytesIO()
    test_img = Image.new('RGB', (200, 200), color=(200, 169, 106))
    test_img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    upload = SimpleUploadedFile("spec008_test_portrait.jpg", img_io.read(), content_type="image/jpeg")
    gallery_item = GalleryImage.objects.create(
        image=upload,
        caption="SPEC-008 WebP Test Item",
        category="bridal"
    )
    
    try:
        saved_name = gallery_item.image.name
        print(f"Saved Image Name: {saved_name}")
        assert saved_name.endswith('.webp'), f"Expected .webp extension, got {saved_name}"
        # Verify content is valid WebP
        gallery_item.image.file.seek(0)
        verified_img = Image.open(gallery_item.image.file)
        assert verified_img.format == 'WEBP', f"Expected WEBP format, got {verified_img.format}"
        print(f"[PASS] WebP conversion confirmed: format={verified_img.format}, size={verified_img.size}")
    finally:
        # Cleanup
        if gallery_item.image and os.path.exists(gallery_item.image.path):
            try:
                os.remove(gallery_item.image.path)
            except Exception:
                pass
        gallery_item.delete()

if __name__ == '__main__':
    print("==================================================")
    print("SPEC-008: PERFORMANCE, PWA & LIGHTHOUSE VALIDATION")
    print("==================================================")
    test_pwa_manifest()
    test_service_worker_endpoint()
    test_offline_fallback()
    test_base_metadata_and_schema()
    test_breadcrumbs()
    test_whitenoise_compression()
    test_webp_conversion_on_model_save()
    print("\n==================================================")
    print("[SUCCESS] ALL SPEC-008 ACCEPTANCE CHECKS PASSED EMPIRICALLY!")
    print("==================================================")
