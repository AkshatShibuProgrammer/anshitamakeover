# Cute Bunny 3D Mascot & Emotion Engine (v1.0.0)

> A lightweight, procedural 3D cartoon rabbit mascot with natural eye-gaze tracking, organic blinking, and 5 reactive emotion states.

---

## 🌟 Key Features
- **100% Procedural**: Zero heavy GLTF/GLB models to download. Fast load times (< 15KB minified).
- **5 Damped Emotion States**:
  - `welcoming`: Sweet smile, head tilt, gentle greeting wave.
  - `ram_ram`: Traditional folded posture / respectful nod (Hindi & cultural greetings).
  - `happy_deal`: Joyful bounce, ear wagging, blushing cheeks, sparkling specular highlights.
  - `sad_hesitant`: Drooping ears, downcast gaze, soft sigh.
  - `thinking_coupon`: Upward contemplative gaze, ear/brush twitch (calculating discounts).
- **Zero-Config Standalone Demo**: Double-click `index.html` on any machine (Windows, Mac, Linux) to test directly via `file:///` without needing a local web server or `npm`.
- **Dual Distribution**: Universal Module Definition (`.umd.js`) for script tags + ES6 Module for modern bundlers (`Vite`, `Webpack`, `React`, `Vue`).

---

## 🚀 Quick Start

### 1. Plain HTML (`<script>` tag)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="./CuteBunnyCharacter.umd.js"></script>

<canvas id="mascotCanvas" width="240" height="240"></canvas>

<script>
  const mascot = new CuteBunnyCharacter({
    canvas: '#mascotCanvas',
    theme: 'festive' // or 'minimal'
  });

  // Switch emotion dynamically:
  mascot.setEmotion('happy_deal');
</script>
```

### 2. Modern Bundler (React / Vite / Next.js)
```javascript
import { CuteBunnyCharacter } from './CuteBunnyCharacter.umd.js';

const mascot = new CuteBunnyCharacter({
  canvas: document.getElementById('myCanvas'),
  autoBlink: true,
  onEmotionChange: (emotion) => console.log('Emotion changed to:', emotion)
});
```

---

## 🛠️ API Reference

### Constructor Options
| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `canvas` / `target` | `HTMLCanvasElement \| string` | *Required* | Canvas element or CSS selector |
| `theme` | `string` | `'festive'` | `'festive'` (with bindi/bell) or `'minimal'` (clean fur) |
| `autoBlink` | `boolean` | `true` | Enables natural ~3.8s double-blink cycles |
| `interactiveCursor`| `boolean` | `true` | Eyes and head track user mouse coordinates |
| `initialEmotion` | `string` | `'welcoming'` | Default emotion state upon load |
| `onEmotionChange` | `function` | `null` | Callback fired on emotion transition |

### Methods
- `setEmotion(name)`: Transition to `'welcoming'`, `'ram_ram'`, `'happy_deal'`, `'sad_hesitant'`, or `'thinking_coupon'`.
- `start()` / `stop()`: Controls animation render loop.
- `destroy()`: Disposes of geometries, materials, and WebGL contexts cleanly.

---

## 📄 Commercial Licensing
This package is licensed for commercial use in web applications, e-commerce storefronts, chatbots, and interactive landing pages.
