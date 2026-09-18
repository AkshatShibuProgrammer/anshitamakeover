# Granular Implementation Tasks: Evagher Editorial Redesign

**Feature:** Evagher Full-Viewport Editorial Layout & Interactive Gallery Carousel  
**Plan Reference:** [PLAN-002](file:///.specify/plans/PLAN-002-evagher-editorial-redesign.md)  
**Spec Reference:** [SPEC-002](file:///.specify/specs/SPEC-002-evagher-editorial-redesign.md)  
**Status:** Ready for Implementation

---

## Task Matrix & Dependencies

| Task ID | Component | Description | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **TSK-201** | Header & Nav | Implement Evagher-style top bar: Left `☰ MENU`, Center Logo, Right `{EN} / HI` toggle | `[DONE]` | None |
| **TSK-202** | Side Drawer | Build architectural left collapsible navigation drawer with smooth expand/restore | `[DONE]` | TSK-201 |
| **TSK-203** | Hero Section | Restructure `#hero` into Left 60% full-bleed sequential photo slider & Right 40% brand typography | `[DONE]` | None |
| **TSK-204** | Photo Slider Logic | Add auto-advancing crossfade + Ken Burns zoom + fraction counter (`01 / 04`) | `[DONE]` | TSK-203 |
| **TSK-205** | Peek Gallery Modal | Build full-viewport interactive gallery modal showing center active image with left/right peeks | `[DONE]` | None |
| **TSK-206** | Gesture Engine | Implement wheel scroll (Down/Right = Next, Up/Left = Prev) and touch drag/swipe navigation | `[DONE]` | TSK-205 |
| **TSK-207** | Package Deck | Present bridal packages sequentially (one by one) with large visuals and clear rates | `[DONE]` | None |
| **TSK-208** | Quick Actions | Add floating / docked action bar: "Compare All", "Custom Package Builder", "WhatsApp" | `[DONE]` | TSK-207 |
| **TSK-209** | Verification | QA in desktop and mobile viewports; verify gesture smoothness and clean Git tree | `[DONE]` | All |
