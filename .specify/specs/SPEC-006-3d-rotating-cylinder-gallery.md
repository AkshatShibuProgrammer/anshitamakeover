# SPEC-006: 3D Rotating Cylindrical Album Showcase & Haute Motion Engine

**Status:** Draft / Active  
**Milestone:** Haute Motion & 3D Album Experience  
**Constitutions:** `.specify/memory/constitution.md`, `.specify/memory/constitution-3d-orbit-and-motion.md`

---

## 1. Overview & Objective
Replace the flat 2D horizontal gallery track on the homepage with an interactive **3D Cylindrical Orbit Carousel** (as demonstrated in user-provided GIF and Art Lebedev / Juan Mora benchmarks). Enable inertial momentum scrolling via **Lenis**, kinetic rolling numbers for bridal metrics, and a Demilie-inspired 4-step craftsmanship storytelling experience.

---

## 2. User Stories & Acceptance Criteria

### 2.1 Story: 3D Cylindrical Album Orbit
* **As a bride visiting the website**, I want to see a luxurious, floating 3D circular ring of bridal albums rotating gracefully so that I feel immersed in haute couture wedding artistry.
* **Acceptance Criteria:**
  - [ ] 6 to 10 active featured albums are arrayed equidistant in 3D cylindrical space (`perspective: 1400px; transform-style: preserve-3d;`).
  - [ ] Supports auto-orbit (~0.2° per frame) when idle.
  - [ ] Supports mouse drag, touch swipe, and wheel scrub with inertial velocity damping.
  - [ ] Hovering a card pauses orbit, scales it towards the viewer, and highlights it with a gold ambient glow.
  - [ ] Fully responsive on mobile viewports (cylinder radius and card width dynamically scale).

### 2.2 Story: Seamless Album Suite Expansion
* **As a bride**, when I click an album card in the 3D cylinder, I want it to expand seamlessly into the Hybrid Album Suite / Theater Reel Viewer without a jarring page reload.
* **Acceptance Criteria:**
  - [ ] Clicking a card triggers an expansion animation into the hybrid modal or smooth navigation to `{% url 'gallery' %}?album=<slug>`.
  - [ ] Displays high-definition multi-photo reel, client details, and "Reserve Look" CTA.
  - [ ] Pressing `Esc` or the close button smoothly restores the 3D gallery view.

### 2.3 Story: Studio Freight Lenis Smooth Scrolling
* **As a visitor**, I want smooth, cinematic momentum scrolling throughout the entire site.
* **Acceptance Criteria:**
  - [ ] Lenis momentum scrolling initialized cleanly in `base.html`.
  - [ ] Synced with Three.js particle canvas on `#bg-canvas` and GSAP timelines.
  - [ ] Bypassed automatically when `prefers-reduced-motion: reduce` is active.

### 2.4 Story: Demilie-Inspired Craftsmanship Rituals
* **As a client evaluating Anshita Studio**, I want to understand the rigorous 4-step artistry behind an 18-hour cry-proof bride.
* **Acceptance Criteria:**
  - [ ] Dedicated interactive section detailing the 4 sacred rituals (Skin Metallurgy, Heritage Chandan, Velvet Harmony, Royal Starlight Reveal).
  - [ ] Scroll-triggered reveals with soft gold ambient lighting.
