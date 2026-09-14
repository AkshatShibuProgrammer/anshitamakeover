# Implementation Roadmap: Haute Couture Preloader & Animation Engine

This document defines the 3-stage transition plan to elevate **Anshita Makeover** from a raster MP4 preloader to a world-class, vector-driven, 60/120 FPS animated entrance inspired by [evagher.com](https://evagher.com/en).

---

## Overall Comparison: Current State vs. Target State

| Feature | Current State | Target State (Evagher-grade) |
| :--- | :--- | :--- |
| **Animation Medium** | Raster MP4 / WebM `<video>` inside preloader container | Mathematical SVG Vector Stroke (`stroke-dashoffset`) & WebGL Morph |
| **Frame Rate & Latency** | 24–30 FPS fixed; hardware decoder latency (100–300ms initial freeze) | 60–120 FPS native monitor refresh rate; 0ms frame-zero rendering |
| **Visual Integration** | Video container with dark background boundaries | Seamless alpha transparency; native DOM integration |
| **Entrance / Exit Transition**| Basic CSS opacity / scale fade out | Dual architectural curtain split (`.curtain-left` & `.curtain-right`) sliding on custom Bezier curves |
| **Micro-Interactions** | Static video playback requiring user to wait passively | Dynamic SVG stroke draw + subtle mouse-parallax glow + skip on click |
| **Session Control** | Basic `sessionStorage` flag | Bulletproof session guard with zero-flicker inline CSS script execution |

---

## 3 Implementation Stages

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Vectorization & Monogram Stroke Geometry           │
│ Convert logo to clean SVG paths + stroke-dashoffset engine  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Architectural Dual-Curtain Split & Transitions      │
│ Implement .curtain-left / .curtain-right with easing physics │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: WebGL Background Handoff & Micro-Interactions       │
│ Sync Three.js shader activation with curtain opening        │
└─────────────────────────────────────────────────────────────┘
```

---

### [STAGE 1: Vectorization & Monogram Stroke Geometry](stage1_vector_monogram.md)
- **Current State**: Uses `Logo_reveal_animation_beauty_brand_delpmaspu_.mp4` which renders as an embedded rectangular video element.
- **Goal**: Clean vector SVG monogram ("AM" luxury crest + "ANSHITA MAKEOVER" typography) with dynamic path length calculation and animated stroke drawing.
- **Key Deliverables**:
  - `anshita_project/core/static/core/images/brand/anshita_crest.svg`
  - Stroke drawing animation with gold gradient fill handoff (`#D4AF37` to `#F3E5AB`).

### [STAGE 2: Architectural Dual-Curtain Split & Transitions](stage2_curtain_split.md)
- **Current State**: Preloader fades out with opacity over 0.8s, revealing the page all at once.
- **Goal**: Replicate Evagher's signature dual sliding panel curtain (`mask-left` and `mask-right`) that slides out horizontally with `cubic-bezier(0.77, 0, 0.175, 1)`.
- **Key Deliverables**:
  - `.preloader-curtain-left` and `.preloader-curtain-right` structural markup in `base.html`.
  - Coordinated CSS keyframes and GSAP / JavaScript sequence triggers.

### [STAGE 3: WebGL Background Handoff & Motion Micro-Interactions](stage3_webgl_handoff.md)
- **Current State**: Three.js fluid silk shader starts rendering in the background immediately behind the opaque video.
- **Goal**: Three.js canvas dynamically ripples and intensifies as the curtains split open, creating seamless depth as the hero title zooms into focus.
- **Key Deliverables**:
  - Shader uniform ramp (`u_revealProgress` from 0.0 to 1.0).
  - Ambient particle dispersion on cursor hover over the monogram.
  - Fail-safe skip button (`ESC` key or click anywhere) for instantaneous entry.
