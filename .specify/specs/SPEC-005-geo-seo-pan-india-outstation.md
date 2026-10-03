# Feature Specification: Pan-India Multi-State Geo-SEO Engine & Outstation Service Hub

**Feature Branch:** `feature/geo-seo-pan-india-outstation`  
**Spec ID:** `SPEC-005`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Approved for Implementation  
**Estimated Complexity:** Medium (Schema.org JSON-LD, Geo-Meta Tags, Regional Footer Matrix)

---

## 1. Executive Summary & Problem Description

### Current Problem
The site only has generic schema (`"areaServed": "India"`), meaning it fails to rank on Google when brides search location-specific queries such as:
- *"Bridal makeup artist near me"*
- *"Best bridal makeup artist in Jabalpur / Bhopal / Raipur / Indore"*
- *"Destination wedding makeup artist MP CG UP Maharashtra"*
- *"Bridal makeup artist Delhi / Bengaluru / Hyderabad / Pune / Lucknow"*

Furthermore, trying to solve this by dumping a raw string of 10+ cities directly into the hero section caused severe visual clutter, broken line-wraps, and clipped CTA buttons on laptop screens.

### Target Solution
1. **Schema.org Multi-City Structured Data**: Embed rich structured JSON-LD defining all key target regions (MP, CG, UP, Maharashtra, Delhi NCR, Karnataka, Telangana, Tamil Nadu) in `base.html`.
2. **Geo-Meta Tags**: Add `<meta name="geo.region" content="IN-MP">` and multi-state coverage tags.
3. **Regional SEO Directory Hub in Footer**: Build an elegant, luxurious, crawlable **Regional Bridal Coverage Matrix** in `home.html` indexing all target cities without crowding the above-the-fold hero.
4. **Hero Presentation**: Streamlined luxury indicator (`Flagship Atelier: Jabalpur · Destination Weddings Pan-India`) with a clean link to the Travel Estimator.

---

## 2. User Stories & Acceptance Criteria

### User Story 1: Bride Searching Locally
> *As a bride in Bhopal, Raipur, or Lucknow searching Google for "bridal makeup artist near me",*  
> *I want Anshita Makeover to appear prominently in the organic search results with local relevance,*  
> *So that I discover her artistry and book her for my wedding.*

### Acceptance Criteria
- [ ] **AC-1 (Schema.org Accuracy)**: JSON-LD passes Google Rich Results test with structured `BeautySalon`, `areaServed` covering MP, CG, UP, MH, DL, KA, TS, TN, and explicit service catalog.
- [ ] **AC-2 (Search Snippet Relevance)**: Meta descriptions and titles dynamically optimize for local bridal keywords.
- [ ] **AC-3 (Crawlable Regional Matrix)**: Dedicated regional accordion/grid in the footer indexing all 8 target states and key metropolitan cities.
- [ ] **AC-4 (Zero Hero Clutter)**: The hero section remains completely pristine and high-fashion, with zero awkward city wraps.
