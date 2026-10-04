# Task Breakdown: 3D Pixar-Style Cute Kid AI Concierge (`Asha`)

**Task Suite ID:** `TASKS-003`  
**Related Spec:** [SPEC-003](file:///.specify/specs/SPEC-003-pixar-3d-cute-kid-ai-concierge.md)  
**Related Plan:** [PLAN-003](file:///.specify/plans/PLAN-003-pixar-3d-cute-kid-ai-concierge.md)

---

## Task Matrix

| Task ID | Component | Task Description | Verification Gate |
| :--- | :--- | :--- | :--- |
| **TASK-003.1** | `base.html` | Replace old abstract disc/torus mesh with cute Pixar kid 3D geometry (Head, rosy cheeks, hair, maang tikka, velvet collar) | Canvas renders smiling Pixar face on load |
| **TASK-003.2** | `base.html` | Implement Big Round Eye Assembly (white sclera, honey amber iris, deep pupil, double glossy catchlight) | Eyes clearly visible, round and cartoonish |
| **TASK-003.3** | `base.html` | Wire real-time cursor tracking kinematics with lerp smoothing | Pupils and head yaw/pitch smoothly follow mouse |
| **TASK-003.4** | `base.html` | Add organic blink scheduler (3.5–6s intervals) and gentle breathing idle | Realistic natural micro-animations running at 60 FPS |
| **TASK-003.5** | `base.html` | Add hover reaction: joyful bounce + happy eye squint | Hovering `#chat-toggle` triggers cheerful bounce |
| **TASK-003.6** | Playwright | End-to-end verification script capturing screenshots of cursor at top-left, center, and bottom-right | High-res screenshot proof verifying cute Pixar face |
