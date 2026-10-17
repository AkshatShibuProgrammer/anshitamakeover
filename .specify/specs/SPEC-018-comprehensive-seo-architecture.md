# Feature Specification: Comprehensive Luxury SEO, Structured Schema & Crawlability Framework

**Feature Branch:** `arena/01a105d6-anshitamakeover`  
**Spec ID:** `SPEC-018`  
**Governing Documents:** `.specify/memory/constitution.md`, `.specify/memory/constitution-high-conversion-seo.md`  
**Status:** In Review & Planning  
**Estimated Complexity:** Medium (Django Meta Tag Inheritance, Schema.org JSON-LD Generation, Dynamic Sitemap Framework, Robots.txt)

---

## 1. Executive Summary & Problem Description

### 1.1 Problem Statement
An SEO audit of the current Anshita Makeover platform revealed critical deficiencies that impair organic discovery, social preview quality, and local search rankings:
1. **Missing or Generic Meta Descriptions**: Primary routes (`/`, `/services/`, `/gallery/`, `/academy/`) lack explicit, keyword-rich `<meta name="description">` tags. Search engines generate arbitrary snippet text from navigation and preloader code.
2. **Missing Open Graph & Social Card Metadata**: Links shared on WhatsApp, Instagram, Facebook, and Twitter lack proper rich preview cards (`og:image`, `og:title`, `og:description`), undermining luxury credibility when clients share bridal looks.
3. **Absence of Canonical Tagging**: Routes can be accessed via varying query strings or URL variations without `<link rel="canonical">`, risking duplicate content penalties.
4. **Lack of Structured Data (Schema.org JSON-LD)**: The site lacks machine-readable schemas (`BeautySalon`, `LocalBusiness`, `BreadcrumbList`, `AggregateRating`, `Service`). Search engines cannot extract price ranges, operating hours, ratings, or geographical coordinates for Google Maps and rich snippets.
5. **No Dynamic XML Sitemap or Robots Directives**: Search crawlers lack a canonical sitemap index (`/sitemap.xml`) and crawl guidance (`/robots.txt`).

### 1.2 Core Objectives
- **Dynamic Meta Tag Inheritance**: Refactor `base.html` to declare overridable template blocks for `meta_title`, `meta_description`, `canonical_url`, and `og_tags`.
- **Bespoke Per-Page SEO**: Implement targeted titles, descriptions, and keywords across all core views (Home, Services, Gallery, Academy, Packages).
- **JSON-LD Schema Engine**: Implement complete `BeautySalon` and `LocalBusiness` schema with verified geo-coordinates (Jhansi, Bundelkhand), opening hours, price range, and review aggregation.
- **Dynamic Sitemap & Robots Generator**: Configure Django sitemap framework or endpoint serving auto-updating `/sitemap.xml` and `/robots.txt`.
- **Pan-India & Regional Geo-Targeting**: Optimize content for bridal inquiries in Jhansi, Gwalior, Kanpur, Lucknow, and destination/outstation weddings.

---

## 2. Technical Architecture & Implementation Blueprint

### 2.1 Template Inheritance Structure in `base.html`
```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  
  <!-- Primary SEO Tags -->
  <title>{% block meta_title %}Anshita Makeover | Luxury Bridal Makeup Studio & Academy Jhansi{% endblock %}</title>
  <meta name="description" content="{% block meta_description %}Experience world-class luxury bridal makeup, HD airbrush artistry, and certified beauty masterclasses by Anshita Sinha in Jhansi, Bundelkhand & Pan-India.{% endblock %}">
  <link rel="canonical" href="{% block canonical_url %}https://anshitamakeover.com{{ request.path }}{% endblock %}">

  <!-- Open Graph / WhatsApp / Facebook -->
  <meta property="og:type" content="{% block og_type %}business.business{% endblock %}">
  <meta property="og:site_name" content="Anshita Makeover Haute Couture">
  <meta property="og:title" content="{% block og_title %}{{ block.super }}{% endblock %}">
  <meta property="og:description" content="{% block og_description %}{{ block.super }}{% endblock %}">
  <meta property="og:url" content="https://anshitamakeover.com{{ request.path }}">
  <meta property="og:image" content="{% block og_image %}https://anshitamakeover.com/static/core/images/brand/og_luxury_bridal.jpg{% endblock %}">
  <meta property="og:locale" content="en_IN">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{% block twitter_title %}{{ block.super }}{% endblock %}">
  <meta name="twitter:description" content="{% block twitter_description %}{{ block.super }}{% endblock %}">
  <meta name="twitter:image" content="{% block twitter_image %}{{ block.super }}{% endblock %}">

  <!-- JSON-LD Structured Data Block -->
  {% block structured_data %}
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BeautySalon",
    "name": "Anshita Makeover",
    "alternateName": "Anshita Makeover Luxury Bridal Studio & Academy",
    "image": "https://anshitamakeover.com/static/core/images/brand/logo_crest.png",
    "@id": "https://anshitamakeover.com/#beautysalon",
    "url": "https://anshitamakeover.com/",
    "telephone": "+91-95594-55444",
    "priceRange": "₹₹₹₹",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Civil Lines",
      "addressLocality": "Jhansi",
      "addressRegion": "Uttar Pradesh",
      "postalCode": "284001",
      "addressCountry": "IN"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 25.4484,
      "longitude": 78.5685
    },
    "openingHoursSpecification": [
      {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "10:00",
        "closes": "20:00"
      }
    ],
    "sameAs": [
      "https://www.instagram.com/anshitamakeover/",
      "https://facebook.com/anshitamakeover"
    ]
  }
  </script>
  {% endblock %}
</head>
```

