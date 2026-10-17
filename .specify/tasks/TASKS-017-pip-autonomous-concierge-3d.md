# Granular Implementation Tasks: 3D Pip Mascot Autonomous Concierge & Scroll Engine Decoupling

**Feature:** 3D Pip Mascot Autonomous Concierge & Scroll Engine Decoupling  
**Plan Reference:** [PLAN-017](file:///.specify/plans/PLAN-017-pip-autonomous-concierge-3d.md)  
**Spec Reference:** [SPEC-017](file:///.specify/specs/SPEC-017-pip-autonomous-concierge-3d.md)  
**Parent Constitution:** [constitution-pip-mascot-concierge.md](file:///.specify/memory/constitution-pip-mascot-concierge.md)  
**Status:** Ready for Implementation  

---

## Task Matrix & Dependencies

| Task ID | Component | Description | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **TSK-17-01** | Template | Swap default character to Pip in `components/concierge.html` (`cur=pip`, `curId='pip'`, `pip.root.visible=true`) | `[DONE]` | None |
| **TSK-17-02** | UI Buttons | Update character switcher UI in `components/concierge.html` to mark Pip button as `active` | `[DONE]` | TSK-17-01 |
| **TSK-17-03** | Three.js | Verify and align Pip's rig with `patch_pip.py` (feather brows, dynamic scaling beak group, plume mood channel) | `[DONE]` | TSK-17-01 |
| **TSK-17-04** | Timing | Replace `setupScrollTrigger` in `concierge.html` with autonomous timer sequence (`peek` @ 2.5s, `comeOut` @ 3.5s) | `[DONE]` | TSK-17-01 |
| **TSK-17-05** | Greeting | Configure Pip default greeting speech bubble text & voice/sound cues | `[DONE]` | TSK-17-04 |
| **TSK-17-06** | Cleanup | Disable/comment out `mascot-scroll-engine.js` in `base.html` and neutralize `#mascot-walk-stage` overlay | `[DONE]` | None |
| **TSK-17-07** | Chat Bridge | Connect chatbot intent triggers to `cur.setEmotion()` and enforce bubble suppression when chat is open | `[DONE]` | TSK-17-04 |
| **TSK-17-08** | Verification | Verify autonomous timing, zero scroll scrubbing, 60 FPS rendering, and switcher functionality | `[DONE]` | TSK-17-01 to TSK-17-07 |

---

## Detailed Task Specifications

### TSK-17-01 & TSK-17-02: Pip Default Active Character & Switcher UI
- File: `django/core/templates/components/concierge.html`
- In `init3D()`:
  - Set `mochi.root.visible = false;`
  - Set `pip.root.visible = true;`
  - Set `cur = pip; curId = 'pip';`
- In the `.cast-strip` HTML:
  - Move `.active` class to `<button class="cast-btn active" data-char="pip" title="Pip the Haute Bird">🦜</button>`.

### TSK-17-03: Three.js Rigging Alignment with Reference Studio
- File: `django/core/templates/components/concierge.html`
- Ensure `LC.PipCharacter` has:
  - `this.brows = eyeBrows(...)` instantiated with feather brow material (`0x2e7f80`).
  - Beak group with both opening rotation and curvature scaling (`scale.x = 1 + cc * 0.07`).
  - `this.plumes` array with dynamic `plumeLift` responding to emotion states.
  - `this.animateExtra()` applying wing flap and body swing physics.

### TSK-17-04 & TSK-17-05: Autonomous Timing Sequence & Pip Greeting
- File: `django/core/templates/components/concierge.html`
- Remove all `ScrollTrigger.create({ trigger: '#services-section', ... })` bindings.
- Implement:
  ```javascript
  setTimeout(() => {
    peek();
    setTimeout(() => {
      if (phase === 'peek') {
        comeOut();
        if (window.setConciergeSpeech) {
          window.setConciergeSpeech("✨ Namaste! I'm Pip, your bridal concierge. Looking for royal wedding styling?", 'pip', 6000);
        }
      }
    }, 1000);
  }, 2500);
  ```

### TSK-17-06: Deactivate Conflicting Mascot Scroll Engine
- File: `django/core/templates/core/base.html`
- Comment out `<script src="{% static 'core/js/controllers/mascot-scroll-engine.js' %}"></script>`.
- Set `#mascot-walk-stage { display: none !important; }` in CSS.
- Add safe checks around any `window.mascotScrollEngine` references in inline scripts.

### TSK-17-07: Chatbot Intent Emotion Bridge & Bubble Circuit Breaker
- File: `django/core/templates/components/concierge.html` & `django/core/templates/components/chatbot_modal.html`
- Enforce: When `#chat-box.open` is true, remove `.active` on `#chat-speech-bubble` and cancel speech timers.
- Forward chatbot reply intents to `window.ConciergeController.setEmotion(emotion)`.

### TSK-17-08: Automated & Visual Verification
- Run `python manage.py check` to ensure clean template syntax.
- Launch browser and verify:
  1. No mascot visible before 2.4s.
  2. Smooth peek at 2.5s.
  3. Smooth reveal at 3.5s with Pip greeting bubble.
  4. Scroll page up/down: Pip remains docked without scrubbing or jittering.
  5. Switching to Mochi and back to Pip works without errors.
