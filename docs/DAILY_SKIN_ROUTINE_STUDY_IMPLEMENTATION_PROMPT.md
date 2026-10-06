# Copyable implementation prompt: Daily Skin Routine Study

Copy the prompt between **PROMPT START** and **PROMPT END** into the coding/research AI that will work on the Anshita Makeover site. The goal is a small, useful learning experience inspired by Duolingo's teaching loop—not a Duolingo visual clone or a medical-advice app.

---

## PROMPT START

You are a senior product designer, learning-experience designer, Django engineer, accessibility reviewer, and health-content safety reviewer. Design and implement a **Daily Skin Routine Study** for the existing Anshita Makeover website. Begin by inspecting the repository and current deployment evidence available to you. Make changes only within this feature's scope, preserve the existing site, and clearly separate verified facts from assumptions.

### 1. Product goal

Create a friendly, premium, bite-sized learning experience that helps visitors understand the basics of a gentle daily skincare routine through short lessons, practice, helpful explanations, and optional progress rewards.

Use **Duolingo only as inspiration for learning mechanics**: short sessions, a visible learning path, retrieval practice, immediate explanations, spaced review, gentle progress feedback, and an optional streak. Do **not** copy its owl, characters, exact screens, colors, wording, sounds, visual style, or product architecture.

This is a secondary learning area of a bridal-artistry brand—not a replacement for the main website, protected opening, premium 3D story, gallery, booking journey, or chatbot. It must feel like a thoughtfully art-directed editorial learning experience, not a generic gamified app.

### 2. Project constraints — preserve these

- Work within the current repository and framework. The project is an existing Django site; inspect its actual routes, templates, assets, language handling, and reusable components before choosing an integration point. Do not migrate frameworks or rebuild the main site.
- Do **not** change the protected opening “Anshita Makeover” introduction before entering the studio.
- Preserve the current chatbot, security posture, business pages, and homepage CTA destinations: “Explore Lookbook” → Gallery; “Book on WhatsApp” → WhatsApp.
- Keep the study secondary and discoverable without turning the homepage hero into an app promotion. Inspect the current Academy and navigation first; recommend whether this belongs within Academy or on a separate learning route. Do not create a new prominent navigation item without showing the proposed placement.
- Mochi is the rabbit and is the default; Pip is the bird and may be selected as an alternate learning companion. The owner wants the intended actual 3D character asset from `3d character for anshitamakeover/`, not a still image, unrelated demo model, or the earlier procedural character as a substitute. The exact asset is unresolved: inspect and show candidate filenames/previews, then ask the owner if ambiguous. If it is not confirmed, build the lesson experience **without a character**; never insert a placeholder, still image, or different rig. Keep at most one live rig. If WebGL is used, the strict G8 target remains **fewer than 25 draw calls**; do not weaken it.
- Reuse current language/localization conventions. Do not silently publish untranslated or machine-translated health guidance as reviewed content.
- Do not request or expose passwords, tokens, private deployment details, or health information.

### 3. Health-content safety and evidence rules

This feature is **general education, not medical advice, diagnosis, treatment, or an individualized regimen**. Do not diagnose skin type or conditions; do not ask for face photos, symptoms, medication, pregnancy status, age, or other sensitive health details. Do not promise “clear skin,” “glass skin,” whitening, anti-aging, treatment outcomes, or bridal-makeup results. Do not sell or rank products inside quiz feedback.

Build a reviewable content system. Every factual health/safety statement must have a direct, authoritative source, a last-checked date, and a content-review status. Prefer current dermatologist-authored/medical-society guidance (including the American Academy of Dermatology and qualified Indian dermatology sources such as IADVL where relevant). Use FDA or other government sources for their stated jurisdiction and subject; **do not present U.S. regulatory rules as Indian law**. Do not rely on influencers, product marketing, SEO listicles, or unsourced model memory.

Starting source leads to verify—not a substitute for review:

