# TASKS-007: WhatsApp Booking CTA & Kinetic Typography

**Spec:** SPEC-007 | **Plan:** PLAN-007  
**Status:** Pending Execution  
**Total Tasks:** 8

---

## Task Checklist

### TSK-007.01 — Font Preload & Kinetic Hero Tagline
- [ ] Add `<link rel="preload" as="font">` for `Cormorant Garamond` in `base.html` `<head>`.
- [ ] Add Google Fonts import for `Cormorant+Garamond:wght@300;400;600;700` (display swap).
- [ ] In `home.html`, replace plain hero tagline `<h1>` with `.kinetic-headline` wrapper.
- [ ] Add `splitAndAnimate()` JavaScript that wraps each character in `<span class="char" style="--i:N">`.
- [ ] Add CSS `@keyframes char-rise` (translateY 30px → 0, opacity 0 → 1) with stagger `calc(var(--i) * 0.04s)`.
- **Acceptance Check:** First load shows characters rising in stagger sequence.

### TSK-007.02 — Dual-Direction Marquee Service Strip
- [ ] Add `.marquee-band` section in `home.html` just below the hero section.
- [ ] Populate two `.marquee-track` divs (forward + reverse) with 12 service items each (doubled for seamless loop).
- [ ] Add `@keyframes marquee-fwd` and `@keyframes marquee-rev` to `style.css`.
- [ ] Style: gold text `#E2BA45` on dark translucent strip, uppercase, letter-spacing 0.2em.
- [ ] Add hover pause: `.marquee-band:hover .marquee-track { animation-play-state: paused; }`.
- **Acceptance Check:** Marquee scrolls continuously, reverses on second row, pauses on hover.

### TSK-007.03 — WhatsApp FAB Button
- [ ] Add `WHATSAPP_PHONE` to `anshita_project/settings.py` (placeholder: `'919XXXXXXXXX'`).
- [ ] Add `django.template.context_processors.settings` (or custom processor) to expose `WHATSAPP_PHONE` in templates.
- [ ] Add `#whatsapp-fab` anchor tag in `base.html` before `</body>`.
- [ ] Inline WhatsApp SVG icon (green `#25D366`).
- [ ] Add `.fab-pulse-ring` span inside FAB for animated ring.
- [ ] CSS: `position: fixed; bottom: 28px; right: 88px; z-index: 9000` (offset from Asha at right: 24px).
- [ ] Add `@keyframes fab-appear` (scale from 0.3 → 1 with 3s delay on page load).
- [ ] Add `@keyframes pulse-ring` (scale 1 → 1.8, opacity 0.8 → 0, repeating).
- **Acceptance Check:** FAB visible bottom-right, opens WhatsApp with pre-filled message on click.

### TSK-007.04 — Desktop Inline WhatsApp CTA in Hero
- [ ] Add `<a class="btn-whatsapp-inline">📲 Book on WhatsApp</a>` inside the hero CTA group in `home.html`.
- [ ] Style: gold gradient button with WhatsApp icon, only visible on desktop (`@media (min-width: 1024px)`).
- [ ] UTM link: `?utm_source=website&utm_medium=whatsapp_cta&utm_campaign=bridal_2024`.
- **Acceptance Check:** CTA visible on desktop hero, hidden on mobile (use FAB instead).

### TSK-007.05 — Metric Counter Glass Cards
- [ ] Add `.metrics-band` section in `home.html` (below marquee or above About section).
- [ ] Three counter cards: `1200+ Brides`, `15 Cities`, `12+ Years`.
- [ ] Add `countUp(el, target, suffix)` function using `IntersectionObserver` (threshold: 0.4).
- [ ] Style: dark glass card (`background: rgba(255,255,255,0.05); backdrop-filter: blur(12px); border: 1px solid rgba(226,186,69,0.2)`).
- [ ] Gold number display (Cormorant Garamond 72px), white label (14px).
- **Acceptance Check:** Numbers count from 0 to target when section scrolls into view.

### TSK-007.06 — Scroll Kinetic Parallax on Headline
- [ ] Add Lenis scroll listener: on each frame, shift `.kinetic-headline` chars by `scrollY * 0.015` on X-axis (subtle).
- [ ] Clamp max X drift to ±40px.
- [ ] Respect `prefers-reduced-motion: reduce` — disable kinetic shift if reduced motion preferred.
- **Acceptance Check:** Characters drift subtly left/right with scroll momentum.

### TSK-007.07 — Reduced Motion & Accessibility Compliance
- [ ] Wrap all marquee + kinetic animations in `@media (prefers-reduced-motion: no-preference)`.
- [ ] Add `aria-hidden="true"` to all decorative `.marquee-band` elements.
- [ ] Add `aria-label` to `#whatsapp-fab`: `"Book a consultation on WhatsApp"`.
- [ ] Add `title="Book on WhatsApp"` to FAB for tooltip.
- **Acceptance Check:** No animations in reduced-motion mode; screen reader announces FAB correctly.

### TSK-007.08 — Browser Verification
- [ ] Run Playwright test capturing: kinetic headline on load, marquee scrolling, FAB visible, metric counters animated.
- [ ] Verify FAB does not overlap Asha mascot toggle on any viewport.
- [ ] Save screenshots: `verify_whatsapp_fab.png`, `verify_marquee_strip.png`, `verify_metric_counters.png`.
- **Acceptance Check:** All 3 screenshots show expected UI states.
