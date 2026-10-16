# Granular Implementation Tasks: Website Simplification, Modular Page Architecture & High-Conversion Funnel

**Feature:** Website Simplification, Modular Page Architecture & High-Conversion Funnel  
**Plan Reference:** [PLAN-019](file:///.specify/plans/PLAN-019-website-simplification-and-modular-pages.md)  
**Spec Reference:** [SPEC-019](file:///.specify/specs/SPEC-019-website-simplification-and-modular-pages.md)  
**Parent Constitution:** [constitution-high-conversion-seo.md](file:///.specify/memory/constitution-high-conversion-seo.md)  
**Status:** Ready for Implementation  

---

## Task Matrix & Dependencies

| Task ID | Component | Description | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **TSK-19-01** | Navigation | Refactor `components/header_nav.html` into a streamlined luxury navbar with 5 links and gold WhatsApp CTA | `[DONE]` | None |
| **TSK-19-02** | Hero Section | Extract and simplify `hero_showcase.html` with singular primary CTA and Three.js softbox lighting | `[DONE]` | None |
| **TSK-19-03** | Footer | Clean up and standardize `components/footer.html` with Sinha crest and location links | `[DONE]` | None |
| **TSK-19-04** | Dedicated Route | Create dedicated `/packages/` view & template `packages.html` displaying clear luxury tiers | `[DONE]` | TSK-19-01 |
| **TSK-19-05** | Template Refactor | Break down monolithic `home.html` into clean component includes (`service_preview`, `lookbook_grid`) | `[DONE]` | TSK-19-02, TSK-19-03 |
| **TSK-19-06** | CSS De-bloat | Extract monolithic inline stylesheets from `base.html` into modular external CSS assets | `[DONE]` | TSK-19-05 |
| **TSK-19-07** | Dead Code Purge | Audit and remove unused scripts, deprecated video preloader remnants, and obsolete test canvases | `[DONE]` | TSK-19-06 |
| **TSK-19-08** | Verification | Verify end-to-end responsiveness across mobile (375px), tablet (768px), and laptop (1366px+) viewports | `[DONE]` | TSK-19-01 to TSK-19-07 |

---

## Detailed Task Specifications

### TSK-19-01: Luxury Header Navigation Streamlining
- File: `django/core/templates/components/header_nav.html`
- Retain only: Brand Logo Crest, Services, Lookbook, Packages, Academy, About, and primary Golden WhatsApp VIP CTA.
- Remove redundant, duplicate, or secondary clutter.

### TSK-19-02: Hero Section Conversion Simplification
- File: `django/core/templates/components/hero_showcase.html`
- Singular headline: *Haute Bridal Couture & 18-Hour Cry-Proof Artistry*.
- Primary action: WhatsApp VIP booking with pre-filled message.
- Feathered studio portrait blending smoothly into dark canvas.

### TSK-19-03: Couture Footer Componentization
- File: `django/core/templates/components/footer.html`
- Include authentic Sinha crest, quick links, Jhansi studio address, WhatsApp button, and copyright.

### TSK-19-04: Dedicated `/packages/` View & Template
- Files: `django/core/views/packages.py` & `django/core/templates/core/packages.html`
- Render 3 transparent luxury tiers (Solitaire Bride, Imperial Couture, Grand Dynasty Suite) with direct WhatsApp lock-in.

### TSK-19-05 to TSK-19-07: Monolith Deconstruction & CSS Modularization
- Files: `django/core/templates/core/home.html` & `django/core/templates/core/base.html`
- Replace 4,000+ lines in `home.html` with component includes.
- Move inline CSS into `static/core/css/modules/`.
- Purge obsolete video tags and abandoned test canvases.

### TSK-19-08: Cross-Device & Conversion Testing
- Test on 375px (iPhone SE), 390px (iPhone 14), 768px (iPad), and 1366px+ (Desktop).
- Confirm zero horizontal scroll, fast first contentful paint ($<1.8\text{s}$), and seamless navigation between all subpages.
