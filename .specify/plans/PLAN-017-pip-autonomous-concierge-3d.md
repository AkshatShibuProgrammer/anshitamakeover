# Technical Plan: 3D Pip Mascot Autonomous Concierge & Scroll Engine Decoupling

**Spec ID Reference:** `SPEC-017`  
**Parent Constitution:** `.specify/memory/constitution-pip-mascot-concierge.md`  
**Target Files:**
- `django/core/templates/components/concierge.html`
- `django/core/templates/core/base.html`
- `django/core/static/core/js/controllers/mascot-scroll-engine.js` (disabled/decoupled)
**Status:** Ready for Task Breakdown  

---

## 1. Technical Architecture & Component Flow

```
Page DOM Ready
      │
      ▼
init3D() in concierge.html
      │  - Creates WebGLRenderer, Scene, PerspectiveCamera
      │  - Creates dockRig at HIDDEN_Y (-1.8)
      │  - Instantiates PipCharacter (visible=true, cur=pip)
      │  - Instantiates MochiCharacter (visible=false)
      │  - Starts clock & animate() loop
      │
      ▼
Autonomous Timer Sequence (Zero Scroll Dependency)
      │
      ├── t = 2.5s : peek() ──────► GSAP animates dockRig.position.y to -0.55
      │                             Pip peeks over dock, blinks, scans cursor
      │
      └── t = 3.5s : comeOut() ───► GSAP animates dockRig.position.y to 0.0 (back.out)
                                    Pip performs happy wing flutter
                                    Shows teaser speech bubble ("✨ Namaste! I'm Pip...")
      │
      ▼
Interactive Companion State
      │  - Tracks mouse pointer with lerp(0.08)
      │  - Click on mascot or #chat-toggle ──► opens #chat-box
      │
      ▼
Chat Drawer Active State
      │  - Floating speech bubble suppressed (display: none !important)
      │  - Intent hooks bridge chat replies ──► cur.setEmotion(...)
      │    • Price/Booking ──► 'happy_deal'
      │    • Discount/Coupon ──► 'thinking_coupon'
      │    • Rejection ──► 'sad_hesitant'
      │    • Cultural Greeting ──► 'ram_ram'
```

---

## 2. File-by-File Implementation Details

### 2.1 Modifications to `django/core/templates/components/concierge.html`

#### Edit 1: Pip Character Instantiation & Default Active State
```javascript
// Before (Lines 704-706):
pip.root.visible = false;
cur = mochi;
curId = 'mochi';

// After:
mochi.root.visible = false;
pip.root.visible = true;
cur = pip;
curId = 'pip';
```

#### Edit 2: UI Character Switcher Active State
```html
<!-- Before (Lines 185-188): -->
<button class="cast-btn active" data-char="mochi" title="Mochi">🐰</button>
<button class="cast-btn" data-char="pip" title="Pip">🦜</button>

<!-- After: -->
<button class="cast-btn active" data-char="pip" title="Pip the Haute Bird">🦜</button>
<button class="cast-btn" data-char="mochi" title="Mochi the Bunny">🐰</button>
```

#### Edit 3: Replace ScrollTrigger with Autonomous Timing
```javascript
// Before (Lines 800-815):
function setupScrollTrigger() {
  if (window.gsap && window.ScrollTrigger) {
    window.gsap.registerPlugin(window.ScrollTrigger);
    window.ScrollTrigger.create({
      trigger: '#services-section',
      start: 'top 72%',
      onEnter: peek,
      onLeaveBack: unpeek
    });
  } else {
    setTimeout(peek, 1800);
  }
}
setupScrollTrigger();

// After:
function setupAutonomousEntrance() {
  // Graceful 2.5s delay after page load: peek over the dock
  setTimeout(() => {
    peek();
    // 1.0s after peeking: automatically emerge into full mascot stance
    setTimeout(() => {
      if (phase === 'peek') {
        comeOut();
        if (window.setConciergeSpeech) {
          window.setConciergeSpeech("✨ Namaste! I'm Pip, your bridal concierge. Looking for royal wedding styling?", 'pip', 6000);
        }
      }
    }, 1000);
  }, 2500);
}
setupAutonomousEntrance();
```

#### Edit 4: Pip Three.js Rigging Alignment with `patch_pip.py`
Verify and ensure `LC.PipCharacter` includes:
- Expressive feather brow tufts (`this.brows` with `MeshStandardMaterial 0x2e7f80`).
- Beak grouping with `rotation.x` opening and emotional curvature scaling.
- Crown plumes array with dynamic `plumeLift` responding to mood.
- Wing flap updates incorporating `this.armSwingX * 0.55` in `animateExtra()`.

### 2.2 Modifications to `django/core/templates/core/base.html`

#### Edit 1: Deactivate `mascot-scroll-engine.js` Script Loading
```html
<!-- Line 103: Wrap in conditional or disable to prevent scroll-scrubbing conflicts -->
<!-- DEPRECATED SCROLL SCRUBBING ENGINE: Disabled in favor of autonomous Pip Concierge (SPEC-017) -->
<!-- <script src="{% static 'core/js/controllers/mascot-scroll-engine.js' %}"></script> -->
```

#### Edit 2: Hide Legacy `#mascot-walk-stage` Overlays
Ensure CSS rules for `#mascot-walk-stage` are set to `display: none !important; pointer-events: none;` to eliminate redundant canvas allocations and zero-out compositor thread memory.

#### Edit 3: Guard Legacy `window.mascotScrollEngine` Invocations
Add safe existence checks around `if (window.mascotScrollEngine) { ... }` so removing the script never raises `Uncaught TypeError` in the console.

---

## 3. Risk Assessment & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| User has low bandwidth and Three.js CDN or script takes $>2.5\text{s}$ to load | Mascot appears abruptly or timer fires before scene ready | Timer is started strictly inside `init3D()` *after* renderer and camera are initialized. |
| User opens chatbot before 2.5s timer expires | Mascot might trigger `comeOut()` and overwrite open modal state | Check `phase` and modal state before triggering `comeOut()`; suppress speech bubble if chat is open. |
| Browser tab switched to background during load | Timers fire while hidden, creating animation jump upon return | Check `document.hidden`; pause timers or transition immediately to idle dock on tab focus. |

---

## 4. Verification & Validation Steps

1. **Terminal Command Verification**:
   ```bash
   python manage.py check
   ```
2. **Browser Network & Console Audit**:
   - Confirm `mascot-scroll-engine.js` is not active or causing errors.
   - Confirm Three.js r128 canvas renders at 60 FPS in DevTools Performance panel.
3. **Visual Timing Verification**:
   - $t \in [0, 2.4\text{s}]$: Dock is empty.
   - $t = 2.5\text{s}$: Pip peeks smoothly up.
   - $t = 3.5\text{s}$: Pip emerges, flutters wings, displays speech bubble.
   - Wheel scroll: Zero character displacement or jitter.
