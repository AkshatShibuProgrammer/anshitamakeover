# Granular Implementation Tasks: Pip Flight Kinematics, Draggable Relocation & Editorial Refinement

**Feature:** Pip Flight Kinematics, Draggable Relocation & Editorial Refinement  
**Plan Reference:** [PLAN-020](file:///.specify/plans/PLAN-020-pip-flight-drag-and-editorial-refinement.md)  
**Spec Reference:** [SPEC-020](file:///.specify/specs/SPEC-020-pip-flight-drag-and-editorial-refinement.md)  
**Status:** In Progress  

---

## Task Matrix & Dependencies

| Task ID | Component | Description | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **TSK-20-01** | Cleanup | Remove crawling ticker `.marquee-band` from `home.html` and related CSS | `[DONE]` | None |
| **TSK-20-02** | Copywriting | Replace exaggerated "Sacred Rituals/Metholegy" copy with authentic luxury bridal terminology | `[DONE]` | None |
| **TSK-20-03** | Showcase | Redesign Section 3B into pinned one-time split view: left photo transformation, right pricing & character | `[DONE]` | TSK-20-01 |
| **TSK-20-04** | Three.js | Implement organic 3D flight entrance for Pip with wing flutter and settling landing halo ring | `[DONE]` | None |
| **TSK-20-05** | Drag Engine | Implement pointer drag-and-drop system on Pip: flies with pointer movement, lands anywhere on screen with ring | `[DONE]` | TSK-20-04 |
| **TSK-20-06** | Verification | Verify smooth 60fps flight, draggable placement, one-time scroll pin, and editorial clean layout | `[DONE]` | TSK-20-01 to TSK-20-05 |

---

## Detailed Task Specifications

### TSK-20-01: Remove Crawling Ticker Marquee
- File: `django/core/templates/core/home.html`
- Delete lines 2725-2758 (`.marquee-band` forward and reverse tracks).

### TSK-20-02: Authentic Bridal Artistry Copywriting
- File: `django/core/templates/core/home.html`
- Update Section 4 rituals:
  - Header: `SIGNATURE STANDARDS / The 4 Pillars of Luxury Bridal Artistry`.
  - Step 01: `Dermal Prep & 18-Hour Cry-Proof Longevity`.
  - Step 02: `Cultural Heritage & Dupatta Draping`.
  - Step 03: `HD Airbrush & Flawless Complexion`.
  - Step 04: `Ceremonial Glow & Mandap Radiance`.

### TSK-20-03: Pinned One-Time Transformation & Pricing Split
- File: `django/core/templates/core/home.html`
- Transform Section 3B into `#artistry-disciplines-showcase`.
- Left column: High-resolution authentic bridal transformation before/after viewer.
- Right column: Clean pricing tiers with transparent inclusions and direct booking pills.
- JavaScript: Pin section during first scroll, reveal pricing cards sequentially, then permanently destroy the scroll lock.

### TSK-20-04: Pip 3D Flight Entrance & Landing Halo Ring
- File: `django/core/templates/components/concierge.html`
- Add `.cc-landing-ring` radiating CSS effect.
- Animate Pip flying into dock coordinates along 3D flight curve, with high wing flap rate settling down to idle.

### TSK-20-05: Draggable Flight Relocation
- File: `django/core/templates/components/concierge.html`
- Add draggable physics to `#cc-canvas`. On drag, Pip spreads wings, banks toward pointer movement vector, and lands with ring pulse when released.
