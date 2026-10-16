# Constitutional Sub-Standard: 3D Pip Mascot Concierge & Autonomous Kinematics Engine

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Sub-System:** 3D Autonomous Interactive Concierge & Mascot Emotion Engine  
**Standard:** Spec-Driven Development (SDD) via Spec Kit & GSD  
**Parent Constitution:** `.specify/memory/constitution.md`  
**Spec ID Reference:** `SPEC-017`  
**Status:** Canonical & Active

---

## 1. Mascot Identity & Autonomous Presence Mandate

### 1.1 Character Silhouette & Default Identity: Pip the Haute Bird
1. **Pip as Primary Studio Mascot**:
   - The default AI Concierge mascot for Anshita Makeover MUST be **Pip**, the bespoke luxury couture bird modeled in Three.js (r128).
   - Pip represents precision, artistry, and swift bridal consultation, adorned in royal teal-emerald tones (`#2e7f80`), coral-peach accents (`#ff8577`), and 24K gold couture embellishments (`#D4AF37`).
2. **Complete Character Roster Availability**:
   - While Pip is the default active launcher companion, the system must retain clean switching support for **Mochi** (the royal playful bunny), **Asha** (the bridal apprentice), and **Noor** without code duplication or state leakage.
3. **Strict Prohibition Against Scroll-Tied Scrubbing**:
   - **MANDATE:** Mascot entrance, body hops, and conversational engagement MUST NEVER be tied to or scrubbed by page scroll position.
   - Scroll-scrubbed motion (e.g. `mascot-scroll-engine.js` hopping across the viewport on mousewheel) creates visual jank, layout occlusion, erratic framerates, and user disorientation.
   - The mascot must live in a clean dock anchor in the bottom-right viewport and enter smoothly based on autonomous timing.

---

## 2. Three.js (r128) Geometry, Shading & Rigging Specifications

### 2.1 Geometry & Material Authenticity (Matching `3d character for anshitamakeover/`)
Pip's mesh structure in `components/concierge.html` MUST match the master reference specification from `3d character for anshitamakeover/patch_pip.py`:
1. **Feather Brow Tufts (`this.brows`)**:
   - Pip MUST have an active expressive brow channel:
     - Material: `MeshStandardMaterial` (`color: 0x2e7f80`, `roughness: 0.42`, `metalness: 0.06`, `clearcoat: 0.55`).
     - Dimensions: `y: 0.235`, `z: 0.335`, `x: 0.165`, `w: 0.062`, `h: 0.030`, `r: 0.011`.
     - Behavior: Brows dynamically tilt, raise, and arch in synchrony with facial emotions (preventing the "frozen face" artifact).
2. **Dynamic Scaling Beak Group (`this.mouth`)**:
   - The beak MUST be encapsulated in a dedicated `THREE.Group` (`position: [0, -0.12, 0.441]`) consisting of a base spheroid and a cone tip (`ConeGeometry(0.092, 0.17, 7)`).
   - The mouth controller must support both opening rotation (`rotation.x = Math.PI/2 + open * 0.26`) and emotional curvature scaling (`scale.x = 1 + curve * 0.07`, `scale.y = 1 - curve * 0.045`).
3. **Plume Mood Channel (`this.plumes`)**:
   - 3 crown plumes positioned on the head rig with alternating gold and coral tones.
   - Dynamic lift: `this.plumeLift` smoothly interpolates toward `this.plumeTarget` (splaying outward when celebratory/bright, sweeping back when contemplative).
4. **Wing Flap & Stance Physics (`this.animateExtra`)**:
   - Left and right wings must execute autonomous breathing flaps (`Math.sin(t * frequency + side) * amplitude`).
   - Pose swings (`this.armSwingX * 0.55`) must fold into the wing group rotation so offering gestures read naturally on an avian rig.
   - Tail feathers execute gentle counter-oscillation (`Math.sin(t * 1.5) * 0.07`).

---

## 3. Autonomous Entrance & Conversational Lifecycle

### 3.1 Time-Sequenced Entrance Architecture
The mascot MUST transition from initial page load to interactive readiness without user scrolling:
```
[Page Load (t=0.0s)] 
       │  (Pip hidden below dock dockRig.position.y = -1.8)
       ▼
[Stage 1: Autonomous Peek (t=2.5s)]
       │  (dockRig slides up to y = -0.55, Pip peeks curiously over border)
       ▼
[Stage 2: Full Reveal & Greeting (t=3.5s)]
       │  (dockRig springs to y = 0.0 with elastic ease, Pip waves wing)
       ▼
[Stage 3: Interactive Dock & Chat Companion (t >= 4.0s)]
       │  (Follows cursor gaze, responds to clicks, acts as launcher for Chatbot)
```

### 3.2 Speech Bubble Circuit Breaker & Chat Coexistence
1. **Suppression During Active Chat**:
   - When the user opens the AI Chat Drawer (`#chat-box.open` or equivalent modal), all floating speech bubble teasers (`#chat-speech-bubble`) MUST be immediately suppressed (`active` class removed, timer cleared).
   - Under no circumstances may a speech bubble overlap the active chat dialogue or input field.
2. **Intent-Driven Emotion Bridge**:
   - Pip must dynamically mirror conversation sentiment via `cur.setEmotion(state)`:
     - `happy_deal`: Triggered on price quotes, booking confirmations, VIP privileges.
     - `thinking_coupon`: Triggered during discount calculation and promo evaluation.
     - `sad_hesitant`: Triggered when user hesitates or declines.
     - `ram_ram`: Triggered on Indian cultural greetings ("Namaste", "Ram Ram", "Pranam").
     - `welcoming`: Default idle state with organic pupil blinks and gentle floating.

---

## 4. Performance & Resource Isolation

1. **Draw Call & GPU Budget**:
   - Max 35 draw calls on the WebGL mascot context.
   - Canvas resolution clamped to viewport pixel density (`Math.min(window.devicePixelRatio, 2)`).
2. **Zero Scroll Engine Interference**:
   - No event listeners for `window.scroll` or GSAP ScrollTrigger may manipulate Pip's Y position after initial reveal.
   - Mascot canvas MUST NOT inject full-screen fixed overlays that trap pointer events or interfere with page touch scrolling.
