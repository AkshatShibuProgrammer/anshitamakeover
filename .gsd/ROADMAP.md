# ROADMAP.md — Anshita Makeover 3D Atelier & Spec-Driven Development

## Active Milestone: 3D Pixar AI Mascot & Hero Studio Portrait Showcase

### Milestone 1: 3D Pixar Cute Kid AI Concierge (`Asha`) — [SPEC-003]
- [ ] **Phase 1: Procedural Pixar 3D Character Mesh & Rigging** (TASK-003.1, TASK-003.2)
  - Replace mechanical geometric disc/ring in `base.html` with cute Pixar child character (Head, chubby blushing cheeks, stylized hair, miniature gold maang tikka, royal burgundy velvet cape).
  - High-definition round Disney cartoon eyes with deep amber irises, black pupils, and glossy catchlights.
- [ ] **Phase 2: Cursor Kinematics & Living Micro-Motions** (TASK-003.3, TASK-003.4, TASK-003.5)
  - Smooth 3D pupil tracking and head yaw/pitch lerp following the mouse cursor across screen coordinates.
  - Organic double-blinks (every 3.5–6s), gentle breathing idle, and joyful hover bounce.
- [ ] **Phase 3: Visual & Interactive Validation** (TASK-003.6)
  - Playwright visual tests capturing cursor deflection at multiple coordinates.

### Milestone 2: Hero Studio Portrait Showcase & Three.js Atmospheric Lighting — [SPEC-004]
- [ ] **Phase 4: Seamless Image Blending & Viewport Optimization** (TASK-004.1, TASK-004.2, TASK-004.3)
  - Apply multi-stop feathered directional mask to bridal portrait, eliminating hard vertical split lines.
  - Re-anchor hero container with centered flex alignment so CTAs (`लुकबुक` / `तारीख आरक्षित करें`) and all editorial text are 100% visible above the fold on all standard laptop displays.
  - Clean up stray indicator dots/rings under logo and awkward ghost watermarks.
- [ ] **Phase 5: Three.js Studio Softbox Rim Lighting & 2.5D Parallax** (TASK-004.4, TASK-004.5, TASK-004.6)
  - Cursor-following Three.js studio softbox light grazing gold jewelry and lehenga.
  - 2.5D spatial depth tilt on mouse move and floating golden stardust particles.
  - Royal Devanagari typography refinement.
- [ ] **Phase 6: Multi-Device Verification** (TASK-004.7)
  - Playwright automated verification across 1366x768, 1440x900, and 1920x1080 viewports.

### Milestone 3: 3D Cylindrical Album Orbit & Haute Motion Engine — [SPEC-006]
- [x] **Phase 7: Lenis Smooth Inertial Scrolling & Engine Sync**
  - Integrated Lenis smooth scroll engine into `base.html`.
  - Synchronized scroll updates with Three.js particle canvas and GSAP ScrollTrigger ticker.
- [x] **Phase 8: 3D Cylindrical Orbit Carousel Implementation**
  - Replaced 2D horizontal gallery track with hardware-accelerated 3D cylindrical stage (`transform-style: preserve-3d`).
  - Trigonometric radial card distribution: $R = \frac{W/2}{\tan(\pi/N)} + \text{offset}$, auto-orbit loop (~0.14°/frame), mouse drag, touch swipe, inertia damping, and spotlight elevation.
- [x] **Phase 9: Seamless Card-to-Suite Transformation**
  - 3D album cards connect to hybrid lookbook suites with drag distance threshold protection (clicks only trigger if drag < 12px).
- [x] **Phase 10: Demilie Craftsmanship Storytelling & Automated Visual Verification**
  - Implemented the 4 Sacred Rituals of Royal Bridal Radiance in the About section (Skin Metallurgy, Sacred Geometry, Velvet Complexion, Royal Starlight Seal).
  - Validated with automated Playwright browser test across desktop (1440px) and mobile (375px).

---

## Future Milestones
- **Milestone 4**: Oracle Cloud Always-Free Deployment & Cloudflare Edge Optimization.
