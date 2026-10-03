# Asha — 3D Bridal Concierge Mascot & Emotion Engine (v1.0.0)

> A procedural 3D Indian little girl bride mascot holding a 24K makeup brush with living eye tracking, natural blinking, and 5 reactive emotion states.

---

## 🌟 Key Features
- **100% Procedural WebGL**: Zero external GLTF/GLB models. Instant loading (< 18KB minified).
- **Authentic Bridal Artistry**:
  - Dainty button nose, rosy blushing cheeks, warm golden-honey skin tone.
  - Jasmine floral side buns (*Gajra*), 24K gold *Maang Tikka* with ruby center, *Kundan jhumkas*, and choker necklace.
  - Hand-sculpted royal crimson velvet bridal choli with gold zari borders.
  - Right hand holds an authentic **24K Gold Bridal Makeup Brush** that waves gently and responds to cursor movements.
- **5 Damped Emotion States**:
  - `welcoming`: Sweet smile, head tilt, gentle greeting wave.
  - `ram_ram`: Traditional folded posture / respectful nod (Hindi & cultural greetings).
  - `happy_deal`: Joyful bounce, brush waving, blushing cheeks, sparkling specular highlights.
  - `sad_hesitant`: Downcast gaze, gentle sigh.
  - `thinking_coupon`: Upward contemplative gaze, brush tapping (calculating discounts).
- **Zero-Config Standalone Demo**: Double-click `index.html` on any machine to test directly via `file:///` without needing a local web server or `npm`.

---

## 🚀 Quick Start

### 1. Plain HTML (`<script>` tag)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="./PixarBridalGirlCharacter.umd.js"></script>

<canvas id="mascotCanvas" width="240" height="240"></canvas>

<script>
  const mascot = new PixarBridalGirlCharacter({
    canvas: '#mascotCanvas'
  });

  // Switch emotion dynamically:
  mascot.setEmotion('happy_deal');
</script>
```

---

## 📄 Commercial Licensing
This package is licensed for commercial use in bridal websites, luxury salons, e-commerce storefronts, chatbots, and interactive landing pages.
