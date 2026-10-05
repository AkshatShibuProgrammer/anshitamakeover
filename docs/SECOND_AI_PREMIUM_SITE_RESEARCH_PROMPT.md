# Copyable research brief: Anshita Makeover premium 3D story-site

Copy the prompt below into a second AI that can browse the live web and inspect the supplied repository/files. The goal is an evidence-led research and implementation plan—not code changes. It deliberately separates the existing site from the intended next experience and calls out known conflicts that must be verified.

---

## PROMPT START

You are an independent senior digital art director, luxury/bridal experience designer, real-time 3D and animation specialist, scrollytelling interaction designer, mobile accessibility reviewer, and technical performance reviewer. Your assignment is **research, verification, and a recommended implementation plan only**. Do not edit code, claim implementation, or replace an asset. Be specific, cite evidence, and distinguish direct observation from source-code notes and third-party descriptions.

### 1. The brief: what the owner wants to make

Anshita Makeover is a bridal makeup and artistry brand. The target is a **distinctive, art-led, premium 3D animated experience** that makes beauty craft, transformation, material, light, character and motion feel authored. The site should feel like a small digital artwork or cinematic fashion/editorial experience—not a generic beauty-template redesign, static brochure site, or SaaS interface with a decorative 3D hero.

The center of gravity is **art direction and animation craft**: thoughtful composition, camera choreography, skin/fabric/jewellery/material language, lighting, color, space, pacing, expressive motion, and meaningful transitions between scenes. Use real, permission-cleared bridal work as evidence of the brand's artistry. Keep copy concise and customer information/bookings easy to reach; don't bury the business inside an art experiment.

The owner specifically wants a sequential 3D story: scroll should advance an authored scene/animation, and the **next chapter or ordinary page section should take over only after the active chapter reaches its intended endpoint**. This is not satisfied by normal document scrolling with decorative fade-ins, parallax, or isolated scroll-triggered reveals. Research and recommend the right mechanism; do not assume that a hard full-page scroll lock is the answer.

### 2. Owner requirements that override older project notes

- **Protected opening:** preserve exactly the opening “Anshita Makeover” introduction that plays before entering the studio. The owner says it is perfect. Do not alter its artwork, timing, choreography, sound, transition, or presentation. First locate it precisely; do not confuse it with the separate GSAP entrance of the homepage heading. Recommend a non-regression check before any adjacent changes.
- **Mochi/Pip identity:** Mochi is the rabbit and must be selected by default; Pip is the bird and must remain selectable. Preserve the existing chatbot and its useful functions.
- **Character asset gate:** the owner wants the intended **actual 3D character asset in `3d character for anshitamakeover/`**. Do not substitute a still image, unrelated sample model, or the previously built procedural character for that requested model. Older notes point to `index-expressions.html`, while a prior implementation report says the file named `mochi.glb` is a copy of `Fox.glb` (an orange fox). Those notes conflict with the latest owner direction. Inspect the actual folder, enumerate and preview plausible model files, report rig/animation capabilities, and ask the owner to identify the correct model if ambiguous. Do not silently select a model by filename or begin implementation while the asset is unresolved.
- **“Proper physics” is not yet precisely defined.** Explain the difference between grounded, weighty animation (foot/paw contact, gait, acceleration, inertia, secondary ear/wing/body motion) and literal rigid-body simulation. Recommend only what serves the story, performance and reversible scroll. Do not promise or add a physics engine without confirmation.
- **Mochi default, Pip selectable; one active rig is preferred** unless measured evidence shows both can stay within the strict draw-call gate while preserving the models.
- **G8 is strict:** fewer than 25 draw calls. Do not weaken this target without explicit owner approval. Count every rendered pass that belongs to the experience, including particles/effects, and measure a representative moving/walking state—not only an idle/showcase frame.
- Preserve the current homepage CTA destinations: “Explore Lookbook” → Gallery; “Book on WhatsApp” → WhatsApp.
- The confirmed city names are **Jabalpur, Bhopal, Indore and Lucknow**. Do not reintroduce Raipur, other old city lists, or “All Over India” without confirmation. Distinguish regular service from destination-by-enquiry and flag unknowns rather than inventing coverage.
- Preserve the chatbot and current security posture. Do not ask for passwords, tokens, or private credentials. Inspect source safely; production exposure cannot be proven from source alone.
- Reduce excessive text and make desktop/mobile presentation more premium, but do not reduce the project to generic “minimal luxury” patterns.
- Duolingo may inform **learning/gamification/character-feedback mechanics only**. It is not a core visual reference, site architecture, or scroll-story benchmark.

