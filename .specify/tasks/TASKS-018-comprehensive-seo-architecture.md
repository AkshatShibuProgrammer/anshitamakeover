# Granular Implementation Tasks: Comprehensive Luxury SEO, Structured Schema & Crawlability Framework

**Feature:** Comprehensive Luxury SEO, Structured Schema & Crawlability Framework  
**Plan Reference:** [PLAN-018](file:///.specify/plans/PLAN-018-comprehensive-seo-architecture.md)  
**Spec Reference:** [SPEC-018](file:///.specify/specs/SPEC-018-comprehensive-seo-architecture.md)  
**Parent Constitution:** [constitution-high-conversion-seo.md](file:///.specify/memory/constitution-high-conversion-seo.md)  
**Status:** Ready for Implementation  

---

## Task Matrix & Dependencies

| Task ID | Component | Description | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **TSK-18-01** | Base Template | Add overridable `<title>`, `<meta name="description">`, canonical, and OG blocks in `base.html` | `[DONE]` | None |
| **TSK-18-02** | Base Template | Implement complete `BeautySalon` / `LocalBusiness` JSON-LD schema block in `base.html` | `[DONE]` | TSK-18-01 |
| **TSK-18-03** | Template Overrides | Add tailored title, meta description, and keywords in `home.html` | `[DONE]` | TSK-18-01 |
| **TSK-18-04** | Template Overrides | Add tailored metadata and service schema in `services.html` | `[DONE]` | TSK-18-01 |
| **TSK-18-05** | Template Overrides | Add tailored metadata in `gallery.html` and `academy.html` | `[DONE]` | TSK-18-01 |
| **TSK-18-06** | Sitemap Engine | Create `django/core/sitemaps.py` with `StaticViewSitemap` covering all primary routes | `[DONE]` | None |
| **TSK-18-07** | Crawl Directives | Create `django/core/templates/robots.txt` and register `/sitemap.xml` & `/robots.txt` in `urls.py` | `[DONE]` | TSK-18-06 |
| **TSK-18-08** | Verification | Verify sitemap XML syntax, robots.txt response, and Google Rich Results Schema compliance | `[DONE]` | TSK-18-01 to TSK-18-07 |

---

## Detailed Task Specifications

### TSK-18-01 & TSK-18-02: Base Master Shell Meta & Structured Data
- File: `django/core/templates/core/base.html`
- Insert blocks:
  - `{% block meta_title %}...{% endblock %}`
  - `{% block meta_description %}...{% endblock %}`
  - `{% block canonical_url %}...{% endblock %}`
  - `{% block og_tags %}...{% endblock %}`
  - `{% block structured_data %}...{% endblock %}`
- Render valid JSON-LD schema with name, address, telephone, price range, geo-coordinates, and aggregated rating.

### TSK-18-03 to TSK-18-05: Child View Metadata Customization
- Files: `django/core/templates/core/home.html`, `services.html`, `gallery.html`, `academy.html`
- Override `meta_title` and `meta_description` in each template with exact 150-160 character descriptions focusing on Jhansi, Bundelkhand, and luxury bridal services.

### TSK-18-06: Create Django Sitemap Class
- File: `django/core/sitemaps.py`
- Inherit `from django.contrib.sitemaps import Sitemap`.
- Register routes: `core:home` (1.0), `core:services` (0.9), `core:packages` (0.9), `core:gallery` (0.8), `core:academy` (0.8).

### TSK-18-07: Robots.txt & URL Registration
- File: `django/core/templates/robots.txt`
  - Allow `/`, disallow `/admin/` and `/api/internal/`, reference absolute sitemap URL.
- File: `django/anshita_project/urls.py`
  - Wire `path('sitemap.xml', ...)` and `path('robots.txt', ...)`.

### TSK-18-08: Automated & Crawlability Verification
- Run `python manage.py check`.
- Curl `http://127.0.0.1:8000/sitemap.xml` and verify HTTP 200 with XML tags.
- Curl `http://127.0.0.1:8000/robots.txt` and verify text output.
- Validate JSON-LD syntax using schema validator.
