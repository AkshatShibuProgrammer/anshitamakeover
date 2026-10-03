# Implementation Plan: Pan-India Multi-State Geo-SEO Engine & Outstation Service Hub

**Plan ID:** `PLAN-005`  
**Related Spec:** [SPEC-005](file:///.specify/specs/SPEC-005-geo-seo-pan-india-outstation.md)  
**Target Files:**
- `django/core/templates/core/base.html` (Schema.org JSON-LD & Geo-meta tags)
- `django/core/templates/core/home.html` (Regional Service Directory in footer & streamlined hero location bar)

---

## 1. Technical Architecture & Geo-Targeting

### A. Schema.org JSON-LD Enrichment (`base.html`)
- Update the `<script type="application/ld+json">` in `base.html`:
  - `areaServed`: Array of `City` and `AdministrativeArea` objects covering:
    - **MP**: Jabalpur (Flagship Studio), Bhopal, Indore, Gwalior, Ujjain
    - **CG**: Raipur, Bilaspur, Durg-Bhilai
    - **UP**: Lucknow, Varanasi, Prayagraj, Kanpur, Noida
    - **Maharashtra**: Mumbai, Pune, Nagpur
    - **Delhi NCR**: New Delhi, Gurugram
    - **Karnataka**: Bengaluru
    - **Telangana**: Hyderabad
    - **Tamil Nadu**: Chennai
  - `hasOfferCatalog`: Structured services for *"Bridal Makeup Artist Near Me"*, *"Airbrush HD Bridal Makeup"*, *"Destination Wedding Makeup Artist"*.

### B. Regional Service Hub Component (`home.html`)
- Insert a luxurious, crawlable **Regional Bridal Coverage Matrix** right above the footer:
  - Organizes the 8 states into 4 clean editorial luxury columns.
  - Links to the Travel Distance Estimator (`/travel-estimator/`) for instant surcharge calculation.
  - Provides rich semantic text for Google bot indexing without compromising the visual layout.