### 3. Project, evidence sources, and verification rules

- **Review date:** 6 October 2026. If this brief is reused later, update the date and recheck every live site.
- Candidate live site recorded in project documents: **https://anshitamakeover.com/**. Verify it is reachable and canonical; record the date and what you actually saw. Do not treat old screenshots as the live site.
- Repository: **https://github.com/AkshatShibuProgrammer/anshitamakeover**, branch `arena/01a105d6-anshitamakeover`. The local working tree may contain uncommitted changes that are not on GitHub. If you only have GitHub, say so; do not claim to have reviewed local changes. Ask for the current diff/files if needed.
- Read and cross-check, where available:
  - `docs/PLAN_AUDIT_AND_GAP_ANALYSIS.md`
  - `docs/PROFESSIONAL_WEBSITE_REFINEMENT_PLAN.md`
  - `docs/MASCOT_RUNWAY_IMPLEMENTATION_AND_VERIFICATION.md`
  - `docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md`
  - `docs/ANIMATION_SPECIFICATION.md`
  - `docs/MASCOT_WALK_AND_SCROLL_GAP_ANALYSIS.md`
  - `docs/MOBILE_AND_MASCOT_GAP_ANALYSIS.md`
  - `django/core/templates/core/home.html`, `django/core/templates/core/base.html`, `django/core/templates/components/chatbot_modal.html`
  - `django/core/static/core/js/controllers/mascot-scroll-engine.js` and the character modules under `django/core/static/core/js/characters/`
  - `3d character for anshitamakeover/`, the current local diff, and screenshots if supplied.
- The audit documents were written against different snapshots. When notes conflict, inspect the exact source/date and identify the discrepancy. Label evidence as one of: **observed on live site**, **observed in supplied source**, **historical screenshot/test**, **third-party case-study/award description**, or **unverified**.
- Do not report test, performance, security, SEO, or accessibility passes unless you ran the relevant test on the current source/deployment. State limitations and the exact evidence needed.

### 4. What the site and repository already contain (verify before repeating)

The repository is an existing Django site with real business pages and purpose-built animation work. Do not propose replacing it wholesale or imply it is a blank template. The following is a **source/audit baseline**, not proof of current production behavior:

