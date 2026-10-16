# Feature Specification: 3D Pip Mascot Autonomous Concierge & Scroll Engine Decoupling

**Feature Branch:** `arena/01a105d6-anshitamakeover`  
**Spec ID:** `SPEC-017`  
**Governing Documents:** `.specify/memory/constitution.md`, `.specify/memory/constitution-pip-mascot-concierge.md`  
**Status:** In Review & Planning  
**Estimated Complexity:** Medium-High (Three.js r128 Rigging Alignment, Scroll Engine Eradication, Autonomous Entrance Timing, Chatbot State Bridge)

---

## 1. Executive Summary & Problem Description

### 1.1 Problem Statement
During visual auditing and user review of the live platform, critical issues were identified regarding the 3D character:
1. **Unwanted Scroll Dependency**: The 3D mascot movement was tightly bound to page scroll via a legacy controller (`mascot-scroll-engine.js`), causing the character to awkwardly scrub, jitter, and hop across sections as the visitor scrolled. The user explicitly stated: *"the animation of 3d character is dependent on scroll and it looks very bad i told to hide it in a character and appear and become chatbot like that automatically"*.
2. **Visual Discrepancy Against Reference Implementation**: In the standalone 3D reference suite (`3d character for anshitamakeover/`), the characters (especially **Pip**, the haute couture bird) possess rich expressive features: dynamic feather brow tufts, opening and scaling beak curves, splaying crest plumes, and lively wing gestures. In the Django deployment, the mascot rendered flat, defaulted to Mochi (bunny), and lacked the visual fidelity of the reference suite.
3. **Engine Conflict**: Two competing 3D mascot mechanisms existed in parallel:
   - `core/templates/core/base.html` (lines 103, 2861-2940, 7257-8052) loading `mascot-scroll-engine.js` with `#mascot-walk-stage` fixed canvases.
   - `core/templates/components/concierge.html` hosting the self-contained Three.js r128 dock rig.

### 1.2 Core Objectives
- **Decouple Mascot from Scroll**: Completely disable or purge `mascot-scroll-engine.js` and remove all scroll-scrubbed hop cycles.
- **Default to Pip the Haute Bird**: Make Pip the primary active concierge character on initial load, while preserving character switching to Mochi, Asha, and Noor.
- **Implement Autonomous Entrance Sequence**:
  - Initial load: Mascot is completely hidden (`dockRig.position.y = -1.8`).
  - At $t = 2.5\text{s}$: Autonomous `peek()` triggers smoothly, elevating the mascot so its head and eyes peer over the dock border.
  - At $t = 3.5\text{s}$: Autonomous `comeOut()` triggers, smoothly elevating the full character into view with celebratory wing flutter and speech bubble greeting.
- **Seamless AI Chatbot Transition**:
  - The mascot acts as the physical launcher and companion for the AI Chatbot drawer.
  - Clicking the mascot opens the chat drawer.
  - While chat is open, floating speech bubble popups are strictly suppressed (preventing dialogue obstruction).
  - Intent emotion bridge: Mascot reacts in real time to bot responses (price quotes $\rightarrow$ `happy_deal`, discounts $\rightarrow$ `thinking_coupon`, objections $\rightarrow$ `sad_hesitant`, cultural greetings $\rightarrow$ `ram_ram`).

---

## 2. User Stories & Acceptance Criteria

### User Story 1: Autonomous, Elegant Entrance
*As a visitor browsing the luxury bridal portfolio, I want the mascot to introduce itself gracefully after a brief delay without requiring me to scroll, so that I experience a polished, high-end welcome.*
- **AC 1.1**: On initial page load, the mascot is completely hidden beneath the viewport edge.
- **AC 1.2**: Exactly 2.5 seconds after page load, `peek()` executes automatically via `setTimeout`, raising the mascot to `y = -0.55` over 0.75 seconds using `power2.out` easing.
- **AC 1.3**: Exactly 3.5 seconds after page load (or 1.0s after peek begins), `comeOut()` executes, elevating the mascot to `y = 0.0` with a gentle overshoot bounce (`back.out(1.2)`).
- **AC 1.4**: Page scrolling does NOT reset, reverse, or scrub the mascot's position.

