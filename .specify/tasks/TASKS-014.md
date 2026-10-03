# Tasks: SPEC-014 — Pinned Viewport WorksWheel Scroll Engine

- [ ] **TSK-014.01**: Refactor `.works-wheel-section` to flex column with 14vh header, 76vh stage, 5vh hint, and `box-sizing: border-box;` in `home.html`.
- [ ] **TSK-014.02**: Register GSAP `ScrollTrigger.create({ trigger: '#gallery-showcase', pin: true, end: '+=3200', scrub: 0.5 })` in `home.html`.
- [ ] **TSK-014.03**: Implement rest state buffer ($p \le 0.12$) and linear drum interpolation ($p \in 0.12..0.92$) mapping to `target.current`.
- [ ] **TSK-014.04**: Ensure dynamic `computeMetrics()` calculates card dimensions based on measured `stage.clientHeight` for 768px laptop compatibility.
- [ ] **TSK-014.05**: Add `touch-action: pan-y;` on `#gallery-showcase` and `#worksWheelStage`.
- [ ] **TSK-014.06**: Run automated browser test `verify_works_wheel_scroll.py` and capture screenshots.
