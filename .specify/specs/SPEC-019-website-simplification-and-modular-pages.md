# Feature Specification: Website Simplification, Modular Page Architecture & High-Conversion Funnel

**Feature Branch:** `arena/01a105d6-anshitamakeover`  
**Spec ID:** `SPEC-019`  
**Governing Documents:** `.specify/memory/constitution.md`, `.specify/memory/constitution-high-conversion-seo.md`  
**Status:** In Review & Planning  
**Estimated Complexity:** High (Monolithic Template Refactoring, Navigation Simplification, Modular Subpage Generation, Conversion Funnel Architecture)

---

## 1. Executive Summary & Problem Description

### 1.1 Problem Statement
The current frontend architecture suffers from severe architectural bloat and cognitive friction:
1. **Monolithic Template Bloat**:
   - `core/templates/core/home.html` spans 4,462 lines (172KB).
   - `core/templates/core/base.html` spans over 8,100 lines.
   - All interactive systems (3D cylinder gallery, preloader, audio player, AI negotiation modal, review marquee, rituals accordion, coupon generator) are crammed into a single monolithic page.
2. **Cognitive Overload & Diluted Conversion Intent**:
   - Prospective brides landing on the site encounter multiple competing visual stimuli, conflicting CTAs, and confusing scroll-scrubbed elements.
   - There is no clear single conversion hierarchy guiding a bride from discovery to securing her wedding date.
3. **SEO Impairment**:
   - A single-page monolith cannot rank effectively for segmented search queries (e.g., someone searching for "bridal makeup courses in jhansi" should land directly on `/academy/`, while someone searching for "airbrush bridal makeup price" should land on `/packages/`).

### 1.2 Core Objectives
- **Streamline the User Journey (Conversion-First)**:
  - Clear header navigation: `Home`, `Services`, `Bridal Gallery`, `Academy`, `Packages`, and a prominent golden `Book VIP Date` CTA.
  - Hero simplification: 1 singular primary action (Instant WhatsApp Consultation / Booking Lock-in) and 1 secondary action (Explore Lookbook).
- **Deconstruct Monolithic Templates into Modular Pages**:
  - Transform monolithic anchor jumps into fast, dedicated Django routes:
    - `/` $\rightarrow$ Editorial Luxury Homepage (Curated highlights of each pillar).
    - `/services/` $\rightarrow$ Comprehensive bridal, HD airbrush, cocktail, and occasion makeup catalog.
    - `/gallery/` $\rightarrow$ Authentic high-resolution lookbook, transformation reels, and client spotlights.
    - `/packages/` $\rightarrow$ Transparent luxury tiers, bridal party packages, and privilege booking perks.
    - `/academy/` $\rightarrow$ Certified bridal masterclasses, curriculum, syllabus, and student transformations.
    - `/book/` $\rightarrow$ Dedicated high-intent booking funnel with date availability check and WhatsApp concierge.
- **Componentize Shared Partials**:
  - Extract reusable components into `django/core/templates/components/`:
    - `header_nav.html` (Simplified, sticky luxury navbar)
    - `concierge.html` (Pip 3D autonomous mascot)
    - `footer.html` (Couture footer with Sinha crest and location links)
    - `service_card.html`, `review_card.html`, `package_card.html`

---

## 2. Information Architecture & Target Sitemap

```
                      [Anshita Makeover Platform]
                                   │
      ┌────────────────┬───────────┼───────────┬──────────────┐
      │                │           │           │              │
      ▼                ▼           ▼           ▼              ▼
  / (Home)        /services/   /gallery/   /packages/     /academy/
  Editorial       Full Menu    Authentic   Pricing &      Certified
  Highlights      & Details    Lookbooks   Suite Deals    Masterclasses
      │                │           │           │              │
      └────────────────┴───────────┼───────────┴──────────────┘
                                   │
                                   ▼
                             /book/ (Direct WhatsApp / Form Funnel)
```

### 2.1 Navigation & Header Simplification
- **Left**: Luxury interlocking monogram crest ("AM" / Anshita Makeover).
- **Center**: Clean, uncluttered links with subtle gold active underline:
  1. `Services` (`/services/`)
  2. `Lookbook` (`/gallery/`)
  3. `Packages` (`/packages/`)
  4. `Academy` (`/academy/`)
  5. `About` (`/#craftsmanship`)
- **Right**:
  - High-visibility golden pill CTA: `✨ Book VIP Date` (Direct WhatsApp anchor with pre-filled bridal template).
  - Floating 3D Pip concierge docked neatly in bottom-right corner.

---

## 3. Modularization Strategy & Phased Execution

### Phase 1: Core Base & Shared Component Extraction
1. Extract monolithic CSS blocks from `base.html` into dedicated modular stylesheets (`static/core/css/nav.css`, `static/core/css/footer.css`, `static/core/css/concierge.css`).
2. Extract the header navigation into `components/header_nav.html`.
3. Extract the footer into `components/footer.html`.

### Phase 2: Dedicated Modular Views & Templates
1. Verify and polish existing secondary views (`views/services.py`, `views/gallery.py`, `views/academy.py`) so each renders its own focused, lightweight template extending `base.html`.
2. Add dedicated `/packages/` and `/book/` routes with optimized metadata.

### Phase 3: Homepage Streamlining
1. Refactor `home.html` from 4,462 lines down to $<1,000$ lines by referencing clean component includes (`{% include 'components/hero_showcase.html' %}`, `{% include 'components/service_preview.html' %}`, etc.).
2. Remove deprecated code, inline debug scripts, and abandoned test markup.

---

## 4. Acceptance Criteria & Quality Gates

- [ ] **AC-19.1**: Navigation bar displays exactly 5 clean links and 1 high-contrast CTA without visual crowding on 1366px, 1440px, and 1920px viewports.
- [ ] **AC-19.2**: On mobile viewports ($\le 768\text{px}$), hamburger menu opens a clean luxury drawer with identical links and direct WhatsApp call button.
- [ ] **AC-19.3**: Each dedicated route (`/services/`, `/gallery/`, `/packages/`, `/academy/`) loads independently under 1.5 seconds without requiring full homepage script bundles.
- [ ] **AC-19.4**: `home.html` line count is reduced by at least 60% through componentization.
- [ ] **AC-19.5**: Zero dead links in header, footer, or CTA buttons across all pages.
- [ ] **AC-19.6**: All pages pass Django URL reverse lookups (`{% url 'core:services' %}`, `{% url 'core:gallery' %}`, etc.).
