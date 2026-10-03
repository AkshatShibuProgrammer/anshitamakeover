# Feature Specification: Pinned Viewport WorksWheel Scroll Engine

**Feature Branch:** `arena/01a0d489-anshitamakeover`  
**Spec ID:** `SPEC-014`  
**Governing Document:** `.specify/memory/constitution.md`  
**Status:** Architecture Refined & Gap-Mitigated  
**Estimated Complexity:** Medium-High  

---

## 1. Executive Summary & Problem Description

### The Problem
On the homepage, standard vertical scroll events cause the browser to scroll past the WorksWheel section without turning the 3D drum. The user explicitly requires a pinned luxury editorial scroll experience (inspired by Stanzza, Juan Mora, and Apple), where the stage locks to the viewport and scrolling directly powers the 3D rotation before releasing to the rest of the page.

### Forensic Gap Mitigations Incorporated
1. **GSAP ScrollTrigger Native Pinning (`pin: true`)**:
   - Instead of manual CSS `450vh` wrappers that collide with Lenis, the section utilizes native GSAP `ScrollTrigger.create({ trigger: '#gallery-showcase', pin: true, start: 'top top', end: '+=3200', scrub: 0.5 })`.
   - GSAP automatically injects and manages the `.pin-spacer` element, synchronizing flawlessly with the existing Lenis ticker on `base.html` line 8160 (`ScrollTrigger.update()`) and preventing 1-frame lag or scroll stutter.
2. **Elastic Viewport Flex Budgeting (768px Laptop Protection)**:
   - `#gallery-showcase` is structured as a strict `100vh` / `100dvh` flex column:
     - Header (`.home-gallery-header`): `max-height: 14vh; padding: 12px 4vw;`.
     - Stage (`.works-wheel-stage-container`): Elastic flex center occupying `76vh`, with internal `computeMetrics()` dynamically scaling card dimensions so no clipping occurs on 768px or 900px displays.
     - Hint (`.works-wheel-hint`): Sleek bottom bar occupying `5vh`.
3. **Rest State Deadband Buffer**:
   - $P \in [0.00, 0.12]$: Holds the 3D ring steady at $turn = 0$ (framing "Works '26") so visitors can appreciate the at-rest layout.
   - $P \in [0.12, 0.92]$: Maps to $turn = 1 \dots 8$, cycling through all portfolio cards in uncropped portrait perspective (`object-fit: contain`) and highlighting the active side title index.
   - $P \in [0.92, 1.00]$: Settles on the final card before releasing the sticky pin to smoothly transition to `#bridal-transformation`.
   - Reverse scroll smoothly unwinds the drum back to item 0 and the resting ring.
4. **Touch & Gesture Conflict Resolution**:
   - `touch-action: pan-y;` on the stage ensures vertical touch gestures scrub the pin runway naturally, while horizontal swipes allow manual card orbit.

---

## 2. Technical Architecture & DOM Schema

```html
<section class="home-gallery-showcase works-wheel-section" id="gallery-showcase" aria-label="Haute Bridal Repertoire & 3D Works Wheel">
  <!-- Header: Compact 14vh flex row -->
  <div class="home-gallery-header">
    <div class="home-gallery-title-wrap">
      <span class="looks-eyebrow">CINEMATIC REPERTOIRE · 4K STUDIO</span>
      <h2 class="home-gallery-title">Curated Lookbook & Works Wheel</h2>
      <p class="home-gallery-sub">Authentic bride transformations & sacred vivah rituals sculpted by Anshita Sinha.</p>
    </div>
    <div class="home-gallery-controls">
      <button type="button" class="hg-nav-arrow" id="wheelPrevBtn" aria-label="Previous Look">‹</button>
      <button type="button" class="hg-nav-arrow" id="wheelNextBtn" aria-label="Next Look">›</button>
      <a href="/gallery/" class="hg-explore-all-btn">
        <span>Enter 4K Cinema Studio</span>
        <span>→</span>
      </a>
    </div>
  </div>

  <!-- Central Elastic 76vh Stage -->
  <div class="works-wheel-stage-container" id="worksWheelContainer">
    <div class="works-wheel-stage" id="worksWheelStage" tabindex="0" role="listbox" aria-label="Works Wheel">
      <div class="works-wheel-pivot" id="worksWheelPivot">
        <!-- 8 Uncropped Cards in 3D cylindrical drum -->
      </div>
      <div class="works-wheel-ring-label" id="worksWheelRingLabel">Works '26</div>
      <div class="works-wheel-front-title" id="worksWheelFrontTitle"></div>
      <ol class="works-wheel-index" id="worksWheelIndex"></ol>
    </div>
  </div>

  <!-- Bottom Hint: 5vh -->
  <div class="works-wheel-hint">
    <span>✦ SCROLL DOWN TO TURN 3D PORTFOLIO DRUM · DRAG TO BROWSE ✦</span>
  </div>
</section>
```

### GSAP ScrollTrigger Integration Algorithm
```javascript
if (typeof ScrollTrigger !== 'undefined') {
  ScrollTrigger.create({
    trigger: '#gallery-showcase',
    pin: true,
    start: 'top top',
    end: '+=3200',
    scrub: 0.5,
    anticipatePin: 1,
    onUpdate: (self) => {
      const p = self.progress;
      let targetTurn = 0;
      if (p <= 0.12) {
        targetTurn = 0; // Ring at rest
      } else if (p < 0.92) {
        const drumProgress = (p - 0.12) / (0.92 - 0.12);
        targetTurn = 1 + drumProgress * (last - 1);
      } else {
        targetTurn = last;
      }
      target.current = targetTurn;
    }
  });
}
```

---

## 3. Verification Criteria
- [ ] Section pins smoothly at `top: 0` when scrolling down without layout jitter.
- [ ] 12% deadband buffer allows viewing the at-rest ring framing "Works '26".
- [ ] Progressive scroll advances cards 1 to 8 without image cropping (`object-fit: contain`).
- [ ] Active title in side index menu highlights in gold corresponding to the front card.
- [ ] At end of pin distance, page unpins cleanly and flows into `#bridal-transformation`.
- [ ] Upward scroll rewinds drum rotation cleanly back to resting ring.
