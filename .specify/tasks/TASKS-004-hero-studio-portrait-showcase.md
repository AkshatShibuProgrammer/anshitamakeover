# Task Breakdown: Hero Studio Portrait Showcase & Three.js Atmospheric Experience

**Task Suite ID:** `TASKS-004`  
**Related Spec:** [SPEC-004](file:///.specify/specs/SPEC-004-hero-studio-portrait-showcase.md)  
**Related Plan:** [PLAN-004](file:///.specify/plans/PLAN-004-hero-studio-portrait-showcase.md)

---

## Task Matrix

| Task ID | Component | Task Description | Verification Gate |
| :--- | :--- | :--- | :--- |
| **TASK-004.1** | `home.html` | Apply feathered directional mask & soft vignette to left bride portrait | Zero sharp vertical cut-offs against black background |
| **TASK-004.2** | `home.html` | Clean up background watermark letters and remove stray top-left dots/rings under logo | Clean header bar and background with 0 stray artifacts |
| **TASK-004.3** | `home.html` | Re-anchor hero right content with flex vertical centering so CTAs are 100% above fold | Both CTAs fully visible on 768px and 900px viewports |
| **TASK-004.4** | `home.html` | Refine Devanagari/Hindi typography (`शाही ब्राइड`) with regal line-height and letter-spacing | Flawless Hindi editorial hierarchy |
| **TASK-004.5** | `base.html` | Add Three.js studio softbox rim light & golden stardust responding to cursor movement | Cursor motion visibly illuminates portrait edge with warm light |
| **TASK-004.6** | `home.html` | Add 2.5D mouse parallax tilt to bridal portrait frame | Subtle 3D spatial depth tilt on mouse move |
| **TASK-004.7** | Playwright | Full visual regression test at 1366x768 and 1440x900 verifying zero cutoff and lighting | Screenshot validation of perfect hero showcase |
