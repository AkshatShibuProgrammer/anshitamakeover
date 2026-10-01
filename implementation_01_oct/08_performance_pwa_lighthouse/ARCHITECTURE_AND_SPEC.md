# Module 08: Performance, PWA & Lighthouse Score 90+

**Spec:** [SPEC-008](../../.specify/specs/SPEC-008-performance-pwa-lighthouse.md)  
**Plan:** [PLAN-008](../../.specify/plans/PLAN-008-performance-pwa-lighthouse.md)  
**Tasks:** [TASKS-008](../../.specify/tasks/TASKS-008-performance-pwa-lighthouse.md)  
**Status:** ⏳ Pending Execution  
**Inspired by:** Juan Mora (CDN speed) • Demilie (instant loads)

---

## What This Module Delivers

| Feature | Description |
| :--- | :--- |
| **PWA Manifest** | Add-to-home-screen capability with branded 512px icon and standalone display mode |
| **Service Worker** | Cache-first static assets, network-first HTML, offline fallback page |
| **JSON-LD Schema** | `BeautySalon` rich snippets with aggregateRating for Google Search appearance |
| **Open Graph / Twitter Card** | Rich social previews with 1200×630 branded image for all shared pages |
| **Image Optimisation** | WebP conversion, lazy loading, LCP hero `fetchpriority="high"` |
| **WhiteNoise Compressed** | Gzip+Brotli compressed static assets with content-hash filenames |
| **Lighthouse ≥ 90** | Performance, Accessibility, Best Practices, and SEO all ≥ 90 |

---

## Key Technical Decisions

1. **Service Worker scope**: registered at `/` with `Service-Worker-Allowed: /` header from Django
2. **WebP conversion**: Pillow `save()` override in Gallery model — no external microservice needed
3. **Cache busting**: Service worker cache key includes Django `STATIC_VERSION` env variable
4. **Schema ratings**: aggregateRating values pulled from actual Google My Business data (hardcoded initially, later dynamic via API)

---

## Files to Create / Modify

```
django/core/static/core/
├── manifest.json        ← PWA manifest (new)
├── sw.js                ← Service Worker (new)
└── images/
    ├── icons/
    │   ├── icon-192.png
    │   └── icon-512.png
    └── og-cover.jpg     ← Open Graph 1200×630 branded image

django/core/templates/core/
├── base.html            ← Manifest link, SW registration, JSON-LD, OG meta
└── offline.html         ← Offline fallback page (new)

anshita/gallery/models.py  ← WebP Pillow conversion override
anshita_project/settings.py ← WhiteNoise storage backend
```

---

## Lighthouse Score Targets

| Category | Current (est.) | Target |
| :--- | :--- | :--- |
| Performance | ~65 | ≥ 90 |
| Accessibility | ~78 | ≥ 90 |
| Best Practices | ~83 | ≥ 90 |
| SEO | ~72 | ≥ 95 |

---

## Acceptance Test Checklist

- [ ] Chrome DevTools Manifest tab shows correctly parsed PWA manifest
- [ ] Service Worker active in DevTools > Application > Service Workers
- [ ] Offline mode shows branded offline fallback page
- [ ] Google Rich Results Test shows `BeautySalon` schema with star rating
- [ ] Facebook URL Debugger shows correct OG image and title
- [ ] Lighthouse Performance ≥ 90 in desktop audit
- [ ] `python manage.py check --deploy` → 0 issues
