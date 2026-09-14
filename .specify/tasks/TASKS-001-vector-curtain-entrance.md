# Granular Implementation Tasks: Haute Couture Vector Entrance

**Feature:** Vector Entrance & Dual-Curtain System  
**Plan Reference:** [PLAN-001](file:///.specify/plans/PLAN-001-vector-curtain-entrance.md)  
**Spec Reference:** [SPEC-001](file:///.specify/specs/SPEC-001-vector-curtain-entrance.md)  
**Status:** Ready for Implementation

---

## Task Matrix & Dependencies

| Task ID | Component | Description | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **TSK-01** | Brand Asset | Generate / code high-precision luxury AM SVG crest with continuous vector paths | `[TODO]` | None |
| **TSK-02** | Styles | Implement `.curtain-left`, `.curtain-right` GPU transforms & `cubic-bezier` easing | `[TODO]` | None |
| **TSK-03** | Styles | Implement SVG stroke-dashoffset drawing keyframes & gold metallic gradient | `[TODO]` | TSK-01 |
| **TSK-04** | Template | Refactor `base.html` preloader: purge `<video>`, insert dual curtains & SVG stage | `[TODO]` | TSK-01, TSK-02 |
| **TSK-05** | Logic | Implement inline head session guard to eliminate FOUC on route navigation | `[TODO]` | TSK-04 |
| **TSK-06** | Logic | Add `Escape` key and click-to-skip fail-safe handler | `[TODO]` | TSK-04 |
| **TSK-07** | Three.js | Link curtain split event to WebGL background shader wave expansion | `[TODO]` | TSK-04 |
| **TSK-08** | Verification | Visual QA via browser subagent, verifying 60+ FPS and session persistence | `[TODO]` | TSK-01 to TSK-07 |

---

## Detailed Task Specifications

### TSK-01: Create Luxury Vector Monogram SVG
- File: `anshita_project/core/static/core/images/brand/anshita_crest.svg`
- Paths: Outer royal medallion border, inner calligraphy "AM" monogram, ornamental floral filigree, luxury subtitle.
- Attributes: `vector-effect="non-scaling-stroke"`, clean `pathLength` / stroke parameters.

### TSK-02 & TSK-03: CSS Curtain Physics & Vector Stroke Animation
- File: `anshita_project/core/static/core/css/style.css`
- Add `.preloader-curtain` with `will-change: transform; transition: transform 1.2s cubic-bezier(0.77, 0, 0.175, 1)`.
- Keyframe `@keyframes crestDraw` calculating dynamic stroke offset.

### TSK-04 & TSK-05: Template Restructure & Zero-Flicker Session Guard
- File: `anshita_project/core/templates/core/base.html`
- Remove video element, poster image, and video play listeners.
- Add dual curtain divs: `<div class="preloader-curtain curtain-left"></div><div class="preloader-curtain curtain-right"></div>`.
- Insert instant head script to suppress preloader DOM if `sessionStorage.getItem('anshita_preloader_seen') === 'true'`.

### TSK-06 & TSK-07: Interactive Bypass & Shader Handoff
- Add `skipPreloader()` triggerable via `keydown` (key === 'Escape') or clicking `.preloader-skip-btn`.
- Trigger Three.js uniform pulse `window.triggerEntranceBurst()` when curtains part.