1. **Home and business journey:** `home.html` has a split bridal hero with a small real-work photo carousel, “Haute Bridal Artistry” heading, a long/static city line and longer supporting copy. The two homepage CTAs already have the correct destinations above. The site also has signature-look storytelling, service/artistry sections, a bridal lookbook/gallery and albums, services and service detail, packages, booking/cart flows, a travel estimator, reviews, an Academy, and a chatbot. Map what is live and which pages are source-only.
2. **Existing image-wheel experience:** a “Curated Lookbook & Works Wheel” uses bridal stills arranged with CSS 3D transforms. Source pins it with GSAP ScrollTrigger (`scrub` and a long scroll range) and also has wheel, pointer and keyboard interaction code. It is an image-card carousel with 3D perspective—not a real-time 3D scene. Verify current behavior, pin/release behavior and accessibility; do not call it a full 3D character/scene experience.
3. **Existing “Sacred Bridal Transformation”:** source includes a canvas that scrubs through 48 preloaded WebP frames with three labeled stages. This is a frame-sequence illusion, not a real-time 3D model. Verify whether it is present/live, how it loads and behaves on mobile, and whether it actually pins or merely scrubs within its current section range.
4. **Existing mascot/chat work:** a separate normalized-scroll mascot engine has hidden/enter, walk, showcase, docking and reverse states, and can dock a character into the existing chat launcher. Character rendering/treatment, copy-safe runway placement, Mochi/Pip selection and resource disposal have been worked on. The current design is **not yet a verified chapter scheduler that stages every story section until an animation endpoint**. Do not claim that the new chapter requirement is already met.
5. **Known verification gaps that must be reconciled:** an audit records a mobile `runwayBlocked` path that can jump to an endpoint (390×844 had only one of eight samples visibly moving), an old 180/80-pixel fallback, and 26 draw calls in a moving/walking state against the strict `<25` gate. A later implementation report records 22 calls in a showcase pose and says ScrollTrigger snapping was removed because it could write to page scroll. These measurements/states are not interchangeable: inspect current code and measure a representative moving state. Existing captures are diagnostic only; a partial §8 run is not a complete release pass.
6. **3D character files are ambiguous:** the repository/folder contains multiple prototypes and sample GLBs. Previous reports disagree about which character is canonical. The latest owner requirement above wins: show actual candidate 3D assets and resolve the intended model before implementation. Do not pass off a CSS/DOM carousel, a sprite/frame sequence, or a code-built procedural rabbit as the requested 3D asset.
7. **Security/chatbot:** retain current chatbot behavior and review the source-level security audit. It records serious admin/credential/CSRF concerns; do not repeat secrets or infer that a route is exposed in production without deployment evidence. Map risk and verification steps safely.
8. **SEO/business facts:** older source lists many cities and broad coverage that conflicts with the current four-city confirmation. Verify visible copy, schema, metadata and canonical URLs. Do not invent prices, ratings, addresses, hours, travel policies or outcomes.

### 5. The scroll-story requirement — investigate this deeply

Treat the desired behavior as a **sequence of authored animation chapters**. During an active chapter the 3D stage remains composed/pinned; user scroll advances that chapter's animation beats. The next chapter or ordinary page section takes over only when the current scene reaches its designed endpoint. Scrolling upward should return through/reverse the current scene predictably. This experience must feel deliberate, cinematic and controlled by the visitor.

Do not equate this with ordinary scrolling, smooth-scroll libraries, a few scroll-triggered reveals, or a progress bar. Do not assume a hard snap or custom wheel lock is accessible. Compare and recommend among at least:

- **Pinned, scroll-scrubbed chapter timelines:** a chapter owns a deliberate scroll distance; scroll position deterministically maps to authored scene progress; chapter releases at its endpoint and reverses on upward scroll.
- **Snap/step chapter transitions:** discrete progression per gesture/section; assess wheel/trackpad overshoot, touch intent, keyboard, backscroll, browser history and the risk of trapping visitors.
- **A hybrid:** e.g. pinned scrub within a chapter plus explicit “continue/skip” and clear release at the endpoint; native page scroll before and after the film.

Recommend a pattern and explain why. Define concrete behavior for mouse wheel, high-resolution trackpad, touch drag/swipe, keyboard/page keys, reverse scrolling, direct links/anchor navigation, resize/orientation change, loading/failed 3D, and browser back/forward. Provide accessible escape/skip/navigation controls and a reduced-motion path that communicates the story without forcing the animation. Never auto-scroll the document against the visitor's input; do not capture all wheel/touch input globally or create an inescapable scroll trap. If a chapter is pinned, explain its start/end, release, focus order, native fallback, and mobile version.

### 6. Starting reference set: inspect and verify, do not copy

These are research leads, not instructions to clone. Review the actual current site on desktop and mobile where possible; record what is directly observed, what is only claimed in an award/studio page, what transfers, and what must not be copied. Check that each link remains live.

