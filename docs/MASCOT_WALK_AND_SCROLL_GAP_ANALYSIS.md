# 3D Mascot Walk-and-Transform Scroll Specification & Benchmark Gap Analysis

**Date:** 2026-10-04  
**Subject:** High-Fidelity 3D Mochi (Bunny) & Pip (Finch) Walk-Cycle, Video-Like Scroll-Driven Transformation into AI Chatbot Concierge, and Benchmark Comparison against Reference Websites (e.g., Evagher, Apple product landing pages, Gucci/LVMH editorial WebGL experiences).

---

## 1. Executive Summary & Vision

The user objective is clear:
> *"we want proper rabbit walking and becoming the chatbot proper like animation video is happening... we want proper 3d character of mochi and pip... we dont want this kind of scrolling instead you already check other website such scrolling. Also perform the gap analysis from the website we analyzed with our website and comprehensively put that analysis as well in the md file"*

### Core Vision
Rather than a simple CSS bounce or pop-up button, the character experience must feel like a **cinematic 3D animation video driven seamlessly by the user's scroll**:
1. **Initial State (Hero Top):** The 3D bunny (Mochi) is completely hidden / off-screen or peeking naturally.
2. **Scroll Phase 1 (The Emergence & Walk Cycle):** As the visitor initiates scroll, Mochi hops/walks dynamically into the 3D scene from the right or depth, animated with true character physics (ears flopping, paws moving, soft fur lighting, golden dust trailing).
3. **Scroll Phase 2 (The Approach & Perspective Scale):** Mochi approaches the camera, performs an endearing turnaround / wave gesture, and moves smoothly toward the bottom corner.
4. **Scroll Phase 3 (The Docking & Chatbot Transformation):** The 3D mascot shrinks in perspective and seamlessly docks into the interactive circular/medallion chatbot trigger position, accompanied by a subtle golden aura bloom.
5. **Scroll Phase 4 (The Conversational Greeting):** Immediately upon settling, a luxury speech bubble unfurls with:
   > *"How may I help you today? ✨"*
   alongside quick inquiry chips (Bridal Looks, Travel Rates, Chat).
6. **Bidirectional Scrubbing:** Scrolling back up reverses the sequence smoothly without glitches or stutter.
7. **Switchable Mascot System:** Both **Mochi (Velvet Bunny)** and **Pip (Celestial Finch)** have full 3D rig support, head-tracking gaze towards user cursor, and interactive emotional responses during conversation.

---

## 2. Comparative Benchmark Gap Analysis

We analyzed the motion design, WebGL integration, and scroll mechanics of top-tier references:
- **Reference A: Evagher (Luxury French Editorial Beauty)**
  - *Key Strengths:* Fluid Lenis smooth scrolling, pinned storytelling layers, micro-particle glitter physics, zero layout shifts, continuous fixed navigation visibility.
- **Reference B: Apple Product Reveal Pages (e.g., AirPods / Vision Pro)**
  - *Key Strengths:* Video-like scrubbing (`canvas` frame interpolation or Three.js timeline scrubbing pinned to scroll progress), absolute sync between scroll position and character pose, cinematic ease curves.
- **Reference C: LVMH / Gucci Haute Editorial 3D Experiences**
  - *Key Strengths:* Warm studio lighting, rich physically based rendering (PBR), specular highlights, seamless transitions between 3D narrative element and interactive UI widgets.

### Gap Analysis Matrix

| Feature / Dimension | Industry Benchmark (Evagher / Apple / Luxury 3D) | Current Anshita Makeover Implementation | Gap Severity | Target Architecture Solution |
| :--- | :--- | :--- | :--- | :--- |
| **Mascot Scroll Behavior** | Scroll position scrubs a continuous 3D skeletal/procedural timeline (like an interactive video) | Triggered via scroll position threshold threshold (`scrollY > 180px`) playing CSS keyframes | **High Gap** | Implement continuous scroll scrubbing (`GSAP ScrollTrigger` + Three.js progress interpolation `progress: 0.0 -> 1.0`). |
| **Walk / Movement Physics** | Full bodily walk cycle: hopping gait, paw movement, ear inertia, secondary bounce | Head/gaze tracking and idle bobbing; lacks full ambulatory locomotion path across the screen | **High Gap** | Add multi-stage path trajectory: entrance coordinates $(X_0, Y_0, Z_0) \to$ settle $(X_1, Y_1, Z_1) \to$ dock $(X_{\text{dock}}, Y_{\text{dock}}, Z_{\text{dock}})$ with gait cycle linked to delta scroll. |
| **Character Fidelity (3D Mochi & Pip)** | Three.js procedural & GLTF character meshes with velvet sheen, pearl shaders, and blinking/expressive eyes | Both `MochiCharacter.js` and `PipCharacter.js` exist with procedural Three.js geometry and blinking, but docked canvas is small ($168\times 168$px) | **Medium Gap** | Render full-viewport transparent WebGL overlay canvas or dynamically sized canvas during the scroll journey, seamlessly transferring texture/mesh to the docked medallion. |
| **Transformation into Chatbot** | Smooth spatial handoff: character shrinks and nests into the floating action button without DOM jump | CSS `transform: translateY(90px) scale(0.2)` into fixed bottom-left container | **Medium Gap** | Spatial anchor tracking: Three.js camera/object transforms linearly interpolate directly into the screen-space bounding rect of the chatbot dock. |
| **Speech Bubble Timing** | Contextual speech bubble pops up with clean audio/visual chime exactly when docking finishes | Speech bubble pops up 800ms after threshold with auto-cycle timer | **Low Gap (Aligned)** | Synchronize speech bubble trigger strictly to `progress >= 0.95`. |
| **Navigation & Header Stability** | Navigation remains pinned or smoothly condenses without layout jank on mobile | Navigation bar is responsive, but previous mobile headroom script occasionally caused jitter | **Resolved/Low Gap** | Keep navigation bar cleanly pinned with backdrop-filter blur. |
| **Mobile & Reduced Motion Performance** | Lightweight CSS sprite or reduced particle count on low-tier mobile; graceful fallback | Canvas rendering runs on mobile device pixel ratio; needs battery/performance optimization | **Medium Gap** | Add device detection & `prefers-reduced-motion` to snap directly to docked state without continuous heavy WebGL compute. |

