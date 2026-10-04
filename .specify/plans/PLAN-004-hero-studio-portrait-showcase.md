# Implementation Plan: Hero Studio Portrait Showcase & Three.js Atmospheric Experience

**Plan ID:** `PLAN-004`  
**Related Spec:** [SPEC-004](file:///.specify/specs/SPEC-004-hero-studio-portrait-showcase.md)  
**Target Files:**
- `django/core/templates/core/home.html`
- `django/core/templates/core/base.html` (for `#three-bg` canvas interaction)

---

## 1. Technical Architecture & Visual Overhaul

### A. Seamless Cinematic Image Blending
- Apply a multi-stage directional mask to `.am-hero__split-left`:
  ```css
  -webkit-mask-image: linear-gradient(to right, black 0%, black 70%, rgba(0,0,0,0.3) 90%, transparent 100%);
  mask-image: linear-gradient(to right, black 0%, black 70%, rgba(0,0,0,0.3) 90%, transparent 100%);
  ```
- Layer a subtle radial dark-amber vignette on the portrait container to eliminate any harsh edge cutoffs.

### B. Proportional Viewport & CTA Protection
- Adjust `.am-hero__split-right` and `.am-hero__split`:
  - Set `min-height: calc(100vh - 84px)` with flex centering `justify-content: center`.
  - Tighten vertical line-heights and margin spacings on `.am-hero__heading` and `.am-hero__cities-top`.
  - Ensure both CTA buttons (`लुकबुक` / `तारीख आरक्षित करें`) maintain clear margin above the viewport bottom on laptop screens (720px–900px height).

### C. Clean Header Architecture
- Remove stray rogue floating rings and orphaned indicator dots hovering under the brand logo.
- Consolidate slide progress indicators into an elegant, discreet bottom-center pill dock.

### D. Three.js Interactive Studio Softbox & Parallax
- Update `#three-bg` canvas script:
  - Add mouse-reactive directional spotlight `PointLight(0xFFEED6, 2.8, 1200)` simulating a physical photographer's softbox grazing the portrait.
  - Apply 2.5D mouse parallax tilt (`transform: perspective(1000px) rotateY(...) rotateX(...)`) to the bridal image frame.
  - Implement golden floating stardust with subtle velocity drag on cursor motion.
