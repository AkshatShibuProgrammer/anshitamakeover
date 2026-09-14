# Technical Implementation Plan: Haute Couture Vector Entrance

**Feature:** Vector Entrance & Dual-Curtain System  
**Spec Reference:** [SPEC-001](file:///.specify/specs/SPEC-001-vector-curtain-entrance.md)  
**Constitution:** [constitution.md](file:///.specify/memory/constitution.md)  
**Status:** In Progress

---

## 1. Architectural Architecture & File Changes

```
anshita_project/
├── core/
│   ├── static/
│   │   └── core/
│   │       ├── css/
│   │       │   └── style.css            <-- [MODIFY] Add curtain physics & vector stroke rules
│   │       ├── js/
│   │       │   └── main.js              <-- [MODIFY] Add stroke runner, keyboard skip, WebGL uniform sync
│   │       └── images/
│   │           └── brand/
│   │               └── anshita_crest.svg <-- [NEW] High-fashion royal AM vector crest
│   └── templates/
│       └── core/
│           └── base.html                <-- [MODIFY] Replace <video> preloader with dual-curtains & SVG stage
```

---

## 2. Component Design & Sequence

### 2.1 Timeline Sequence (Total: 2.8s, or instant on Skip)
```
0.0s ─── SVG stroke-dashoffset animation begins (AM crest draws itself in gold)
1.6s ─── Stroke completed; soft metallic radial glow activates & fill blends in
1.8s ─── Preloader stage scales slightly (scale: 1.05, opacity: 0)
1.9s ─── Curtain left splits to translateX(-100%), Curtain right to translateX(100%)
1.9s ─── Three.js u_entrance uniform ramps from 0.0 to 1.0; Hero typography glides up
2.8s ─── Preloader DOM element detached (`display: none`); session token locked
```

### 2.2 FOUC Prevention & Session Guard
In `<head>` of `base.html`:
```html
<script>
    if (sessionStorage.getItem('anshita_preloader_seen') === 'true') {
        document.documentElement.classList.add('preloader-skipped');
    }
</script>
<style>
    .preloader-skipped #preloader { display: none !important; }
</style>
```

---

## 3. Verification & Validation Protocol
1. **Visual Regression:** Run headless browser subagent to verify vector stroke drawing and curtain split.
2. **Session Persistence:** Navigate across pages and verify preloader never re-triggers.
3. **Responsive Testing:** Verify on 375px mobile viewport and 1920px desktop.
4. **Git Tree Sanity:** Ensure no API keys or unwanted binaries are touched.
