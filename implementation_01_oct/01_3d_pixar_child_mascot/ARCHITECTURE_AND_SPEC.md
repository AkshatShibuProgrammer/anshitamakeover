# 01 — 3D PIXAR CUTE KID BRIDE MASCOT ("ASHA")

## 1. Specification & Standards
- **Persona**: Adorable 3D toddler girl bride ("Asha"), inspired by Pixar and Disney character design. Joyful, friendly, inviting, and respectful of Indian bridal traditions.
- **Colorimetry & Metallurgy**:
  - Skin Tone: Warm Indian golden-wheat / honey-caramel (`#BA7742`). No pale white or cartoonish plastic pinks.
  - Blushing Cheeks: Soft terracotta-rose (`#CF5A50`), layered with gentle opacity (`0.35`).
  - Bridal Attire: Vivah crimson red velvet (`#981423`) cape and sheer dupatta veil (`#B5182D`) with 24K Kundan gold zari border (`#E2BA45`).
  - Bridal Adornments: Dainty gold maang tikka with ruby center (`#BD182A`) and gold jhumka earrings with hanging pearls (`#FFFDF8`) positioned at earlobes.
  - Hair: Natural soft black-brown espresso hair (`#160F0B`) styled in a baby top bun with gentle framing bangs.
- **Eyes & Expression**:
  - Giant round cartoon eyes with dark limbal rings (`#1A0903`), warm honey-amber irises (`#8C4415`), and dual glossy catchlights.
  - Joyful curved toddler smile (`#6E101D`).

## 2. Technical Implementation Architecture
- **Rendering Engine**: Three.js WebGL with `ACESFilmicToneMapping` on `#ashaMascotCanvas`.
- **Kinematic Controllers**:
  - `mousemove` listener normalizes cursor position across entire viewport `[-1, 1]`.
  - Dampened head yaw ($\pm 24^\circ$), pitch ($\pm 16^\circ$), and playful head tilt ($\pm 4.5^\circ$).
  - Pupil pivot shifts organically inside eye socket.
  - Disney-style periodic double-blinks every 3.5s to 6.0s via parametric eyelid rotation.
  - Breathing oscillation ($\pm 0.032$ Y units) and hover celebration scale ($1.08\times$ bounce).

## 3. Files Impacted
- `django/core/templates/components/chatbot_modal.html`
- `django/core/templates/core/base.html`
- `test_asha_mascot_live.py`

## 4. Verification Evidence
- `verify_asha_hover_bounce.png`
- `verify_asha_gaze_top_left.png`
- `verify_asha_full_screen.png`
