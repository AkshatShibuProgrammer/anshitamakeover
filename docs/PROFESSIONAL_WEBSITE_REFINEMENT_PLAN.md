# Professional Website Refinement Plan

- **Prepared:** 6 October 2026
- **Purpose:** Provide design and implementation options for a more professional, polished Anshita Makeover website, based on the source-level audit in `docs/PLAN_AUDIT_AND_GAP_ANALYSIS.md`.
- **Status:** Planning only. No application code or animation was changed.

## Owner selections and clarifications to date

- **Visual direction:** A — Couture editorial, retaining the existing brand palette with more restraint.
- **Protected animation:** The opening “Anshita Makeover” sequence that plays before entering the studio. Preserve it exactly; do not retime or redesign it.
- **Mochi/Pip:** Mochi is the rabbit and default; Pip is the bird and remains selectable. Use the real 3D character, never a flat image or unrelated substitute. The previous owner handoff identifies `3d character for anshitamakeover/index-expressions.html` as the intended Mochi/Pip reference; use that as the working source unless the owner identifies another file. Implement believable grounded motion and secondary movement; clarify any request for a full physics simulation before adding one.
- **City treatment:** A — Gentle rotator with pause/next controls and a reduced-motion static state. The owner named Jabalpur, Bhopal, Indore and Lucknow; confirm whether each is regular service or destination-by-enquiry before publishing the details.
- **First prototype scope:** A — Homepage and shared mobile shell, then extend page by page.
- **Admin/customization knowledge:** The owner does not know the admin route or deployment customization. No credentials are requested; production reachability remains unverified.
- **Homepage CTA:** The owner confirms the current actions are correct: “Explore Lookbook” links to Gallery and “Book on WhatsApp” opens WhatsApp. Preserve those destinations.

These are the owner's preferred directions, not permission to begin implementation. Review the second AI's research and confirm the 3D asset before finalizing the motion details.

---

## 1. Non-negotiable constraints

- **Keep the existing Anshita Makeover brand animation exactly as it is.** It is protected. Do not alter its timing, keyframes, artwork, or choreography. Limit surrounding layout changes so they cannot affect it, and add a visual non-regression check before touching adjacent CSS/JS.
- Keep the current chatbot and its useful behavior. Improve its first impression and accessibility; do not remove or replace it.
- Keep the existing character designs. **Mochi is the rabbit; Pip is the bird.** Make their appearances easier to see, and make their entrances/exits calmer and more intentional.
- Keep G8 strict: **fewer than 25 draw calls**. Do not trade away character fidelity or loosen this target without explicit approval.
- Do not invent service cities, prices, ratings, timings, treatment outcomes, or travel promises. Verify business facts first.
- The second AI's current premium-site research is still pending. Use this plan to compare options; select and implement only after that research is reviewed with the owner.

---

## 2. Recommended experience direction

The goal is **quiet, confident bridal luxury**: clear hierarchy, beautiful real work, precise service information, restrained motion, and an easy path to enquire or book. Premium should come from typography, photography, spacing, consistency and trust—not from adding more gold effects, animations, badges or promotional copy.

### Visual-system options

| Option | Direction | Advantages | Risks / trade-offs |
|---|---|---|---|
| **A. Couture editorial — recommended** | Retain the existing wine/plum, ivory and gold identity, but use gold more sparingly; alternate calm light/ivory content areas with a small number of deep-plum feature sections. Give bridal photography more space and reduce ornamental borders, glows and gradients. Pair one expressive display face with a highly readable body face. | Feels premium and personal while retaining brand recognition; supports strong photography; can make long pages feel calmer. | Needs a consistent page-by-page system so it does not become a generic template or an abrupt rebrand. |
| **B. Deep royal studio** | Keep the dark/wine canvas as the dominant treatment. Reduce glow/gradient layers, increase text contrast, use larger image-led cards and more negative space. | Lowest palette change; preserves the existing dramatic brand mood. | Dense dark pages can still feel heavy, especially on phones; careful contrast and section rhythm are essential. |
| **C. Modern bridal minimal** | Use warm white/ivory and charcoal as the default, with restrained rose or champagne accents and photography as the main color. Keep plum for selected calls-to-action and brand moments. | Very legible, contemporary and image-forward; gives the strongest visual reset. | Highest brand change and rework; should not be chosen without owner approval and a small visual prototype. |

