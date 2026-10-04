# SPEC-007: WhatsApp Instant Booking CTA & Kinetic Stanzza-Style Typography

**Status:** Active  
**Milestone:** Haute Conversion Engine  
**Constitutions:** `.specify/memory/constitution.md`  
**Inspired by:** Stanzza.design (kinetic oversized typography), LxL Creative (animated CTAs)

---

## 1. Overview & Objective

Elevate the Anshita Makeover homepage and gallery pages with **kinetic oversized headline typography** and a **one-tap WhatsApp Booking CTA** that converts visitors into bookings without friction. Inspired by Stanzza's ultra-bold serif animations and LxL Creative's fluid interaction patterns.

---

## 2. User Stories & Acceptance Criteria

### 2.1 Story: Kinetic Oversized Hero Typography
* **As a bride landing on the homepage**, I want to see bold, animated Sanskrit/Hindi headline text that moves with scroll momentum, so I immediately feel the luxury and grandeur of Anshita Studio.
* **Acceptance Criteria:**
  - [ ] Oversized display typeface (`Cormorant Garamond` or `Playfair Display SC`, 96–140px desktop) for the primary hero tagline.
  - [ ] Letter-spacing and character-by-character stagger reveal animation on first load (GSAP `SplitText` or custom span-splitting).
  - [ ] Scroll-linked kinetic parallax: headline characters shift subtly on Y-axis tied to Lenis scroll position (horizontal drift < 40px).
  - [ ] Hindi/Sanskrit tagline: *"रूप की पराकाष्ठा — Anshita Makeover"* displayed as two-line oversized display.
  - [ ] Zero CLS (Cumulative Layout Shift) — font preloaded via `<link rel="preload">`.

### 2.2 Story: Animated Marquee Service Band
* **As a visitor scrolling**, I want to see an infinite horizontal marquee showing Anshita's signature services in glittering gold text, so I immediately grasp the breadth of offerings.
* **Acceptance Criteria:**
  - [ ] Infinite horizontal ticker/marquee with `animation: marquee-scroll 20s linear infinite`.
  - [ ] Items: `✦ BRIDAL COUTURE  ✦ AIRBRUSH ARTISTRY  ✦ HD FLAWLESS FINISH  ✦ DESTINATION BRIDE  ✦ ACADEMY MASTERCLASS  ✦ CELEBRITY BRIDES`.
  - [ ] Gold text (`#E2BA45`) on translucent dark strip (`rgba(6,6,6,0.85)`).
  - [ ] Reversed direction on second marquee row (LxL Creative dual-row pattern).
  - [ ] Pauses on hover (`animation-play-state: paused`).

### 2.3 Story: One-Tap WhatsApp Instant Booking
* **As a mobile bride**, I want to tap a single button and instantly open WhatsApp with a pre-filled message booking enquiry to Anshita Studio, so I can book within seconds.
* **Acceptance Criteria:**
  - [ ] Floating sticky WhatsApp FAB (Floating Action Button) in bottom-right corner on mobile (`position: fixed; bottom: 28px; right: 24px; z-index: 9000`).
  - [ ] Opens `https://wa.me/91XXXXXXXXXX?text=Hi%20Anshita%20Studio%21%20I%20would%20like%20to%20book%20a%20bridal%20consultation.` in new tab.
  - [ ] FAB has pulse-ring animation (green `#25D366`) attracting attention after 3 seconds on page.
  - [ ] Desktop: Inline "Book on WhatsApp" CTA in hero section (gold gradient button with WhatsApp icon).
  - [ ] UTM-tracked link: `?utm_source=website&utm_medium=whatsapp_cta&utm_campaign=bridal_2024`.

### 2.4 Story: Scroll-Triggered Bridal Metric Counters
* **As a visitor**, I want to see animated counting numbers revealing Anshita's bridal portfolio statistics (brides served, cities covered, years of expertise) so I feel confidence in booking.
* **Acceptance Criteria:**
  - [ ] Three counters: `1200+ Brides`, `15 Cities`, `12+ Years`.
  - [ ] CountUp animation triggers once when section scrolls into viewport (IntersectionObserver).
  - [ ] Gold accent numbers on dark glass card with micro-shimmer animation.

---

## 3. Design Reference

| Reference Site | Feature Borrowed | Adaptation for Anshita |
| :--- | :--- | :--- |
| Stanzza.design | Oversized kinetic serif display type | Hindi/Sanskrit tagline in `Cormorant Garamond` |
| LxL Creative | Dual-direction marquee service ticker | Bridal services in glittering gold |
| Demilie.ru | Minimal CTAs with craft story | WhatsApp booking with pre-filled context |
| Juan Mora | Hero layout with single dominant CTA | Floating WhatsApp FAB + inline CTA |

---

## 4. Technical Constraints

- **No external dependencies beyond GSAP** (already loaded) — use CSS `@keyframes` for marquee.
- WhatsApp number must be loaded from Django settings/template variable, never hardcoded.
- FAB must not overlap the Asha mascot toggle button.
- All animations must respect `prefers-reduced-motion: reduce`.
- Font preload must use `crossorigin="anonymous"` for Google Fonts.
