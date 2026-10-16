# Technical Plan: Pip Flight Kinematics, Draggable Relocation & Editorial Refinement

**Spec ID Reference:** `SPEC-020`  
**Parent Constitution:** `.specify/memory/constitution.md`, `.specify/memory/constitution-pip-mascot-concierge.md`  
**Target Files:**
- `django/core/templates/components/concierge.html`
- `django/core/templates/core/home.html`
- `django/core/templates/core/base.html`
**Status:** In Execution  

---

## 1. Technical Architecture & Component Tree

```
                           [Visitor Screen]
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
[Draggable Pip Concierge]                       [Artistic Disciplines Split]
├── Fly-in Entrance Timeline                    ├── Left: Authentic Look Photo
│   - Arced 3D Bezier curve                     │   (Clean luxury transformation)
│   - Rapid wing flutter (flap=2.4)             ├── Right: Clear Pricing & Inclusions
│   - Landing gold pulse ring                   └── One-Time Pinned Scroll Guard
├── Pointer Drag-and-Drop System                    (Unlocks permanently after 1 view)
│   - PointerDown -> Take-off flight stance
│   - PointerMove -> Pip follows pointer, tilts
│   - PointerUp   -> Glide-down landing & ring
└── Settled Chatbot Anchor
```

---

## 2. File-by-File Blueprint

### 2.1 `django/core/templates/components/concierge.html`
1. **Fly-In Entrance & Landing Halo Ring**:
   - Add `.cc-landing-ring` radiating animation element into `#cc-stage`.
   - Update `peek()` and `comeOut()` into a unified `flyInAndSettle()` choreography:
     - Pip starts slightly off-screen (`x = 0.8`, `y = 1.2`, `z = 1.5`, `rotation.z = -0.35`).
     - Wings flap vigorously (`cur.flap = 2.4`).
     - Smooth GSAP tween curves Pip down into dock position (`x = 0`, `y = 0`, `z = 0`, `rotation.z = 0`).
     - On touchdown: Trigger `.cc-landing-ring` CSS pulse and wing flutter relaxation (`cur.flap = 1.0`).
2. **Draggable Relocation Engine**:
   - Attach pointer listeners to `#cc-canvas`:
     - `pointerdown`: Capture initial pointer offset, set `isDragging = true`, Pip triggers flight mode (`cur.setEmotion('shyFly')`, `cur.flap = 2.2`).
     - `pointermove`: Update `#cc-stage` CSS `left` / `top` / `bottom` / `right` so stage smoothly follows pointer; calculate pointer delta $dx, dy$ and tilt Pip (`dockRig.rotation.z = -dx * 0.02`).
     - `pointerup`: Drop Pip at new location, save coordinates in `localStorage`, trigger landing ring pulse, Pip returns to idle welcoming stance.

### 2.2 `django/core/templates/core/home.html`
1. **Purge Ticker Marquees**:
   - Remove `<div class="marquee-band">...</div>` (lines 2725-2758) entirely.
2. **Replace Exaggerated Rituals with Authentic Artistry Disciplines**:
   - In Section 4 / Craftsmanship, replace:
     - `Skin Metallurgy` $\rightarrow$ **18-Hour Dermal Prep & Longevity**
     - `Sacred Geometry` $\rightarrow$ **Cultural Heritage & Dupatta Draping**
     - `Velvet Complexion` $\rightarrow$ **HD Airbrush & Flawless Finish**
     - `Royal Starlight Seal` $\rightarrow$ **Mandap Radiance & Cinematic Glow**
3. **Refactor Section 3B into Pinned One-Time Transformation & Pricing Split**:
   - Left side: High-definition before/after luxury transformation image.
   - Right side: Clear service pricing packages (Bridal Couture ₹25,000, Reception Glamour ₹15,000, Party Makeover ₹8,000) with direct booking actions.
   - Implement one-time pin: Uses GSAP ScrollTrigger `pin: true`, `once: true`. Once scrolled through, the pin is permanently killed and standard scroll resumes effortlessly.

---

## 3. Verification & Acceptance Steps
1. Run `python manage.py check` to verify template integrity.
2. Verify in browser that Pip flies into view with wings flapping, lands with expanding golden ring, and can be dragged anywhere on the screen.
3. Confirm marquee ticker text is completely gone.
4. Confirm Section 3B pins once, transitions smoothly to pricing, and unpins cleanly without trapping the visitor.
