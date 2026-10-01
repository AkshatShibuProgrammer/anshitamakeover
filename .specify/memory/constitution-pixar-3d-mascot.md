# Constitutional Sub-Standard: 3D Pixar Cute Kid AI Mascot ("Asha")

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Sub-System:** AI Concierge 3D Character Rendering & Living Kinematics Engine  
**Standard:** Spec-Driven Development (SDD) via Spec Kit & GSD (Get Stuff Done)  
**Parent Constitution:** `.specify/memory/constitution.md`  
**Spec ID Reference:** `SPEC-003`

---

## 1. Non-Negotiable Character Aesthetics & Identity

1. **Disney/Pixar Child Aesthetic Standard**:
   - The mascot MUST be an endearing, smiling child character ("Asha", the young royal bridal apprentice) with chubby rounded blushing cheeks, warm porcelain skin tones (`#FEE0D2` base with soft coral blush `#FFAAA6`), and a sweet friendly smile.
   - **Strict Prohibition**: Abstract mechanical toruses, concentric gold rings, flat discs, robotic cyber spheres, or static 2D stickers are unconditionally forbidden as the concierge launcher avatar.

2. **Big Expressive Cartoon Eyes (Round Pixar Geometry)**:
   - Sclera: Smooth, round white spheroids with high subdivision count (`SphereGeometry(0.24, 32, 32)`).
   - Irises: Deep, warm honey-amber curved discs (`0x9E5A22`) with dark outer limbal borders and warm golden flecks.
   - Pupils & Highlights: Jet black center pupils surrounded by crisp double-catchlight glossy specular highlights (`0xFFFFFF`), providing authentic animated-film lifelike presence.

3. **Royal Haute Couture Bridal Adornments**:
   - Stylized glossy dark espresso hair with bangs framing the forehead.
   - Miniature 24K gold Maang Tikka jewel suspended precisely at the frontal hairline parting.
   - Royal maroon velvet cape collar with embroidered zardozi gold brocade trim around the base of the neck.

---

## 2. Interactive Kinematics & Motion Physics

1. **Cursor Gaze Tracking & Easing**:
   - The head yaw (`max ±22°`) and pitch (`max ±14°`), as well as both pupil coordinates, MUST track the client's mouse cursor across the entire viewport.
   - Kinematics MUST use smooth exponential dampening (`lerp(0.08)`) to eliminate mechanical jerkiness or sudden snapping.
   - Clamping guards must ensure pupils never clip through the eye cornea or exceed physical eye sockets.

2. **Living Micro-Motions (Organic Blinks & Idle Floating)**:
   - Natural organic blinking engine running every 3.5 to 6.0 seconds using smooth eyelid squash-and-stretch (`scale.y` down to 0.05 over 80ms, reopening smoothly over 120ms).
   - Idle breathing floating oscillation (`Math.sin(time * 2.2) * 0.035`).

3. **Celebratory Hover Response**:
   - Hovering over `#chat-toggle` must trigger an immediate joyful scale bounce (`1.08x`), happy eye squint, and a cheerful head tilt.

---

## 3. Performance & Battery Preservation

1. **Visibility & Modal Throttling**:
   - When the user opens the full chatbot drawer modal, or when the browser tab transitions to the background (`document.hidden`), the WebGL animation loop MUST pause or throttle to reduce GPU and battery consumption to zero.
2. **GPU Compositor Acceleration**:
   - The canvas element must render inside hardware-accelerated layers with `will-change: transform`.
