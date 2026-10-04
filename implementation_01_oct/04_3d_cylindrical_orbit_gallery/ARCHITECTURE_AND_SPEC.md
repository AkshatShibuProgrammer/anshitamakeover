# 04 — 3D CYLINDRICAL ORBIT SHOWCASE

## 1. Specification & Standards
- **Inspiration**: Stanzza, Demilie, and LxL Creative interactive 3D exhibit galleries.
- **Radial Geometry Standard**:
  Cards must form a hardware-accelerated 3D polygon cylinder in CSS 3D space:
  $$R = \frac{W / 2}{\tan(\pi / N)} + \text{depth\_offset}$$
  where $N$ is the number of album cards and $W$ is the card width (~260px desktop).
- **Interactive Mechanics**:
  - Auto-orbit rotation (~0.14° per frame).
  - Mouse drag and touch swipe with physics velocity dampening.
  - Spotlight elevation and border glow on hover (`translateZ` push).
  - Drag threshold protection: Clicking triggers the Hybrid Lookbook Suite only if drag travel is $< 12\text{px}$.

## 2. Technical Implementation Architecture
- Stage container `#orbitGalleryStage` with `perspective: 1200px` and `transform-style: preserve-3d`.
- Orbit rotor `#orbitGalleryRotor` rotated dynamically via `rotateY(angle deg)`.
- Cards pre-distributed with `transform: rotateY(index * step) translateZ(radius)`.

## 3. Files Impacted
- `django/core/templates/core/home.html`
- `django/core/templates/core/base.html`
- `.specify/memory/constitution-3d-orbit-and-motion.md`

## 4. Verification Evidence
- Playwright screenshot tests validating desktop (1440px) and mobile (375px) orbit interaction.
