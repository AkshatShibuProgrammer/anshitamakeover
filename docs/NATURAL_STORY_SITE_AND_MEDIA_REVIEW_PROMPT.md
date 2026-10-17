# Master Review Prompt: Natural Bridal Story, Website, Media & Admin

**Prepared:** 17 October 2026
**For:** A second AI/reviewer with access to this repository, a browser, and (if public) the Instagram account below.
**Working mode:** Evidence-first audit and recommendations. Do not change website code or assets during this review; write findings into the designated section of this file.

---

## Prompt to the reviewing AI

Act as a careful senior reviewer combining the roles of a bridal-beauty content strategist, visual storyteller, UX/accessibility reviewer, local-search/SEO reviewer, media librarian, and admin-workflow reviewer. Review the current Anshita Makeover website and its content as a real small bridal-makeup business—not as a generic luxury brand, AI demo, or business brochure.

The goal is to make the experience **natural, specific, warm, useful, visually led, and factually honest**. Find whether the existing photography and videos already contain a compelling real story. Recommend how the website and admin panel can express that story with less filler and purposeful motion. Do not invent the story if the media does not support one.

### 1. Start with the correct Instagram source

The owner’s supplied account is:

**https://www.instagram.com/anshitamakeover21/**

Review that account directly if public access is available. Confirm that every post/reel you discuss actually belongs to this exact profile. Record the post/reel URL and visible date/caption where available. Do not use search thumbnails, competitor galleries, similarly named accounts, or images from third-party results as substitutes for this account.

A previous image-search attempt returned unrelated “Makeover by Shivangi” images. **Those images were wrong and must be discarded; they are not evidence about Anshita Makeover.** A direct fetch of the owner-provided Instagram URL returned HTTP 403 in the first review pass. If access is still blocked, state that precisely, do not claim to have reviewed the Instagram feed, and complete the repository/local-media review. Ask the owner only for the minimum helpful input—such as selected public post links or an owner-provided export/screenshots—never for Instagram credentials, passwords, cookies, or two-factor codes.

For a public-feed review, sample a manageable, representative set rather than scraping the account. Prefer a mix of recent posts/reels and posts that visibly show different stages or looks. Separate what is directly visible from what is inferred. Do not infer a client’s name, exact venue/city, skin condition, personal circumstances, or consent from an image or caption alone.

### 2. Look for a real story in the social media and local photography

Assess whether the material can support a story such as:

1. the bride’s chosen look, outfit, ceremony, or preferences;
2. preparation and the artist’s choices;
3. makeup details and how they work with the styling;
4. hair, jewellery or draping/final touches;
5. the finished look, candid moment, or client-approved reflection.

This is a *possible structure*, not a claim that every client follows those steps. Identify repeated real themes across posts—such as natural/soft glam, cultural detailing, eye looks, draping, or preparation—only when the media supports them. Recommend a few specific story candidates and explain why each is stronger than a generic service list.

The owner says there are local photos that may work for before/after storytelling. Check whether there are genuine matched pairs or a clear sequence. Call something “before/after” only when the evidence supports the same person and a genuine progression. Record lighting, angle, crop, retouching and timing concerns; do not create or imply a transformation by pairing unrelated images. If no trustworthy pair exists, suggest a process-to-finish story instead.

For every candidate, mark image ownership, client consent, public-use permission, and identification permission as **confirmed / not confirmed / unknown**. Do not recommend publishing client imagery with unknown permission. Do not upload private media to external services or redistribute it; inspect only what is available in the approved workspace.

### 3. Inventory the repository’s media carefully

Inspect likely portfolio/media locations, including (but not limited to):

- `django/core/static/core/images/`
- `django/core/static/core/images/authentic/`
- `django/core/static/core/images/curated/`
- `django/core/static/core/videos/`
- `resources/gallery_curation/`
- `implement/phase_2_gallery_media_cleanup/`
- `implementation_01_oct/04_3d_cylindrical_orbit_gallery/`

The first source scan found roughly **511 still-image files and 28 video files across the repository**. These counts are not de-duplicated and include possible UI/brand/test/archive assets; they are not a count of approved client portfolio items. Re-count by relevant directory and identify duplicates/variants where possible. Exclude mascots, logos, model-test renders, UI screenshots, probes and unrelated archive assets from bridal-story candidates.

Create a small asset index for promising portfolio items with:

- exact repository path and filename;
- media type, dimensions/duration and file size where feasible;
- what is visibly shown, without guessing identity or location;
- likely story role (prep/detail/reveal/candid/etc.);
- possible paired files or sequence order, with confidence;
- caption/alt-text suggestion based only on visible/verified facts;
- permission/consent status (normally unknown unless documented);
- whether the file is already used on a website page.

Do not rename, alter, optimize, publish or delete any media during this audit.

### 4. Review the website page by page

