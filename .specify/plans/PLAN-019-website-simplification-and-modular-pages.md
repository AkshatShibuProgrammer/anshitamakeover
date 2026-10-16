# Technical Plan: Website Simplification, Modular Page Architecture & High-Conversion Funnel

**Spec ID Reference:** `SPEC-019`  
**Parent Constitution:** `.specify/memory/constitution-high-conversion-seo.md`  
**Target Files:**
- `django/core/templates/core/base.html`
- `django/core/templates/core/home.html`
- `django/core/templates/components/header_nav.html`
- `django/core/templates/components/footer.html`
- `django/core/templates/components/hero_showcase.html` (new)
- `django/core/views/packages.py` (new/refactored)
- `django/core/templates/core/packages.html` (new/refactored)
**Status:** Ready for Task Breakdown  

---

## 1. Technical Architecture & Component Tree

```
                       base.html (Master Shell)
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
components/header_nav.html  {% block content %}     components/footer.html
- Monogram Crest            - Child Page Template   - Sinha Heritage Crest
- 5 Primary Links           - Clean Grid            - Location / Contacts
- Golden WhatsApp CTA                               - Legal & Copyright
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
home.html (Editorial)     services.html           packages.html
├── hero_showcase.html    ├── bridal_tier.html    ├── pricing_table.html
├── service_preview.html  ├── airbrush.html       └── privilege_pass.html
├── lookbook_grid.html    └── add_ons.html
└── academy_preview.html
```

---

## 2. Component Refactoring & Implementation Details

### 2.1 Refactor Header Navigation (`components/header_nav.html`)
Transform the busy header navigation into an uncluttered luxury bar:
```html
<nav class="luxury-navbar" id="luxury-navbar" role="navigation" aria-label="Main Navigation">
  <div class="nav-container">
    <!-- Brand Monogram -->
    <a href="{% url 'core:home' %}" class="brand-link" aria-label="Anshita Makeover Home">
      <img src="{% static 'core/images/brand/anshita_crest.svg' %}" alt="Anshita Makeover Crest" class="nav-crest">
      <span class="brand-text">ANSHITA MAKEOVER</span>
    </a>

    <!-- Primary Nav Links -->
    <div class="nav-links">
      <a href="{% url 'core:services' %}" class="nav-item {% if request.resolver_match.url_name == 'services' %}active{% endif %}">Services</a>
      <a href="{% url 'core:gallery' %}" class="nav-item {% if request.resolver_match.url_name == 'gallery' %}active{% endif %}">Lookbook</a>
      <a href="{% url 'core:packages' %}" class="nav-item {% if request.resolver_match.url_name == 'packages' %}active{% endif %}">Packages</a>
      <a href="{% url 'core:academy' %}" class="nav-item {% if request.resolver_match.url_name == 'academy' %}active{% endif %}">Academy</a>
      <a href="{% url 'core:home' %}#craftsmanship" class="nav-item">About</a>
    </div>

    <!-- High-Conversion Primary CTA -->
    <div class="nav-action">
      <a href="https://wa.me/919559455444?text=Hi%20Anshita!%20I%20would%20like%20to%20inquire%20about%20a%20luxury%20bridal%20booking." 
         class="btn-gold-vip" 
         target="_blank" 
         rel="noopener noreferrer"
         aria-label="Book VIP Consultation on WhatsApp">
        <span class="btn-sparkle">✨</span> Book VIP Date
      </a>
    </div>
  </div>
</nav>
```

### 2.2 Hero Simplification (`components/hero_showcase.html`)
Streamline the hero section to focus on 1 primary action and eliminate distracting overlapping rings:
- **Headline**: *Haute Bridal Couture & 18-Hour Cry-Proof Artistry*
- **Sub-headline**: *Crafting unforgettable royal transformations for distinguished brides across Jhansi, Bundelkhand & Destination Weddings.*
- **Primary CTA**: Direct WhatsApp consultation button with real-time response indicator (*"Typical reply: under 15 mins"*).
- **Secondary Action**: Seamless scroll to *"Explore Authentic 2026 Lookbook"*.
- **Visual**: Studio portrait with feathered horizontal alpha mask seamlessly merging into `#070605` background canvas with Three.js softbox lighting simulation.

### 2.3 Modular Dedicated Pages Breakdown
1. **`/services/` (`templates/core/services.html`)**:
   - Focus: Detailed service cards with duration, products used (MAC, Huda, Dior, NARS), technique descriptions, and direct booking pills.
2. **`/gallery/` (`templates/core/gallery.html`)**:
   - Focus: Clean masonry/grid of authentic brides with filters (Bridal, Engagement, Reception, Haldi) and high-resolution lightbox modal.
3. **`/packages/` (`templates/core/packages.html`)**:
   - Focus: 3 clear tiers:
     - *The Royal Solitaire Bride* (Signature HD Bridal)
     - *The Imperial Couture Bride* (Airbrush + Jewellery Styling + Saree Drape)
     - *The Grand Dynasty Suite* (Bride + Mother + 2 Sisters / Party)
4. **`/academy/` (`templates/core/academy.html`)**:
   - Focus: Professional curriculum, syllabus breakdown, student work gallery, and enrollment inquiry form.

### 2.4 Monolith Code Cleanup
- Extract over 3,000 lines of inline `<style>` and `<script>` tags currently sitting in `base.html` and `home.html` into static asset bundles:
  - `static/core/css/modules/header.css`
  - `static/core/css/modules/hero.css`
  - `static/core/css/modules/cards.css`
- Eliminate redundant or dead event listeners, orphaned test scripts, and deprecated video preloader remnants.

---

## 3. Implementation Phasing & Risk Mitigation

| Phase | Tasks | Risk / Guardrail |
|---|---|---|
| **Phase 1** | Extract `header_nav.html` and `footer.html` into reusable components | Test active route classes to ensure no visual regression. |
| **Phase 2** | Create dedicated `packages.html` and link URL routes | Keep old package anchor on `home.html` as fallback redirection. |
| **Phase 3** | Deconstruct `home.html` into component includes | Keep git commit atomic so any template regression can be immediately reverted. |

---

## 4. Verification & Testing Checklist

- [ ] **V-19.1**: Django test suite passes without broken URL names (`reverse('core:packages')` succeeds).
- [ ] **V-19.2**: Header navigation renders cleanly without wrapping or overflow on viewports from 375px to 2560px.
- [ ] **V-19.3**: Primary WhatsApp CTA successfully opens WhatsApp with pre-filled bridal booking message.
- [ ] **V-19.4**: Page payload for `home.html` decreases significantly, with under 1.5s DOM load time.
