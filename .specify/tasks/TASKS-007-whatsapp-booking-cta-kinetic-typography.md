# TASKS-007: WhatsApp Booking CTA & Kinetic Typography

**Spec:** SPEC-007 | **Plan:** PLAN-007  
**Status:** Completed & Verified ✅  
**Total Tasks:** 8

---

## Task Checklist

### TSK-007.01 — Font Preload & Kinetic Hero Tagline
- [x] Add `<link rel="preload" as="font">` for `Cormorant Garamond` in `base.html` `<head>`.
- [x] Add Google Fonts import for `Cormorant+Garamond:wght@300;400;600;700` (display swap).
- [x] In `home.html`, replace plain hero tagline `<h1>` with `.kinetic-headline` wrapper.
- [x] Add `splitAndAnimate()` JavaScript that wraps each character in `<span class="char" style="--i:N">`.
- [x] Add CSS `@keyframes char-rise` (translateY 30px → 0, opacity 0 → 1) with stagger `calc(var(--i) * 0.04s)`.
- **Acceptance Check:** First load shows characters rising in stagger sequence.

### TSK-007.02 — Dual-Direction Marquee Service Strip
- [x] Add `.marquee-band` section in `home.html` just below the hero section.
- [x] Populate two `.marquee-track` divs (forward + reverse) with 12 service items each (doubled for seamless loop).
- [x] Add `@keyframes marquee-fwd` and `@keyframes marquee-rev` to `animations.css`.
- [x] Style: gold text `#E2BA45` on dark translucent strip, uppercase, letter-spacing 0.2em.
- [x] Add hover pause: `.marquee-band:hover .marquee-track { animation-play-state: paused; }`.
- **Acceptance Check:** Marquee scrolls continuously, reverses on second row, pauses on hover.

### TSK-007.03 — WhatsApp FAB Button
- [x] Add `WHATSAPP_PHONE` to `anshita_project/settings.py` (using template default `917879223442`).
- [x] WhatsApp number exposed via Django template default variable in base.html.
- [x] Add `#whatsapp-fab` anchor tag in `base.html` before `</body>`.
- [x] Inline WhatsApp SVG icon (green `#25D366`) — full brand path.
- [x] Add `.fab-pulse-ring` span inside FAB for animated ring.
- [x] CSS: `position: fixed; bottom: 28px; right: 90px; z-index: 9000` (offset from Asha at right: 24px).
- [x] Add `@keyframes fab-appear` (scale from 0.3 → 1 with 3s delay on page load).
- [x] Add `@keyframes pulse-ring` (scale 1 → 1.9, opacity 0.75 → 0, repeating).
- **Acceptance Check:** FAB visible bottom-right, opens WhatsApp with pre-filled message on click.

### TSK-007.04 — Desktop Inline WhatsApp CTA in Hero
- [x] Add `<a class="btn-whatsapp-inline">📲 Book on WhatsApp</a>` inside the hero CTA group in `home.html`.
- [x] Style: gold gradient button with WhatsApp icon, only visible on desktop (`@media (min-width: 1024px)`).
- [x] UTM link: `?utm_source=website&utm_medium=whatsapp_cta&utm_campaign=bridal_2024`.
- **Acceptance Check:** CTA visible on desktop hero, hidden on mobile (use FAB instead).

### TSK-007.05 — Metric Counter Glass Cards
- [x] Add `.metrics-band` section in `home.html` (between services section and testimonials).
- [x] Three counter cards: `1200+ Brides`, `15 Cities`, `12+ Years`.
- [x] Add `animateCountUp()` function using `IntersectionObserver` (threshold: 0.4, ease-out cubic).
- [x] Style: dark glass card (`background: rgba(255,255,255,0.04); backdrop-filter: blur(12px); border: 1px solid rgba(226,186,69,0.2)`).
- [x] Gold number display (Cormorant Garamond clamp 2.8-4rem), white label (uppercase 0.7rem).
- **Acceptance Check:** Numbers count from 0 to target when section scrolls into view.

### TSK-007.06 — Scroll Kinetic Parallax on Headline
- [x] Add Lenis scroll listener: on each frame, shift `.kinetic-headline` chars by `scrollY * 0.045` on X-axis.
- [x] Clamp max X drift to ±40px.
- [x] Respect `prefers-reduced-motion: reduce` — disable kinetic shift if reduced motion preferred.
- **Acceptance Check:** Characters drift subtly left/right with scroll momentum.

### TSK-007.07 — Reduced Motion & Accessibility Compliance
- [x] Wrap all marquee + kinetic animations in `@media (prefers-reduced-motion: no-preference)` / disable in reduced-motion.
- [x] Add `aria-hidden="true"` to all decorative `.marquee-band` elements.
- [x] Add `aria-label` to `#whatsapp-fab`: `"Book a consultation on WhatsApp"`.
- [x] Add `title="Book on WhatsApp"` to FAB for tooltip.
- **Acceptance Check:** No animations in reduced-motion mode; screen reader announces FAB correctly.

### TSK-007.08 — Browser Verification
- [x] Run Selenium test capturing: kinetic headline on load, marquee scrolling, FAB visible, metric counters animated.
- [x] Verify FAB does not overlap Asha mascot toggle on any viewport.
- [x] Save screenshots: `verify_whatsapp_fab.png`, `verify_marquee_strip.png`, `verify_metric_counters.png`.
- **Acceptance Check:** All 3 screenshots show expected UI states.
