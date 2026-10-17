# Anshita Makeover — Search Visibility & Story Audit

**Review date:** 17 October 2026
**Scope:** Source-level review of the Django templates, public SEO endpoints and current homepage/story implementation, plus a small public-search sample. This is not a verified production crawl or rankings report.

## Executive verdict

**There is a real visual foundation for a memorable makeup-artistry story, but the search setup is only partly ready and the business facts need reconciling before more SEO copy or schema is added.** The most important opportunity is not an “AI SEO trick”; it is to make the site, Google Business Profile, public portfolio and other listings all tell the same accurate story about the artist, location, service area and work.

The repository has a crawlable `robots.txt`, a sitemap route, server-rendered page content, descriptive image alt text in the reviewed templates, and a strong set of real visual assets. But the sitemap is hand-maintained, key metadata is generic, local-business markup includes facts that have not been verified, and the homepage/`llms.txt` make broader claims than the four confirmed cities. The homepage also starts all 48 transformation-frame image requests at once, a material mobile-performance risk.

**Actual Google ranking, indexing, organic traffic, AI Overviews/AI Mode impressions, ChatGPT citations and Core Web Vitals are unknown.** Search Console, Google Business Profile, analytics, Bing Webmaster Tools and production hosting/CDN logs were not available. A public-search sample did not surface the official domain for the exact brand query and returned some similarly named artist/directory results; that is a signal to improve entity clarity, **not proof that the domain is de-indexed**.

## Evidence boundaries

- Findings below are verified in the current repository source, not confirmed in the live deployment. `robots.txt`, `sitemap.xml` and `llms.txt` are Django views; their source strings were reviewed, but the views were not rendered against a running Django app.
- `python manage.py check` could not run because Django is not installed in this environment (`ModuleNotFoundError: django`). No browser, Lighthouse, URL Inspection or rich-results test was run.
- No production access or private account access was attempted. The owner-confirmed facts below supersede conflicting claims in the repository; other business claims remain unverified until confirmed.

## Owner-confirmed facts added after the review

- The business is **primarily based in Jabalpur**. This does not yet confirm a public walk-in address or exact street address.
- Anshita has **3 years of experience** and has performed **100+ makeup**. For public copy, use “100+ makeup looks” only if that accurately describes the count; do not convert it to “100+ brides” without confirmation.
- **Do not claim 18+ hour, cry-proof or sweat-proof wear.** Longevity varies by service and by person.
- The **Academy is coming soon**; it is not currently an active course offer.
- The chatbot should sound **friendlier and more conversational**, while retaining its existing security posture and useful handoff to WhatsApp.

## Evidence-based scorecard

| Area | Status | Why |
|---|---|---|
| Crawl foundation | **Partly ready** | Wildcard robots access and a sitemap route exist; the sitemap is static and incomplete for data-driven detail pages. Live response, redirects and indexing are unknown. |
| On-page SEO | **Needs work** | Homepage description is inherited and generic; social-card metadata is generic; several public templates have titles but no page-specific description. |
| Local/entity trust | **Highest priority** | LocalBusiness JSON-LD and page copy contain unverified rating, hours, coverage, address and longevity claims that do not line up cleanly with the confirmed city list. |
| AI-search eligibility | **Some source-level access is open; outcomes unknown** | `User-agent: *` allows crawling in the source policy. Google’s property setting, live crawler access, indexing and any citations are unknown. |
| Performance | **Risk visible in code; not measured** | Global render-blocking scripts/fonts and the homepage’s eager 48-frame sequence can cost load time and data. No field or lab metrics are available. |
| Story / animation | **Strong ingredients; story can be simpler** | The lookbook and transformation sequence are compelling assets, but they sit inside a long marketing-section stack. The new scroll chapters have not been browser-verified. |

## Findings and recommended fixes

### 1. Reconcile business facts before publishing more copy — P0

`django/core/templates/core/base.html` currently emits `BeautySalon`/`LocalBusiness` JSON-LD with:

- `ratingValue` **4.98** and `ratingCount` **120**;
- an address containing only `addressCountry: IN`;
- `areaServed: India`;
- daily opening hours of **07:00–22:00**;
- a hard-coded phone number and `priceRange: ₹₹₹`.

