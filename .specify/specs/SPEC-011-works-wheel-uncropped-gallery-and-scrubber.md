# Feature Specification: WorksWheel Uncropped Gallery & 48-Frame Transformation Scrubber

**Feature Branch:** `feature/works-wheel-uncropped-gallery`  
**Spec ID:** `SPEC-011`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Completed & Integrated  
**Estimated Complexity:** High (React WorksWheel Component, shadcn, Tailwind, Canvas Scroll Scrubbing)

---

## 1. Executive Summary & Problem Description

### Objectives
1. **WorksWheel React Component Integration**: Integrate the portfolio wheel component that transitions cards into a vertical perspective drum on scroll into `/components/ui/works-wheel.tsx`.
2. **Zero Image Cropping Constraint**: Strictly enforce `object-contain` and uncropped display so intricate bridal jewelry, mukuts, and dupattas are 100% visible without cutoff.
3. **Canvas Video Scroll Transformation**: Extract 48 high-resolution WebP frames from `royal_velvet_bride_muted.mp4` and render them into a high-performance `<canvas id="bridal-transformation-canvas">` driven by GSAP ScrollTrigger.
4. **shadcn, Tailwind CSS, TypeScript Setup**: Ensure project supports shadcn component structure (`components.json`, `tailwind.config.js`, `tsconfig.json`).

---

## 2. Technical Architecture

### Uncropped Image Framing
```css
.hg-card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: radial-gradient(circle, #2d0e22 0%, #12030d 100%);
  border-radius: 12px;
}
```

### Video Frame Scrubbing Engine
- Extracted 48 frames via OpenCV into `django/core/static/core/images/transformation_frames/frame_000.webp` to `frame_047.webp`.
- High-efficiency preloader caches image objects in memory.
- GSAP ScrollTrigger updates canvas context at 60 FPS on desktop and mobile.
