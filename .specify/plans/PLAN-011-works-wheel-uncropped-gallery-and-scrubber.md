# Implementation Plan: SPEC-011 — WorksWheel Gallery & Transformation Scrubber

**Governing Spec:** [SPEC-011-works-wheel-uncropped-gallery-and-scrubber.md](file:///.specify/specs/SPEC-011-works-wheel-uncropped-gallery-and-scrubber.md)  
**Status:** Completed & Integrated

---

## 1. Phase Breakdown
- **Phase 1: React & shadcn Configuration**
  - Install dependencies and create `package.json`, `tsconfig.json`, `tailwind.config.js`, `components.json`.
  - Add utility helpers in `lib/utils.ts` (`cn` function with `clsx` and `tailwind-merge`).
- **Phase 2: WorksWheel Component Implementation**
  - Create `components/ui/works-wheel.tsx` with dynamic rotation drum, scroll responsiveness, and uncropped `object-contain` item rendering.
  - Create interactive demo in `components/ui/demo.tsx`.
- **Phase 3: Frame Extraction & Canvas Scrubber**
  - Extract 48 WebP frames from `royal_velvet_bride_muted.mp4`.
  - Add canvas scrubber markup `#bridal-transformation` in `home.html` with GSAP ScrollTrigger timeline.