The homepage currently states **1,200+ brides**, **15 cities** and **12+ years**, while the owner confirms **3 years of experience** and **100+ makeup performed**. Its reviews heading and shared JSON-LD also publish **4.98 / 120**; that rating and source remain unconfirmed. The hero lists the four confirmed cities — **Jabalpur, Bhopal, Indore and Lucknow** — and the owner confirms the business is primarily based in Jabalpur. By contrast, `llms.txt` claims India-wide service and a “24/7 AI Concierge,” and multiple pages promise a “cry-proof” 18+ hour finish. The user explicitly says wear duration depends on the service and person; do not make a universal longevity or waterproof claim.

**Action:** Use the confirmed facts—Jabalpur as the primary base, 3 years’ experience and 100+ makeup performed—in a simple approved facts sheet. Clarify whether “100+” means completed looks, applications or distinct clients before choosing the noun in public copy. Confirm the exact physical/service-area model, phone, hours, coverage/booking arrangements in the other confirmed cities, and the source of the 4.98/120 rating. Correct the 1,200+, 15-city and 12-year claims; remove “cry-proof,” “sweat-proof” and fixed-hour guarantees; remove pan-India/24-7 claims unless independently confirmed. Reuse the approved facts consistently in page copy, metadata, JSON-LD, `llms.txt` and business listings.