**Closest art-direction, beauty, craft and chapter-story leads**

- **Evagher** — `https://evagher.com/en` (also `https://evagher.com/`): identified in project notes as an owner-shared visual reference. Re-check which parts are relevant to the brand's own artwork and 3D ambition.
- **Nymphai Cosmetics** — live site `https://nymphaicosmetics.com/en`; Awwwards entry `https://www.awwwards.com/sites/nymphai-cosmetics`. A current beauty/WebGL lead: Awwwards describes a cinematic hero, interactive 3D product page, editorial slider and texture storytelling; verify the live experience and mobile fallback rather than treating the award description as a usability audit.
- **Sarine Diamond Journey** — live `https://diamond-journey.com/`; studio case `https://www.charmerstudio.com/cases/sarine`; Awwwards `https://www.awwwards.com/sites/diamond-journey`. The studio describes five scrollable story chapters and 3D in “Birth” and “Transformation.” This is especially relevant to material/craft storytelling and chapter structure, though the diamond subject and visual mood should not be copied literally.
- **Cartier Watches & Wonders 2026** — live lead `https://www.cartier.com/watchesandwonders`; Awwwards `https://www.awwwards.com/sites/cartier-watches-wonders-2026`; technical description `https://www.webgpu.com/showcase/cartier-watches-and-wonders-immersive-garden/`. A luxury-object/immersive-world lead; the technical article describes six scrollable 3D alcoves. Verify the page's current availability and whether it has appropriate mobile/reduced-motion behavior.
- **The Watch** — Awwwards entry `https://www.awwwards.com/sites/the-watch`. A luxury object / real-time WebGL and Three.js lead. The direct live project URL is not yet confirmed; find it if possible and mark it unverified if unavailable.
- **Mousham Singh 3D Web** — portfolio lead `https://mousham.design`; Awwwards `https://www.awwwards.com/sites/mousham-singh-3d-web`. Useful as a 3D artist/portfolio and scroll-motion reference, not as a beauty-business template.
- **The World of Vogue Talents** — FWA case `https://thefwa.com/cases/the-world-of-vogue-talents-p2`. A fashion/editorial 3D-world lead: the FWA case describes a walkable desert, symbolic portals and photogrammetry fashion objects. Inspect its current availability and use only the world-building/art-direction lessons, not its navigation as a default for bookings.
- **Sleep Well Creatives** — `https://sleep-well-creatives.com`. A 3D narrative/pacing lead; study story sequencing and craft separately from luxury beauty art direction. Use third-party writeups only as leads, not primary proof.
- **MONOGRID** — `https://www.monogrid.com/`; Awwwards entry `https://www.awwwards.com/sites/monogrid-com`. Creative-studio 3D/scroll craft; use for technique and atmosphere, not a ready-made salon structure.
- **Future of Beauty** — Awwwards project lead `https://www.awwwards.com/sites/future-of-beauty`; investigate the original L’Oréal experience/live archive if available and mark availability honestly.

**Additional owner/project references and narrow-use examples**

- Fashion/brand art direction: Gucci `https://www.gucci.com/`, Dior `https://www.dior.com/`, Sabyasachi `https://www.sabyasachi.com/`; treat as craft/photography/editorial references, not assumed 3D or scroll models.
- Animation/scroll mechanics: Apple AirPods Pro `https://www.apple.com/airpods-pro/` and Apple Vision Pro `https://www.apple.com/apple-vision-pro/`. Inspect the interaction pattern and current mobile fallback; do not copy Apple's product strategy or site architecture.
- Bruno Simon `https://bruno-simon.com/`: only as a playful interactive-3D / portfolio mechanic reference, not the core visual direction.
- Duolingo `https://www.duolingo.com/`: **learning progression, gamification and character-feedback mechanics only**. Do not use its mascot style, bright app aesthetic, product architecture, or interaction model as the core Anshita site reference.
- Awwwards `https://www.awwwards.com/`, The FWA `https://thefwa.com/` and Godly `https://godly.website/` are discovery directories. Cite the actual project and primary case/live URL, not only a directory/listicle.
- Local/Indian bridal-business leads from the project audit: `https://www.instagram.com/dreammakeoversbykavya/`, `https://www.facebook.com/aanchalsingraha2/`, Vogue India article `https://www.vogue.in/beauty/content/top-indian-bridal-makeup-artists-you-should-follow-on-instagram-for-some-serious-inspiration`, and Anshita Makeover's Instagram `https://www.instagram.com/anshitamakeover21/`. Verify authenticity, access and relevance; do not invent claims from social previews.

