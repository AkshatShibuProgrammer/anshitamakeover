# Project Constitution: Anshita Makeover Haute Couture Platform

**Repository:** `AkshatShibuProgrammer/anshitamakeover`  
**Standard:** Spec-Driven Development (SDD) via Spec Kit & GSD (Get Stuff Done)  
**Status:** Canonical & Active

---

## 1. Foundational Architectural Principles

### 1.1 Pure Vector & Hardware Acceleration Over Raster Bloat
- **Mandate:** Preloaders, logos, brand emblems, and page transition masks MUST be rendered using vector mathematics (SVG `<path>` elements, Lottie/Bodymovin JSON, or Three.js GPU shaders).
- **Prohibition:** Video media (`.mp4`, `.webm`, `.avi`) MUST NEVER be used as a full-screen preloader or hero logo reveal. Video decoding introduces unavoidable 100–300ms hardware initialization lag, fixed 24/30 FPS judder, and raster letterboxing that compromises luxury brand credibility.
- **Scope for Video:** HTML5 `<video>` is strictly reserved for the Couture Reels Showcase, bridal transformation portfolios, and masterclass streams.

### 1.2 Luxury Editorial Aesthetics Benchmark ([evagher.com](https://evagher.com/en))
- **Color Palette:** Curated obsidian black (`#070605`), deep velvet (`#0e0c0a`), royal gold accents (`#D4AF37`, `#F3E5AB`), and ivory silk (`#FAF8F5`). Plain primary colors (basic red, blue, green) are strictly forbidden.
- **Typography:** Modern luxury serif (`Cinzel`, `Playfair Display`, or `Cormorant Garamond`) paired with sleek geometric grotesque sans-serif (`Montserrat`, `Inter`) and regal Devanagari typography (`Rozha One`, `Poppins`). Default browser fonts are prohibited.
- **Motion Physics:** All entrance and parting animations must utilize bespoke cubic-bezier curves (e.g., `cubic-bezier(0.77, 0, 0.175, 1)` or `cubic-bezier(0.16, 1, 0.3, 1)`) matching luxury stage curtain mechanics.

### 1.3 3D Character & Mascot Mandate (Pip the Haute Bird & Roster)
- **Primary Studio Mascot:** The default interactive mascot is **Pip**, the couture Three.js bird character modeled with expressive feather brow tufts, dynamic scaling beak, crown plumes, and wing flapping kinematics matching the master reference (`3d character for anshitamakeover/patch_pip.py`).
- **Autonomous Time-Driven Entrance:** Mascot appearance must be triggered by an autonomous time delay (peek at 2.5s, reveal at 3.5s) without requiring user page scrolling. Scroll-tied hopping/scrubbing engines (`mascot-scroll-engine.js`) are strictly forbidden.
- **Roster Switching & Coexistence:** Seamless switching between Pip, Mochi (bunny), Asha (bridal apprentice), and Noor must remain supported.
- **Pupil & Eyelid Kinematics:** Eyes must smoothly track the cursor with dampening lerp physics (`lerp(0.08)`).
- **Sub-Standard Reference:** Detailed specifications governed by `.specify/memory/constitution-pip-mascot-concierge.md`.

### 1.4 Hero Editorial & Studio Portrait Showcase Standard
- **Zero Hard Demarcation:** Hero portraits MUST blend seamlessly into the background canvas using multi-stop feathered directional masks (`linear-gradient(to right, ...)`). Stark vertical dividing lines between photographs and dark backgrounds are strictly forbidden.
- **100% Above-the-Fold Viewport Guarantee:** All primary calls-to-action (CTAs) and editorial typography must sit comfortably above the fold on all standard laptop viewports (from 720px height upwards).
- **Three.js Interactive Studio Lighting:** Hero showcases must integrate cursor-responsive studio softbox / rim lighting simulation, creating dynamic depth on jewelry, embroidery, and skin.
- **Cleanliness:** Stray indicator dots, clipped watermark letters, and accidental overlapping rings are prohibited.

### 1.5 Strict Session Memory & Zero Repetition
- **Mandate:** The preloader animation must run **exactly once per visitor session**.
- **Enforcement:** The state MUST be recorded in `sessionStorage.setItem('anshita_preloader_seen', 'true')` and evaluated synchronously in the document `<head>` to prevent any flash of preloader content (FOUC) when users navigate between routes.

### 1.6 High-Refresh Rate (60/120/144 FPS) Target
- **Mandate:** All DOM transitions must run on GPU compositor layers using `transform` and `opacity` properties with `will-change: transform`. No layout reflow properties (`top`, `left`, `width`, `height`, `margin`) may be animated during transitions.

### 1.7 Security & Secret Sanitization
- **Non-Negotiable Rule:** API keys, access tokens, credentials, and `.env` secrets MUST NEVER be committed to Git history. All commits must be pre-sanitized, and push protection alerts (GH013) must be resolved via clean history re-writing.

### 1.8 Technical SEO & Canonical Crawlability Mandate
- **Zero Missing Meta Tags:** Every Django view must supply unique `<title>`, `<meta name="description">`, `<link rel="canonical">`, Open Graph, and Twitter Card tags.
- **Structured Data:** Enterprise JSON-LD `BeautySalon` / `LocalBusiness` / `BreadcrumbList` markup must be rendered on all primary pages.
- **Sitemap & Robots:** Valid `/sitemap.xml` and `/robots.txt` endpoints must be dynamically served and updated.
- **Sub-Standard Reference:** Governed by `.specify/memory/constitution-high-conversion-seo.md`.

### 1.9 Conversion-First Modular Page Architecture
- **Dedicated Landing Pages:** The platform must provide distinct, optimized routes for high-intent queries: `/` (Editorial Showcase), `/services/`, `/gallery/`, `/packages/`, `/academy/`, and `/book/`.
- **Singular Hero CTA:** Every key page must feature a singular, unconfused primary conversion path (WhatsApp VIP Bridal Consultation lock-in).
- **Monolith Deconstruction:** The 4,400+ line monolithic `home.html` and 8,000+ line `base.html` must be progressively refactored into clean modular partials and dedicated subpages.

---

## 2. Governance Workflow & Quality Gates
1. **Spec Gate (`/speckit.specify`)**: Requirements, user stories, and acceptance criteria must be explicitly documented in a feature specification before code is written.
2. **Plan Gate (`/speckit.plan`)**: Technical architecture, data flows, and component interfaces must be planned.
3. **Tasks Gate (`/speckit.tasks`)**: Work must be broken down into granular, dependency-ordered tasks.
4. **Implement Gate (`/speckit.implement`)**: Execution with automated verification (Django test suite, browser visual checks, Git clean tree verification).