Read the current templates, routes and relevant views before reviewing the site. Cover the public journey and note a page’s purpose, what works, friction, factual risks, content that feels generic/artificial, accessibility/mobile concerns, and one or two focused improvements.

At minimum, include:

- Homepage and its hero/story chapters;
- Gallery and gallery-album detail pages;
- Services and service-detail pages;
- Packages and package-detail pages;
- Build-your-look/package builder and cart;
- Travel estimator;
- Academy (now intended to be **Coming Soon**, not an active enrolment offer);
- chatbot modal, standalone chatbot and relevant chatbot copy;
- About/studio content and other customer-facing sections;
- any public learning/gameplay page and whether it remains appropriate while Academy is Coming Soon;
- any other public routes that could affect a visitor’s understanding or booking.

Do not treat the admin portal, animation lab, staff onboarding, or internal tools as public marketing pages. Identify them separately and do not expose credentials, private data, or admin-only details in public copy.

For each customer-facing page, recommend the smallest clear job it should do. Prefer useful, concise text and genuine imagery over adding more sections, keyword blocks, decorative “luxury” claims, duplicate CTAs, or generic FAQs.

### 5. Review the admin panel as an operating tool

Inspect the admin interface and its source-level workflows without logging in or requesting credentials. The existing panel contains controls for topics such as media, services/prices, packages/offers, travel, reviews and site content. Report what an owner/staff member needs to do, where terminology or layout is confusing, and how to reduce mistakes.

Recommend an owner-friendly workflow that can support accurate publishing, for example:

- a single source of truth for public business facts and approved claims;
- clear draft → preview → approve → publish states;
- media records with caption, alt text, artist/occasion/city when verified, source URL, usage rights and consent status;
- clear price inclusions/exclusions and effective dates;
- review source/permission and moderation status;
- separate operational settings from promotional copy;
- preview of title, description, social card, canonical URL and indexability;
- an audit trail for changes to public facts, prices and offers.

These are recommendations, not assumptions about current capabilities. Do not change the admin route, roles, authentication, CSRF, rate limits, data access, or other security behavior. Do not inspect or reproduce secrets. The current chatbot and its security posture must remain intact; tone may be improved, but do not weaken its safety controls.

### 6. Audit factual trust, SEO and AI-search readiness

Use the owner-confirmed facts below as the source of truth. Treat conflicting repository copy as a finding, not as authority. For every additional business claim, label it **owner-confirmed / verified in public source / visible in source only / unverified / contradicted**.

Review:

- page titles, meta descriptions, Open Graph/Twitter metadata, canonical host, language/`hreflang`, `robots.txt`, sitemap, `llms.txt`, indexability and dynamic detail pages;
- business identity, Jabalpur base, city coverage, phone, address/hours, reviews/rating and any product or wear-time claim;
- visible text versus JSON-LD, and whether structured data is accurate and eligible;
- whether public portfolio images have descriptive alt text and videos have useful captions/transcripts where appropriate;
- performance risks in source versus measured results. Do not call a Core Web Vitals issue measured unless actual field/lab data was collected.

Do not claim the site is indexed/de-indexed, ranks for a query, or is cited by an AI unless verified by the relevant search platform data. Do not recommend fake reviews, fabricated client stories, mass-generated city pages, keyword stuffing, hidden text, or “AI SEO hacks.” If account access is unavailable, list the exact reports/screenshots needed from the owner; never ask for passwords or tokens.

### 7. Known owner-confirmed facts and standing constraints

Treat these as the current approved baseline:

- The business is **primarily based in Jabalpur**. This does not by itself prove a walk-in studio or a publishable street address.
- Anshita has **3 years of experience**.
- Anshita has performed **100+ makeup**. The precise unit—looks, applications or unique clients—has not been clarified. Do not silently turn this into “100+ brides.”
- The owner does **not** know or claim a universal “18+ hour,” “cry-proof,” or “sweat-proof” result. Wear time depends on the chosen service and the individual.
- The Academy should say **Coming Soon**. Do not present enrolment, fixed tuition, limited seats, scholarships or launch dates as currently available unless separately confirmed.
- The chatbot should feel friendlier and more conversational, while preserving its current functionality and security posture.
- Confirmed cities in the current project context: **Jabalpur, Bhopal, Indore and Lucknow**. Exact booking/travel arrangements for each city still need confirmation. Do not claim pan-India coverage or invent a physical address/hours.

Preserve all standing constraints:

- Do not change the protected **“Anshita Makeover” opening animation before entering the studio**; the owner says it is perfect.
- Mochi is the rabbit and Pip is the bird. Their canonical source is `3d character for anshitamakeover/index-expressions.html`; do not substitute unrelated/generic models or generated stills.
- Keep animation purposeful, mobile-friendly, reduced-motion aware and accessible; no scroll traps or forced wheel/touch interception. Story chapters should sequence rather than overlap.
- Keep G8 strictly **under 25 draw calls**; do not weaken that limit.
- Preserve **Explore Lookbook → Gallery** and **Book on WhatsApp → WhatsApp**.
- Keep copy concise, factual and artist-led—not a long business brochure.