### 7. Research tasks

1. **Establish the current state.** Inspect the live site and available source. Create an inventory separating production, source, historical screenshot and planned work. Map the homepage sections, page journey, existing photo/3D/frame-sequence pieces, mascot/chat behavior, mobile states, keyboard behavior and current chapter pin/release behavior. Name files/selectors and cite screenshots/URLs when possible.
2. **Research 6–10 relevant experiences.** Prioritize premium beauty, bridal/fashion/editorial, art portfolios, real-time 3D craft and authored scrollytelling. Include the strongest leads above and add only useful, verifiable examples. For each, view the actual live page on desktop and mobile if possible; capture review date, actual URL, what you directly observed, what came from a studio/award page, and confidence. Avoid SEO listicles unless clearly labeled as secondary.
3. **Make a reference comparison table.** Columns: rank/category; verified live URL; relevant experience/interaction; art direction and material/light/camera craft; scroll/chapter behavior; what transfers to Anshita; what should not be copied; mobile/performance/accessibility observations; evidence source/confidence. Do not reduce the analysis to screenshots, font/color recommendations or award scores.
4. **Synthesize a distinctive art direction.** Propose a coherent digital world for an Indian bridal-artistry brand, rooted in real work and relevant material/ritual detail—not a generic “luxury beauty” checklist. Describe palette, lighting, surfaces, depth, typography, image/3D balance, camera language, sound (optional and user-controlled), transition grammar and how the visual narrative supports booking. Give 2–3 genuinely distinct directions with trade-offs, then recommend one.
5. **Storyboard the scroll film.** Create a sequence of named chapters/beats (e.g. arrival, craft/detail, transformation, reveal, hand-off to real portfolio/services—propose a better story if warranted). For each: visual composition; selected 3D asset/character and interaction; camera/material/lighting; scroll range/time/animation endpoint; text; transition to next chapter; reverse-scroll result; mobile version; reduced-motion/skip version; performance cost. This is a research proposal, not permission to edit the protected opening.
6. **Resolve the chapter interaction.** Provide a clear comparison of pinned-scrub, snap/step and hybrid. Recommend one architecture with a simple state diagram or sequence description, exact chapter entry/hold/complete/release semantics, user-input mapping, reverse-scroll behavior, progress/navigation UI and explicit no-trap/no-auto-scroll rules. Include wheel, trackpad, touch, keyboard, resize, loading, reduced motion and direct-link cases. State which patterns are technically robust and which need prototyping.
7. **Resolve the 3D asset question before implementation.** Inventory plausible model files in the 3D folder; do not assume older documents are right. Show filenames and preview/contact-sheet references if available, distinguish the owner's actual asset from sample/demo assets, list rig/clip/material/texture/scale/performance properties, and ask the owner to identify it if uncertain. Explain grounded animation/secondary motion versus literal physics and what requires approval.
8. **Review performance and accessibility honestly.** Keep the strict G8 `<25` draw-call gate. Specify measurement method/state and include all passes. Note model/texture/animation cost, loading/fallback, mobile GPU/thermal constraints, reduced motion, keyboard/focus, screen-reader narrative, skip controls and escape path. Test at minimum 1440×900, 1024-wide, 390×844 and a narrower phone width; use real devices when available. Do not certify FPS from software rendering or an idle frame.
9. **Review business usability, security and SEO as constraints.** Preserve both CTA destinations and the chatbot. Identify content that needs owner confirmation (cities, prices, ratings, address, hours, travel terms, service outcomes). Check production security only with safe authorized evidence; describe source risks without exposing secrets or requesting credentials. Use current authoritative search guidance for SEO; no ranking promises, hidden text or doorway pages.
10. **Turn research into an implementation plan.** Prioritize low-risk/high-value steps; name exact source files/systems likely involved; separate discovery/prototype from production implementation; call out dependencies and approval gates (especially the protected opening and correct 3D asset). Give measurable acceptance criteria, a browser/device test matrix, rollback strategy and explicit “not yet verified” items. Do not recommend switching frameworks unless evidence proves it is necessary.

