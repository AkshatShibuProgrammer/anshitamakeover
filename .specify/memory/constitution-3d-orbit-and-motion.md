# Project Constitution Addendum: Haute Couture Motion & 3D Album Experience

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Sub-System:** 3D Cylindrical Orbit Showcase, Smooth Inertial Physics & Haute Editorial Flow  
**Standard:** Spec-Driven Development (SDD) via Spec Kit & GSD (Get Stuff Done)  
**Parent Constitution:** `.specify/memory/constitution.md`

---

## 1. Cylindrical 3D Album Orbit Standard (Rotating Image Gallery)

### 1.1 True 3D Spatial Geometry
- **Geometry:** Featured lookbooks and bridal albums MUST be positioned on a 3D cylindrical manifold using `perspective`, `transform-style: preserve-3d`, and exact radial trigonometry:
  $$\theta = \frac{360^\circ}{N}, \quad Z_{\text{radius}} = \frac{W / 2}{\tan(\theta / 2)} + \text{depth\_offset}$$
  where $N$ is the number of active featured albums and $W$ is the card width.
- **Prohibition:** Flat 2D horizontal flex tracks with basic overflow scrolling (`scrollBy(340)`) are strictly forbidden as the primary homepage lookbook experience.
- **Performance:** All rotational transforms (`rotateY`, `translateZ`) must operate strictly on GPU compositor layers using hardware acceleration.

### 1.2 Interactive Physics & Touch Mechanics
- **Momentum Drag:** The cylinder must support mouse drag, wheel scroll, and mobile touch swipe with inertia damping (velocity lerp + friction coefficient ~0.94).
- **Auto-Orbit:** When idle, the cylinder auto-rotates at an elegant, slow rate (~0.2° per frame).
- **Spotlight Hover:** Hovering any album card pauses the auto-orbit, elevates the card forward (`translateZ` boost), applies a warm gold border glow (`#D4AF37`), and reveals the "▶ Watch Reel / Explore Album" action pill.
- **Card-to-Suite Transformation:** Clicking an album card must trigger a seamless camera zoom / card expansion into the Hybrid Album Suite / Theater Viewer, maintaining visual continuity without jarring page jumps.

---

## 2. Motion Physics & Smooth Scrolling Standard

### 2.1 Inertial Smooth Scrolling (Lenis)
- **Mandate:** Smooth momentum scrolling must be powered by **Lenis** (`lenis.min.js`), syncing window scrolling directly with Three.js coordinate space and GSAP timelines.
- **Accessibility:** Must respect `prefers-reduced-motion` and seamlessly fallback to standard browser scrolling on low-power devices without breaking touch accessibility.

### 2.2 Kinetic Editorial Typography & Numerical Metrics
- **Dynamic Counters:** Numbers, pricing packages (`₹58,000 → ₹45,000`), and trust metrics (`500+ Brides Blessed`) must animate via kinetic rolling digit counters or GSAP scrubbed tweens when scrolled into the viewport.
- **Magnetic Micro-Interactions:** Primary CTAs must implement subtle magnetic cursor attraction physics on desktop viewports.

---

## 3. Demilie-Inspired Craftsmanship Storytelling

### 3.1 Step-by-Step Editorial Rituals
- The About Us and Craftsmanship presentation must be structured as an immersive 4-stage bridal transformation journey:
  1. *Skin Metallurgy & Cry-Proof Priming* (18-Hour longevity, sweat-proof dermis prep)
  2. *Sacred Heritage Geometry* (Hand-painted Banarasi Chandan & Mukut balance)
  3. *Velvet Complexion & Jewel Balancing* (Polki, Emerald & Crimson harmony)
  4. *The Royal Starlight Reveal* (Masterclass airbrush seal & 4K cinematic glow)
- Elements must gracefully reveal on scroll with soft gold light washes and parallax depth.

---

## 4. Governance & Verification Protocol
- Every phase must pass:
  1. `python manage.py check` & Django test suite.
  2. Automated Playwright browser verification across mobile (375px), laptop (1366px), and desktop (1920px).
  3. Clean Git working tree with zero uncommitted drift.
