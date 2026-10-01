# IMPLEMENTATION ROADMAP — 01 OCT (HAUTE COUTURE UPGRADE)

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Execution Standard:** GSD & Spec-Driven Development (SDD) via Spec Kit  
**Architecture Context:** High-converting luxury bridal salon, pan-India destination bookings, and academy masterclasses. Inspired by world-class high-fashion web design (*Demilie*, *Juan Mora*, *LxL Creative*, *Stanzza*).

---

## Sub-Folder Directory Structure

```
implementation_01_oct/
├── README.md                                        # Master index & execution status
├── 01_3d_pixar_child_mascot/                        # Adorable 3D child bride mascot ("Asha")
│   └── ARCHITECTURE_AND_SPEC.md
├── 02_speech_to_text_voice_concierge/               # Multilingual hands-free voice AI
│   └── ARCHITECTURE_AND_SPEC.md
├── 03_hero_seamless_feathering_parallax/            # Zero-line portrait blending & 2.5D tilt
│   └── ARCHITECTURE_AND_SPEC.md
├── 04_3d_cylindrical_orbit_gallery/                 # 3D Rotating cylinder album stage
│   └── ARCHITECTURE_AND_SPEC.md
├── 05_haute_motion_kinetic_typography/              # Lenis momentum scroll & kinetic numbers
│   └── ARCHITECTURE_AND_SPEC.md
├── 06_demilie_craftsmanship_rituals/                # 4-stage royal bridal transformation journey
│   └── ARCHITECTURE_AND_SPEC.md
├── 07_whatsapp_booking_kinetic_typography/          # WhatsApp FAB + Stanzza kinetic type ⬅ NEXT
│   └── ARCHITECTURE_AND_SPEC.md
├── 08_performance_pwa_lighthouse/                   # PWA, JSON-LD schema, Lighthouse 90+
│   └── ARCHITECTURE_AND_SPEC.md
└── 09_oracle_cloud_deployment/                      # Production deployment & Cloudflare CDN
    └── ARCHITECTURE_AND_SPEC.md
```

---

## Detailed Module Breakdown & Status

| Sub-Folder / Domain | Primary Files Impacted | Key Innovation & Benchmark | Current Status |
| :--- | :--- | :--- | :--- |
| **01. 3D Pixar Child Mascot** | `core/base.html`, `chatbot_modal.html` | Adorable Indian toddler girl bride ("Asha") with warm golden-wheat skin, red chunni veil, gold jhumkas, and gaze kinematics. | **✅ COMPLETED & VERIFIED** |
| **02. Speech-to-Text Concierge** | `core/base.html`, `chatbot_modal.html` | Native Web Speech API (`hi-IN`, `mr-IN`, `en-IN`) with glowing microphone toggle for voice queries. | **✅ COMPLETED & VERIFIED** |
| **03. Hero Seamless Feathering** | `core/home.html`, `core/base.html` | Multi-stop gradient mask eliminating harsh division lines; 100% above-the-fold CTA visibility; 2.5D mouse parallax. | **✅ COMPLETED & VERIFIED** |
| **04. 3D Cylindrical Orbit** | `core/home.html`, `core/base.html` | Rotating 3D carousel (`preserve-3d`, radial trig $R = W/2\tan(\pi/N)$), auto-orbit, momentum drag, and card-to-suite zoom. | **✅ COMPLETED & ACTIVE** |
| **05. Haute Motion & Kinetics** | `core/base.html`, `index.css` | Lenis smooth inertial scrolling, GPU-accelerated ticker synchronization, and kinetic number counting. | **✅ ACTIVE** |
| **06. Demilie Story Rituals** | `core/home.html`, `core/base.html` | 4-Stage Sacred Bridal Radiance transformation ritual storytelling with interactive scroll reveals. | **✅ COMPLETED & ACTIVE** |
| **07. WhatsApp Booking + Kinetic Type** | `core/base.html`, `core/home.html`, `style.css` | Stanzza-style oversized Hindi headline, LxL dual marquee, WhatsApp FAB with pulse ring, metric counters. | **⏳ SPEC-007 PENDING** |
| **08. Performance + PWA + Lighthouse** | `manifest.json`, `sw.js`, `base.html`, gallery models | PWA, offline fallback, JSON-LD schema, WebP conversion, Lighthouse ≥ 90. | **⏳ SPEC-008 PENDING** |
| **09. Oracle Cloud Deployment** | `nginx.conf`, `gunicorn.service`, `deploy.sh`, `deploy.yml` | Always-Free Oracle ARM instance, Nginx+Gunicorn, Let's Encrypt SSL, Cloudflare CDN, GitHub Actions CI/CD. | **⏳ SPEC-009 PENDING** |

---

## Empirical Verification Proofs (Completed Modules)

All visual states captured via Playwright headless browser testing:

1. `verify_asha_hover_bounce.png` — Toddler bride Asha with warm golden skin, round eyes, red chunni, jhumkas
2. `verify_asha_gaze_top_left.png` — Real-time cursor tracking kinematics
3. `verify_chat_opened_with_mic.png` — AI Concierge drawer with active microphone button (`#chat-mic-btn`)
4. `verify_asha_full_screen.png` — Complete hero composition with feathered portrait and 100% CTA visibility
5. `verify_3d_cylinder_desktop.png` — 3D cylindrical orbit gallery on desktop 1440px
6. `verify_3d_cylinder_mobile.png` — 3D cylindrical orbit gallery on mobile 375px
7. `verify_about_rituals_desktop.png` — Demilie-inspired 4-stage craftsmanship storytelling section

---

## Speckit Command Reference

| Phase | Command | Output |
| :--- | :--- | :--- |
| Define | `/speckit.specify [Feature]` | `.specify/specs/SPEC-NNN.md` |
| Blueprint | `/speckit.plan` | `.specify/plans/PLAN-NNN.md` |
| Tasks | `/speckit.tasks` | `.specify/tasks/TASKS-NNN.md` |
| Execute | `/speckit.implement TSK-NNN.01..08` | Code + verification |
