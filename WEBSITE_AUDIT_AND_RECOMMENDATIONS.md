# Anshita Makeover — product audit

## Executive recommendation

The visual direction is strong and distinctive: editorial split hero, gold/maroon palette, lookbook, estimator, WhatsApp CTA, theme toggle, and a Three.js layer. The main risk is not a lack of features; it is **too many competing features on the first visit**. Make the booking journey the product: inspire → shortlist a look → see starting price/availability → WhatsApp consultation.

## Findings

### High priority

1. **The home page is doing the work of several products.** Admin controls, coupons, AI copy, media management, travel pricing, academy, cart, reels, packages, reviews, and event vendors are all close to the public experience. Keep admin-only UI server-side and move secondary experiences behind clear routes.
2. **The CTA hierarchy is unclear.** There are three hero CTAs and several utility actions in the nav. Use one primary action (`Check date availability`) and one secondary action (`Explore looks`). Keep Concierge as a persistent mobile action.
3. **Proof is asserted, not explained.** Claims such as “500+ brides”, “8+ years”, “Dior & CT kit”, and “18-hour” should link to proof, a service policy, or be softened to avoid trust and compliance issues.
4. **Instagram is a fragile content source.** Do not scrape or hot-embed third-party posts in the critical path. Curate owned, consented images locally; use Instagram only as an optional “see more work” link with a graceful fallback.
5. **Motion needs a performance contract.** Three.js, GSAP, a preloader, slider, skew effects, custom cursor, and particles can compete on mobile. The template now skips the decorative WebGL layer on small touch devices and for `prefers-reduced-motion` users. Keep all future motion progressive and interruptible.
6. **The custom cursor previously removed the native pointer globally.** It is now opt-in for fine pointers only. Continue to test keyboard focus, touch, reduced motion, and screen readers.

### Medium priority

- Add visible “from ₹…” pricing and “last updated” dates to service cards.
- Add a short booking flow: date, city, event, guest count, look reference, phone/WhatsApp consent.
- Add alt text that describes the look, not marketing claims; avoid repeating the same words in every image.
- Add loading dimensions, `loading="lazy"`, and responsive `srcset`/WebP for gallery media.
- Use a single typography system and reduce inline styles in templates.
- Add `aria-live` regions for coupon, estimator, and chat status messages; ensure every icon-only control has an accessible name.
- Do not show scarcity or exit-intent offers until the visitor has had time to understand the service. Cap frequency and make dismissal easy.

## Competitive/newcomer scan

I did not inspect or reuse Anshita Makeover photos. A quick public search surfaced nearby/early-growth positioning signals worth learning from, not copying:

- **Kavya Rai / Dream Makeovers by Kavya** presents a clear location, studio neighborhood, travel availability, and educator identity. Source: Instagram search result, https://www.instagram.com/dreammakeoversbykavya/
- **Jabalpur Bridal Makeover / Aanchal** leads with a compact service list and direct booking contact. Source: https://www.facebook.com/aanchalsingraha2/
- A broader India bridal scan shows that recognizable artists differentiate with a signature finish, portfolio consistency, and education/content rather than a long service menu. Source: Vogue India, https://www.vogue.in/beauty/content/top-indian-bridal-makeup-artists-you-should-follow-on-instagram-for-some-serious-inspiration

### What to borrow strategically

1. Make location + travel radius visible above the fold.
2. Give each signature look a memorable name and 3 tags: finish, ceremony, complexion suitability.
3. Publish short process proof: sanitized kit, skin prep, time taken, team size, and final-lighting video.
4. Use “new bride / recent work” cards with date and location instead of follower-count language.
5. Build a repeatable 3-post content system: transformation, technique close-up, client testimonial.

## Three implementation options

### Option A — conversion-first (recommended)
- Keep the editorial hero and lookbook.
- Replace the three hero CTAs with `Check availability` + `Explore looks`.
- Add a 4-step booking drawer and save selected look IDs into the WhatsApp message.
- Move academy, travel estimator, cart, and vendor marketplace to secondary routes.
- Best for: more qualified enquiries, lower cognitive load, quickest payoff.

### Option B — portfolio-first
- Make the lookbook the landing experience with filters for ceremony, finish, and budget.
- Add before/after and short reels only where consent is recorded.
- Keep estimator after a user selects a look.
- Best for: a newer artist building visual proof and social discovery.

### Option C — luxury interactive
- Keep Three.js, but use one low-density gold particle field and a single GSAP reveal timeline.
- Add a cursor-follow spotlight only on desktop.
- Use section transitions based on opacity/transform, never scroll hijacking.
- Best for: brand memorability; only after Core Web Vitals and mobile booking are stable.

## Recommended next sprint

1. Instrument hero CTA clicks, gallery opens, estimator starts, WhatsApp clicks, and completed enquiry.
2. Reduce the public nav to Services, Looks, Packages, About, and one gold availability CTA.
3. Add a sticky mobile bottom bar: `View looks` / `Check date`.
4. Add consented newcomer-style content cards and a moderation workflow; never auto-publish scraped Instagram media.
5. Run Lighthouse + keyboard + 360px viewport tests before adding more effects.
6. Validate claims and pricing with the business owner; remove anything that cannot be substantiated.