---

## 3. Technical Architecture for the "Animation Video" Walk & Dock Experience

### 3.1 The Scroll Timeline Stages (`ScrollTrigger` Progress 0.0 to 1.0)

```
[Scroll: 0% — Hero Viewport Top]
  │  Mochi Bunny is hidden (X: +40vw, Y: +20vh, Z: -5, opacity: 0)
  │
  ▼ [Scroll: 10% — 35% : The Grand Entrance & Walk]
  │  Mochi hops onto the scene along a spline curve.
  │  Hopping animation frequency = f(dScroll / dt).
  │  Ears sway backwards with inertia; golden ambient sparkles trail behind.
  │
  ▼ [Scroll: 35% — 70% : The Showcase & Approach]
  │  Mochi pauses near center-right, turns toward camera, winks or waves paw.
  │  Size is prominent (~320px screen height), looking directly at the user cursor.
  │
  ▼ [Scroll: 70% — 95% : The Scale-Down & Docking Vector]
  │  Camera perspective shifts or Mochi translates along a smooth cubic bezier toward
  │  the bottom-left screen coordinates (bottom: 24px, left: 24px).
  │  Mesh scale smoothly transitions from 1.0 (large mascot) to 0.28 (dock medallion).
  │
  ▼ [Scroll: 95% — 100% : Golden Medallion Settle & Chat Greeting]
  │  Mochi locks into the circular medallion `#chat-toggle`.
  │  Golden portal aura flashes softly (`box-shadow: 0 0 25px var(--gold)`).
  │  Speech bubble unfurls: "How may I help you today? ✨"
  │  Interactive Chatbot is fully primed for user click.
```

### 3.2 Continuous Scrubbing Formula (Three.js Math)
Instead of binary `if (scrollY > 180)`:
```javascript
const scrollProgress = Math.min(Math.max((window.scrollY - startOffset) / travelDistance, 0), 1);

// Position Interpolation
mascotMesh.position.x = THREE.MathUtils.lerp(startX, dockX, easeOutCubic(scrollProgress));
mascotMesh.position.y = THREE.MathUtils.lerp(startY, dockY, easeOutCubic(scrollProgress));
mascotMesh.scale.setScalar(THREE.MathUtils.lerp(largeScale, dockScale, easeInOutQuad(scrollProgress)));

// Walk-cycle oscillation based on scroll progress delta
const walkCycle = Math.sin(scrollProgress * Math.PI * 8);
mascotLegs.rotation.x = walkCycle * 0.4;
mascotEars.rotation.z = Math.sin(scrollProgress * Math.PI * 4) * 0.15;
```

---

## 4. Characters Implementation Status: Mochi & Pip

1. **Mochi (Velvet Bunny Mascot):**
   - Implemented in `django/core/static/core/js/characters/MochiCharacter.js`.
   - Procedural three-point lighting, velvet material shaders, customizable ear twitches, eye blinking, and breathing idle animation.
   - Set as default concierge mascot across `chatbot_modal.html` and `base.html`.

2. **Pip (Celestial Finch Concierge):**
   - Implemented in `django/core/static/core/js/characters/PipCharacter.js`.
   - Procedural jewel-toned plumage, wing flap gestures, head cocking, and golden beak animations.
   - Switchable dynamically via the concierge character toggle button.

---

## 5. Branch Synchronization & Main Branch Strategy

- **Feature Branch:** `arena/01a0d489-anshitamakeover`
  - Fully synced with remote origin commit `4c72ad7`.
- **Target Branch:** `main`
  - Can be synchronized and pushed cleanly so that both `arena/01a0d489-anshitamakeover` and `main` contain all latest templates, batch automation scripts, and detailed documentation.
