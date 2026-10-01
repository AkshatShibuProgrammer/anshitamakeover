# Feature Specification: 3D Mascot Dynamic Chat Emotions & Hindi Concierge Welcome

**Feature Branch:** `feature/mascot-chat-emotions-hindi-welcome`  
**Spec ID:** `SPEC-010`  
**Governing Document:** [.specify/memory/constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Completed & Verified  
**Estimated Complexity:** High (Three.js Kinematics, WebGL Rigging, Chat State Machine)

---

## 1. Executive Summary & Problem Description

### User Problem & Objectives
The AI concierge launcher needed to feel alive and contextually reactive to the conversation:
1. **Emotional Reactions to Chat Tone**: When the user expresses dissatisfaction or hesitation ("mujhe nahi chahiye bahut mehnga hai"), the mascot should express sadness. When a deal is closed ("chalo book kar do done hai"), it should celebrate happily. When negotiating discounts ("kuch discount milega kya"), it should cock its ear and think, then offer deals with distinct animations.
2. **Hindi Cultural Welcome**: When Hindi is selected as the language, greeting with traditional "🙏 राम राम जी! Anshita Makeover में आपका स्वागत है!".
3. **Popup Bubble Suppression**: The floating speech bubble should appear ONLY when the chat is minimized. When the user is actively chatting, speech popups must be strictly suppressed to prevent visual clutter.

---

## 2. Technical Architecture & Emotional State Machine

### 3D Rig Kinematics
Implemented in procedural Three.js inside `base.html`:
- **Neutral / Idle**: Breathing subtle Y-axis oscillation, twitching nose (frequency 1.5–3s), organic gaze tracking toward the mouse cursor.
- **Sad (`sad`)**: Ears droop down (`rotZ: ±0.35rad`), head tilts downwards (`rotX: +0.2rad`), eyes narrow slightly, soothing blue-violet ambient glow.
- **Celebrating (`celebrating`)**: Joyful hopping vertical bounce (`scaleY: 1.1`, `pos.y: +12px`), rapid ear perking and wiggling (`rotZ: ±0.15rad` at 12Hz), golden sparkles.
- **Thinking / Generating Coupon (`thinking_coupon`)**: Head cocks sideways (`rotZ: +0.25rad`), one ear straight up and one bent forward, eyes looking upwards in contemplation.
- **Offering Deal (`offering_deal`)**: Eager forward lean toward the screen (`rotX: -0.18rad`), perky upright ears, pulsating 24K gold ring aura.

### Strict Speech Bubble Suppression
```css
/* Multi-layer CSS suppression when chat is open */
body.chat-is-open #chat-speech-bubble,
body.chat-modal-open #chat-speech-bubble,
.chat-window.active ~ #chat-speech-bubble {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
}
```
Checked inside `toggleChat()` and auto-greeting timer to guarantee zero popups during active conversation.