### User Story 2: Master Pip Visual Fidelity
*As a brand owner, I want Pip to appear identical to the high-fidelity render in the 3D studio reference folder, with expressive brows, lively beak, and crown plumes.*
- **AC 2.1**: Pip's feather brow tufts (`this.brows`) are instantiated using `0x2e7f80` with proper dimensions (`w: 0.062, h: 0.030, r: 0.011`), tilting and raising with emotional states.
- **AC 2.2**: Pip's beak is grouped with dual support for rotation (`rotation.x`) and emotional curvature scaling (`scale.x`, `scale.y`).
- **AC 2.3**: Pip's 3 crown plumes dynamically lift and splay (`this.plumeLift`) when happy or speaking, and sweep back when contemplative.
- **AC 2.4**: Pip's wings execute organic idle breathing flaps via `animateExtra()`.

### User Story 3: Clean Chat Drawer Integration
*As a prospective bride chatting with the concierge, I want the conversation to be clean and unobstructed by floating popups.*
- **AC 3.1**: Clicking the Pip mascot or the chat launcher opens the `#chat-box` drawer.
- **AC 3.2**: When `#chat-box` has class `.open`, `#chat-speech-bubble` is hidden (`classList.remove('active')`) and any pending bubble timers are cleared.
- **AC 3.3**: Mascot tracks cursor coordinates inside the chat drawer with smooth lerp physics (`lerp(0.08)`).
- **AC 3.4**: When the AI chatbot quotes bridal packages or discounts, Pip reflects matching celebratory or thinking animations.

---

## 3. Technical Specifications & Architecture

### 3.1 Component Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    core/templates/core/base.html             │
│                                                             │
│  [DISABLED / REMOVED]                                       │
│  - mascot-scroll-engine.js script tag                       │
│  - #mascot-walk-stage CSS & DOM elements                     │
│  - Scroll-bound window.mascotScrollEngine event hooks       │
│                                                             │
│  [ACTIVE COMPONENT]                                         │
│  {% include "components/concierge.html" %}                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               components/concierge.html                      │
│                                                             │
│  Three.js Scene Graph:                                      │
│  Scene                                                      │
│  └── dockRig (Group) ── Controlled by peek() / comeOut()    │
│      ├── PipCharacter.root (visible = true) [DEFAULT]       │
│      │   ├── headRig (Gaze lerp, Pupils, Blinking)          │
│      │   │   ├── brows (Feather brow tufts)                 │
│      │   │   ├── beak (Group with scaling & rotation)       │
│      │   │   └── plumes (3 Crown Plumes with mood lift)     │
│      │   └── wings (Autonomous flap physics)                │
│      └── MochiCharacter.root (visible = false)              │
│                                                             │
│  Timeline Controller:                                       │
│  t=0.0s : Hidden                                            │
│  t=2.5s : peek() ──────► GSAP dockRig.y = -0.55             │
│  t=3.5s : comeOut() ───► GSAP dockRig.y = 0.0 + Speech      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Key Variable and Configuration Changes
| Target File | Current Implementation | New Implementation | Rationale |
|---|---|---|---|
| `components/concierge.html` | `cur = mochi; curId = 'mochi';` | `cur = pip; curId = 'pip';` | Make Pip the primary active mascot |
| `components/concierge.html` | `pip.root.visible = false;` | `mochi.root.visible = false;` | Set initial visibility to Pip |
| `components/concierge.html` | `setupScrollTrigger()` binds `#services-section` | `setTimeout(peek, 2500)` and auto `comeOut()` | Decouple from scroll; trigger autonomous entrance |
| `components/concierge.html` | Mochi button has class `active` | Pip button has class `active` | Align UI switcher with active character |
| `core/base.html` | Loads `mascot-scroll-engine.js` | Commented out / disabled | Eliminate conflicting scroll-scrub engine |
| `core/base.html` | `#mascot-walk-stage` fixed canvas active | Canvas deactivated / hidden | Prevent double canvas and GPU waste |

---

## 4. Verification & Testing Checklist

- [ ] **V-17.1**: Load `http://127.0.0.1:8000/` without scrolling. Verify mascot is invisible for the first 2.4 seconds.
- [ ] **V-17.2**: At 2.5 seconds, verify Pip smoothly rises to peek over the dock.
- [ ] **V-17.3**: At 3.5 seconds, verify Pip comes fully out with wing flutter and greeting bubble.
- [ ] **V-17.4**: Scroll rapidly up and down the page. Verify Pip stays anchored in the dock without jitter or hop scrubbing.
- [ ] **V-17.5**: Click the chat button to open `#chat-box`. Verify speech bubble vanishes immediately.
- [ ] **V-17.6**: Click character switcher in UI to switch between Pip and Mochi. Verify smooth transition without memory leak.
- [ ] **V-17.7**: Verify `mascot-scroll-engine.js` console errors are zero.
