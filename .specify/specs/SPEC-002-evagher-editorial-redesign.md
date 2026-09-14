# Feature Specification: Evagher Full-Viewport Editorial Layout & Interactive Gallery Carousel

**Feature Branch:** `feature/evagher-editorial-redesign`  
**Spec ID:** `SPEC-002`  
**Governing Document:** [constitution.md](file:///.specify/memory/constitution.md)  
**Reference Benchmark:** [evagher.com](https://evagher.com/en) & `uploads/Eva García _ Makeup Artist in Barcelona.html`  
**Status:** Approved for Technical Planning

---

## 1. Executive Summary & Vision
The user has analyzed [evagher.com](https://evagher.com/en) and requested an architectural redesign of the homepage layout to embody the signature luxury editorial experience:

1. **Full-Viewport Screen-Covering Photo Sequence with Asymmetrical Branding**:
   - High-impact, full-bleed images that transition smoothly (`photo 1 -> photo 2 -> photo 3`).
   - "Anshita Makeover" branding, accolades, and key editorial details elegantly placed at the **right side** with generous negative space.
2. **Interactive Multi-Directional Modal Gallery (Full-Bleed Peek Carousel)**:
   - Clicking any photograph opens a full-screen immersive gallery.
   - **Gesture & Mouse Navigation**:
     - Drag/swipe right or scroll down ➔ advances to **Next Image**.
     - Drag/swipe left or scroll up ➔ returns to **Previous Image**.
     - **Peek Framing**: The active image commands center stage (~80–85vw), while slices of the previous and next images peek gracefully into the left and right margins.
3. **Sequential Couture Package Showcase & Direct Actions**:
   - As the visitor scrolls down, packages are presented one by one with large editorial visuals.
   - Intuitive floating/docked controls:
     - **"View All Packages"**
     - **"Compare All Packages"** (opening our upgraded glassmorphic comparison modal)
     - **"Create Custom Package"** (interactive calculator/builder)
4. **Editorial Collapsible Navigation & Top Language Switcher**:
   - Clean, minimal top header with **Language Switcher** (`EN / HI`).
   - Left/Side minimal navigation bar with an expandable/restorable menu toggle button matching Evagher's architectural layout.

---

## 2. User Stories & Persona Scenarios

### User Story 1: Editorial Lookbook Explorer
> *As a discerning bride exploring bridal aesthetics,*  
> *I want to see screen-filling editorial photographs transition smoothly with Anshita's artistry details on the right,*  
> *and click into an interactive peek gallery where I can swipe or scroll to smoothly navigate lookbooks,*  
> *so that I feel like I am browsing Vogue or Harper's Bazaar.*

### User Story 2: Transparent Package Evaluator
> *As a bride-to-be comparing wedding day services,*  
> *I want to see each package presented with its own large imagery and have one-click options to compare all suites or build a custom package,*  
> *so that I can make confident investment decisions without confusing layout clutter.*

### User Story 3: Multi-Lingual & Seamless Navigation
> *As a visitor,*  
> *I want an expandable side navigation drawer and an instant language toggle at the top,*  
> *so that the interface feels uncluttered and effortless.*

---

## 3. Functional Requirements Matrix

| Req ID | Component | Requirement Description | Success Criteria |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Hero Editorial Sequence** | Full-screen photo showcase with automatic or scroll-synced image sequencing; brand typography pinned on right side | Smooth crossfade/slide transition with zero layout jitter; responsive portrait/landscape framing |
| **FR-02** | **Peek Gallery Modal** | Clicking any photo opens full-screen gallery with peek margins showing prev/next images | Main image ~82vw, side peeks ~8vw each; smooth transform physics |
| **FR-03** | **Bi-Directional Gesture Nav** | Mouse drag, wheel scroll, touch swipe, and arrow keys move images (Right/Down = Next, Left/Up = Prev) | Natural drag physics with rubber-band bounds and snap-to-center |
| **FR-04** | **Sequential Package Deck** | Packages display sequentially with high-res photos and prominent tags | Clean vertical progression as user scrolls down |
| **FR-05** | **Quick Package Actions** | Dedicated buttons: "View All", "Compare All", "Build Custom" | Instantly opens comparison modal or scrolls to specific deck |
| **FR-06** | **Top Header & Language** | Minimal top header with clean `EN / HI` toggle and brand insignia | Instant language cookie persistence; zero layout flash |
| **FR-07** | **Collapsible Side Drawer** | Minimalist side navigation button that expands into full editorial menu and restores cleanly | Smooth 60 FPS drawer transition with glassmorphic blur |
