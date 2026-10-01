# TASKS-006: 3D Cylindrical Orbit Album Showcase & Motion Tasks

**Spec:** `.specify/specs/SPEC-006-3d-rotating-cylinder-gallery.md`  
**Plan:** `.specify/plans/PLAN-006-3d-rotating-cylinder-gallery.md`  
**Constitution:** `.specify/memory/constitution-3d-orbit-and-motion.md`

---

## Task Checklist

### Phase 1: Smooth Inertial Scrolling Engine
- [x] **TASK-006.1**: Load Lenis v1.0.42 smooth scroll engine in `base.html` with battery/low-power optimization and `prefers-reduced-motion` check.
- [x] **TASK-006.2**: Synchronize Lenis scroll ticker with Three.js particle ripple canvas and GSAP ticker.

### Phase 2: 3D Cylindrical Geometry & Radial Matrix
- [x] **TASK-006.3**: Implement `#orbitGalleryStage` with `perspective: 1200px` and `#orbitGalleryRotor` with `transform-style: preserve-3d`.
- [x] **TASK-006.4**: Calculate dynamic radius $R = \frac{W / 2}{\tan(\pi / N)} + 30\text{px}$ and distribute album cards uniformly around $360^\circ$.
- [x] **TASK-006.5**: Add auto-orbit loop (~0.14°/frame), mouse drag, touch swipe, and inertia velocity damping.

### Phase 3: Interactive Card Elevation & Lookbook Integration
- [x] **TASK-006.6**: Add spotlight hover state: pause auto-orbit, elevate card with `translateZ` boost, and reveal 24K gold border glow.
- [x] **TASK-006.7**: Implement drag distance protection ($< 12\text{px}$) to seamlessly transition clicked card into Hybrid Lookbook Suite.

### Phase 4: Demilie Rituals & Empirical Verification
- [x] **TASK-006.8**: Implement the 4 Sacred Rituals of Royal Bridal Radiance in the About section.
- [x] **TASK-006.9**: Execute automated visual Playwright test across mobile (375px), laptop (1366px), and desktop (1920px).
