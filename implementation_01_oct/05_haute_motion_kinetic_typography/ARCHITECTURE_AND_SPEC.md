# 05 — HAUTE MOTION & KINETIC TYPOGRAPHY

## 1. Specification & Standards
- **Inertial Momentum Scroll Engine**:
  - Integrated **Lenis** (`@studio-freight/lenis` v1.0.42) for smooth, luxurious momentum scrolling.
  - Duration: `1.2s`, Easing: `Math.min(1, 1.001 - Math.pow(2, -10 * t))`.
  - Synced with Three.js particle canvas animation and GSAP tickers.
- **Kinetic Numbers & Metrics**:
  - Live animated metric counters (`500+ Brides Blessed`, `18-Hour Radiance`, `100% Cry-Proof`).
  - Metrics roll upward smoothly as they scroll into view.
- **Magnetic Micro-Interactions**:
  - Soft magnetic cursor tracking on primary CTAs (`.btn-p`, `.btn-o`, `#chat-toggle`).

## 2. Technical Implementation Architecture
- Configured inside `django/core/templates/core/base.html`:
  ```javascript
  window.lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    orientation: 'vertical',
    smoothWheel: true
  });
  ```
- Graceful degradation: Respects `(prefers-reduced-motion: reduce)`.

## 3. Files Impacted
- `django/core/templates/core/base.html`
- `ANIMATIONS_AND_CSS_RESOURCES.md`