- AAD, dermatologist guide to basic skincare: `https://www.aad.org/news/dermatologist-guide-skincare`
- AAD, testing a skincare product: `https://www.aad.org/public/everyday-care/skin-care-secrets/prevent-skin-problems/test-skin-care-products`
- AAD, sunscreen in daily skincare: `https://www.aad.org/news/survey-worry-skin-aging-still-skip-sunscreen`
- FDA, sunscreen and sun-safety information: `https://www.fda.gov/consumers/consumer-updates/tips-stay-safe-sun-sunscreen-sunglasses`

Before public release, require a qualified dermatologist/clinician to review the lesson content. If no reviewer is available, mark health lessons as **draft / review required** and do not represent them as clinically reviewed. Include a concise, accessible note that the lessons are general education and are not a substitute for care from a qualified clinician. For persistent irritation, severe reactions, or ongoing skin concerns, direct learners to a qualified dermatologist; do not attempt triage.

Keep explanations cautious and non-prescriptive. Avoid ingredient stacking, treatment schedules, “skin-type” diagnosis, claims that one routine works for everyone, or telling someone to start/stop a medication. If discussing a new product or irritation, use vetted source wording and a safe “stop using it if a reaction occurs and seek professional advice when needed” pattern; have a clinician review the exact copy.

### 4. Learning experience and lesson loop

Design the MVP around a **7-lesson foundations path**, each lesson taking roughly 2–4 minutes. This is a proposed content outline, not pre-approved medical copy; research and cite every lesson before writing final answers.

1. **The basics:** what a simple routine is for; introduce gentle cleansing, moisturizing, and sun protection as broad educational topics.
2. **Morning routine order:** practice placing the routine steps in a sensible order, with an explanation and source.
3. **Evening reset:** learn about gentle cleansing and removing makeup before sleep, with cautious, sourced language.
4. **Trying a new product:** practice reading directions and understanding a source-backed patch-test lesson; no diagnosis.
5. **Sun-protection literacy:** learn how to read relevant sunscreen labels and follow the specific product directions; localize carefully for India.
6. **Marketing and ingredient literacy:** distinguish supported information from common unsupported skincare claims; avoid prescribing active ingredients.
7. **Review and build a simple checklist:** repeat foundational knowledge and let the learner save a general checklist, not a personalized treatment plan.

Every lesson should follow this loop:

1. A short, welcoming objective (“Learn one useful idea”).
2. One small concept card or visual explanation.
3. Two to four interactions, using a mix of:
   - reorder/sequence cards (with keyboard controls as well as drag/touch),
   - single-answer questions,
   - safe next-step scenarios,
   - myth/claim checks with a sourced explanation.
4. Immediate, kind feedback for both correct and incorrect answers; explain **why**, cite the source, and allow a retry without shame or penalty.
5. A one-sentence takeaway and a clear “Continue / Review” action.

Use retrieval practice and spaced review, but never make lessons time-limited. Let learners pause, leave, resume, repeat a lesson, or skip ahead. Do not use lives/hearts, punitive streak loss, countdowns, public leaderboards, pressure notifications, loot boxes, or rewards tied to purchases.

### 5. Progress, rewards, and privacy

Use a simple progress path with completed/current/up-next lessons, a small completion celebration, and optional learning points/badges (working labels only; propose tasteful names for approval). A streak may be opt-in, private, and forgiving; it must not imply that missing a day harms the learner's skin or health. Reminders are off by default and require clear consent.

Default to a **guest-first MVP** with versioned browser-local progress if the current architecture supports it. Do not require an account to learn. Do not collect or store skin type, diagnoses, photos, symptoms, product use, or other health data. If cross-device sync requires an account/backend, present it as a separately approved phase with data minimization, retention/deletion controls, and a privacy review. Provide a visible “Reset my progress” control.

### 6. Art direction and interaction design

- Keep the main website's premium bridal/editorial language: considered typography, generous space, restrained brand colors, authentic artistry imagery, strong legibility, and careful transitions. Let the learning area feel related to the brand without redesigning the entire site.
- Use a calm progress path, elegant lesson cards, small celebratory feedback, and clear learning states. Avoid Duolingo's bright green palette, cartoon owl, childish illustrations, sound effects, and clone-like map UI.
- Mochi can offer gentle encouragement, with Pip selectable, **only after the correct actual 3D asset is confirmed**. Do not let character animation delay or block learning. Use motion sparingly; keep the game loop usable with the character disabled.
- No new WebGL scene is required for the MVP. Prefer lightweight HTML/CSS feedback. If a 3D companion is approved, lazy-load it only on the relevant screen, load one character at a time, dispose it on exit, respect reduced motion, and measure the strict `<25` draw-call gate in its moving state.
- Do not introduce autoplay audio, disruptive popups, timers, or scroll hijacking.

