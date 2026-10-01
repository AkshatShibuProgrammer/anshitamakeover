# TASKS-008: Performance, PWA & Lighthouse 90+

**Spec:** SPEC-008 | **Plan:** PLAN-008  
**Status:** Pending Execution  
**Total Tasks:** 7

---

## Task Checklist

### TSK-008.01 — PWA Manifest & Icons
- [ ] Create `django/core/static/core/manifest.json` with name, start_url, display, theme_color, icons.
- [ ] Generate `icon-192.png` and `icon-512.png` from the Anshita logo (use PIL or pre-export).
- [ ] Add `<link rel="manifest" href="/static/core/manifest.json">` to `base.html` `<head>`.
- [ ] Add Apple PWA meta tags: `apple-mobile-web-app-capable`, `apple-mobile-web-app-title`, `apple-touch-icon`.
- **Acceptance Check:** Chrome DevTools > Application > Manifest shows correctly parsed manifest.

### TSK-008.02 — Service Worker (Cache-First Static)
- [ ] Create `django/core/static/sw.js` with install/fetch handlers.
- [ ] Cache all CSS, JS, fonts, and icons on install.
- [ ] Network-first for HTML responses; cache-first for `/static/`.
- [ ] Create `django/core/templates/core/offline.html` as offline fallback.
- [ ] Register service worker in `base.html`: `navigator.serviceWorker.register('/static/sw.js')`.
- [ ] Serve `sw.js` with correct headers: `Service-Worker-Allowed: /`.
- **Acceptance Check:** DevTools > Application > Service Workers shows active SW; offline page loads when disconnected.

### TSK-008.03 — JSON-LD Schema & Open Graph Meta
- [ ] Add `BeautySalon` JSON-LD block in `base.html` `<head>` with aggregateRating.
- [ ] Add `BreadcrumbList` JSON-LD in gallery and booking page templates.
- [ ] Add `og:title`, `og:description`, `og:image` (1200×630px branded image), `og:url`, `og:type` meta tags.
- [ ] Add Twitter Card `summary_large_image` tags.
- [ ] Create `og-cover.jpg` (1200×630px) in `static/core/images/`.
- **Acceptance Check:** Paste URL in https://developers.facebook.com/tools/debug/ — preview shows correct image + title.

### TSK-008.04 — Image Lazy Loading & LCP Optimisation
- [ ] Add `loading="lazy"` to all `<img>` tags in gallery templates and home.html (except hero portrait).
- [ ] Add `fetchpriority="high"` to the hero LCP image (`#hero-portrait-img`).
- [ ] Add preload link for hero image: `<link rel="preload" as="image" href="...">` in `<head>`.
- [ ] Convert gallery thumbnail display to WebP `<picture>` srcset with JPG fallback.
- **Acceptance Check:** Lighthouse LCP < 2.5s in DevTools audit.

### TSK-008.05 — WhiteNoise Compressed Manifest Storage
- [ ] Update `settings.py`: `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`.
- [ ] Run `python manage.py collectstatic --noinput` — verify no errors.
- [ ] Run `python manage.py check --deploy` — resolve all warnings.
- [ ] Verify `.gz` files created alongside static assets in `staticfiles/`.
- **Acceptance Check:** `collectstatic` completes, `check --deploy` returns 0 issues.

### TSK-008.06 — Gallery Model WebP Conversion
- [ ] In `anshita/gallery/models.py`, override `save()` to convert uploaded images to WebP using Pillow.
- [ ] Keep original filename, replace extension with `.webp`.
- [ ] Quality setting: 85 (balance quality vs. size).
- [ ] Add `Pillow>=10.0` to `requirements.txt`.
- **Acceptance Check:** Uploaded gallery photo saved as `.webp` with ~50–70% size reduction.

### TSK-008.07 — Lighthouse Audit & Fix
- [ ] Run Lighthouse CI in Chrome DevTools for home page, gallery page, and booking page.
- [ ] Fix any Accessibility issues: `alt` text, ARIA labels, colour contrast.
- [ ] Fix any Best Practices issues: deprecated APIs, console errors.
- [ ] Fix any SEO issues: missing meta descriptions, robots.txt.
- [ ] Target scores: Performance ≥ 90, Accessibility ≥ 90, Best Practices ≥ 90, SEO ≥ 95.
- [ ] Save Lighthouse report as `testing/reports/lighthouse_report.html`.
- **Acceptance Check:** All 4 Lighthouse categories ≥ 90.