### 2.2 Per-Page Metadata Specifications
| Route | Meta Title | Meta Description | Target Keywords |
|---|---|---|---|
| `/` (Home) | Anshita Makeover \| Luxury Bridal Makeup Studio & Academy Jhansi | Book Jhansi's leading luxury bridal makeup artist. 18-hr cry-proof HD airbrush, royal jewellery styling, and destination wedding bridal packages. | luxury bridal makeup jhansi, wedding makeup artist jhansi, anshita makeover, bridal studio bundelkhand |
| `/services/` | Bridal & Beauty Services \| HD Airbrush & Reception Makeup \| Anshita Makeover | Explore bespoke bridal makeup services: Royal Bridal Couture, HD Airbrush, Reception Glamour, Mehendi, Cocktail & Pre-Wedding looks. | bridal services jhansi, airbrush makeup packages, party makeup jhansi |
| `/gallery/` | Authentic Bridal Lookbook & Portfolio \| Anshita Makeover | View 100+ real brides styled by Anshita Sinha. HD transformation reels, Banarasi drape artistry, and authentic client testimonials. | bridal makeover photos, real brides jhansi, makeup artist portfolio jhansi |
| `/academy/` | Professional Makeup Academy & Bridal Masterclass \| Anshita Makeover | Learn from celebrity makeup artist Anshita Sinha. Certified professional bridal courses, airbrush masterclasses, and hands-on bridal training in Jhansi. | makeup academy jhansi, beauty courses bundelkhand, learn bridal makeup jhansi |
| `/packages/` | Luxury Bridal Packages & Pricing \| Anshita Makeover | Transparent luxury bridal packages with customized bride-and-family suites. Special privilege bookings and destination wedding options. | bridal makeup price jhansi, wedding makeover packages, bridal booking |

### 2.3 Dynamic Sitemap & Robots Configuration
1. **`django/core/sitemaps.py`**:
   - Class `StaticViewSitemap(Sitemap)` with `priority = 0.8-1.0` and `changefreq = 'weekly'`.
   - Items: `['home', 'services', 'gallery', 'academy', 'packages', 'contact']`.
2. **`django/anshita_project/urls.py`**:
   - Route `path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')`.
   - Route `path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'))`.
3. **`django/core/templates/robots.txt`**:
   ```
   User-agent: *
   Allow: /
   Disallow: /admin/
   Disallow: /api/internal/

   Sitemap: https://anshitamakeover.com/sitemap.xml
   ```

---

## 3. Acceptance & Verification Criteria

- [ ] **AC-18.1**: Every page template renders valid `<title>`, `<meta name="description">`, and `<link rel="canonical">` without empty string fallbacks.
- [ ] **AC-18.2**: Open Graph inspector (or curl test) confirms valid `og:title`, `og:image`, `og:description`, and `og:url` on all primary routes.
- [ ] **AC-18.3**: Structured data test (Google Rich Results test syntax) validates JSON-LD without syntax errors or missing required fields.
- [ ] **AC-18.4**: Navigating to `http://127.0.0.1:8000/sitemap.xml` returns well-formed XML with HTTP 200 and all public endpoints listed.
- [ ] **AC-18.5**: Navigating to `http://127.0.0.1:8000/robots.txt` returns text/plain with Sitemap directive.
- [ ] **AC-18.6**: Meta descriptions adhere to the 150-160 character limit.
