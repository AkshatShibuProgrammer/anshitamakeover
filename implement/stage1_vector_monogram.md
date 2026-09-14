# Stage 1: Vectorization & Monogram Stroke Geometry

## 1. Context & Problem Statement
Currently, the site loads `Logo_reveal_animation_beauty_brand_delpmaspu_.mp4` inside an HTML5 `<video>` tag.
- The browser must instantiate a media decoder, causing an unavoidable 100–300ms delay.
- The video is encoded at 24fps with H.264 compression artifacts and has a rectangular bounding frame that creates visual friction with the website background.
- It feels like an embedded clip rather than an organic, high-fashion web animation.

On [evagher.com](https://evagher.com/en), the logo reveal is **not a video**. It is an **SVG vector line drawing** rendered with mathematical precision at the native frame rate of the user's display (up to 120Hz).

---

## 2. Current State vs. Target State

```
CURRENT STATE (Raster Video):
[ Browser Loading ] ──> [ Init Hardware Decoder ] ──> [ 24fps Video Box with Black Bars ] ──> [ Fade Out ]

TARGET STATE (Mathematical SVG Stroke):
[ Zero Latency ] ──> [ Sub-pixel Vector Geometry ] ──> [ 60-120fps Golden Stroke Draw ] ──> [ Metallic Fill Handoff ]
```

| Metric / Attribute | Current State | Target State |
| :--- | :--- | :--- |
| **Asset Format** | `.mp4` video (2.4 MB) | Vector `<svg>` path (~4–8 KB) |
| **Asset Load Time** | 400ms – 1.2s depending on network | Instantaneous (< 10ms, inlined in DOM) |
| **Render Engine** | HTML5 `<video>` element | SVG `<path>` with CSS `stroke-dashoffset` |
| **Frame Rate** | Fixed 24 FPS (choppy on ProMotion / 144Hz monitors) | 60–144 FPS synced with `requestAnimationFrame` |
| **Background Match** | Slight color mismatch with dark DOM | Perfect 100% alpha transparency |
| **Scalability** | Pixelates or blurs on 4K Retina screens | Infinite vector resolution |

---

## 3. Technical Implementation Specification

### 3.1 Vector Asset Construction
- Design a high-fashion crest incorporating:
  - Interlocking cursive monogram **"AM"** (Anshita Makeover) styled with luxury calligraphy curves.
  - Symmetrical royal filigree / floral flourishes flanking the crest.
  - Serif typography beneath: **"ANSHITA MAKEOVER"** with subtitle **"HAUTE COUTURE BRIDAL ARTISTRY"**.
- Export each element as separate SVG `<path>` elements with clean single-stroke continuous paths.

### 3.2 Stroke-Dashoffset Engine
For each path element:
```javascript
const path = document.querySelector('#monogram-path');
const length = path.getTotalLength();
path.style.strokeDasharray = length;
path.style.strokeDashoffset = length;
```

Animate `stroke-dashoffset` from `length` down to `0` over 1.6 seconds using cubic-bezier easing:
```css
.monogram-draw {
    animation: drawStroke 1.6s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

@keyframes drawStroke {
    to {
        stroke-dashoffset: 0;
    }
}
```

### 3.3 Shimmer & Fill Handoff
Once the stroke finishes drawing (`animationend` event or after 1.5s):
1. The stroke animates a metallic linear gradient:
   `linear-gradient(135deg, #ECC874 0%, #D4AF37 50%, #FFF3B0 100%)`.
2. The inner fill fades in subtly (`fill-opacity: 0` -> `fill-opacity: 1` over 0.4s).
3. A subtle gold particle flare pulses from the center of the crest.

---

## 4. Acceptance Criteria
1. **Zero video decoders**: No `<video>` element used in the preloader.
2. **Sharpness**: Crisp at any zoom level, mobile device, or 4K desktop.
3. **Smoothness**: Consistent 60+ FPS animation timeline without frame drops.
4. **Lightweight**: Total asset payload under 15 KB (versus 2.4 MB video).
