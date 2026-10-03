# 02 — SPEECH-TO-TEXT VOICE CONCIERGE

## 1. Specification & Standards
- **Feature Goal**: Allow prospective brides, outstation families, and academy students to interact hands-free with the AI Concierge by speaking naturally instead of typing.
- **Multilingual Support**:
  - Automatically matches speech recognition language with the selected regional locale:
    - Hindi: `hi-IN`
    - Marathi: `mr-IN`
    - Regional Hindi dialects (Bundelkhandi / Bhojpuri): `hi-IN`
    - English: `en-IN`

## 2. Technical Implementation Architecture
- **Web API**: Utilizes native browser Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`).
- **Interactive Component**:
  - Microphone button `#chat-mic-btn` embedded directly inside `.chat-inp-row`.
  - Triggered via `window.toggleSpeechToText()`.
- **States & Visual Indicators**:
  - Idle state: Elegant gold microphone outline.
  - Recording state (`.recording`): Glowing red pulsating badge with animated wave effect.
  - Input field updates placeholder: `"Listening... Speak now 🎙️"`.
  - Asha's character mood switches to `'listening'`.
  - On transcript finalization, automatically populates the text field and submits query (`sendChat()`).

## 3. Files Impacted
- `django/core/templates/components/chatbot_modal.html`
- `django/core/templates/core/base.html`

## 4. Verification Evidence
- Verified via Playwright: `verify_chat_opened_with_mic.png` captures the active `#chat-mic-btn` in the drawer.
