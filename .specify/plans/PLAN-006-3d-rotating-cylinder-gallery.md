# PLAN-006: 3D Cylindrical Orbit Album Showcase & Motion Architecture

**Spec:** `.specify/specs/SPEC-006-3d-rotating-cylinder-gallery.md`  
**Constitution:** `.specify/memory/constitution-3d-orbit-and-motion.md`  
**Standard:** Spec Kit & GSD

---

## 1. Technical Architecture & Trigonometry

### 1.1 Cylindrical Radial Geometry
Given $N$ active cards and card width $W$ (e.g. $280\text{px}$ on desktop, $190\text{px}$ on mobile):
$$\theta = \frac{360^\circ}{N}, \quad \text{Radius } R = \frac{W / 2}{\tan(\pi / N)} + 30\text{px}$$
Each card $i \in [0, N-1]$ receives a static transform:
$$\mathbf{T}_i = \text{rotateY}(i \cdot \theta) \cdot \text{translateZ}(R)$$
The parent container `#cylinderCarousel` rotates around the Y-axis:
$$\mathbf{T}_{\text{carousel}} = \text{rotateY}(\text{currentAngle}) \cdot \text{rotateX}(-4^\circ)$$
A slight negative tilt on X ($-3^\circ$ to $-5^\circ$) gives the authentic 3D isometric perspective shown in the user's reference GIF.

### 1.2 Drag & Inertial Damping Loop
```javascript
let currentAngle = 0;
let targetAngle = 0;
let velocity = 0;
let isDragging = false;
let isHovered = false;

function orbitLoop() {
  if (!isDragging && !isHovered) {
    currentAngle += 0.18; // auto orbit
  }
  // lerp towards target during drag or inertia
  currentAngle += velocity;
  velocity *= 0.94; // friction
  cylinderEl.style.transform = `rotateX(-4deg) rotateY(${currentAngle}deg)`;
  requestAnimationFrame(orbitLoop);
}
```

---

## 2. Phased Implementation Breakdown

### Phase 1: Smooth Scroll & Animation Foundation (Lenis + GSAP)
* Integrate `lenis.min.js` into `django/core/templates/core/base.html`.
* Connect Lenis `raf` loop to Three.js `#bg-canvas` renderer.
* Add prefers-reduced-motion safety guard.

### Phase 2: 3D Cylindrical Album Orbit Component
* In `django/core/templates/core/home.html`, replace `#homeGalleryTrack` flex list with the 3D Cylindrical Orbit viewport (`#home-3d-cylinder-stage`).
* Bind mouse drag (`mousedown`, `mousemove`, `mouseup`), wheel event, and touch events (`touchstart`, `touchmove`, `touchend`).
* Add dynamic calculation of card angles and radius based on active album count.
* Style cards with glassmorphism, warm gold rim highlights, and 4K reel play badges.

### Phase 3: Card-to-Suite Expansion & Modal Theater
* Connect card click event to expand the selected lookbook into the Hybrid Album Suite.
* Ensure full keyboard accessibility (`Esc` to dismiss, arrow keys to navigate).

### Phase 4: Demilie-Inspired Craftsmanship Rituals on Homepage / About
* Structure the 4-step royal bridal transformation journey with scroll-tied reveals and gold particle glow.

### Phase 5: Verification & Automated Visual Test
* Run `python manage.py check` and execute automated Playwright test across 375px, 1366px, and 1920px viewports.
* Verify 60 FPS compositor smoothness and zero console errors.