**Selected direction:** A. Prototype the couture-editorial treatment for the homepage and compare one representative screen with the current darker treatment before implementation. Keep the existing brand palette recognizable; do not perform a wholesale palette rewrite. Standardize spacing, heading scale, button shape, card radius, image treatment, focus styles and hover states in shared design tokens rather than patching pages independently.

---

## 3. Animation options — excluding the protected brand animation

The brand animation remains untouched in every option below. These options concern the separate Mochi/Pip scroll experience and minor interface motion only.

### Shared motion rules

- Use one clear entrance, one readable pause/showcase, and one clear departure. Avoid repeated bouncing, overshoot, spin, strobe, large zooms and gratuitous particles.
- Keep the motion tied to scroll progress and reversible in both directions. No `runwayBlocked` endpoint snap and no legacy threshold pop.
- Give the characters enough reserved space to be recognized. Do not enlarge them by covering copy, booking controls, navigation or the chatbot.
- Keep both designs faithful to the approved models. Use character-specific expression only where supported by the current rig; do not redraw their identity to solve a layout problem.
- Honor reduced-motion settings with a stable, attractive composition or a short, non-essential fade. The journey must not imply that a walk occurred when the character was never visible.
- Continue testing with exact-pixel appearance checks and the strict `<25` draw-call gate. A simultaneous two-rig design must not be selected until it meets that gate without visual damage.

### Character-story options

| Option | Choreography | Pros | Risks / trade-offs |
|---|---|---|---|
| **1. Sequential cameos — alternative** | Mochi and Pip take turns in clearly separated parts of the journey. Each gets a deliberate arrival, brief showcase and departure; only one live rig is active at a time. A visible label or small portrait makes it clear who is present. | Makes both characters visible and recognizable while limiting concurrent WebGL work; easiest to test at mobile sizes; aligns with the current one-active-rig architecture. | Owner must approve the order and story. A poorly timed hand-off could still feel like a character swap rather than a natural entrance. |
| **2. Paired appearance** | Both characters share a single composed moment, with one leading and the other reacting. | Strongest sense of friendship and makes both visible together. | Highest draw-call and layout risk; may conflict with strict G8 or force compromised character fidelity. Treat as an optional later experiment, not the default. |
| **3. Visitor-selected character — selected direction** | A small, accessible “Meet Mochi / Meet Pip” control selects which character appears in the journey; no automatic switching. | Gives visitors control; predictable, easy to pause and more comfortable for motion-sensitive users. | Adds a control and decision to the homepage; may make the page less magical and requires a clear default state. |

**Selected choreography:** Use Option 3 with Mochi selected by default and a clearly named, keyboard-operable control to switch to Pip. Activating a choice loads only that character's live 3D rig. Give the selected character a steady entrance, a pause long enough for its face and silhouette to read, one restrained character-specific gesture, and a complete departure/dock. Keep the journey continuous and reversible. The owner wants the source character from the `3d character for anshitamakeover/` folder, not an image or an unrelated substitute; identify the exact source file before implementation. “Proper physics” should be clarified as grounded locomotion, body inertia and subtle secondary motion versus a full physics simulation; do not claim physical simulation unless it is implemented and measured. Avoid promising a precise pixel size until the responsive stage has been redesigned and measured at 1440, 1024, 390 and 360 px widths.

Do not load both live rigs simultaneously unless a later approved test proves the strict G8 `<25` gate and visual fidelity. **Do not change the named Anshita Makeover animation to make room.** Recompose adjacent content around it, or use a separate mascot area lower in the page if that is the safer layout.

---

## 4. City-rotation options and local SEO

Use the owner's current list—Jabalpur, Bhopal, Indore and Lucknow—as the starting source for a coverage check. Distinguish regular service from destination-by-enquiry and establish one verified source for that distinction. The travel estimator, visible site copy, LocalBusiness structured data and any coverage page must not contradict one another. Remove broader city/all-India claims unless the owner confirms them.

