# Implementation Plan: SPEC-013 — 3D Interactive Makeup Gameplay ("Atelier Chronicles")

**Governing Spec:** [SPEC-013-3d-interactive-makeup-gameplay-stories.md](file:///.specify/specs/SPEC-013-3d-interactive-makeup-gameplay-stories.md)  
**Status:** Staged for Implementation

---

## 1. Phase Breakdown

### Phase 1: Gameplay Route, View & Template Foundation
- Create Django view `gameplay_view` in `django/core/views/public.py` mapping to `/gameplay/`.
- Create `django/core/templates/core/gameplay.html` inheriting from `base.html` with full Three.js, OrbitControls, and Web Audio API setup.
- Add navigation link `Atelier Game` in header menu and academy page.

### Phase 2: 3D Face Model & Real-Time Dynamic UV Painter
- Initialize Three.js scene with stylized bridal head mesh, studio key/rim lighting, and soft skin shaders.
- Implement Raycaster to convert mouse/touch click events into UV coordinate painting on a live 1024×1024 texture canvas.
- Build tool belt selector UI (Ubtan roller, chandan calligraphy pen, blender sponge, airbrush mist).

### Phase 3: Episodic Narrative Story Engine
- Implement 4 narrative chapters with dialog popups, objectives, and guide targets:
  * **Chapter 1**: Ayurvedic skin prep (ice & ubtan coverage meter).
  * **Chapter 2**: Kuhu Khare Banarasi Chandan precision (7-point symmetry accuracy).
  * **Chapter 3**: Thakur Shivani Sangeet cut-crease (eyeshadow blending).
  * **Chapter 4**: The 18-Hour Cry-Proof Starlight Seal (airbrush mist & tear simulation).

### Phase 4: Gamification, Scoring & Scholarship Voucher Generation
- Accuracy scoring, star ranking (1–3 stars), sound effects (Web Audio API), and confetti celebration.
- Generate dynamic scholarship voucher code with direct 1-click WhatsApp redemption.