**Review markup:** Remove the hard-coded `aggregateRating` from the business entity. A LocalBusiness/Organization marking up reviews it controls itself is ineligible for Google review-rich-result stars; review data must also be accurate, user-sourced and visible. Keep genuine, consented testimonials for visitors, but do not use self-review schema as a rich-result tactic. See [Google’s review-snippet guidelines](https://developers.google.com/search/docs/appearance/structured-data/review-snippet).

### 2. Make every important page say what it is — P1

- The homepage sets a title but inherits the broad base description (“India’s Premier…”). Several pages have no unique description, including package/service detail, packages, academy, travel estimator, chatbot and cart templates.
- Open Graph description and Twitter title/description are static generic copy; page title overrides do not make the share cards page-specific.
- The canonical URL uses the incoming request’s scheme and host. If production accepts more than one hostname/proxy scheme, that can emit multiple canonicals; confirm the production redirect and configure one fixed canonical origin.
- The homepage H1 (“Haute Bridal Artistry”) is elegant but not locally descriptive. A truthful title/description can pair the artistry with the actual primary market, for example **“Bridal Makeup Artist in Jabalpur | Anshita Makeover.”** Jabalpur is now confirmed as the primary base.
- The Academy is **coming soon**. The current template presents course pricing, limited seats, discounts and a scholarship/game link as active offers. Replace that with a small, honest teaser; do not show enrolment, fees or launch dates until they are real. Keep the route if desired, but consider removing it from the sitemap until it has substantive launch information.

**Action:** Add one distinctive title, concise description, canonical and social-card title/description per index-worthy page. Use the primary city only where it is true. Keep “India’s premier” and other superiority claims only if they are substantiated and genuinely useful to the reader.

### 3. Fix discovery plumbing and language intent — P1

- `robots.txt` allows `/` and disallows admin/login paths; it points to the canonical-domain sitemap. The wildcard rule does not explicitly block OAI-SearchBot.
- `sitemap.xml` is a hard-coded list of eight URLs. It omits the data-driven gallery album, service and package detail URLs, has no `lastmod`, and includes utility/concierge pages whose search value should be decided intentionally. `changefreq` and `priority` are not a substitute for current, canonical URLs.
- No template-level `noindex` or `hreflang` directives were found in the reviewed templates. The language is switchable through a query parameter/cookie, while the shared document is always `<html lang="en">` and canonical URLs omit the language parameter.

**Action:** Generate the sitemap from active, published, canonical records; include only pages intended to appear in search and provide truthful `lastmod` values. Decide whether the standalone chatbot and transactional utility pages are search landing pages; use `noindex` where appropriate, without changing their functionality or the existing access controls. If Hindi/Hinglish pages are meant to rank separately, give each language a stable URL, correct `lang`, self-canonical and reciprocal `hreflang`; otherwise treat the language switch as a visitor preference rather than an indexable alternate page.

### 4. Improve local discoverability without doorway pages — P1

The owner confirms Jabalpur as the primary base and the four confirmed cities remain Jabalpur, Bhopal, Indore and Lucknow. The structured data says “India” and a counter says 15 cities. Confirm whether there is a walk-in studio or a service-area setup, the exact public address (if any), and how bookings are handled in the other confirmed cities. Then align the public site, Google Business Profile, Bing Places and legitimate directory listings on the exact business name, contact details, primary category, location/service area and hours. Do not publish a street address or claim pan-India coverage without confirmation. Add only cities where the service is actually available, and only create a city page when it has distinct useful material (real work, venue context, availability/travel details), not a template repeated for every city.

Google describes local results in terms of relevance, distance and prominence, and recommends complete, accurate Business Profile information; there is no guaranteed ranking shortcut. See [Google’s local-ranking guidance](https://support.google.com/business/answer/7091?hl=en).

### 5. Treat AI search as normal search plus factual clarity

- **Google AI Overviews / AI Mode:** Google’s guidance says a page must be indexed and eligible for a normal Search snippet; there are no extra AI-specific technical requirements. The Google AI performance report in Search Console can show impressions by page, country, device and date, but the property’s inclusion setting and data are not available here. Check both in Search Console. See [AI-features eligibility](https://developers.google.com/search/docs/appearance/ai-features), [the generative-AI performance report](https://support.google.com/webmasters/answer/16984139?hl=en) and [the Search generative-AI control](https://support.google.com/webmasters/answer/16908024?hl=en).
- **`llms.txt`:** It is not a Google ranking/AI-inclusion lever; Google says it does not use special `llms.txt` files for Search. Keeping one is optional for other systems, but this one should not publish unverified “India-wide,” 18-hour or 24/7 statements. See [Google’s generative-AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).
- **ChatGPT Search:** The wildcard robots rule allows crawlers at the source-policy level. That does not prove the production firewall/CDN permits the published IPs or that the site is indexed/cited. OpenAI distinguishes **OAI-SearchBot** (search inclusion) from **GPTBot** (training crawl); these controls are independent. Do not change that policy without deciding the business preference and checking hosting logs. See [OpenAI crawler guidance](https://developers.openai.com/api/docs/bots).
- **Bing / Copilot:** Verify the domain in Bing Webmaster Tools and review its AI Performance report for cited URLs and trends; add/verify the correct business details in Bing Places if applicable. See [Bing AI Performance](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview).
- **Chatbot voice:** Its current greeting promises “24/7” help and promotes pan-India travel and Academy masterclasses. Make the welcome warmer and more conversational, while being clear about what it can answer and when a human needs to confirm availability or pricing. Preserve the existing chatbot and security behavior.

Across all of these, the durable recommendation is the same: real bridal work, first-hand and specific descriptions of the artistry, consistent facts, crawlable text, clear page structure, useful image/video captions and an accurate business entity. No schema or “AI hack” guarantees a recommendation.

### 6. Protect the visual quality while reducing mobile cost — P1

The shared `<head>` loads Three.js, GSAP, ScrollTrigger, Lenis, Headroom, character scripts and six Google font families without `defer`/`async`. On the homepage, the transformation script creates 48 `Image` objects and assigns every frame’s `src` immediately; the local sequence totals about **5.4 MB**. The poster is a good fallback and the hero image is preloaded, but the full sequence still starts loading before the visitor reaches it. This is a code-level risk, not a measured Core Web Vitals failure.

**Action:** Preserve the protected studio-opening animation, but avoid loading every below-the-fold frame at initial page load. Keep the poster, request the first/nearby frames on intersection, progressively load the rest while the scene is active, and stop/abort work when it leaves view. Load heavy animation libraries only on pages/scenes that need them, defer non-critical scripts, and trim font families/weights. Test on a real mid-range Android/mobile network. Use Search Console field data and Lighthouse/PageSpeed for LCP, INP and CLS (Google’s good targets are LCP ≤2.5s, INP <200ms, CLS <0.1; see [Core Web Vitals guidance](https://developers.google.com/search/docs/appearance/core-web-vitals)).

The shared viewport also sets `maximum-scale=1.0`, which prevents pinch zoom. Remove that restriction as part of the mobile/accessibility pass. Static image tags in the reviewed templates generally have alt text; the transformation poster is deliberately decorative and has an accessible canvas label.

## Story and animation direction

The current homepage has a sequence of looks, a 3D Works Wheel, a 48-frame preparation-to-finish scene, services, counters, testimonials, studio information and rituals. The pieces are there, but the page can still feel like a feature catalogue. **Make the making of one bridal look the organizing story; do not add more copy-heavy sections.**

Recommended home arc:

1. **The look:** one strong final portrait, one short promise about considered bridal artistry, and the existing two clear actions.
2. **The making:** the real transformation sequence — preparation → complexion/finish → final look — with short, accurate labels, not technical promises that are not proven.
3. **The details:** three visual close-ups (eyes/skin, hair, veil/jewellery) with one-line captions showing why each choice suits that bride and occasion.
4. **The reveal:** one full-frame final image, then a small selection of real portfolio stories and a concise availability/booking cue.

Keep service/package specifics on their own pages. Prefer a few meaningful images and visible technique details over repeated “luxury/royal/imperial” claims and ticker copy. Use real client work only with appropriate consent and accurate captions. The central story should be the artist’s craft; Mochi/Pip can quietly guide visitors but should not displace the bride or become extra sales copy.

The current local chapter code is directionally aligned: it reserves scroll space with ScrollTrigger pinning, does not cancel wheel/touch input, includes skip links and falls back to a static scene for reduced-motion/no-ScrollTrigger users. It has **not** been browser-tested. Validate ordering, focus/keyboard flow, reduced motion, page-length burden and small-screen behavior before expanding it; the transformation chapter currently has a minimum 900px pin distance on narrow screens. Keep the opening animation untouched, preserve “Explore Lookbook” → Gallery and “Book on WhatsApp” → WhatsApp, and hold the G8 limit at **<25 draw calls**.

## Recommended order of work

1. **Facts first:** use the confirmed Jabalpur base, 3 years’ experience and 100+ makeup performed; clarify the exact meaning of the 100+ count, business/address model, public hours, phone and rating source. Remove the unverified 1,200+/15-city/12-year, India-wide/24-7 and fixed wear-time claims. Correct visible copy, schema and `llms.txt` together; make the Academy a Coming Soon page and soften the chatbot greeting without changing its safeguards.
2. **Technical SEO:** fix canonical origin, page descriptions/social metadata, language behavior, dynamic sitemap and index policy for utility routes; validate with Search Console URL Inspection and a structured-data test.
3. **Local profiles:** align Google Business Profile, Bing Places and consistent legitimate public listings; publish genuinely useful work from confirmed cities.
4. **Performance/accessibility:** lazy-load the transformation frames and non-critical libraries; permit zoom; test mobile CWV and chapter behavior.
5. **Story pass:** simplify the homepage around the four-part artistry arc above, then measure gallery visits and WhatsApp enquiries rather than adding more sections.
6. **Baseline and measure:** verify Search Console ownership; review indexing, query/page/country/device data, the Google generative-AI report and Core Web Vitals; verify Bing Webmaster AI Performance; use analytics only if already approved in the site’s privacy posture. Compare a consistent before/after period and do not treat a single manual rank check as a ranking report.

## Facts still needed before factual SEO edits

1. Is there a visitor-facing studio in Jabalpur, or is Jabalpur the service base? What address, if any, is appropriate to publish? How are bookings in Bhopal, Indore and Lucknow arranged?
2. Does “100+ makeup” mean completed looks/applications or 100+ distinct clients? What is the source for the displayed **4.98 / 120** rating, and what public hours should be shown?
3. Should Hindi/Hinglish be independently discoverable in Search, or remain a language preference? For the warmer chatbot, should it speak as “Mochi” in first person, or as the Anshita Makeover team?

The owner has already clarified that 3 years’ experience is accurate and that there is no universal 18+ hour/cry-proof guarantee. Keep the current WhatsApp and Gallery destinations and do not replace uncertain facts with guesses.

## Official references

- [Google Search AI features](https://developers.google.com/search/docs/appearance/ai-features)
- [Google generative-AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Google Search Console generative-AI performance report](https://support.google.com/webmasters/answer/16984139?hl=en)
- [Google Search generative-AI control](https://support.google.com/webmasters/answer/16908024?hl=en)
- [Google LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business)
- [Google review-snippet guidelines](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)
- [Google local-ranking guidance](https://support.google.com/business/answer/7091?hl=en)
- [Google Core Web Vitals and Search](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots)
- [Bing Webmaster Tools AI Performance](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
