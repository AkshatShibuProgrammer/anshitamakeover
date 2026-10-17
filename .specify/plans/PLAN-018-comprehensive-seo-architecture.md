# Technical Plan: Comprehensive Luxury SEO, Structured Schema & Crawlability Framework

**Spec ID Reference:** `SPEC-018`  
**Parent Constitution:** `.specify/memory/constitution-high-conversion-seo.md`  
**Target Files:**
- `django/core/templates/core/base.html`
- `django/core/templates/core/home.html`
- `django/core/templates/core/services.html`
- `django/core/templates/core/gallery.html`
- `django/core/templates/core/academy.html`
- `django/core/sitemaps.py` (new)
- `django/core/templates/robots.txt` (new)
- `django/anshita_project/urls.py`
**Status:** Ready for Task Breakdown  

---

## 1. Architecture & Component Blueprint

```
                     [Search Engine Crawler / Visitor]
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        GET /sitemap.xml                         GET /robots.txt
                 │                                       │
      [StaticViewSitemap]                    [Robots TemplateView]
      - / (priority: 1.0)                    - Allow: /
      - /services/ (0.9)                     - Disallow: /admin/
      - /gallery/ (0.8)                      - Sitemap: https://...
      - /packages/ (0.9)
      - /academy/ (0.8)
                 │
                 ▼
        GET https://anshitamakeover.com/
                 │
                 ▼
       [base.html Master Shell]
        ├── Overridable <title> Block
        ├── Overridable <meta name="description"> Block
        ├── Overridable <link rel="canonical"> Block
        ├── Overridable Open Graph & Twitter Cards Block
        └── Overridable JSON-LD Structured Data Block
                 │
        ┌────────┴────────────────────────────────────────┐
        ▼                                                 ▼
[home.html Child Template]                      [services.html Child Template]
- Unique Jhansi Bridal Title                    - Unique HD Airbrush Title
- 158-char Curated Meta Description             - 155-char Services Meta
- Canonical https://.../                        - Canonical https://.../services/
- BeautySalon JSON-LD                           - Service / OfferCatalog JSON-LD
```

---

## 2. File-by-File Implementation Details

### 2.1 Refactor `<head>` in `django/core/templates/core/base.html`
Declare clean inheritance blocks in `base.html`:
```html
<title>{% block meta_title %}Anshita Makeover | Luxury Bridal Makeup Studio & Academy Jhansi{% endblock %}</title>
<meta name="description" content="{% block meta_description %}Experience world-class luxury bridal makeup, 18-hour cry-proof HD airbrush artistry, and certified beauty masterclasses by Anshita Sinha in Jhansi, Bundelkhand & Pan-India.{% endblock %}">
<meta name="keywords" content="{% block meta_keywords %}luxury bridal makeup jhansi, wedding makeup artist jhansi, anshita makeover, bridal studio bundelkhand, airbrush makeup jhansi{% endblock %}">
<link rel="canonical" href="{% block canonical_url %}{{ request.build_absolute_uri }}{% endblock %}">

<!-- Open Graph / WhatsApp Sharing -->
{% block og_tags %}
<meta property="og:type" content="business.business">
<meta property="og:site_name" content="Anshita Makeover">
<meta property="og:title" content="Anshita Makeover | Luxury Bridal Studio & Academy Jhansi">
<meta property="og:description" content="18-hour cry-proof bridal makeup, HD airbrush artistry, and royal bridal couture transformations.">
<meta property="og:image" content="{% static 'core/images/brand/og_luxury_bridal.jpg' %}">
<meta property="og:url" content="{{ request.build_absolute_uri }}">
<meta property="og:locale" content="en_IN">
{% endblock %}

<!-- Structured Data Block -->
{% block structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BeautySalon",
  "name": "Anshita Makeover",
  "image": "https://anshitamakeover.com/static/core/images/brand/anshita_crest.svg",
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
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "520"
  }
}
</script>
{% endblock %}
```

### 2.2 Template Overrides in Child Views
1. **`home.html`**:
   ```django
   {% block meta_title %}Anshita Makeover | Premier Luxury Bridal Makeup Studio & Academy Jhansi{% endblock %}
   {% block meta_description %}Book Jhansi's leading luxury bridal makeup artist Anshita Sinha. 18-hr cry-proof HD airbrush, royal jewellery styling, and destination wedding bridal suites.{% endblock %}
   ```
2. **`services.html`**:
   ```django
   {% block meta_title %}Bridal Makeup Services & HD Airbrush Pricing | Anshita Makeover Jhansi{% endblock %}
   {% block meta_description %}Discover couture bridal makeup packages: Royal Bride, HD Airbrush, Reception Glamour, Mehendi, and Pre-Wedding shoots by celebrity artist Anshita Sinha.{% endblock %}
   ```
3. **`gallery.html`**:
   ```django
   {% block meta_title %}Authentic Bridal Lookbook & Transformation Portfolio | Anshita Makeover{% endblock %}
   {% block meta_description %}Explore 100+ authentic bridal looks styled by Anshita Sinha. Banarasi drape artistry, high-definition bridal transformations, and verified client testimonials.{% endblock %}
   ```
4. **`academy.html`**:
   ```django
   {% block meta_title %}Certified Bridal Makeup Academy & Masterclasses | Anshita Makeover Jhansi{% endblock %}
   {% block meta_description %}Launch your professional beauty career with hands-on bridal makeup masterclasses, airbrush certifications, and portfolio building in Jhansi with Anshita Sinha.{% endblock %}
   ```

### 2.3 Creation of `django/core/sitemaps.py`
```python
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority_dict = {
        'core:home': 1.0,
        'core:services': 0.9,
        'core:packages': 0.9,
        'core:gallery': 0.8,
        'core:academy': 0.8,
        'core:contact': 0.7,
    }
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:services', 'core:packages', 'core:gallery', 'core:academy', 'core:contact']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.priority_dict.get(item, 0.5)
```

### 2.4 Registration in `django/anshita_project/urls.py`
```python
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from core.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]
```

---

## 3. Verification & Validation Steps

1. **Django URL & View Integrity**:
   ```bash
   python manage.py check
   ```
2. **Sitemap XML Validation**:
   - Query `http://127.0.0.1:8000/sitemap.xml`.
   - Verify XML declaration, root `<urlset>`, and presence of all 6 primary routes with HTTP 200.
3. **Robots.txt Validation**:
   - Query `http://127.0.0.1:8000/robots.txt`.
   - Confirm `Content-Type: text/plain` and valid `Sitemap:` directive pointing to the absolute sitemap URL.
4. **Metadata Extraction Test**:
   - Inspect `<head>` of `/`, `/services/`, `/gallery/`, and `/academy/`.
   - Verify no duplicate tags and unique content descriptions in each.
