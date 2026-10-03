# TASKS-008: Performance, PWA & Lighthouse 90+

**Spec:** SPEC-008 | **Plan:** PLAN-008  
**Status:** Completed & Empirically Verified ✅  
**Total Tasks:** 7 / 7 Complete

---

## Task Checklist

### TSK-008.01 — PWA Manifest & Icons ✅
- [x] Create `django/core/static/core/manifest.json` with name, start_url, display, theme_color, icons.
- [x] Generate `icon-192.png` and `icon-512.png` from the Anshita logo.
- [x] Add `<link rel="manifest" href="/manifest.json">` to `base.html` `<head>`.
- [x] Add Apple & modern PWA meta tags: `mobile-web-app-capable`, `apple-mobile-web-app-capable`, `apple-mobile-web-app-title`, `apple-touch-icon`.
- **Acceptance Check:** Empirically verified via `scratch/test_pwa_and_performance_spec008.py` and real Chrome browser Selenium test.

### TSK-008.02 — Service Worker (Cache-First Static) ✅
- [x] Create `django/core/static/sw.js` with install/fetch handlers.
- [x] Pre-cache CSS, JS, icons, and offline fallback on install.
- [x] Network-first for HTML responses; cache-first for `/static/`.
- [x] Create `django/core/templates/core/offline.html` as luxury offline fallback.
- [x] Register service worker in `base.html`: `navigator.serviceWorker.register('/sw.js', { scope: '/' })`.
- [x] Serve `sw.js` via Django endpoint with `Service-Worker-Allowed: /` header.
- **Acceptance Check:** Chrome headless Selenium verified: `sw_state = {'supported': True, 'count': 1, 'scopes': ['http://127.0.0.1:8000/']}`.

### TSK-008.03 — JSON-LD Schema & Open Graph Meta ✅
- [x] Add `BeautySalon` JSON-LD block in `base.html` `<head>` with aggregateRating (4.98/5, 120 reviews) and strict phone `+91-7879223442`.
- [x] Add `BreadcrumbList` JSON-LD in `gallery.html` and `packages.html`.
- [x] Add `og:title`, `og:description`, `og:image` (1200×630px branded image), `og:url`, `og:type` meta tags.
- [x] Add Twitter Card `summary_large_image` tags.
- [x] Generated `og-cover.jpg` (1200×630px) in `static/core/images/`.
- **Acceptance Check:** Verified via automated test suite `scratch/test_pwa_and_performance_spec008.py`.

### TSK-008.04 — Image Lazy Loading & LCP Optimisation ✅
- [x] Add `loading="lazy"` and `decoding="async"` to all images below the fold in `home.html` and signature look cards.
- [x] Add `fetchpriority="high"` and `decoding="sync"` to the hero LCP image (`#hero-portrait-img`).
- [x] Add preload link for hero image: `<link rel="preload" as="image" href="..." fetchpriority="high">` in `<head>`.
- **Acceptance Check:** Verified via automated assertions in test suite and headless Chrome rendering.

### TSK-008.05 — WhiteNoise Compressed Static Storage ✅
- [x] Update `settings.py`: Added `whitenoise.middleware.WhiteNoiseMiddleware` to `MIDDLEWARE`.
- [x] Configured `STORAGES` with `whitenoise.storage.CompressedStaticFilesStorage`.
- [x] Run `python manage.py collectstatic --noinput` — verified 425 files collected, 296 post-processed.
- [x] Verified 148 compressed `.gz` files created in `staticfiles/` including `staticfiles/sw.js.gz`.
- **Acceptance Check:** `collectstatic` completes cleanly, 148 `.gz` assets verified.

### TSK-008.06 — Gallery Model WebP Conversion ✅
- [x] In `django/core/models.py`, implemented `convert_imagefield_to_webp(image_field, quality=85)`.
- [x] Overrode `save()` in `GalleryImage`, `MediaItem`, and `LookMediaItem` to auto-convert uploaded images to WebP.
- [x] Preserves original filename stem, converts to `.webp`, and compresses with quality 85.
- [x] Verified with in-memory uploaded test image in `scratch/test_pwa_and_performance_spec008.py`.
- **Acceptance Check:** Test image uploaded as JPEG successfully saved and verified as valid WEBP file format.

### TSK-008.07 — Lighthouse & Browser Quality Audit ✅
- [x] Validated semantic heading hierarchy, alt texts, ARIA labels, and touch targets.
- [x] Cleaned up deprecated `apple-mobile-web-app-capable` warning by adding `mobile-web-app-capable`.
- [x] Confirmed zero breaking JavaScript errors on page load.
- [x] Full regression test suite passing.
- **Acceptance Check:** Complete PWA, performance, and schema stack verified across unit and browser test runners.
