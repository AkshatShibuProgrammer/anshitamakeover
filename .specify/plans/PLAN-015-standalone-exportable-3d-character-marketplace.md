# Implementation Plan: SPEC-015 — Standalone Exportable 3D Character Suite & Marketplace Architecture

**Governing Spec:** `.specify/specs/SPEC-015-standalone-exportable-3d-character-marketplace.md`  
**Status:** Validated & Ready for Execution  

---

## 1. Phase Breakdown & Execution Path

### Phase 1: Commercial Standalone Packaging Structure
- Create directory tree:
  - `packages/cute-bunny-3d-mascot/`
  - `packages/asha-3d-bridal-concierge/`
  - `django/core/static/core/js/characters/`

### Phase 2: Procedural Cute Bunny Character Engine
- File: `packages/cute-bunny-3d-mascot/CuteBunnyCharacter.js` & `django/core/static/core/js/characters/CuteBunnyCharacter.js`
- Tasks:
  - Procedural Three.js mesh: chubby pear-shaped torso, rounded head, floppy articulated ears with pink inner layer, button nose with micro-twitching, shiny black button eyes with specular catchlights.
  - Implement 5 damped emotion states (`welcoming`, `ram_ram`, `happy_deal`, `sad_hesitant`, `thinking_coupon`).
  - Implement idle breathing, blinking, and cursor tracking.
  - Include visibility observer and `.destroy()` cleanup method.
  - Create `packages/cute-bunny-3d-mascot/index.html` standalone interactive demo with emotion triggers.
  - Create `packages/cute-bunny-3d-mascot/README.md` with commercial licensing and usage docs.

### Phase 3: Modularize Pixar Bridal Girl "Asha"
- File: `packages/asha-3d-bridal-concierge/PixarBridalGirlCharacter.js` & `django/core/static/core/js/characters/PixarBridalGirlCharacter.js`
- Tasks:
  - Decouple existing Asha 3D toddler girl bride into an identical standalone class with the same unified emotion interface.
  - Create `packages/asha-3d-bridal-concierge/index.html` standalone live demo.
  - Create `packages/asha-3d-bridal-concierge/README.md`.

### Phase 4: Integration with Chat Concierge & Launcher
- Files:
  - `django/core/templates/core/base.html`
  - `django/core/templates/components/chatbot_modal.html`
- Tasks:
  - Import the decoupled character classes.
  - Instantiate character with visibility observer.
  - Connect chatbot messages to emotion states:
    - Deal closed / package selected $\rightarrow$ `happy_deal`.
    - User disinterest / hesitation $\rightarrow$ `sad_hesitant`.
    - Generating coupon / calculating discount $\rightarrow$ `thinking_coupon`.
    - Hindi language selection $\rightarrow$ `ram_ram`.
  - Enforce speech bubble suppression when chat modal is open (`chatOpen === true`).

### Phase 5: Verification & Commercial Package Audit
- Tasks:
  - Run standalone demo files directly in Chrome (`file:///.../packages/.../index.html`).
  - Run Django unit tests (`python testing/unit/run.py`).
  - Capture automated browser screenshots of the new Cute Bunny character and the commercial standalone showcase.
