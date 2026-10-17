# Constitutional Sub-Standard: Luxury Editorial SEO & High-Conversion Architecture

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Sub-System:** Technical Search Engine Optimization, Schema Engine & Modular UX  
**Standard:** Spec-Driven Development (SDD) via Spec Kit & GSD  
**Parent Constitution:** `.specify/memory/constitution.md`  
**Spec ID References:** `SPEC-018`, `SPEC-019`  
**Status:** Canonical & Active

---

## 1. Technical SEO & Crawlability Mandates

### 1.1 Zero Missing Meta Tag Policy
- Every rendered HTML route in the Django application MUST emit:
  1. `<title>`: Bespoke, luxury-tailored brand title with high-intent keywords (`Anshita Makeover | Luxury Bridal Makeup Studio & Academy`).
  2. `<meta name="description">`: Unique 150-160 character compelling summary with location keywords (Jhansi, Bundelkhand, Gwalior, Kanpur, Pan-India).
  3. `<link rel="canonical">`: Absolute canonical URL preventing duplicate content indexing between HTTP/HTTPS, trailing slash variations, or query parameters.
  4. **Open Graph Protocol**: `og:title`, `og:description`, `og:type`, `og:url`, `og:image`, `og:locale` (`en_IN`).
  5. **Twitter Cards**: `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`.
- **Enforcement Mechanism**: The root `base.html` MUST provide overridable template blocks:
  - `{% block meta_title %}`
  - `{% block meta_description %}`
  - `{% block canonical_url %}`
  - `{% block og_tags %}`

### 1.2 Enterprise JSON-LD Structured Data
- Every page must render semantic, machine-readable JSON-LD schemas validated against Schema.org:
  1. **Primary Entity**: `BeautySalon` / `LocalBusiness` / `HealthAndBeautyBusiness`.
     - Fields: `name`, `image`, `telephone`, `priceRange` (`₹₹₹₹`), `address` (Street, City: Jhansi, PostalCode, Region: UP, Country: IN), `geo` (`latitude`, `longitude`), `openingHoursSpecification`.
  2. **Service Hierarchy**: `Service` / `OfferCatalog` representing Bridal Makeup, HD Airbrush, Reception Glamour, and Bridal Academy.
  3. **Trust & Social Proof**: `aggregateRating` and `review` schema matching authentic verified client feedback.
  4. **BreadcrumbList**: Structured navigation trail reflecting site hierarchy.

### 1.3 Automated Sitemap & Robots Directives
- **Dynamic Sitemap Endpoint**: The Django app MUST serve a valid `sitemap.xml` at `/sitemap.xml` listing all canonical endpoints (`home`, `services`, `gallery`, `academy`, `contact`, `packages`) with proper `changefreq` and `priority` weights.
- **Strict Robots Configuration**: A dedicated `/robots.txt` route specifying allowlist for search engines, sitemap link, and disallow rules for sensitive admin/API endpoints (`/admin/`, `/api/internal/`).

---

## 2. High-Conversion Page Architecture Standard

### 2.1 Modular Route Separation Over Monolithic Bloat
- **Problem**: Monolithic single-page templates (e.g. 4,400+ line `home.html`) hurt SEO (keyword cannibalization, slow First Contentful Paint, diluted search intent).
- **Mandate**: The site MUST support clear, dedicated subpages for high-intent queries:
  - `/` (Editorial Luxury Overview & Flagship Showcase)
  - `/services/` (Comprehensive bridal, HD, airbrush, engagement offerings)
  - `/gallery/` (Authentic bride lookbooks, high-res portraits, reels)
  - `/packages/` (Transparent luxury pricing, bridal party suites, negotiation tier)
  - `/academy/` (Professional masterclasses, certifications, student portfolios)
  - `/book/` (High-converting booking funnel with instant WhatsApp lock-in)

### 2.2 Singular Clear Call-To-Action (CTA) Hierarchy
- Above-the-fold hero zones MUST feature **one primary conversion action**:
  - Primary: Direct WhatsApp VIP Bridal Consultation / Booking lock-in.
  - Secondary: View Authentic Portfolio / Curated Lookbook.
- Competing or confusing CTAs that distract visitors from securing their wedding date are prohibited.

### 2.3 Core Web Vitals & Performance Budget
- **Largest Contentful Paint (LCP)**: $\le 1.8\text{s}$ on 4G networks.
- **First Input Delay (FID) / Interaction to Next Paint (INP)**: $\le 100\text{ms}$.
- **Cumulative Layout Shift (CLS)**: $\le 0.05$ (guaranteed by explicit image aspect ratios and vector skeletons).