### 8. Required answer format

1. **Executive verdict:** what is distinctive/valuable in the existing site, the strongest opportunity, and the biggest risk.
2. **Current-state inventory:** source vs live vs historical vs planned; implemented/partial/broken/unverified; cite files, routes, screenshots and live pages.
3. **Ranked reference matrix:** 6–10 researched sites with the columns specified above and a clear best reference for (a) premium beauty art direction, (b) 3D craft, and (c) sequential scroll mechanics.
4. **Art-direction recommendation:** 2–3 non-generic creative directions with rationale and a selected direction.
5. **Chapter storyboard:** ordered scenes with endpoint hand-offs, reverse scroll, mobile and reduced-motion behavior.
6. **Scroll mechanics decision:** pinned-scrub vs snap/step vs hybrid, with input matrix and anti-trap safeguards.
7. **3D asset/physics findings:** candidate file list/previews, unresolved owner choice, and an honest motion recommendation. Do not silently decide the asset.
8. **Prioritized implementation plan:** phases, exact files/systems, low-risk first step, approval gates, acceptance criteria, test matrix and rollback.
9. **Risks and open questions:** ask only questions that block a safe decision. Clearly identify all facts that need owner confirmation.
10. **Sources:** live URLs, studio/award pages, source files and review date. Cite claims near the claim; separate first-hand observations from descriptions written by others.

Be candid and concrete. Do not produce generic advice such as “add a 3D hero,” “use more animation,” “make it gold,” “use smooth scrolling,” “make it like Duolingo,” or “switch to React.” Do not treat normal scroll-triggered reveals as the requested chapter sequence. Do not change code, the protected opening, CTA destinations, chatbot or security controls. The owner will review the research before implementation begins.

## PROMPT END

---

## Research links we found for the brief

These are starting points and should still be checked live by the second AI:

- [Nymphai Cosmetics — Awwwards Honorable Mention](https://www.awwwards.com/sites/nymphai-cosmetics) · [live site](https://nymphaicosmetics.com/en)
- [Diamond Journey — Charmer Studio case](https://www.charmerstudio.com/cases/sarine) · [live site](https://diamond-journey.com/) · [Awwwards](https://www.awwwards.com/sites/diamond-journey)
- [Cartier Watches & Wonders 2026 — Awwwards](https://www.awwwards.com/sites/cartier-watches-wonders-2026) · [Immersive Garden technical overview](https://www.webgpu.com/showcase/cartier-watches-and-wonders-immersive-garden/)
- [The Watch — Awwwards](https://www.awwwards.com/sites/the-watch)
- [Mousham Singh 3D Web — Awwwards](https://www.awwwards.com/sites/mousham-singh-3d-web) · [portfolio](https://mousham.design)
- [The World of Vogue Talents — FWA](https://thefwa.com/cases/the-world-of-vogue-talents-p2)
- [Sleep Well Creatives — live experience](https://sleep-well-creatives.com)
- [MONOGRID — Awwwards](https://www.awwwards.com/sites/monogrid-com)
