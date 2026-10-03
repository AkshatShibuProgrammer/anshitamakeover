# Feature Specification: Chatbot Intent-Driven Emotion Bridge & Speech Bubble Circuit Breaker

**Feature Branch:** `arena/01a0d489-anshitamakeover`  
**Spec ID:** `SPEC-016`  
**Governing Document:** `.specify/memory/constitution.md`  
**Status:** In Design & Review  
**Estimated Complexity:** Medium (Chat Stream Interception, Intent Regex Parsing, 3D State Machine Bridge, Bubble Suppression Guard)

---

## 1. Executive Summary & Problem Description

### Objectives
1. **Hard Speech Bubble Suppression During Active Chat**:
   - The user explicitly requested: *"also if we are in chat and chatting i dont want popup message only when chat is minimize popup is required"*.
   - A circuit breaker must be placed on `window.setConciergeSpeech(...)` and all automatic speech timers:
     - When `#chat-box` has the `.open` class (or active user input), all speech bubble popups are strictly blocked/hidden (`display: none !important; opacity: 0;`).
     - When minimized, gentle cultural greetings (e.g. Hindi *"🙏 राम राम जी! Anshita Makeover में आपका स्वागत है!"*) and periodic assistance prompts can appear.
2. **Real-Time Chatbot Intent Emotion Bridge**:
   - The 3D mascot (Bunny or Asha) in both the floating toggle and header medallion must react naturally to the conversation:
     - **Deal Closing / Package Selection**: Bot response containing `₹`, `Book`, `Reserve`, `Package`, `Suite`, `Privilege` $\rightarrow$ Mascot triggers `happy_deal` (joyful bounce, sparkling specular catchlights, ear wag/brush wave).
     - **Discount / Coupon Generation**: Bot response containing `Coupon`, `Discount`, `GLAMOUR`, `Calculate`, `Off` $\rightarrow$ Mascot triggers `thinking_coupon` (contemplative gaze, ear twitch / brush tapping, thinking expression).
     - **Hesitation / Disinterest**: User inputs like `no`, `expensive`, `not interested`, `later`, `cancel` $\rightarrow$ Mascot triggers `sad_hesitant` (ears droop slightly, soft downcast gaze).
     - **Cultural Greeting**: User selects Hindi/Bundelkhandi/Bhojpuri or says `namaste`, `ram ram`, `pranam` $\rightarrow$ Mascot triggers `ram_ram` (polite nod, respectful folded posture).
     - **Idle / Normal conversation**: Mascot smoothly transitions back to `welcoming`.

---

## 2. Technical Architecture & Interception Flow

```
[User Types Message] 
       │
       ▼
[appendMsg(text, 'user')] ─── Intent Match: 'expensive', 'no', 'cancel' ───► mascot.setEmotion('sad_hesitant')
       │
       ▼
[Server Fetch /api/chatbot/]
       │
       ▼
[appendMsg(reply, 'bot')] ─── Intent Match: '₹', 'Book', 'Suite' ───────► mascot.setEmotion('happy_deal')
                          ─── Intent Match: 'Coupon', 'Discount' ────────► mascot.setEmotion('thinking_coupon')
                          ─── Intent Match: 'राम राम', 'Namaste' ────────► mascot.setEmotion('ram_ram')
```

### Circuit Breaker Code
```javascript
window.setConciergeSpeech = function(text, sender, duration = 7000) {
  const chatBox = document.getElementById('chat-box');
  const speechBubble = document.getElementById('chat-speech-bubble');
  if (!speechBubble) return;

  // HARD CIRCUIT BREAKER: Never popup speech bubbles when user is actively in chat
  if (chatBox && chatBox.classList.contains('open')) {
    speechBubble.classList.remove('active');
    return;
  }

  const bubbleText = document.getElementById('csb-text');
  if (bubbleText) bubbleText.textContent = text;
  speechBubble.classList.add('active');

  clearTimeout(window.speechBubbleTimer);
  window.speechBubbleTimer = setTimeout(() => {
    speechBubble.classList.remove('active');
  }, duration);
};
```

---

## 3. Verification Criteria
- [ ] Speech bubble never pops up when chat modal is open.
- [ ] Speech bubble only displays when chat is minimized.
- [ ] Hindi language selection triggers "राम राम जी" and sets mascot to `ram_ram`.
- [ ] Price or booking responses trigger `happy_deal` with joyful animation.
- [ ] Discount calculation responses trigger `thinking_coupon`.
- [ ] Negative/hesitant responses trigger `sad_hesitant`.
