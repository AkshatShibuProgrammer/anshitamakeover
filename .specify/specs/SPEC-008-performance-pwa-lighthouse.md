# SPEC-008: Performance Optimisation, PWA & Lighthouse Score 90+

**Status:** Active  
**Milestone:** Production-Ready Launch  
**Constitutions:** `.specify/memory/constitution.md`  
**Inspired by:** Juan Mora (ultra-fast CDN delivery), Demilie (instant page loads)

---

## 1. Overview & Objective

Achieve **Lighthouse scores ≥ 90** across Performance, Accessibility, Best Practices, and SEO. Implement **Progressive Web App (PWA)** capabilities for mobile add-to-home-screen, **WhiteNoise** static asset compression, and **Cloudflare edge caching** headers — making Anshita Makeover load in under 1.5 seconds globally.

---

## 2. User Stories & Acceptance Criteria

### 2.1 Story: Lighthouse Score Baseline & Optimisation
* **As the studio owner**, I want the website to score ≥ 90 on all Lighthouse categories so we rank highly on Google and convert mobile visitors faster.
* **Acceptance Criteria:**
  - [ ] Lighthouse Performance ≥ 90 (LCP < 2.5s, FID < 100ms, CLS < 0.1).
  - [ ] Lighthouse Accessibility ≥ 90 (all images have `alt`, ARIA labels, colour contrast ≥ 4.5:1).
  - [ ] Lighthouse Best Practices ≥ 90.
  - [ ] Lighthouse SEO ≥ 95.
  - [ ] Run: `python manage.py check --deploy` — zero warnings.

### 2.2 Story: Image Optimisation Pipeline
* **As a developer**, I want all hero and gallery images to be served as compressed WebP format with lazy loading so page load time is minimised on slow mobile connections.
* **Acceptance Criteria:**
  - [ ] All `<img>` tags have `loading="lazy"` (except LCP hero image).
  - [ ] Hero LCP image has `fetchpriority="high"` and `preload` link in `<head>`.
  - [ ] Gallery images served as WebP (convert with Pillow in Django `save()` override).
  - [ ] WhiteNoise `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'` active.

### 2.3 Story: Progressive Web App (PWA) Manifest
* **As a mobile bride**, I want to add Anshita Makeover to my home screen and access it like a native app with a branded icon and splash screen.
* **Acceptance Criteria:**
  - [ ] `manifest.json` created with `name`, `short_name`, `start_url`, `display: standalone`, `theme_color: #060606`, `background_color: #060606`.
  - [ ] 512×512, 192×192, and 180×180 favicon/icon set (PNG + WebP).
  - [ ] Service Worker registered (`sw.js`) caching static assets and offline fallback page.
  - [ ] `<link rel="manifest">` in `<head>` of `base.html`.
  - [ ] iOS-compatible `<meta name="apple-mobile-web-app-capable" content="yes">` tags.

### 2.4 Story: Cloudflare Edge Caching Headers
* **As a developer**, I want all static assets served with aggressive Cloudflare cache headers so repeat visitors see zero-latency loads.
* **Acceptance Criteria:**
  - [ ] Static files (`/static/`) respond with `Cache-Control: public, max-age=31536000, immutable`.
  - [ ] HTML responses: `Cache-Control: no-cache, must-revalidate` (dynamic Django content).
  - [ ] Cloudflare Page Rule: `*.anshita.in/static/*` → Cache Level: Cache Everything, Edge TTL: 1 month.

### 2.5 Story: Structured Data & Open Graph
* **As the studio**, I want Google to display rich search results (star rating, price range, location) and beautiful social media preview cards for every shared page.
* **Acceptance Criteria:**
  - [ ] `LocalBusiness` JSON-LD schema injected in `<head>` for every page (name, address, phone, openingHours, priceRange, aggregateRating).
  - [ ] `BreadcrumbList` JSON-LD on gallery and blog pages.
  - [ ] `og:image` (1200×630px), `og:title`, `og:description` for every URL.
  - [ ] Twitter Card `summary_large_image` meta tags.

---

## 3. Technical Constraints

- Django `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True` in production.
- `DEBUG = False` must be enforced in production via environment variable.
- `ALLOWED_HOSTS` must include both `www.` and apex domain.
- Service worker cache versioning must bust on each deployment (append build hash).
