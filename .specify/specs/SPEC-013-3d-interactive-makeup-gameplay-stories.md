# Feature Specification: 3D Interactive Makeup Gameplay & Story-Driven Learning Webpage ("Atelier Chronicles")

**Feature Branch:** `feature/3d-makeup-gameplay-stories`  
**Spec ID:** `SPEC-013`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Approved for Implementation & Staged in Roadmap  
**Estimated Complexity:** High (Three.js Interactive Face Mesh, Texture Painting Canvas, Gamified Audio & State Engine)

---

## 1. Executive Summary & Product Vision

### Problem & Inspiration
Traditional makeup academy websites feature static course catalogs with flat bullet points. Users want an engaging, bite-sized gamified experience—akin to **Duolingo meets interactive 3D gameplay**—that lets them learn real bridal artistry techniques while experiencing rich cultural wedding stories.

### Target Vision: "Atelier Chronicles: The Art of Bridal Grace"
A dedicated, hardware-accelerated 3D webpage (`/gameplay/` / `/atelier-game/`) featuring:
1. **Interactive 3D Face Canvas**: A beautifully stylized 3D bridal head model with orbit controls, realistic subsurface skin scattering, and real-time brush/tool application.
2. **Episodic Narrative Chapters**: Micro-stories centered around real bridal scenarios (Ayurvedic morning prep, Kolkata Banarasi competition artistry, high-energy Sangeet glam, and the 18-hour cry-proof seal).
3. **Interactive Tool Belt**: Ice-roller, herbal ubtan applicator, Banarasi chandan fine-liner pen, micro-blender sponge, and airbrush mist wand.
4. **Duolingo-Inspired Progression**: Star ratings, accuracy metrics, streak counters, and celebratory audio/visual particle feedback.
5. **High-Value Lead Magnet**: Completing the episodes unlocks a verified **₹2,000 Masterclass Scholarship Voucher** or **10% Bridal Privilege Code**, ready to claim via WhatsApp.
6. **Zero Third-Party Ads**: Strictly ad-free to maintain the luxury couture reputation of Anshita Makeover.

---

## 2. Episodic Storyline Breakdown

```
+-----------------------------------------------------------------------------------------+
|                               ATELIER CHRONICLES — STORY MAP                           |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [ Chapter 1: The Mandap Morning ]           [ Chapter 2: The Sacred Vivah ]            |
|  "Ayurvedic Skin Metallurgy & Ice Prep"      "Kuhu Khare Banarasi Chandan Precision"    |
|  * Tool: Herbal Ubtan + Ice-Roller           * Tool: Red & White Fine Chandan Pen       |
|  * Objective: Cool redness & hydrate skin    * Objective: Paint 7 symmetrical brow dots |
|                                                                                         |
|                                       ⬇                                                 |
|                                                                                         |
|  [ Chapter 3: Starlight Sangeet ]            [ Chapter 4: The Sacred Pheras ]           |
|  "Thakur Shivani Glass-Skin & Jewel Crease"  "The 18-Hour Cry-Proof Starlight Seal"     |
|  * Tool: Soft-Focus Blender Sponge           * Tool: Airbrush Micro-Mist Wand           |
|  * Objective: Sculpt cut-crease without fall * Objective: Pass the 4K Mandap Tear Test  |
|                                                                                         |
|                                       ⬇                                                 |
|                                                                                         |
|                       🏆 ROYAL CERTIFICATION & REWARD UNLOCK                            |
|             "₹2,000 Masterclass Scholarship Voucher + Instant WhatsApp Claim"           |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Technical Architecture & Gameplay Engine

### 1. Rendering Architecture
- **Three.js Scene**: OrbitControls with constrained azimuth/elevation (`minPolar: 70°`, `maxPolar: 105°`) to keep focus on the face.
- **Dynamic Face UV Canvas**: A hidden 1024×1024 HTML5 2D canvas dynamically piped into `MeshStandardMaterial.map` (`texture.needsUpdate = true`). As the user moves their brush tool, strokes and dots are drawn directly on the 3D surface.
- **Raycasting**: Mouse/touch coordinates raycast onto the 3D face mesh, calculating UV coordinates `(u, v)` for precision tool contact.

### 2. Gamified Mechanics
- **Target Accuracy Engine**: Compares painted UV points with predetermined golden coordinates (e.g. Chandan eyebrow guide markers).
- **Streak & XP Tracker**: Stored locally in `localStorage` (`asha_game_streak`, `asha_game_xp`) to encourage daily engagement.
- **Audio Micro-Interactions**: Procedural Web Audio API sound effects (soft brush sweeps, crisp bell chimes for correct placement, celebratory sitar strum upon chapter completion).

### 3. Lead Conversion Engine
- At the end of Chapter 4, the player receives a personalized digital certificate signed by Anshita Sinha with a dynamic voucher code redeemable via 1-click WhatsApp message (`https://wa.me/919343716616?text=...`).
