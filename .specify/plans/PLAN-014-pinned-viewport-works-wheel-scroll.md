# Implementation Plan: SPEC-014 — Pinned Viewport WorksWheel Scroll Engine

**Governing Spec:** `.specify/specs/SPEC-014-pinned-viewport-works-wheel-scroll.md`  
**Status:** Validated & Ready for Execution  

---

## 1. Phase Breakdown & Execution Path

### Phase 1: Viewport Flex Budgeting & Layout Styles
- File: `django/core/templates/core/home.html`
- Tasks:
  - Update `.works-wheel-section` CSS: `height: 100vh; height: 100dvh; display: flex; flex-direction: column; justify-content: space-between; padding: 16px 4vw; overflow: hidden; box-sizing: border-box;`.
  - Update `.home-gallery-header`: `flex-shrink: 0; max-height: 14vh; margin-bottom: 8px;`.
  - Update `.works-wheel-stage-container`: `flex: 1; height: auto; max-height: 76vh; position: relative; width: 100%; max-width: 1300px; margin: 0 auto;`.
  - Set `touch-action: pan-y;` on `#gallery-showcase` and `#worksWheelStage`.

### Phase 2: GSAP ScrollTrigger Native Pinning & Math Sync
- File: `django/core/templates/core/home.html`
- Tasks:
  - Wire `ScrollTrigger.create({ trigger: '#gallery-showcase', pin: true, start: 'top top', end: '+=3200', scrub: 0.5, anticipatePin: 1, onUpdate: ... })`.
  - Map progress $p \le 0.12 \rightarrow 0$, $p \in (0.12, 0.92) \rightarrow 1 + \text{norm} \times 7$, $p \ge 0.92 \rightarrow 8$.
  - In `computeMetrics()`, calculate card dimensions relative to `stage.clientHeight` so cards scale dynamically to fit available stage height on 768px screens.
  - Bind `ScrollTrigger.refresh()` on window resize.

### Phase 3: Automated Browser Testing & Verification
- Script: `scratch/verify_works_wheel_scroll.py`
- Tasks:
  - Test at 1440x900 and 1366x768 viewports.
  - Verify pin lock at `top: 0` and unpin after 3200px scroll.
  - Verify cards remain fully within viewport without vertical clipping.
  - Capture automated screenshots at progress 0.05, 0.50, and 0.95.