| Option | Treatment | Pros | Risks / trade-offs |
|---|---|---|---|
| **A. Gentle hero rotator plus visible coverage details — recommended** | Show one verified city at a time in the hero. Use a pause/next control, stop or pause on focus, and respect reduced motion. Elsewhere on the same page or on a useful service-area page, show the actual coverage in normal, visible text with travel caveats. | Delivers the desired visual rotation without making animation the only way to learn coverage; clear path to more detail. | Needs controls and careful mobile spacing. Never rotate unverified destinations. |
| **B. User-controlled city switcher** | Keep one city visible until the visitor selects Next/Previous or a city chip. | No automatic text changes; strong user control and accessibility. | Less dynamic; can add clutter if too many cities are presented in the hero. |
| **C. Static location statement** | Replace the long list with a concise verified statement and a link to service-area details. | Simplest, fastest and least risky; excellent fallback for reduced motion. | Does not deliver automatic city rotation. |

**Selected direction:** A, using the owner's four named cities, subject to confirming which are regular service and which require destination-by-enquiry. Keep C as the reduced-motion/static state. Add visible pause/next controls, stop or pause rotation on focus, and keep all important coverage details visible to visitors and crawlable; do not add hidden keyword lists or thin, near-identical city pages. Google allows user-facing dynamic content such as slideshows, but its spam policy prohibits hidden text used to manipulate search [1](https://developers.google.com/search/docs/essentials/spam-policies). Google says established SEO fundamentals apply to its AI Search features; special schema or `llms.txt` is not required for Google Search [1](https://developers.google.com/search/docs/appearance/ai-features) [2](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). Keep `llms.txt` only if useful to other consumers, not as a promised Google ranking lever. Verify visible ratings and structured data; self-serving LocalBusiness reviews are not eligible for Google's review-star feature [1](https://developers.google.com/search/docs/appearance/structured-data/review-snippet).

---

## 5. Page-by-page refinement plan

| Page / area | Professional refinement | Priority |
|---|---|---|
| **Shared header, footer and mobile navigation** | Reduce simultaneous fixed elements; make the main action obvious; keep navigation names consistent across desktop, drawer and mobile; allow browser zoom; verify touch targets, contrast, keyboard focus and safe-area spacing. Avoid letting the chatbot, bottom navigation and page controls compete. | High |
| **Home** | Preserve the brand animation unchanged. Shorten the surrounding headline and supporting copy; use one primary booking/enquiry action and one secondary browse action. Add a concise, verified location cue. Reduce repeated claims and competing badges. Give signature looks and the gallery stronger photographic emphasis, then present services, trust evidence and booking steps in a calm order. | Highest visual priority |
| **Services catalogue** | Replace internal/ornate labels where they obscure customer meaning. Use a clear category filter, consistent service cards, readable starting price, one-sentence description and a direct detail/booking action. Explain package savings only when the calculations and terms are verified. | High |
| **Service detail** | Use one strong real image, plain-language summary, inclusions, price basis, duration/availability only if verified, travel note and a single primary booking action. Show related services as a secondary choice rather than competing CTAs. | High |
| **Packages and package detail** | Make it easy to compare what is included, who it suits, event count, price and any verified saving. Avoid discount urgency or “save” claims unless the reference price and terms are genuine and clear. Keep add-to-plan and book/enquire actions consistent. | High |
| **Gallery and album detail** | Treat real, permission-cleared work as the main proof. Use fewer, larger images; consistent crops; descriptive alt text; fast responsive images; simple filters and a clear route from a look to its relevant service. Keep cinematic effects optional and restrained. | High |
| **Cart / beauty plan / booking path** | Make the next step obvious, show an itemized estimate and any known taxes/travel/terms before submission, preserve edits, and provide a clear confirmation state. Keep the journey short and mobile-first; avoid asking for information before it is needed. Do not promise final availability until confirmed. | High / conversion |
| **Travel estimator** | Clearly label distances and fees as estimates where appropriate; explain origin, assumptions and what happens for unlisted destinations. Reconcile the city list with verified coverage and the actual booking policy. Keep the input and result readable on a phone. | High / trust |
| **Chatbot modal and full chat page** | Keep the chatbot. Make the first greeting concise and helpful; show a small number of primary actions, with language choices still available but not dominating the opening view. Give clear close/back controls, keyboard/focus behavior, readable transcripts and no automatic promotional message that overwrites the greeting. | High / usability |
| **Academy** | Separate education messaging from bridal-service messaging. Lead with who the program is for, what is taught, format, duration, verified outcomes and fees; put curriculum and FAQs below. Do not imply certification or outcomes that are not documented. | Medium |
| **Package builder** | Use a calm step-by-step form with clear labels, optional fields marked optional, sensible defaults and a readable itemized result. Validate on the server, explain recommendations in plain language and provide a direct next step. | Medium |
| **Admin and security-facing flows** | Treat security remediation as a release prerequisite, not a cosmetic task: remove exposed defaults/secrets, restore CSRF and proper staff authorization, invalidate potentially affected sessions and verify production settings. Keep internal admin tools out of the public visual hierarchy. | **Critical before public release** |

### Copy standard for every page

- One clear page purpose and one primary action.
- Plain language before brand poetry; move detail to the page where it helps the decision.
- Remove repeated superlatives, unsupported performance claims and keyword-stuffed city lists.
- Keep real prices, inclusions, travel terms and availability consistent across the site.
- Make headings descriptive enough to scan and accessible enough to understand out of context.

---

## 6. Recommended order of work

1. **Contain and verify security:** confirm deployment exposure, rotate/remove any exposed credentials if live, close public passcode paths, restore CSRF/staff checks and run privileged-write tests. Confirm coverage, rating, hours, address, service and pricing facts with the owner.
2. **Protect the approved baseline:** identify and capture the exact protected brand animation; document its viewport and state; add a visual regression check before any neighboring layout changes. Do not edit its animation.
3. **Review the second AI's research:** compare cited sites, observed details, mobile behavior, implementation cost and relevance. Separate observed evidence from generic style suggestions.
4. **Apply the selected direction in a prototype:** start with the couture-editorial home/shared-shell treatment, Mochi-default/Pip-selectable control and controlled city rotator. Compare desktop and mobile before extending the system to other pages; identify the exact 3D-folder character source and confirm service coverage details first.
5. **Refine the home and shared shell:** implement only approved copy/layout changes around the protected animation; tune the responsive mascot stage separately and keep the chatbot intact.
6. **Apply the system to customer decision pages:** services, service detail, packages, gallery and cart/booking; then travel estimator and Academy.
7. **Accessibility, SEO, performance and verification:** test keyboard/screen reader/reduced motion/zoom; validate canonical metadata, visible structured facts and crawlable service areas; re-run all tests and real-device checks. Preserve G8 `<25` throughout.

---

## 7. Release-quality acceptance checklist

- Protected Anshita Makeover animation has no visual or timing difference from the owner-approved reference.
- Desktop and mobile pages have a clear hierarchy, legible text, consistent spacing and no overlapping fixed UI.
- Mochi and Pip are each recognizable at their approved size, with a calm entrance, readable hold and complete departure; no text collision or binary jump occurs in either scroll direction.
- Reduced-motion, zoom, keyboard, focus, screen-reader labels and contrast are tested.
- The chatbot still works; concise default presentation does not remove existing functions or language access.
- City names, prices, travel coverage, hours, ratings, service claims and schema agree with verified business facts.
- No thin doorway pages or hidden SEO city lists are introduced; metadata and sitemap contain the real canonical pages.
- Security fixes are verified under the actual production settings, including CSRF, admin authorization, session invalidation, rate limiting and secret cleanup.
- G8 remains **strictly `<25` draw calls** with visually faithful characters; no exception is assumed.
- Fresh desktop/mobile captures and test evidence are recorded from the branch being released, not inferred from old screenshots.

---

## Selections made and open confirmations

Selected/clarified by the owner in this discussion:

1. **Couture editorial** direction, retaining the current brand identity with a more restrained layout.
2. **Mochi default, Pip selectable**, with one live 3D rig at a time.
3. The owner wants the **existing 3D-folder character**, not an image or unrelated substitute, with convincing physical motion.
4. **Jabalpur, Bhopal, Indore and Lucknow** are the owner's named coverage cities; regular service vs destination-by-enquiry still needs to be stated accurately.
5. **Controlled city rotator** with pause/next controls and a reduced-motion static state.
6. **Homepage and shared mobile shell first**, then extend the approved system page by page.
7. The protected animation is the opening **“Anshita Makeover”** sequence before entering the studio; do not change it.

Still to confirm after reviewing the second AI's research:

- Which exact file/model in `3d character for anshitamakeover/` is the intended 3D character. The folder has multiple prototypes and sample models; do not substitute without confirmation.
- Whether “proper physics” means grounded animation with inertia/secondary motion or a true physics simulation.
- Whether the second-AI research suggests a better reference or changes any of the selected visual details.

**Selections guide the prototype; they are not authorization to alter the protected brand animation or begin implementation before the research and open facts are reviewed.**