### 7. Technical approach

1. Inspect the actual branch and local working tree available to you. Confirm the current Django app, route names, Academy entry point, template patterns, static asset conventions, and supported languages. Do not assume file paths from older reports are current.
2. Before coding, provide a short integration plan naming the proposed route, templates/components, lesson-data location, progress-storage choice, and any unresolved owner approvals. Do not change the protected opening or unrelated pages.
3. Keep lessons data-driven and easy to review. Each lesson/step should support fields such as:
   - stable `id`, title, objective, estimated duration, order, locale, draft/reviewed status;
   - interaction type, prompt, answer options, correct answer, accessible explanation, retry feedback;
   - source title/URL, claim supported, source checked date, reviewer name/role and review date;
   - content version and safety notes.
4. Choose the simplest maintainable data source that matches this project. Do not add an authoring/admin interface, external service, analytics SDK, or new dependency unless necessary and approved.
5. Keep logic testable: answer validation, score/progress calculation, lesson completion, resume/reset, locale fallback, and source/review validation should be separate from template markup.
6. Preserve server-side security: validate any submitted progress if a backend is used, use existing CSRF conventions, never put secrets in client code, and do not create public admin/edit endpoints.

### 8. Accessibility, responsive behavior, and performance

Meet WCAG 2.2 AA where applicable. Test keyboard-only use, visible focus, screen-reader names and answer feedback, semantic headings, sufficient contrast, zoom/text enlargement, reduced motion, and mobile touch targets. Drag-and-drop must always have buttons or keyboard alternatives. Do not use color alone to mark correctness. Make animations brief and optional; honor `prefers-reduced-motion`.

Test at minimum 1440×900, 390×844, and a narrow 360px phone width, plus keyboard-only and screen-reader checks where available. Keep the lesson fast on mobile; lazy-load images, avoid large video/3D bundles, and ensure no horizontal overflow. Report actual measurements rather than promising a particular load time without a test environment.

### 9. Acceptance criteria

The feature is ready for review only when:

- A visitor can enter the study without account creation, understand its purpose, complete a short lesson, receive a cited explanation, review progress, resume after refresh, and reset progress.
- The 7-lesson path has a clear progression, but every lesson is repeatable and no daily streak or timer blocks access.
- Every factual health/safety claim has a direct source and a review status; no unsupported diagnosis, product recommendation, outcome guarantee, or India-specific legal claim is published.
- Skin photos and sensitive health data are neither requested nor stored.
- The feature works on desktop and mobile, with keyboard and screen-reader access and a useful reduced-motion experience.
- The page does not change the protected opening, chatbot behavior/security, or either homepage CTA destination.
- If a 3D character is used, the owner has confirmed the exact model and the moving-state draw-call count stays **strictly below 25**. Otherwise, the learning experience remains complete without a character.
- Automated tests cover the course data, answer logic, progress persistence/reset, citations/review metadata, and relevant security/accessibility behavior. Include a concise manual test report and screenshots.

### 10. Required delivery

Return:

1. A brief audit of the existing routes/components and a proposed integration point.
2. A 7-lesson curriculum map with objectives, interaction types, sources, and which content needs clinician approval.
3. The learning-loop and screen-flow design, including desktop/mobile states and progress behavior.
4. A short implementation plan with exact files and any blockers (especially the 3D asset and content review).
5. The feature implementation only within the approved scope, if asked to proceed; list changed files.
6. Tests run, accessibility/performance evidence, source links, unresolved questions, and any item not verified.

Do not claim that the content is dermatologist-approved unless a qualified reviewer has actually reviewed it. Keep the final experience helpful, calm, and enjoyable; the goal is **better understanding and consistent learning**, not more products, more steps, or more screen time.

## PROMPT END
