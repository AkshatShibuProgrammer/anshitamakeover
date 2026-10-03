# Feature Specification: 3D Pixar-Style Cute Kid AI Concierge (`Asha`)

**Feature Branch:** `feature/pixar-cute-kid-concierge`  
**Spec ID:** `SPEC-003`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Approved for Implementation  
**Estimated Complexity:** High (WebGL Three.js 3D Procedural Mesh & Interactive Pupil Rig)

---

## 1. Executive Summary & Problem Description

### Current Failure State (Identified from User Feedback & Screenshot)
The previous floating AI launcher rendered as a dark geometric mechanical disc/torus with concentric gold rings and a small dot. The user explicitly rejected this:
> *"lets put 3d cute kid if required created pixar style character or something with rounded eyes for ai character right now you did wrong"*

It failed because:
1. It felt cold, robotic, and abstract rather than warm, welcoming, and lively.
2. It lacked expressive human/cartoon facial features (no big round eyes, no cheeks, no smiling mouth).
3. It did not communicate that this is a friendly bridal concierge ready to answer queries.

### Target Vision: "Asha" — The Pixar 3D Cute Kid Bridal Assistant
A charming, 3D Pixar/Disney-rendered young bridal apprentice mascot ("Asha") sitting inside the floating concierge bubble (`#chat-toggle`):
- **Facial Architecture**: Cute rounded head, soft chubby cheeks, friendly blushing smile, and silky dark stylized hair with a miniature bridal gold maang tikka.
- **Big Round Expressive Eyes**: Large Disney/Pixar cartoon spheroids with deep warm honey-amber irises, glossy catchlight highlights, and high-frequency pupil tracking that follows the user's cursor across the viewport.
- **Living Micro-Motions**:
  1. *Curious Head Tilt & Yaw/Pitch Lerp*: Head rotates smoothly in 3D (`max ±22° yaw`, `±14° pitch`) pointing toward the mouse.
  2. *Natural Pixar Blink Engine*: Random organic double-blinks (every 3.5–6s) with soft squash-and-stretch eyelid motion.
  3. *Excited Hover Reaction*: When the user hovers over the bubble, the character smiles wider, tilts forward, and performs a joyful celebratory bounce (`scale: 1.08`, `rotate: +4°`).
  4. *Luxury Bridal Uniform*: Wears a cute miniature royal maroon velvet cape collar with gold zardozi stitching, perfectly harmonizing with Anshita Makeover's Option C brand palette.

---

## 2. Technical Architecture & Rendering Strategy

### Why Procedural Three.js WebGL & Vector Layering over Static Bitmaps
Static images become blurry or lose interactivity when animated. By building Asha using a dedicated Three.js WebGL scene with procedural smooth geometries and standard PBR materials:
1. **100% Vector Crispness**: Renders at 60/120 FPS on all Retina and 4K displays without raster pixelation.
2. **Interactive Gaze Geometry**:
   - `Eyes Group`: Left and Right eye spheroids (`SphereGeometry(r, 32, 32)`) with transparent glossy cornea outer shell and colored pupil discs nested inside.
   - `Pupil Target Vector`: Calculates angle from character screen coordinates `(cx, cy)` to `(e.clientX, e.clientY)`. The pupils physically slide across the curved eye surface using spherical coordinates.
3. **Lighting & Materiality**:
   - Soft studio 3-point lighting (`KeyLight` warm champagne `#FFEED6`, `FillLight` soft rose `#FFD5E2`, and `RimLight` 24K gold `#D4AF37`) creates signature Pixar subsurface-scattering warmth.

```
+-------------------------------------------------------------+
|                #chat-toggle (84px × 84px)                   |
|  +-------------------------------------------------------+  |
|  |             Three.js WebGL Canvas (Asha 3D)           |  |
|  |    [ Royal Mini Maang Tikka - 24K Gold ]              |  |
|  |    [ Pixar Soft Hair Geometry - Dark Espresso ]       |  |
|  |    [ Cute Chubby Head Sphere (Skin PBR Material) ]    |  |
|  |      (o)   (o)   <- Big Round Glistening Eyes         |  |
|  |       \     /        (Pupils track cursor position)   |  |
|  |         \_/      <- Joyful Warm Smiling Mouth         |  |
|  |    [ Royal Velvet Burgundy Capelet + Gold Brocade ]   |  |
|  +-------------------------------------------------------+  |
|  +-- [ Live Pulse Indicator Ring: Gold Breathing Glow ] -+  |
+-------------------------------------------------------------+
```

---

## 3. User Stories & Acceptance Criteria

### User Story 1: Prospective Bride Exploring the Website
> *As a bride visiting the website,*  
> *I want to see an adorable, friendly 3D Pixar-style assistant looking at me and following my cursor with big sparkling eyes,*  
> *So that I feel an instant emotional warmth and delight, encouraging me to tap and ask bridal questions.*

### Acceptance Criteria
- [ ] **AC-1 (Visual Identity)**: The character must undeniably look like a cute Pixar/Disney-styled child character—chubby rounded face, big eyes, warm smile, and cute miniature bridal attire.
- [ ] **AC-2 (Pupil & Head Tracking)**: The character's eyes and head must smoothly follow the mouse cursor with zero stutter, easing with dampening coefficient `lerp(0.08)`.
- [ ] **AC-3 (Blink & Emotion Engine)**: Organic blinking occurs at realistic intervals without freezing or interrupting tracking.
- [ ] **AC-4 (Performance Guard)**: When the concierge modal is open or when the page is backgrounded (`visibilitychange`), the animation loop pauses or throttles to 15 FPS to conserve GPU/CPU battery.

---

## 4. Implementation Steps

1. **Step 1: 3D Geometries & Rigging**
   - Head base (`SphereGeometry(0.72, 48, 48)` slightly squashed vertically `scale.y = 0.92`).
   - Cheeks blush (`MeshStandardMaterial` with soft pink diffuse tint `0xFFAAA6`).
   - Eyes (`SphereGeometry(0.24, 32, 32)`) with deep warm amber irises (`0x5c3317`) and crisp glossy highlights (`0xffffff`).
   - Hair bangs and top bun sculpted with soft stylized spheres and toruses.
   - Bridal maang tikka jewel dangling delicately from the forehead parting.
   - Royal burgundy collar with gold trim mesh at the base.
2. **Step 2: Smooth Cursor Kinematics**
   - Normalize mouse `[-1, 1]` relative to toggle position.
   - Clamp maximum rotation so the character never distorts or exposes internal mesh boundaries.
3. **Step 3: Verification & Polish**
   - Playwright end-to-end tests validating pupil deflection at screen corners `(0, 0)`, `(1440, 0)`, `(720, 900)`.
