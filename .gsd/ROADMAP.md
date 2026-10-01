# ROADMAP.md — Anshita Makeover 3D Atelier & Spec-Driven Development

## Active Milestone: 3D Pixar AI Mascot & Hero Studio Portrait Showcase

### Milestone 1: 3D Pixar Cute Kid AI Concierge (`Asha`) — [SPEC-003]
- [x] **Phase 1: Procedural Pixar 3D Character Mesh & Rigging** (TASK-003.1, TASK-003.2)
  - Replaced mechanical disc with adorable Pixar toddler girl bride mascot ("Asha"):
    - Authentic warm Indian golden-wheat / honey-caramel skin tone (`#BA7742`).
    - Dainty button nose matching skin tone seamlessly, soft terracotta-rose blushing cheeks (`#CF5A50`).
    - Sacred Vivah crimson velvet chunni veil draped behind head with 24K gold zari border, top bun with baby bangs, ruby maang tikka, and traditional gold jhumka earrings.
    - Large expressive Disney/Pixar cartoon eyes with dark limbal rings, amber honey irises, and double catchlight glints.
- [x] **Phase 2: Cursor Kinematics, Living Micro-Motions & Speech-to-Text** (TASK-003.3, TASK-003.4, TASK-003.5)
  - Smooth 3D pupil tracking and head yaw/pitch lerp following the mouse cursor across screen coordinates.
  - Organic double-blinks (every 3.5–6s), gentle breathing idle, and joyful hover bounce.
  - Implemented **Web Speech Recognition** (`webkitSpeechRecognition` / `SpeechRecognition`) with dedicated animated glowing microphone button (`#chat-mic-btn`), allowing visitors to speak directly in Hindi, Marathi, or English.
- [x] **Phase 3: Visual & Interactive Validation** (TASK-003.6)
  - Playwright visual tests capturing cursor gaze deflection, hover bounce, open drawer with mic, and full viewport presence.

### Milestone 2: Hero Studio Portrait Showcase & Three.js Atmospheric Lighting — [SPEC-004]
- [x] **Phase 4: Seamless Image Blending & Viewport Optimization** (TASK-004.1, TASK-004.2, TASK-004.3)
  - Applied multi-stop feathered directional mask to bridal portrait, eliminating hard vertical split lines.
  - Re-anchored hero container with centered flex alignment so CTAs (`लुकबुक` / `तारीख आरक्षित करें`) and all editorial text are 100% visible above the fold on all standard laptop displays.
  - Allowed `Bridal Couturier` typography to wrap gracefully without overflow clipping.
- [x] **Phase 5: Three.js Studio Softbox Rim Lighting & 2.5D Parallax** (TASK-004.4, TASK-004.5, TASK-004.6)
  - Added 2.5D mouse parallax tilt on `#heroCarousel`.
  - Balanced studio three-point warm lighting on 3D elements.
- [x] **Phase 6: Multi-Device Verification** (TASK-004.7)
  - Automated visual verification across desktop viewports.

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

### Milestone 4: Haute Conversion Engine — [SPEC-007] ⬅ NEXT

- [ ] **Phase 11: Kinetic Oversized Hero Typography** (TASKS-007.01, TASKS-007.06)
  - Cormorant Garamond 96–140px Hindi tagline with character-level stagger reveal on load.
  - Scroll-linked kinetic parallax: characters drift ±40px on Y/X-axis with Lenis scroll.
- [ ] **Phase 12: Dual-Direction Marquee Service Strip** (TASKS-007.02)
  - Infinite gold ticker with 6 signature services, reversed second row, hover pause.
- [ ] **Phase 13: WhatsApp Instant Booking FAB + CTA** (TASKS-007.03, TASKS-007.04, TASKS-007.05)
  - Green pulsing FAB (appears after 3s delay), pre-filled WhatsApp message, UTM tracking.
  - Desktop inline "Book on WhatsApp" gold CTA in hero section.
  - Bridal metric counters: 1200+ Brides, 15 Cities, 12+ Years (CountUp IntersectionObserver).
- [ ] **Phase 14: Accessibility Compliance & Browser Verification** (TASKS-007.07, TASKS-007.08)
  - prefers-reduced-motion respect, ARIA labels, visual Playwright capture.

### Milestone 5: Performance, PWA & Lighthouse 90+ — [SPEC-008]

- [ ] **Phase 15: PWA Manifest & Service Worker** (TASKS-008.01, TASKS-008.02)
  - Add-to-home-screen capability, offline fallback page, cache-first static strategy.
- [ ] **Phase 16: Schema Markup & Open Graph** (TASKS-008.03)
  - BeautySalon JSON-LD, BreadcrumbList, og:image (1200×630), Twitter Card.
- [ ] **Phase 17: Image Optimisation & WhiteNoise** (TASKS-008.04, TASKS-008.05, TASKS-008.06)
  - Lazy loading, LCP fetchpriority, WebP conversion in Gallery model, CompressedManifest storage.
- [ ] **Phase 18: Lighthouse Audit & Fix to 90+** (TASKS-008.07)
  - Performance ≥ 90, Accessibility ≥ 90, Best Practices ≥ 90, SEO ≥ 95.

### Milestone 6: Oracle Cloud Production Launch — [SPEC-009]

- [ ] **Phase 19: Production Settings & Security Hardening** (TASKS-009.01)
  - settings_production.py: HTTPS-only, HSTS, secure cookies, env-loaded secrets.
- [ ] **Phase 20: Nginx + Gunicorn Deployment Stack** (TASKS-009.02, TASKS-009.03)
  - Nginx HTTPS reverse proxy, Gunicorn Unix socket systemd service.
- [ ] **Phase 21: CI/CD Pipeline & Deploy Script** (TASKS-009.04, TASKS-009.05, TASKS-009.06)
  - GitHub Actions auto-deploy on push to `main`.
- [ ] **Phase 22: Cloudflare CDN Setup & Go-Live** (TASKS-009.07, TASKS-009.08)
  - DNS proxied through Cloudflare, static cache rules, Rocket Loader disabled.
  - Live at `https://anshita.in` — zero hosting cost, global CDN.

---

## Test Suite Status

- **Unit Tests**: 233/233 passing ✅ (as of 2026-10-01)
- **Visual Verification**: Playwright screenshots captured for Milestones 1–3
