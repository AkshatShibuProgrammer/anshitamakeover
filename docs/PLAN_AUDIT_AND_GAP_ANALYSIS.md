# Website Plan Audit & Gap Analysis

- **Prepared:** 5 October 2026
- **Repository:** [`AkshatShibuProgrammer/anshitamakeover`](https://github.com/AkshatShibuProgrammer/anshitamakeover)
- **Branch:** `arena/01a105d6-anshitamakeover`
- **Base / current HEAD at audit:** `0fef5f72451d10c157c1de5123e5364b250bb8cd` (`main` base); implementation files are uncommitted/unpushed.
- **Scope:** Audit the existing 3D mascot, mobile/desktop, premium presentation, copy, city/local SEO, chatbot and security plan against the current working-tree source, available screenshots and last recorded browser results. **No product code was changed for this audit.**

---

## Executive verdict

The plan has a strong technical foundation, but it is **not ready to call complete or visually approved**. It describes a sophisticated 3D journey and hardening work, yet the owner's present priorities—premium impression, clear Mochi/Pip visibility, calm arrivals/departures, less copy, mobile composition, and honest city SEO—are not yet achieved or measured end-to-end.

### Most consequential findings

1. **The mobile runway fallback can turn the scroll film into a binary jump.** When copy leaves no horizontal runway, the engine sets progress directly to `0` or `1`. At the previously tested 390×844 viewport the lane was recorded as blocked, with only one of eight samples showing the character. This is a direct explanation for the poor “come and go” feel and conflicts with the continuous reversible-motion requirement.
2. **The runway's visibility budget conflicts with the 320 px showcase target.** The copy-safe lane caps the nominal character height to roughly 204 px at 900 px screen height, 189 px at 844 px, 177 px at 800 px, and 113 px at 560 px—before considering the mobile copy-free-width failure. The desktop screenshot is consistent with a modest lower-screen mascot, not a 320 px hero moment.
3. **A critical admin-credential exposure exists outside the 3D work.** The artist onboarding route accepts hard-coded passcodes including a query-string path, and `artist_verified` is accepted by the admin authorization decorator. Admin login autofill and credentials are also present in templates/docs. Values are intentionally redacted here; treat them as compromised and rotate/remove them before any public deployment.
4. **The hero location line is static, crowded and makes broad service-area claims.** The homepage currently lists multiple cities and “All Over India” as fixed text, not an appearing/disappearing city treatment. Business coverage needs confirmation before turning this into SEO content.
5. **The current SEO foundation exists but is incomplete and contains unverified structured claims.** `robots.txt`, canonical/OG metadata, JSON-LD, a sitemap and `llms.txt` are present. The sitemap is a static eight-URL list; LocalBusiness data includes hard-coded rating, hours, address and India-wide coverage that must be verified. The plan does not yet define a truthful local SEO content architecture or evidence-based AI/agentic discovery work.
6. **The success criteria can pass without proving the experience happened.** The runway test correctly checks sampled collision and fade states, but exempts docked/faded frames and does not require enough actual walking/showcase frames. Thus a “PASS” can mean “did not collide,” not “Mochi/Pip were visible and moved smoothly.”
7. **The comprehensive audit and related plans contain stale implementation descriptions.** The audit's benchmark matrix still says the active behavior is a `scrollY > 180` threshold; current primary code has a normalized progress engine, while threshold logic remains in a fallback. Several older docs cite another branch/remote baseline. The audit should be reconciled, not treated as current test evidence.

**Overall status:** Technical implementation foundations = **substantial / partial**. User-facing premium redesign and responsive behavior = **open**. Security = **critical follow-up required**. Full §8 sign-off = **not achieved**.

---

## Audit method and evidence limits

- Read the current source on `arena/01a105d6-anshitamakeover`, the authoritative audit, mobile/animation plans, and the relevant test probes.
- Reviewed available images: `docs/verification/runway_walking.png`, `runway_showcase.png`, `runway_docked.png`, `current_mobile_gallery.png`, and `home_showcase_animated.png`. Some image files have no reliable capture metadata; treat them as diagnostic snapshots, **not proof of the current production deployment**.
- The latest recorded runway probe passed at 1440×900, 1280×800 and 390×844 with no sampled copy/lane collisions. At 390×844 the last recorded run had `runwayBlocked` and only one of eight samples with the mascot visible.
- The last recorded full §8 sweep was partial: G3b/G4/G6/G11/G12 passed; G5/G8/G10 failed at that time; G7 was not representative under SwiftShader; the sweep aborted on a mobile navigation timeout, leaving later gates unknown. G10 introspection changes were made after that run and remain unverified.
- Static syntax checks passed this turn for the core character/adapter/engine JS and 10 Python files. `python3 django/manage.py check` could **not** run because Django is not installed in the current sandbox; no Django test suite or fresh browser session was run for this audit. Do not represent this report as a live-site or current §8 pass.

---

## 1. Plan-to-implementation status matrix

| Workstream | Plan / owner requirement | Current evidence | Gap / status |
|---|---|---|---|
| Protected brand animation | Preserve the existing “Anshita Makeover” animation exactly. | Owner has explicitly said it is perfect and must not change. `home.html` has a multi-part GSAP hero timeline. | **Not protected by a measurable baseline yet.** The plan needs a named element/sequence, reference capture and non-regression check. Do not assume the protected brand animation is the mascot animation. |
| Correct character source | Mochi is the rabbit; Pip is the bird; use the `index-expressions.html` version. | `lumiere-characters.js` has procedural Mochi/Pip classes; studio adapter resolves those classes. | **Foundation present.** Confirm current public pixels/palette against the exact reference. The alternate `parts/` build is not the target. |
| Studio rendering | PMREM, ACES, sRGB, soft shadows, pixel-ratio bound. | `mascot-rig-adapter.js` configures environment/tone mapping, shadow map and clamps DPR; low-width perf profile disables shadows/AA. | **Mostly implemented; visual/per-device validation incomplete.** Verify both rigs and device profile, not just a frozen screenshot. |
| Continuous scroll film | Normalized progress, gait, showcase, docking and full reversal; no binary threshold. | `mascot-scroll-engine.js` has progress phases and a rendering loop. `base.html` also retains an 180/80 px threshold fallback. | **Primary path is present; fallback and mobile blocked path violate the no-jump contract.** ScrollTrigger config has `onUpdate`, not the audit's explicit `scrub: 0.8`; engine uses its own `smoothing: 13` dampening instead. Confirm the actual perceived response against the spec. |
| Bottom runway | Stay in a reserved bottom lane and never cover copy. | Dynamic lane/keep-out code and a pixel-based collision probe exist. | **Collision work present, responsive composition incomplete.** On a narrow phone the copy-free x-window can be too small for the sprite. The engine responds by binary endpoint mapping, not by a continuous mobile film. |
| Character prominence | User can see/recognize both characters; graceful entrance and departure. | Current configured showcase asks for 320 px, but the lane clamps it. The dock is a 74 px character in a 78 px medallion. Active canvas is switched between Mochi/Pip. | **Not met / decision required.** At the dock they are intentionally tiny; during the mobile journey the lane can be blocked. The code's selector also cycles a third legacy character, Asha. Current plan does not state whether Mochi and Pip should appear together, take turns, or be switchable only. Ask the owner before choosing. |
| Existing chatbot | Keep current chatbot behavior; improve presentation around it. | `chatbot_modal.html` remains the active included component and contains existing chat, language selection, bubble/chips and character canvases. | **Behavior retained, visual hierarchy unresolved.** Long intro, six language choices and three quick-reply chips make the bubble/modal large. The greeting-vs-promo rotator race remains open (G5). |
| City animation + SEO | City names should appear/disappear; proper Google and AI/agentic discovery. | Hero line in `home.html` is a static list of Jabalpur, Bhopal, Raipur, Lucknow, Nagpur, Pune, Delhi, Chennai, Hyderabad and “All Over India.” `llms.txt` exists. | **Not implemented as requested.** No defined verified service-area data source, rotation/accessibility behavior, or city landing-page policy. Avoid hidden text/doorway pages and verify every coverage claim. |
| App security | CSRF, XSS safety, throttling, UUID references, CSP, safe production settings and bounded WebGL. | Chat/booking/review CSRF and rate limits, chatbot sanitizers, UUID public booking reference, production settings and WebGL disposal are present. | **Partial; critical gaps remain.** Hard-coded artist/admin credential exposure, CSRF-exempt admin mutation endpoints, per-process rate-limit cache and default report-only CSP need review. |
| Performance | Meet §8 FPS and draw-call budget on desktop/mobile. | Identity mesh merge reduced Mochi 61→25 and Pip 73→32; draw calls measured 26 in the walking state including dust. | **G8 fails:** strict `<25` remains required; no exception approved. SwiftShader FPS is not representative. Real-device data absent. |
| Verification | Empirical visible walk, dock coordinates, >55 FPS, zero console errors and security checks. | Runway collision probe passes its current narrow checks; partial §8 results exist. | **No overall gate pass.** Need positive visibility/progression assertions, fresh full run and real-device sampling. |

---

## 2. Findings with priority and source evidence

### F-01 — Mobile blocked runway collapses progress to two endpoints

**Priority: P0 for the mascot experience.**

- `mascot-scroll-engine.js:811–817` sets `runwayBlocked` when the copy-free horizontal window cannot fit the character.
- `mascot-scroll-engine.js:330–337` then replaces actual scroll progress with `0` at the top or `1` after 2% progress whenever `runwayBlocked` is true.
- The same behavior is not limited to reduced-motion preferences: the condition combines `reducedMotion || runwayBlocked`.
- The last recorded 390×844 probe had the band blocked. That means the visitor can go from the hidden start to the docked state with essentially no walk/showcase, then reverse just as abruptly.
- `verify_mascot_runway.py` exempts docked and opacity-faded frames and currently reports collision safety without requiring a minimum number of visible walking samples. It can therefore pass a journey that the owner experiences as “comes and goes terribly.”

**Gap closure:** Do not map `runwayBlocked` to a forced endpoint. First redesign the narrow-screen stage/lane so there is a safe, legible composition; preserve a continuous/reversible state if motion is allowed. If there truly is no usable space, use a deliberate accessible fallback that does not pretend a walk occurred. Make the test fail when expected walking/showcase states are absent.

### F-02 — Lane constraints shrink the character below its showcase target

**Priority: P1.**

The configured target is `showcaseHeightPx: 320` (`mascot-scroll-engine.js:77`), but `maxStagedHeight()` (`:792–801`) computes a smaller safe height:

`((lane height - (26 px hop + 8 px reserve) - 6 px floor gap) / (1 + 0.06 overscan)) × 0.94 fill ratio`.

| Viewport height | Lane height | Approx. maximum nominal character height |
|---:|---:|---:|
| 900 px | 270 px | 204 px |
| 844 px | 253 px | 189 px |
| 800 px | 240 px | 177 px |
| 700 px | 210 px | 151 px |
| 560 px | 168 px | 113 px |

These calculations explain why a nominal 320 px mascot is not actually delivered, especially on shorter screens. The 390 px viewport also has a separate horizontal-blocking problem. This is a **design-budget conflict**, not just an animation bug: reserve space, height, copy and recognition have not been co-designed for each breakpoint.

**Gap closure:** Decide the desktop and mobile composition first. Make the character's visible silhouette height an explicit acceptance measure per breakpoint; either reserve enough space or provide a different mobile layout. Do not solve this by allowing the character to cover the text/CTA.

### F-03 — The current design plan does not settle the two-character story

**Priority: P1 / owner decision.**

- `chatbot_modal.html:120–134` includes Asha, Mochi and Pip stages. Mochi is initially displayed; Pip is initially hidden.
- `base.html:7195+` cycles `asha → mochi → pip` and retains a third legacy persona, while the scroll engine attaches one active rig at a time.
- The plan requires parity/hot-swapping for Mochi and Pip but does not say whether they should walk together, appear one after another, or remain a manual selector choice.

**Gap closure:** Ask the owner to choose the narrative. Keep the chatbot's established function while limiting the *new walk/dock cast* to Mochi and Pip. Do not silently remove Asha's old assistant identity or expand the new animation to extra characters.

### F-04 — Forbidden binary threshold survives in the fallback path

**Priority: P1.**

The main WebGL engine is scroll-progress driven, but `base.html:8103–8130` retains a `legacyThresholdCheck()` with enter/exit values of 180/80 px. It triggers when `engineActive()` is false (for example, if the engine/rigger never becomes active). That can still create the exact threshold-style pop the audit rejects on unsupported devices.

**Gap closure:** Define a fallback that is visibly a fallback—static accessible launcher or simple continuous CSS progress—not a hidden binary entrance. Add a test forcing WebGL/init failure and confirming no threshold pop.

### F-05 — The greeting and rotating concierge speech compete

**Priority: P1.**

The engine gates a post-dock greeting and flags it with `data-mascot-greeting`; `base.html`'s speech rotator has a corresponding guard. Nevertheless, the last full sweep saw a Hindi promotional tip and `flag=None`, while an isolated docking run displayed the correct greeting. G5 remains unresolved due to lifecycle/order interaction, not incorrect copy.

**Gap closure:** Give the dock greeting one owner and a deterministic lifecycle. Test initial load, normal scroll, scroll-up reversal, repeat docking, chat-open state, saved language and the promotion timer in one browser run.

### F-06 — The current copy density and overlays fight the premium goal

**Priority: P1, directly supported by owner feedback and available screenshots.**

- `home.html:2694–2695` uses a long hero tagline with multiple claims (including “international artistry” and “18-hour cry-proof”); in the available 1440×900 runway snapshot the right-column copy wraps into many lines while the mascot sits lower in the lane.
- `home.html:2692` prints a long static string of cities plus an India-wide claim.
- `chatbot_modal.html`'s welcome is a multi-sentence pitch and immediately includes six language choices; the speech bubble adds a heading, text and three chips (`:105–115`).
- The available mobile screenshot `current_mobile_gallery.png` shows the mascot/chat bubble and fixed navigation competing with gallery content. It is an older repository artifact, so re-check the live state before calling it current.

**Gap closure:** Treat this as an information-hierarchy problem, not a request for more motion. Prototype a short hero promise, one primary booking action, concise location cue and one concise concierge greeting; move detailed service/claims into relevant pages. Keep the full chatbot accessible on user request. Verify actual facts before retaining performance/“cry-proof” marketing claims.

### F-07 — The city treatment and local SEO are currently disconnected

**Priority: P1.**

- The homepage city sequence is static HTML in `home.html:2691–2693`; it does not appear/disappear or select one city at a time.
- The business-information JSON-LD in `base.html:41–73` claims a hard-coded aggregate rating/count, India as `areaServed`, hours 07:00–22:00 all week, and only country-level address data. Verify these against real business records and Google Business Profile. Do not fabricate an address, rating or coverage.
- `public.py:377–423` serves a hand-authored sitemap with eight core URLs; DB-driven service/package/gallery detail pages are not listed in that static XML.
- `public.py:352–375` serves a static `llms.txt` with India-wide and service/claim language. `llms.txt` does not replace visible site facts, structured data, internal links, sitemap coverage or Search Console validation.
- Most pages inherit a generic meta description/OG description from `base.html`; some pages override description, but a full crawl has not measured uniqueness.

**Gap closure:** Establish one verified coverage source. A tasteful visual rotator may display one service city at a time, but the semantic page must remain crawlable and truthful. Only make indexable city pages for real, useful service areas with distinct evidence/content; avoid doorway pages or hidden text. Generate/maintain sitemap entries for the canonical pages that should be indexed. Validate structured data and Search Console coverage.

**Current Google guidance checked for this audit:** Google permits user-facing dynamic content such as a slideshow that cycles text, while its spam policy prohibits hidden text used to manipulate search [1](https://developers.google.com/search/docs/essentials/spam-policies). Google's AI Search guidance says existing SEO fundamentals apply—important text should be available, pages crawlable/indexable, internal links useful and structured data match visible content; it specifies no special AI schema/optimization and says `llms.txt` is not required for Google Search (Google says Search ignores it) [1](https://developers.google.com/search/docs/appearance/ai-features) [2](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). The file may still be maintained for other consumers, but should not be sold as a Google ranking lever. Google's review-snippet guidance also says self-serving reviews on a LocalBusiness site are not eligible for its review-star feature; the hard-coded aggregate rating must be verified, and should not be kept as a rich-result tactic [1](https://developers.google.com/search/docs/appearance/structured-data/review-snippet).

### F-08 — Mobile accessibility has a preventable zoom restriction

**Priority: P1.**

`base.html:6` sets `maximum-scale=1.0`, which can prevent user pinch-zoom. This is inconsistent with an accessible mobile experience. The available mobile screenshot also appears to show missing/tofu glyphs for some non-Latin characters; because screenshot freshness/font setup is unknown, this should be checked on a real phone rather than treated as confirmed production behavior.

**Gap closure:** Allow browser zoom; test keyboard/screen-reader/reduced motion and native-language glyphs on actual iOS/Android browsers. Avoid relying on a moving visual city label as the only accessible text.

### F-09 — Critical admin access material is present in source/docs

**Priority: Critical security blocker.**

- `services_pricing.py:663–682` exempts `/artist-onboarding/` from CSRF and accepts hard-coded passcodes from POST **or a `key` query parameter**. A successful attempt sets `session['artist_verified']`.
- `common.py:8–23` treats that session flag as sufficient for `admin_required`; the same flag can therefore authorize administrative APIs.
- `services_pricing.py` also marks multiple admin write handlers `@csrf_exempt` (including price/service/package/studio-service-related handlers).
- Admin password/quick-fill material is present in `admin_login.html`, `base.html` and project documentation. Exact values are intentionally not repeated in this report.
- A query-string secret can be stored in browser history, referrer data and proxy logs. No rate limit is visible on the artist passcode attempt.

**Gap closure:** Treat any exposed/reused values as compromised: rotate production admin/artist credentials, invalidate relevant sessions, remove hard-coded passcode paths and quick-fill UI/docs, require staff authentication or a properly designed one-time secret flow, add rate limiting, restore CSRF protection on authenticated writes, and audit repository history/deploy logs. Add regression tests proving unauthenticated and cross-site requests cannot mutate admin data. This must be handled separately from visual redesign.

### F-10 — Rate limiting is not shared across workers

**Priority: P1 security/LLM-cost risk.**

`settings.py:56–62` configures Django `LocMemCache`, and `rate_limit.py` uses the Django cache. LocMemCache is process-local; with multiple Gunicorn workers/instances, the configured per-IP limit may be multiplied by workers rather than enforced globally.

**Gap closure:** Confirm production topology and use a shared atomic cache (for example, the deployed shared cache service) for production rate limits; add a multi-worker test. Keep the existing endpoint limits and `Retry-After` behavior.

### F-11 — CSP is configured, but enforcement must be proven

**Priority: P1.**

Production settings make CSP configurable and default to report-only mode, while the base template contains inline scripts/styles and several external resources. A report-only header is useful for migration but is not an enforcement guarantee.

**Gap closure:** Verify the deployed settings module and actual response headers; collect violations, then enforce a policy compatible with the site (nonce/hash where appropriate). Do not claim CSP protection merely because middleware exists.

### F-12 — Draw-call gate remains failed; no visual exception is approved

**Priority: P1 performance gate.**

- Walking-state measurement was 26 calls: 25 character mesh calls plus the dust pass.
- The current spec/test requires **strictly `<25`**, so the gate remains failed.
- A broad family merge reduced calls but changed about 2.1% of Mochi's frozen frame; grouping only exact material signatures restored fidelity but did not lower the count further.
- Do not weaken the gate without owner approval, and do not accept a visually changed character merely to reach a counter.

**Gap closure:** Continue only with measured pixel-fidelity and draw-call tests; consider batching/geometry/material architecture or a justified change to the product/spec after owner review. Measure a walking frame, not a quiescent frame. Validate real device performance separately.

### F-13 — G10 and fallback/dual-rig acceptance are not verified

**Priority: P1 verification.**

The original G10 gate read rig parts from the adapter wrapper. Live property getters and Pip tail-feather exposure were added afterward, but no clean full sweep verifies Mochi↔Pip hand-off. The `Asha` branch uses a CSS fallback and has different behavior. Do not mark dual-rig parity complete until both chosen character paths are tested at the same progress points, including reversed scroll and docking.

### F-14 — Obsolete/competing mascot implementation creates plan drift

**Priority: P2 maintainability.**

A repository search found no template include of `components/concierge.html`; active `base.html` includes `components/chatbot_modal.html`. The unreferenced concierge template contains its own fixed 320×520 stage, speech/chat UI, own WebGL render loop and `#services-section` enter/leave trigger. It is not evidence of current live behavior, but it conflicts with the active engine and can mislead future reviewers. The active fallback also remains in `base.html`.

**Gap closure:** After confirming no external include/deployment dependency, clearly archive/remove stale prototype code from deployable templates or label it inactive. Keep one canonical mascot path and one source of truth for chat behavior.

---

## 3. Audit of the plan documents themselves

### What is useful and should remain

- The user constraints against binary scroll thresholds, content collision, excessive WebGL memory and unsafe chat/API handling are strong.
- The normalized journey, character-specific parity, reduced-motion handling and reverse-scroll requirements are testable when expressed as visible acceptance criteria.
- The owner-selected `index-expressions.html` source and Mochi/Pip identities are now clear.
- The current runway probe measures actual pixels and text boxes; it is a useful *collision* test when paired with positive visibility/motion checks.

### What is stale, conflicting or not yet a product plan

1. `docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md` §3 still describes the live site as only a `scrollY > 180px` transition. That is stale for the current primary path; the 180/80 thresholds now survive in a fallback. Update the matrix to state both accurately.
2. The audit's benchmark claims (Evagher/Apple/LVMH/other sites) are not a substitute for a current cited web review. Recheck live references and distinguish observed behavior from assumptions.
3. The prescribed 320 px character, bottom runway, 30%-height lane, content keep-out and 390 px layout cannot all be satisfied in the current implementation. The plan needs a responsive visual solution, not another clamp.
4. The audit asks for ScrollTrigger `scrub: 0.8`; the current `ScrollTrigger.create` only uses `onUpdate`, with custom exponential damping (`smoothing: 13`). Record this as a deliberate implementation difference or bring it into conformance after motion review.
5. The audit's mobile/runway acceptance focuses on no collisions but does not require a visible, recognizable walk. Add positive proof (minimum walking/showcase sample count, sprite dimensions, monotone progress, reversal, and a non-binary blocked/fallback test).
6. The SEO/city/agentic-search outcome is missing from the original 3D/security checklist. It needs a separate data-truth, content, metadata, index coverage and measurement plan.
7. The user's protected brand animation is not anchored to a named element and frozen reference in the current mascot test suite. Add a visual non-regression capture only after the owner identifies that exact animation; never infer it.
8. `docs/MOBILE_AND_MASCOT_GAP_ANALYSIS.md` and other predecessor audit docs refer to older `arena/01a0d489`/remote baselines. Mark them historical or refresh the baseline and date before using them as evidence.
9. `README.md` advertises Python 3.13/Django 6.1, while the recorded sandbox was Python 3.11.2/Django 5.2.17 and `django/requirements.txt` allows Django 5 through `<7`. Correct/verify documentation so reviewers know what actually runs.

---

## 4. Recommended gap-closure sequence

This is a planning order, **not permission to change the protected animation or begin a redesign without owner review**.

### Phase 0 — Critical security containment

- Rotate/remove exposed admin and onboarding secrets; invalidate sessions and inspect whether demo/test accounts exist in production.
- Remove query-string passcode access, quick-fill credentials and hard-coded passwords from templates/docs/source; do not merely hide the controls.
- Restore CSRF protection and staff-only authorization to admin writes; add passcode rate limits only if a non-staff onboarding flow is explicitly retained.
- Verify production settings module, shared cache for throttles, enforced CSP, upload validation and browser response headers.

### Phase 1 — Confirm experience decisions

- Record which exact “Anshita Makeover” animation is protected and capture an untouched reference.
- Ask whether Mochi and Pip should: (a) appear together, (b) take turns in one scroll journey, or (c) be chosen by the visitor. Current implementation is one active rig at a time and also retains Asha.
- Confirm real cities/regions served and which claims (travel, durations, ratings, hours, product names) are factual.
- Confirm whether the speech bubble should appear automatically after docking and what the first greeting should be; keep the existing chat itself.

### Phase 2 — Redesign the responsive mascot stage before tuning animation

- Solve 390/375 px horizontal blocking without walking through text and without endpoint snapping.
- Reconcile readable character height with reserved runway space and the actual hero copy/CTA placement at desktop, tablet and mobile.
- Decide what the visitor sees at the top, during entrance, at showcase and after docking; the characters must be visible for a meaningful interval, not just pass a collision test.
- Keep the main brand animation isolated from mascot-specific selectors and require non-regression.

### Phase 3 — Reduce copy and refine the premium hierarchy

- Use a subtraction-first homepage edit: one short promise, one primary action, verified location cue, concise service proof; move detail to service/package/gallery pages.
- Make the chat introduction concise by default. Keep language selection available but do not let it dominate the initial viewport or the mascot moment.
- Reduce competing decorative layers (marquee, background particles, badges, persistent quick chips) if they weaken product/character focus; evaluate with real screenshots rather than increasing effects.

### Phase 4 — City display and SEO foundations

- Store/derive service coverage from verified business data; animate one city at a time visually with a non-motion accessible alternative.
- Keep canonical page text meaningful and server-rendered/crawlable. Do not hide keyword lists in animation, invent destination coverage, or create thin city doorway pages.
- Audit title/meta/OG uniqueness, canonical host, LocalBusiness facts, reviews/ratings eligibility, internal links, image alt/size, sitemap detail URLs, robots and `llms.txt` accuracy.
- Use Search Console/analytics/server crawl data for outcomes; without those, report implementation-level SEO only, not ranking promises.

### Phase 5 — Repair and verify the motion/performance gates

- Remove the blocked-runway binary mapping and the legacy threshold pop path; test WebGL-init failure and reduced motion separately.
- Resolve G5 greeting ownership, verify G10 Mochi/Pip switching, and keep strict G8 `<25` until either a visually faithful optimization reaches it or the owner explicitly changes the spec.
- Update the runway probe to assert positive walk/showcase visibility and continuous bidirectional progress at all viewports, not just absence of collisions.
- Capture representative real-device FPS/memory on at least one mid-range Android and one desktop; SwiftShader is a sandbox diagnostic only.
- Re-run all security/API tests and the complete §8 suite after dependency/toolchain setup. This turn could not run Django because it is absent in the current environment.

---

## 5. Proposed acceptance gates for the revised plan

1. The identified protected brand animation matches its owner-approved reference and has no mascot CSS/JS side effects.
2. At every supported breakpoint, the chosen Mochi/Pip story is explicit; each intended mascot is visible and recognizable at a measured on-screen size for a meaningful portion of the journey.
3. Scrolling down and up produces continuous, reversible progress—no binary `runwayBlocked` or legacy-threshold jump. Reduced motion is tested separately and remains accessible.
4. Mascots never obscure meaningful copy, booking CTAs, chat controls or mobile navigation; if there is no safe stage, the fallback is graceful and stated, not falsely passed as a walk.
5. The greeting is deterministic and appears only in the approved state; promo tips cannot overwrite it during its display window.
6. Mobile and desktop content hierarchy is reviewed with fresh screenshots. Copy is materially reduced by an owner-approved plan; the fixed city line is replaced only after coverage facts are confirmed.
7. SEO metadata, schema, sitemap and service-area claims are valid and truthful; successful indexing/ranking is not claimed without Search Console evidence.
8. G8 remains `<25` calls and memory is stable, or a documented exception is explicitly approved by the owner. Real-device FPS targets are measured on hardware.
9. CSRF, admin authorization, rate limiting, output escaping, secret hygiene, CSP enforcement and upload handling pass tests in the actual production settings profile.
10. Final proof includes exact branch/commit, viewport/device, test results, console errors and the captures used. No gate is marked complete from stale artifacts.

---

## 6. Immediate owner decisions / unknowns

The following should be answered before the visual implementation plan is finalized; no assumptions were made:

1. Should Mochi and Pip appear together, sequentially, or only via a selector during the walk/dock story?
2. Should the legacy Asha character remain a chat persona, even though the new animated-character scope is only Mochi and Pip?
3. Which exact existing “Anshita Makeover” animation is the protected one? Please identify it with a screenshot/recording if the name is ambiguous.
4. Which named cities are verified service destinations, and is “All Over India” accurate for the business today?
5. Should the rotating city cue live in the hero only, or also appear elsewhere? It must not be the only crawlable location content.
6. Which current production URL and dated mobile/desktop screenshots should be treated as ground truth?

---

## Source map

- Main spec: `docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md`
- Old mobile/scroll analysis: `docs/MOBILE_AND_MASCOT_GAP_ANALYSIS.md`, `docs/MASCOT_WALK_AND_SCROLL_GAP_ANALYSIS.md`
- Animation/premium vocabulary: `docs/ANIMATION_SPECIFICATION.md`, `docs/MASTER_IMPLEMENTATION_PROMPT.md`
- Hero/city and choreography: `django/core/templates/core/home.html`
- Shared metadata, chatbot switching, fallback threshold and speech rotator: `django/core/templates/core/base.html`
- Active chat and stages: `django/core/templates/components/chatbot_modal.html`
- Scroll/runway/docking: `django/core/static/core/js/controllers/mascot-scroll-engine.js`
- Studio rig: `django/core/static/core/js/controllers/mascot-rig-adapter.js`
- Mochi/Pip canonical module: `django/core/static/core/js/lumiere-characters.js`
- API/security/SEO: `django/core/views/chatbot.py`, `public.py`, `reviews.py`, `services_pricing.py`, `common.py`, `django/core/ratelimit.py`, `django/core/security.py`, `django/core/middleware.py`, `django/anshita_project/settings.py`, `settings_production.py`
- Evidence probes: `testing/e2e/verify_mascot_runway.py`, `testing/e2e/verify_mascot_walk_dock.py`
