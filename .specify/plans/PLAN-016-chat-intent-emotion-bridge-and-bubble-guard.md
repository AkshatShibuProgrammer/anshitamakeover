# Implementation Plan: SPEC-016 — Chatbot Intent-Driven Emotion Bridge & Speech Bubble Circuit Breaker

**Governing Spec:** `.specify/specs/SPEC-016-chat-intent-emotion-bridge-and-bubble-guard.md`  
**Status:** Ready for Execution  

---

## 1. Phase Breakdown & Execution Path

### Phase 1: Speech Bubble Circuit Breaker Guard
- File: `django/core/templates/core/base.html`
- Tasks:
  - Update `window.setConciergeSpeech(...)` to immediately return and clear `.active` if `#chat-box` has class `.open`.
  - Add mutation/event observer on `toggleChat(open)` so that opening the chat unconditionally removes `#chat-speech-bubble.active`.

### Phase 2: Intent-to-Emotion Regex Analyzer
- File: `django/core/templates/core/base.html`
- Tasks:
  - Add `evaluateMessageEmotion(text, role)`:
    - User role: checks for rejection/hesitation intents (`/no|nah|expensive|costly|not now|later|cancel|bad/i`) $\rightarrow$ returns `'sad_hesitant'`.
    - Bot role:
      - Booking / Quote intents (`/₹|book|package|suite|reserve|privilege|deal/i`) $\rightarrow$ returns `'happy_deal'`.
      - Discount / Coupon intents (`/coupon|discount|glamour30|promo|calculate|offer/i`) $\rightarrow$ returns `'thinking_coupon'`.
      - Greeting intents (`/राम राम|ram ram|namaste|pranam|hello/i`) $\rightarrow$ returns `'ram_ram'`.
      - Default $\rightarrow$ `'welcoming'`.
  - Hook into `appendMsg(text, role)` to call `window.active3DMascot?.setEmotion(emotion)`.

### Phase 3: Language Switch Greeting Sync
- File: `django/core/templates/core/base.html`
- Tasks:
  - Update `selectChatLanguage(langCode, langName)`:
    - If `langCode === 'hindi'` or `'bundelkhandi'` or `'baghelkhandi'` or `'bhojpuri'`:
      - Set bubble greeting to "🙏 राम राम जी! Anshita Makeover में आपका स्वागत है!".
      - Set mascot emotion to `'ram_ram'`.

### Phase 4: Automated Verification
- Script: `scratch/verify_emotion_bridge.py`
- Tasks:
  - Simulate chat open $\rightarrow$ verify speech bubble disappears.
  - Send "too expensive" $\rightarrow$ verify character transitions to `sad_hesitant`.
  - Send "I want to book Royal Bengali suite" $\rightarrow$ verify character transitions to `happy_deal`.
