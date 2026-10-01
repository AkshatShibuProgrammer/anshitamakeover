# Implementation Plan: SPEC-010 — 3D Mascot Emotions & Hindi Concierge Welcome

**Governing Spec:** [SPEC-010-3d-mascot-chat-emotions-hindi-greeting.md](file:///.specify/specs/SPEC-010-3d-mascot-chat-emotions-hindi-greeting.md)  
**Status:** Completed & Integrated

---

## 1. Phase Breakdown
- **Phase 1: 3D Articulated Rig Kinematics**
  - Add procedural articulated ears and nose twitching to Three.js canvas in `base.html`.
  - Expose `window.setAshaMood(mood, duration)` globally for chat modal events.
- **Phase 2: Intent-Driven Emotional Triggers**
  - Hook user chat messages and bot response patterns into `setAshaMood`:
    * Hesitation / expensive -> `sad`
    * Deal closed / booked -> `celebrating`
    * Discount asked -> `thinking_coupon` then `offering_deal`
- **Phase 3: Cultural Hindi Welcome & Multi-Layer Popup Suppression**
  - Update `chatbot_modal.html` with default Hindi "🙏 राम राम जी! Anshita Makeover में आपका स्वागत है!".
  - Apply `body.chat-is-open` class toggles and multi-layer CSS to suppress `#chat-speech-bubble`.
