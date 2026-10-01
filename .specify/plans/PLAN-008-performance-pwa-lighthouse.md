# PLAN-008: Performance, PWA & Lighthouse 90+ — Technical Blueprint

**Spec:** [SPEC-008](../specs/SPEC-008-performance-pwa-lighthouse.md)  
**Status:** Active  
**Estimated Effort:** 3–4 hours

---

## 1. Files to Touch

| File | Change |
| :--- | :--- |
| `django/core/templates/core/base.html` | PWA manifest link, service worker registration, Open Graph meta, JSON-LD schema |
| `django/core/static/sw.js` | Service Worker (new file) |
| `django/core/static/manifest.json` | PWA Manifest (new file) |
| `django/core/templates/core/home.html` | `fetchpriority="high"` on LCP image, `loading="lazy"` on all others |
| `anshita_project/settings.py` | WhiteNoise `CompressedManifestStaticFilesStorage` |
| `anshita_project/settings_production.py` | Security headers, HTTPS redirect |
| `django/core/models.py` | Pillow WebP conversion in `save()` override |

---

## 2. Architecture

### 2.1 PWA Manifest (`manifest.json`)

```json
{
  "name": "Anshita Makeover Studio",
  "short_name": "Anshita",
  "description": "Luxury Bridal Makeover Studio — Pan India",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait",
  "theme_color": "#060606",
  "background_color": "#060606",
  "icons": [
    { "src": "/static/core/images/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/static/core/images/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### 2.2 Service Worker Strategy

- **Cache-first** for all `/static/` assets (versioned by build hash).
- **Network-first** for `/api/` and Django HTML responses.
- **Offline fallback** page: `/offline.html`.

```javascript
// sw.js
const CACHE_VERSION = 'v{{ BUILD_HASH }}';
const STATIC_ASSETS = ['/static/core/css/style.css', '/static/core/js/main.js', ...];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE_VERSION).then(c => c.addAll(STATIC_ASSETS))));
self.addEventListener('fetch', e => {
  if (e.request.url.includes('/static/')) {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
  }
});
```

### 2.3 JSON-LD LocalBusiness Schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BeautySalon",
  "name": "Anshita Makeover Studio",
  "address": { "@type": "PostalAddress", "addressLocality": "Nagpur", "addressRegion": "Maharashtra", "addressCountry": "IN" },
  "telephone": "+91XXXXXXXXXX",
  "url": "https://www.anshita.in",
  "priceRange": "₹₹₹",
  "openingHours": "Mo-Su 09:00-20:00",
  "aggregateRating": { "@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": "312" },
  "sameAs": ["https://www.instagram.com/anshitamakeover/"]
}
</script>
```

### 2.4 WhiteNoise Configuration

```python
# settings.py
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # After SecurityMiddleware
    ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 3. Phase Sequence

| Phase | Task | Duration |
| :--- | :--- | :--- |
| P8.1 | PWA manifest.json + icons (192/512px) + base.html link | 30 min |
| P8.2 | Service Worker (sw.js) + registration script | 45 min |
| P8.3 | JSON-LD LocalBusiness schema + Open Graph tags | 30 min |
| P8.4 | Image lazy loading + LCP hero `fetchpriority` | 20 min |
| P8.5 | WhiteNoise CompressedManifest + `check --deploy` | 30 min |
| P8.6 | Pillow WebP conversion in Gallery model | 45 min |
| P8.7 | Lighthouse CI audit + fix remaining issues | 60 min |
