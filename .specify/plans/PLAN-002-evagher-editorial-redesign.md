# Technical Implementation Plan: Evagher Editorial Redesign & Peek Gallery

**Feature:** Evagher Full-Viewport Editorial Layout & Interactive Gallery Carousel  
**Spec Reference:** [SPEC-002](file:///.specify/specs/SPEC-002-evagher-editorial-redesign.md)  
**Constitution:** [constitution.md](file:///.specify/memory/constitution.md)  
**Status:** In Progress

---

## 1. Architectural Blueprint & Component Map

```
anshita_project/core/templates/core/
├── base.html                      <-- [MODIFY] Top language toggle (EN/HI) + Left collapsible nav drawer
└── home.html                      <-- [MODIFY]
    ├── #hero                      <-- Split layout: Left 60% full-bleed photo slider, Right 40% brand content
    ├── #editorial-gallery-modal   <-- [NEW] Interactive peek gallery with wheel & touch swipe navigation
    ├── #packages-editorial-deck   <-- [MODIFY] Sequential one-by-one package presentation
    └── #package-quick-actions     <-- Floating action pill: "View All", "Compare All", "Custom Package"
```

---

## 2. Technical Detail by Component

### 2.1 Hero Full-Viewport Sequential Slider (`#hero`)
- **Left Column (60% width on Desktop, 100% on Mobile)**:
  - Full-height container (`height: calc(100vh - 80px)`).
  - High-resolution bridal and editorial images (`uploads/` & `curated/` photography).
  - Automated timed crossfade (every 4.5s) with manual dot/fraction indicator (`01 / 04`).
  - Subtle Ken Burns scale effect (`transform: scale(1) -> scale(1.05)`).
- **Right Column (40% width, centered vertically)**:
  - Luxury gold typography: **ANSHITA MAKEOVER**
  - Subtitle: **Haute Couture Bridal Artistry · India**
  - Founder signature and accolades (`8+ Years Mastery`, `500+ Royal Brides`).
  - Direct Appointment Reserve & Explore Portfolio CTAs.

### 2.2 Interactive Peek Modal Gallery (`#editorial-gallery-modal`)
- **Visual Design**:
  - Full-screen dark velvet overlay with 95% backdrop blur.
  - Active image centered at `width: min(82vw, 950px); max-height: 82vh; border-radius: 16px; object-fit: cover`.
  - Previous image peeking on left margin (`opacity: 0.35; transform: scale(0.85)`).
  - Next image peeking on right margin (`opacity: 0.35; transform: scale(0.85)`).
- **Physics & Control Engine**:
  - **Wheel Scroll**:
    - `deltaY > 0` or `deltaX > 0` ➔ triggers `nextImage()`.
    - `deltaY < 0` or `deltaX < 0` ➔ triggers `prevImage()`.
    - Debounced to prevent multi-skipping.
  - **Touch / Mouse Drag**:
    - Calculates drag delta. If swipe distance > 50px, snaps to adjacent slide.
  - **Keyboard**:
    - `ArrowRight` / `ArrowDown` ➔ Next.
    - `ArrowLeft` / `ArrowUp` ➔ Previous.
    - `Escape` ➔ Closes gallery.

### 2.3 Sequential Package Deck & Quick Action Toolbar
- **Sequential Cards**:
  - As user scrolls down past the hero, each package appears sequentially:
    1. **Master Airbrush Bridal Suite** (Large photo on left, detailed inclusions & rates on right).
    2. **Imperial Royal HD Bridal Suite**.
    3. **Engagement & Roka Couture Glam**.
    4. **Family & Bridesmaids Suite**.
- **Action Toolbar (Sticky or Docked)**:
  - `Compare All Suites` (Opens modal comparison table cleanly without cluttering the page).
  - `Build Custom Package` (Interactive price calculator).
  - `Quick WhatsApp Inquiry`.

### 2.4 Top Header & Collapsible Side Navigation Drawer
- **Top Header (`#mnav`)**:
  - Left: Minimalist Menu Button (`☰ MENU` with animated toggle).
  - Center: Pure Brand Mark (`anshita_haute_emblem.png` + `ANSHITA MAKEOVER`).
  - Right: Minimalist Language Pill (`{EN} / HI` with letter-hover animation matching Evagher).
- **Collapsible Side Drawer (`#side-drawer`)**:
  - Slides in from the left with `transform: translateX(0)` over `0.6s cubic-bezier(0.16, 1, 0.3, 1)`.
  - Full editorial navigation links with subtle stagger and sound/ripple feedback.

---

## 3. Verification Protocol
1. **Desktop Inspection (1920x1080)**: Verify photo sequence, right-side details alignment, and peek gallery.
2. **Mobile Inspection (375x812)**: Verify touch swipes, stacked hero framing, and responsive side drawer.
3. **Multi-Language Test**: Toggle between English and Hindi, verifying instant text swap without reload stutter.