### 8. Required deliverable format

Write findings into this file’s **Reviewer Findings** section below. Do not rewrite or remove the prompt. Begin with date, reviewer, tools/access available and limitations. Use concise evidence tables and exact file paths/URLs. Separate observation from interpretation and recommendation. For each recommendation include priority, evidence, owner question/dependency, and a small acceptance check.

Include at least:

1. Executive summary and confidence/limitations;
2. Instagram access result and representative post/reel findings (or an explicit access block);
3. local media inventory and promising, permission-qualified story candidates;
4. before/after pair audit;
5. page-by-page website findings;
6. admin-panel findings and safe workflow improvements;
7. factual/SEO/local/AI-search findings;
8. proposed natural story arc and page hierarchy;
9. prioritized next steps (P0/P1/P2) and questions that require owner confirmation.

If direct Instagram access fails, do not stop at that point: complete the local repository and website review, then provide a short checklist for the owner to supply selected post URLs or an export. Do not fabricate Instagram findings.

---

## Reviewer Findings

> **Status:** Not yet reviewed by the second AI. Fill this section with evidence; preserve the prompt above. Do not treat this placeholder as a finding.

### Review metadata and access

- Reviewer / model:
- Review date:
- Repository commit/branch reviewed:
- Browser or platform access available:
- Instagram access result for https://www.instagram.com/anshitamakeover21/:
- Limitations (including any login wall, HTTP error or missing data):
- Evidence classification used:

### Executive summary

_To be completed by reviewer._

### Instagram account and story signals

| Post/Reel URL | Visible date/caption | What is directly shown | Possible story role/theme | Confidence | Permission still needed? |
|---|---|---|---|---|---|
| | | | | | |

- Recurring visual/story themes supported by the sample:
- Story themes not supported / not enough evidence:
- Best 3–5 candidate posts/reels to build a website story around:
- Follow-up material the owner should provide, if any:

### Local media inventory and story candidates

| Local path | Type / size / dimensions | Direct visual observation | Story role | Possible matched pair/sequence | Already used on site? | Consent/rights status | Confidence |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

- Files excluded from consideration as UI, tests, mascots, generic renders or unrelated assets:
- Duplicate/variant groups:
- Media gaps for a credible transformation story:

### Before/after verification

| Candidate pair/sequence | Same person visibly verifiable? | Real chronological progression supported? | Lighting/crop/editing caveat | Permission status | Recommendation |
|---|---|---|---|---|---|
| | | | | | |

### Page-by-page website review

| Page / route / template | Current job | Strongest real content | Friction or unverified claim | Natural improvement | Priority |
|---|---|---|---|---|---|
| | | | | | |

### Admin-panel review

| Workflow/module | Evidence in source/UI | Current friction or risk | Recommended simpler workflow | Security/data caveat |
|---|---|---|---|---|
| | | | | |

- Current controls that are useful and should remain:
- Facts/claims that need one source of truth:
- Changes that must not be made without owner approval:

### SEO, local and AI-search review

- Crawlability and sitemap:
- Metadata, canonical URLs and language behavior:
- Local identity/location consistency:
- Structured data and reviews:
- Image/video discoverability:
- Google Search Console/Bing/AI-search evidence available or needed:
- Performance evidence versus code-level risk:

### Proposed story arc and design principles

- Story statement (one sentence, grounded in observed work):
- Recommended homepage chapters:
- Suggested real media for each chapter:
- One-line copy examples that avoid unverified promises:
- Motion/accessibility/mobile notes:

### Prioritized implementation plan

| Priority | Recommendation | Evidence/source | Owner confirmation needed | Acceptance check |
|---|---|---|---|---|
| P0 | | | | |
| P1 | | | | |
| P2 | | | | |

### Questions for the owner

1. _To be completed._
2. _To be completed._
3. _To be completed._

---

## First-pass access notes from the current reviewer

- The owner supplied the exact Instagram profile URL above. Direct page fetch returned **HTTP 403**, so this reviewer did not inspect or identify any Instagram post/reel.
- A public image search returned unrelated images from another Jabalpur makeup vendor. Those results were discarded and must not be reused or attributed to Anshita Makeover.
- A repository-wide filename scan found about **511 still images and 28 video files**, including test, UI, brand, archive and likely portfolio material; this is only an inventory count, not a count of authentic/approved client assets.
- The current reviewer has not visually verified local before/after pairs, chronology, image rights or client consent. The next reviewer should record exact paths and evidence rather than assume.
