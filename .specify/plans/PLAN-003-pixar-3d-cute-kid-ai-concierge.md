# Implementation Plan: 3D Pixar-Style Cute Kid AI Concierge (`Asha`)

**Plan ID:** `PLAN-003`  
**Related Spec:** [SPEC-003](file:///.specify/specs/SPEC-003-pixar-3d-cute-kid-ai-concierge.md)  
**Target Files:**
- `django/core/templates/core/base.html`
- `django/core/static/core/js/` (or inline in `base.html` within concierge component)

---

## 1. Technical Architecture & Mesh Design

### A. Procedural Three.js Character Rig
To achieve the warm, friendly Pixar child aesthetic without external heavy assets:
- **Head & Cheeks**:
  - Main Cranium: `SphereGeometry(0.74, 48, 48)` with subtle vertical squash (`scale.set(1.0, 0.94, 0.96)`).
  - Material: Warm porcelain skin tone `MeshStandardMaterial({ color: 0xFEE0D2, roughness: 0.55, metalness: 0.05 })`.
  - Rosy Blushing Cheeks: Two soft blushing cheek discs layered on the cheekbones with soft coral tint `0xFFAAA6`.
- **Pixar-Style Big Round Eyes**:
  - Left & Right Eye Sclera: Smooth white spheres `SphereGeometry(0.24, 32, 32)` positioned at `x = ±0.28, y = 0.06, z = 0.62`.
  - Amber-Honey Irises: Curved disc geometry `CircleGeometry(0.14, 32)` with gradient honey amber `0x9E5A22` and dark outer limbal ring.
  - Deep Pupils: Jet black center `CircleGeometry(0.08, 32)` with high-gloss double catchlight white glints (`CircleGeometry(0.025)`).
- **Hair & Bridal Adornment**:
  - Stylized glossy espresso hair shell framing the forehead and temples.
  - Miniature Royal Gold Maang Tikka with a tiny suspended teardrop gem centered between the eyebrows.
- **Costume / Cape**:
  - Royal burgundy velvet cape collar (`CylinderGeometry` tapered at neck) with gold brocade edge trim.

### B. Pupil Kinematics & Easing Physics
- Maintain `targetLook = { x: 0, y: 0 }` updated on `window.mousemove`.
- Interpolate current look vector using dampening factor:
  `currentLook.x += (targetLook.x - currentLook.x) * 0.09`
  `currentLook.y += (targetLook.y - currentLook.y) * 0.09`
- Apply `currentLook` to:
  1. Head Group Rotation (`yaw: ±0.32 rad`, `pitch: ±0.18 rad`).
  2. Eye Sclera Sub-Rotations.
  3. Pupil offset positions across the cornea radius.

### C. Organic Animation Loops
- **Blink Controller**: Every 3.5 to 6 seconds, trigger eyelid squash closure (`scale.y -> 0.05` over 80ms, reopen over 120ms).
- **Idle Breathing & Sway**: Gentle sinusoidal vertical floating motion (`Math.sin(time * 2) * 0.03`).
- **Hover Euphoria**: On mouseenter of `#chat-toggle`, trigger scale bounce to `1.1` and wide smile morph.
