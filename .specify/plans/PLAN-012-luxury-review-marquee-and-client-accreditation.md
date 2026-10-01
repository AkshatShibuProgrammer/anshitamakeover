# Implementation Plan: SPEC-012 — Luxury Review Marquee & Client Accreditation

**Governing Spec:** [SPEC-012-luxury-review-marquee-and-client-accreditation.md](file:///.specify/specs/SPEC-012-luxury-review-marquee-and-client-accreditation.md)  
**Status:** Completed & Integrated

---

## 1. Phase Breakdown
- **Phase 1: Database & Model Accreditation**
  - Update `LookGroup` client_name and name to "Kuhu Khare — Traditional Kolkata Banarasi & Chandan Art (Competition Artistry)".
  - Populate `CustomerReview` records for Kuhu Khare, Thakur Shivani, Miss Rajak, Dr. Ritu Saxena, and Priya Sharma.
- **Phase 2: Template Accreditation**
  - Update `gallery.html` cinema dock and album indicators to Kuhu Khare.
  - Update `home.html` cylinder carousel card 1 to Kuhu Khare.
- **Phase 3: Benchmark Review UI & Controller**
  - Replace static quote ticker with `.testimonials-marquee-viewport` and `.testi-card` flex tracks.
  - Implement clone loop, mouse drag scroll, next/prev arrow buttons, and category filter toggles.
- **Phase 4: Contract Regression Verification**
  - Ensure `TC-PUB-009` (reviews capped at 8) and all 21 public page tests pass.
