# Analysis 06 — Animation Overhaul

**Status:** PENDING IMPLEMENTATION
**Branch:** 20092026
**Priority:** MEDIUM

---

## 1. Problem Statement

The user reported: *"The curtain opening animation is lost — check Evagher animations again and see any other animation we can opt."*

The previous implementation plan (in `implement/stage2_curtain_split.md`) described a dual-curtain CSS/JS split. This may have been regressed or never fully implemented. This analysis reviews what currently exists and proposes a complete, robust animation stack.

---

## 2. Current Animation State

### Preloader / Entrance Sequence
- Historically: An MP4 video preloader (`Logo_reveal_animation_beauty_brand_delpmaspu_.mp4`) was the entrance.
- A `sessionStorage`-based skip guard was added to show it only once per session.
- Curtain elements `.curtain-left` / `.curtain-right` were planned but status is unknown.

**Action needed:** Check `base.html` for current preloader markup.

Expected search targets:
- `<div class="curtain` — curtain divs
- `<video` — video preloader
- `preloader` class usage
- `sessionStorage` curtain logic in JS

### Evagher Animations Observed
From previous session captures in `evagher_captures/` directory:
1. **Dual-curtain split** — two opaque panels slide apart horizontally on entry
2. **Monogram stroke-draw** — SVG paths animate stroke-dashoffset
3. **Hero text shimmer** — letter-by-letter reveal with stagger
4. **Scroll-triggered section reveals** — sections translate-Y and fade in as they enter viewport
5. **Cursor trail** — subtle gold glow following mouse on desktop

---

## 3. Proposed Animation Inventory

### 3a. Entrance Sequence (Preloader → Hero)

**Recommended approach: Pure CSS + vanilla JS (no GSAP dependency)**

```
Phase 1 (0.0s – 1.5s): SVG monogram stroke-draw animation
Phase 2 (1.5s – 2.2s): Gold shimmer sweep across monogram
Phase 3 (2.2s – 3.0s): Curtains split left and right (cubic-bezier easing)
Phase 4 (3.0s – 3.8s): Hero content fades in (opacity 0 → 1 + translateY 20px → 0)
Phase 5 (3.8s+): Page is fully interactive; curtain elements hidden from DOM
```

**Curtain CSS (key snippet for planning):**
```css
.curtain-left, .curtain-right {
  position: fixed;
  top: 0;
  width: 50%;
  height: 100vh;
  background: #0a0705;  /* near-black matching brand dark */
  z-index: 9999;
  transition: transform 0.9s cubic-bezier(0.77, 0, 0.175, 1);
}
.curtain-left  { left: 0;  transform-origin: left; }
.curtain-right { right: 0; transform-origin: right; }
.curtain-open .curtain-left  { transform: translateX(-100%); }
.curtain-open .curtain-right { transform: translateX(100%); }
```

**Session guard (already exists, verify):**
```js
if (!sessionStorage.getItem('anshita_entered')) {
  // run preloader sequence
  sessionStorage.setItem('anshita_entered', '1');
} else {
  // skip curtains immediately
  document.body.classList.add('curtain-open');
}
```

### 3b. Scroll-Triggered Section Animations

Use `IntersectionObserver` (no library) for:
- Section headers: fade-in + slide-up from 30px below
- Service cards: stagger-in from left (50ms delay per card)
- Gallery images: scale from 95% + fade
- Timeline / process steps: sequential reveal left → right

CSS class approach:
```css
.reveal-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.revealed {
  opacity: 1;
  transform: translateY(0);
}
```

```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('revealed'), i * 60);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
```

### 3c. Micro-Interactions

| Element | Animation |
|---------|-----------|
| Service card hover | `scale(1.03)` + gold border glow `box-shadow: 0 0 20px rgba(212,175,55,0.3)` |
| CTA buttons | Shimmer sweep on hover (`::after` pseudo-element) |
| Nav links | Underline draw-in from left (`scaleX 0→1`) |
| WhatsApp button | Pulse ring animation (already exists — verify it works) |
| Gallery images | Scale 1→1.05 + brightness increase on hover |
| Package cards | Slight lift + shadow deepen |

### 3d. Cursor Trail (Desktop Only)
A lightweight gold dot trails the cursor:
```js
// Only on non-touch devices
if (window.matchMedia('(pointer: fine)').matches) {
  // spawn 8px gold dot following cursor with 80ms lag
}
```

### 3e. Particle / Bokeh Hero Background
The hero section can have a subtle CSS-only particle shimmer using `::before` and `::after` with radial gradients — no canvas required. Lightweight and elegant.

---

## 4. Evagher Comparison Table

| Animation | Evagher | Current Site | Gap |
|-----------|---------|-------------|-----|
| Dual curtain split | YES | BROKEN / MISSING | HIGH PRIORITY |
| SVG monogram stroke | YES | Partial (video-based) | HIGH PRIORITY |
| Scroll-triggered reveals | YES | Partial / inconsistent | MEDIUM |
| Stagger card animations | YES | Not implemented | MEDIUM |
| Cursor trail | YES | NOT present | LOW |
| Hero text letter reveal | YES | NOT present | MEDIUM |
| Micro-hover interactions | YES | Partial | MEDIUM |

---

## 5. Files to Modify

| File | Change |
|------|--------|
| `django/core/templates/core/base.html` | Add/fix curtain HTML, curtain CSS, session guard JS |
| `django/core/templates/core/home.html` | Add `reveal-on-scroll` classes to sections; add hero letter-stagger markup |
| `django/core/static/core/css/` (if separate CSS files) | Add `animations.css` for scroll-reveal, micro-interactions |
| `django/core/static/core/js/` | Add `curtain.js` or inline in base.html |

---

## 6. Implementation Checklist

- [ ] Audit `base.html` — confirm whether `.curtain-left`/`.curtain-right` divs exist
- [ ] If curtain divs exist: find why animation is broken (JS timing? CSS overwrite?)
- [ ] If curtain divs missing: add them with correct CSS and JS sequence
- [ ] Implement `sessionStorage` skip guard for curtain (show only once per session)
- [ ] Add `IntersectionObserver` scroll-reveal for all major sections
- [ ] Apply `reveal-on-scroll` class to: section titles, package cards, gallery images, team cards
- [ ] Add micro-interaction CSS to: service cards, CTA buttons, nav links, gallery images
- [ ] Review hero text — implement letter-stagger reveal animation
- [ ] (Optional) Add cursor trail on desktop
- [ ] Test on mobile — ensure animations are reduced (`prefers-reduced-motion`)
- [ ] Test session guard — curtains only show on first visit, not on every page refresh
