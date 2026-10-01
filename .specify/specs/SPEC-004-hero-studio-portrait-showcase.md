# Feature Specification: Hero Studio Portrait Showcase & Three.js Atmospheric Experience

**Feature Branch:** `feature/hero-studio-portrait-showcase`  
**Spec ID:** `SPEC-004`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Approved for Implementation  
**Estimated Complexity:** High (Three.js WebGL Interactive Lighting, Viewport Physics & Typography)

---

## 1. Executive Summary & Problem Description

### Current Visual Flaws (Diagnosed from User's Attached Screenshot)
1. **Harsh Split Line**: The bridal portrait abruptly cuts off at 50% width with a stark vertical demarcation line separating the photograph from the black background.
2. **Ghost Lettering Watermark**: Faint outline of `"AN..."` peeks out awkwardly behind the bride's sleeve, appearing like an unintended rendering glitch rather than intentional branding.
3. **Bottom CTAs Clipped**: The primary call-to-action buttons (`लुकबुक` / `तारीख आरक्षित करें`) get clipped at the bottom boundary of standard laptop displays (1366x768 / 1440x900).
4. **Stray Top-Left Floating Dots**: A misplaced gold ring and yellow circle hover under the logo, cluttering the header bar.
5. **Static Presentation**: The hero section currently behaves like a flat static image banner rather than an immersive, high-fashion **"Live Studio Portrait Showcase"**.

---

## 2. Target Design & Three.js Studio Portrait Showcase Features

### A. Seamless Cinematic Blending & Visual Polish
- **Feathered Directional Mask**: Blend the left bride portrait into the right canvas using a smooth multi-stop gradient mask:
  `mask-image: linear-gradient(to right, black 0%, black 72%, rgba(0,0,0,0.4) 88%, transparent 100%)`.
- **Watermark Cleanup**: Remove or reposition the giant unmasked ghost letters into an ultra-luxurious, subtle 3% opacity royal monogram positioned harmoniously in the negative space.
- **Viewport Layout Guard**: Anchor the hero container to `min-height: calc(100vh - 84px); max-height: 100vh;` with vertically centered flex alignment, ensuring the headline, metadata, and both CTA buttons are 100% visible above the fold on all screens.
- **Clean Header Navigation**: Eliminate stray indicators under the logo, unifying slide controls into an elegant, discreet bottom-center pill dock.
- **Royal Hindi/Devanagari Typography**: Style Devanagari text (`शाही ब्राइड`) with dedicated luxury font pairings, generous line-heights, and crisp gold-gradient accents.

### B. High-End Three.js Studio Showcase Capabilities
To give the sensation of an active **Haute Couture Studio Photoshoot in progress**:
1. **3D Cursor-Driven Studio Softbox (Rim Lighting)**:
   - Introduce a Three.js ambient plane behind and around the bride with a mouse-following directional spotlight (`PointLight(0xffeed6, intensity, distance)`).
   - As the client moves their mouse, the studio key light glides subtly over the image, highlighting the gold zardozi embroidery and antique polki jewelry as if a studio lighting technician is illuminating her.
2. **Interactive 2.5D Depth Tilt / Parallax**:
   - Apply a micro 3D rotation (`rotateY`, `rotateX`) to the bridal portrait mesh (`max ±4°`) coupled with mouse coordinates, creating an architectural holographic depth effect.
3. **Atmospheric Studio Bokeh & Stardust**:
   - Golden stardust particles (`BufferGeometry` with custom shader) that drift slowly upwards and dynamically react to the cursor velocity with gentle turbulence.
4. **Cinematic Studio Shutter Transition**:
   - When auto-cycling or tapping through bridal showcases (e.g., *Royal Maroon Velvet* -> *Sacred Vivah Banarasi* -> *Cathedral Ivory Reception*), the changeover triggers a high-speed studio flash aperture pulse with liquid displacement wipe.

```
+-----------------------------------------------------------------------------------------+
|                               ANSHITA MAKEOVER NAV (Clean)                              |
+-----------------------------------------------------------------------------------------+
| [THREE.JS STUDIO LIGHTING LAYER]                                                        |
|  * Mouse-Following Warm Studio Keylight (0xFFEED6)                                      |
|  * Celestial Stardust Particles drifting in background                                  |
|                                                                                         |
|  +-------------------------------------+   +------------------------------------------+ |
|  | 2.5D PARALLAX BRIDAL PORTRAIT       |   | HAUTE COUTURE EDITORIAL TYPOGRAPHY       | |
|  |                                     |   |                                          | |
|  |  (Authentic Royal Maroon Bride)     |   |  शाही ब्राइड · ROYAL BRIDAL COUTURE      | |
|  |   - 3D mouse tilt                   |   |                                          | |
|  |   - Softbox rim illumination        |   |  JABALPUR · BHOPAL · RAIPUR · DELHI      | |
|  |   - Seamless feathered edge >>>>>>  |   |                                          | |
|  |     (blends smoothly into black)    |   |  18-Hour Cry-Proof Longevity Formulation | |
|  +-------------------------------------+   |                                          | |
|                                            |  [ Primary CTA ]    [ Secondary CTA ]    | |
|                                            |  (Both fully visible above the fold!)    | |
|                                            +------------------------------------------+ |
+-----------------------------------------------------------------------------------------+
```

---

## 3. User Stories & Acceptance Criteria

### User Story 1: Discerning Bride Evaluating High-End Studios
> *As an affluent bride looking for an elite wedding makeup artist,*  
> *I want the homepage to feel like an active, prestigious editorial photography studio,*  
> *So that I am immediately captivated by the depth, lighting, and perfection of the brides.*

### Acceptance Criteria
- [ ] **AC-1 (Zero Hard Cutoffs)**: The left bride image must blend seamlessly into the dark background without any sharp vertical seams.
- [ ] **AC-2 (CTAs 100% In-View)**: On screen heights from 720px to 1440px, both CTA buttons and all editorial text must sit comfortably within the first screen without scrolling.
- [ ] **AC-3 (Three.js Studio Illumination)**: Moving the mouse across the hero canvas generates interactive lighting shifts and depth tilt on the bridal portrait.
- [ ] **AC-4 (Stray Artifact Removal)**: Stray dots, clipped watermark letters, and extraneous rings from the header and background are completely removed.
- [ ] **AC-5 (Devanagari Visual Polish)**: Hindi typography displays with elegant balance, refined weights, and royal aesthetic poise.

---

## 4. Implementation Steps

1. **Step 1: CSS Viewport & Image Mask Refactor (`home.html`)**
   - Apply `mask-image` / CSS gradient overlay to `.am-hero__split-left`.
   - Remove hard-coded height constraints and adjust container to flex auto-center.
   - Clean up top-left indicator elements.
2. **Step 2: Three.js Studio Lighting & Depth Integration**
   - Wire cursor interaction into `#three-bg` with a dedicated studio spotlight uniform.
   - Add mouse parallax tilt to the bridal portrait frame.
3. **Step 3: Multi-Device Verification**
   - Run Playwright at 1366x768, 1440x900, and 1920x1080 to ensure 100% CTA visibility and smooth 60fps lighting performance.
