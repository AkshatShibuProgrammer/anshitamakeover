# Feature Specification: Standalone Exportable 3D Character Suite & Marketplace Architecture

**Feature Branch:** `arena/01a0d489-anshitamakeover`  
**Spec ID:** `SPEC-015`  
**Governing Document:** `.specify/memory/constitution.md`  
**Status:** Architecture Refined & Gap-Mitigated  
**Estimated Complexity:** High  

---

## 1. Executive Summary & Problem Description

### Objectives
1. **Procedural Cute 3D Bunny ("Chiku / Bunny")**:
   - In-house Three.js procedural mascot inspired by the Sketchfab model reference (`cute-rabbit-a92db0809f3f447f876d643ac38bf48b`).
   - Chubby cream/pearl body, floppy ears with inner pink cartilage, twitching button nose, shiny black button eyes, optional festive bindi / garland.
   - Zero paid 3D asset dependencies.
2. **Procedural 3D Pixar Little Girl Bride ("Asha")**:
   - Preserves the 3D Indian toddler girl bride with Gajra buns, Maang Tikka, Kundan choker, royal velvet choli, and 24K waving makeup brush.
3. **Sellable Standalone Commercial Packages**:
   - Create self-contained, standalone distribution directories that can be exported, packaged into ZIP files, or sold on marketplaces (Gumroad, Envato, GitHub Sponsors):
     ```
     packages/
     ├── cute-bunny-3d-mascot/
     │   ├── CuteBunnyCharacter.umd.js   # Script-tag ready (works locally via file:// without CORS errors)
     │   ├── CuteBunnyCharacter.esm.js   # ES6 Module for modern bundlers (Vite/Webpack/React)
     │   ├── index.html                  # Standalone live demo (opens in any browser with zero server)
     │   ├── README.md                   # API guide, emotion triggers, license
     │   └── preview.png                 # Commercial marketplace card
     └── asha-3d-bridal-concierge/
         ├── PixarBridalGirlCharacter.umd.js
         ├── PixarBridalGirlCharacter.esm.js
         ├── index.html                  # Standalone live demo
         ├── README.md                   # API guide, emotion triggers, license
         └── preview.png                 # Commercial marketplace card
     ```
4. **Universal Module Architecture**:
   - Dual ESM and UMD support: works with `import * as THREE from 'three'` or standard `<script>` tags referencing `window.THREE` / CDN fallback (`cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`).
5. **Damped Emotion State Engine**:
   - Smooth damped spring interpolation between emotion states:
     - `welcoming`: Sweet smile, head tilt, gentle greeting wave.
     - `ram_ram`: Traditional Indian cultural greeting with nod/folded posture (for Hindi language).
     - `happy_deal`: Joyful bounce, ear wagging / brush waving, sparkling specular catchlights (upon booking/closing).
     - `sad_hesitant`: Drooping ears / downturned expression (when user expresses disinterest).
     - `thinking_coupon`: Upward contemplative gaze, ear/brush twitch (when calculating discount).
6. **Performance & UX Safety**:
   - `IntersectionObserver` / visibility detection pauses the RAF render loop when the character canvas is off-screen or hidden to conserve GPU and battery.
   - Built-in `.destroy()` method disposes of geometries, textures, and renderer contexts.

---

## 2. Standalone Commercial API

```javascript
// Standalone usage via script tag:
const mascot = new CuteBunnyCharacter({
  target: document.getElementById('avatar-box'),
  theme: 'festive', // 'festive' or 'minimal'
  autoBlink: true,
  onEmotionChange: (emotion) => console.log('Current emotion:', emotion)
});

// Reactive Emotion API
mascot.setEmotion('happy_deal');
mascot.setEmotion('thinking_coupon');
mascot.setEmotion('sad_hesitant');
mascot.setEmotion('ram_ram');

// Cleanup on modal close
mascot.destroy();
```

---

## 3. Verification Criteria
- [ ] Both Bunny and Asha render in full procedural 3D with zero third-party GLB dependencies.
- [ ] Both packages open standalone in any local browser via `index.html` without requiring Django or web server (`file:///` safe).
- [ ] All 5 emotion states interpolate smoothly with damped spring physics.
- [ ] RAF render loop pauses when the canvas is hidden or off-screen.
- [ ] Django test suite passes (233/233 unit tests).
