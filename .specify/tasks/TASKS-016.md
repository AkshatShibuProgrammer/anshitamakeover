# Tasks: SPEC-016 — Chatbot Intent-Driven Emotion Bridge & Speech Bubble Circuit Breaker

- [ ] **TSK-016.01**: Implement hard circuit breaker in `window.setConciergeSpeech` and `toggleChat()` to suppress speech bubble popups when `#chat-box` is open.
- [ ] **TSK-016.02**: Create `evaluateMessageEmotion(text, role)` in `base.html` detecting `happy_deal`, `sad_hesitant`, `thinking_coupon`, and `ram_ram` intents.
- [ ] **TSK-016.03**: Connect `appendMsg(text, role)` to `window.active3DMascot.setEmotion(emotion)`.
- [ ] **TSK-016.04**: Sync `selectChatLanguage()` to trigger `ram_ram` emotion and Hindi "राम राम जी" welcome greeting.
- [ ] **TSK-016.05**: Run automated browser verification test and verify unit tests pass.
