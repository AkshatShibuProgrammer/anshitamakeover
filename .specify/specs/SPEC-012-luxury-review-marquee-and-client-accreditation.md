# Feature Specification: Luxury Review Marquee & Authentic Client Accreditation

**Feature Branch:** `feature/luxury-reviews-marquee`  
**Spec ID:** `SPEC-012`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Completed & Integrated  
**Estimated Complexity:** Medium-High (Continuous CSS Marquee, Gesture Scroll, Multi-Entity Accreditation)

---

## 1. Executive Summary & Problem Description

### Objectives
1. **Bengali Bride Accreditation**: Accredit Bengali bride as **Kuhu Khare** across the site, gallery cinema dock, lookbook cards, and review database, clarifying that it was a makeover for **Bridal Artistry Competition Participation**.
2. **Benchmark-Caliber Review Animation (Stanzza / Juan Mora)**:
   - Infinite horizontal continuous scrolling marquee track.
   - Micro-interaction pause on hover (`Hover to read` / `Auto-flow active` indicator).
   - Mouse drag-to-scroll physics and touch swipe gestures.
   - Smooth navigation arrows (`‹` and `›`) for discrete card jumping.
   - Category filtering (`All Praise`, `Competition Artistry`, `Bridal Vivah`, `Sangeet & Reception`).
   - High-contrast editorial cards with uncropped client photo avatars in gold luxury frames.
3. **Real Client Testimonials from Instagram**: Include verified reviews for Kuhu Khare, Thakur Shivani, Miss Rajak, Dr. Ritu Saxena, and Priya Sharma.

---

## 2. Technical Architecture & Database Sync

- **Model Updates**: Synchronized `CustomerReview` and `LookGroup` via `scripts/update_kuhu_review.py`.
- **CSS Marquee**: Keyframe translation from `0%` to `-50%` with duplicated elements for zero-stutter infinite flow.
- **Contract Test Compliance**: Kept homepage context review query capped at 8 items to strictly satisfy `TC-PUB-009`.
