# Project Constitution: Anshita Makeover Haute Couture Platform

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Standard:** Spec-Driven Development (SDD) via Spec Kit  
**Status:** Canonical & Active

---

## 1. Foundational Architectural Principles

### 1.1 Pure Vector & Hardware Acceleration Over Raster Bloat
- **Mandate:** Preloaders, logos, brand emblems, and page transition masks MUST be rendered using vector mathematics (SVG `<path>` elements, Lottie/Bodymovin JSON, or Three.js GPU shaders).
- **Prohibition:** Video media (`.mp4`, `.webm`, `.avi`) MUST NEVER be used as a full-screen preloader or hero logo reveal. Video decoding introduces unavoidable 100–300ms hardware initialization lag, fixed 24/30 FPS judder, and raster letterboxing that compromises luxury brand credibility.
- **Scope for Video:** HTML5 `<video>` is strictly reserved for the Couture Reels Showcase, bridal transformation portfolios, and masterclass streams.

### 1.2 Luxury Editorial Aesthetics Benchmark ([evagher.com](https://evagher.com/en))
- **Color Palette:** Curated obsidian black (`#070605`), deep velvet (`#0e0c0a`), royal gold accents (`#D4AF37`, `#F3E5AB`), and ivory silk (`#FAF8F5`). Plain primary colors (basic red, blue, green) are strictly forbidden.
- **Typography:** Modern luxury serif (`Cinzel`, `Playfair Display`, or `Cormorant Garamond`) paired with sleek geometric grotesque sans-serif (`Montserrat`, `Inter`). Default browser fonts are prohibited.
- **Motion Physics:** All entrance and parting animations must utilize bespoke cubic-bezier curves (e.g., `cubic-bezier(0.77, 0, 0.175, 1)` or `cubic-bezier(0.16, 1, 0.3, 1)`) matching luxury stage curtain mechanics.

### 1.3 Strict Session Memory & Zero Repetition
- **Mandate:** The preloader animation must run **exactly once per visitor session**.
- **Enforcement:** The state MUST be recorded in `sessionStorage.setItem('anshita_preloader_seen', 'true')` and evaluated synchronously in the document `<head>` to prevent any flash of preloader content (FOUC) when users navigate between routes.

### 1.4 High-Refresh Rate (60/120/144 FPS) Target
- **Mandate:** All DOM transitions must run on GPU compositor layers using `transform` and `opacity` properties with `will-change: transform`. No layout reflow properties (`top`, `left`, `width`, `height`, `margin`) may be animated during transitions.

### 1.5 Security & Secret Sanitization
- **Non-Negotiable Rule:** API keys, access tokens, credentials, and `.env` secrets MUST NEVER be committed to Git history. All commits must be pre-sanitized, and push protection alerts (GH013) must be resolved via clean history re-writing.

---

## 2. Governance Workflow & Quality Gates
1. **Spec Gate (`/speckit.specify`)**: Requirements, user stories, and acceptance criteria must be explicitly documented in a feature specification before code is written.
2. **Plan Gate (`/speckit.plan`)**: Technical architecture, data flows, and component interfaces must be planned.
3. **Tasks Gate (`/speckit.tasks`)**: Work must be broken down into granular, dependency-ordered tasks.
4. **Implement Gate (`/speckit.implement`)**: Execution with automated verification (Django test suite, browser visual checks, Git clean tree verification).
