# Stage 2: Architectural Dual-Curtain Split & Transitions

## 1. Context & Problem Statement
Currently, when the preloader finishes, the entire `#preloader` container simply fades its opacity to `0` over 0.8s (`opacity: 0; pointer-events: none`).
- An opacity fade looks like closing a popup modal or dismissing an alert.
- In luxury editorial sites like [evagher.com](https://evagher.com/en), the entrance is physical and architectural: the screen splits down the center, sliding dual vertical curtains left and right into the viewport margins, giving the impression of curtains parting on an opera stage or opening the double doors of a haute couture salon.

---

## 2. Current State vs. Target State

```
CURRENT STATE (Simple Fade):
┌─────────────────────────────────┐
│         Full-screen Box         │ ─── (Opacity 100% -> 0%) ───> [ Site appears all at once ]
└─────────────────────────────────┘

TARGET STATE (Evagher Architectural Dual-Curtain):
┌────────────────┬────────────────┐
│                │                │
│  CURTAIN-LEFT  │ CURTAIN-RIGHT  │ ─── (Parting apart horizontally) ───> [ Core content revealed from center ]
│      ◄──       │       ──►      │
└────────────────┴────────────────┘
```

| Metric / Attribute | Current State | Target State |
| :--- | :--- | :--- |
| **Opening Mechanism** | Flat opacity transition | Dual physical curtain split (`.curtain-left`, `.curtain-right`) |
| **Motion Physics** | `ease-out` standard | Custom high-end easing `cubic-bezier(0.77, 0, 0.175, 1)` |
| **Depth & Parallax** | Flat 2D reveal | Curtain panels slide over Three.js canvas with subtle drop-shadow edge |
| **Content Unveil** | Hero content is already stationary behind the fade | Hero typography scales gracefully from `0.96` to `1.0` as curtains part |

---

## 3. Technical Implementation Specification

### 3.1 DOM Architecture
```html
<div id="preloader" class="preloader-wrapper">
    <!-- Dual Sliding Curtains -->
    <div class="preloader-curtain curtain-left"></div>
    <div class="preloader-curtain curtain-right"></div>

    <!-- Center Stage Container (Holds Stage 1 Monogram) -->
    <div class="preloader-center-stage">
        <div class="monogram-container">
            <!-- Stage 1 SVG Animated Monogram -->
        </div>
        <div class="preloader-loader-bar">
            <div class="loader-progress"></div>
        </div>
    </div>
</div>
```

### 3.2 CSS Hardware Acceleration & Split Physics
```css
.preloader-curtain {
    position: fixed;
    top: 0;
    bottom: 0;
    width: 50vw;
    height: 100vh;
    background: #080706; /* Deep obsidian velvet */
    z-index: 9999;
    will-change: transform;
    transition: transform 1.2s cubic-bezier(0.77, 0, 0.175, 1);
}

.curtain-left {
    left: 0;
    border-right: 1px solid rgba(212, 175, 55, 0.15); /* Delicate gold seam */
}

.curtain-right {
    right: 0;
    border-left: 1px solid rgba(212, 175, 55, 0.15);
}

/* Opening Trigger Class */
.preloader-wrapper.is-revealed .curtain-left {
    transform: translateX(-100%);
}

.preloader-wrapper.is-revealed .curtain-right {
    transform: translateX(100%);
}

.preloader-wrapper.is-revealed .preloader-center-stage {
    opacity: 0;
    transform: scale(1.08);
    transition: opacity 0.5s ease, transform 0.8s cubic-bezier(0.77, 0, 0.175, 1);
    pointer-events: none;
}
```

### 3.3 Dynamic Sequence Orchestration
1. **0.0s – 1.6s**: SVG monogram draws in center stage (Stage 1).
2. **1.6s – 1.9s**: Monogram glows softly; loader progress reaches 100%.
3. **1.9s**: Center stage scales slightly and fades (`opacity: 0`).
4. **2.0s – 3.2s**: Left and Right curtains part symmetrically, unveiling the Three.js canvas and hero title.
5. **3.2s**: Preloader wrapper set to `display: none` and `sessionStorage.setItem('anshita_preloader_seen', 'true')`.

---

## 4. Acceptance Criteria
1. **Curtain seam**: Clean, invisible or micro-hairline gold seam down the exact vertical center before opening.
2. **Smooth parting**: 60fps GPU transform execution without layout thrashing (`will-change: transform`).
3. **Zero re-trigger on internal clicks**: Seamless bypass when clicking "Services", "Reels", or navigating within the session.
