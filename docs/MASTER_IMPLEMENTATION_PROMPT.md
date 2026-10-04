# Master Implementation Prompt — Anshita Makeover Website

You are continuing work on the Anshita Makeover Django website in a real Git repository. Your job is to finish and polish the complete website according to the specification below.

Do not treat the existing implementation as automatically correct. Audit the current code, templates, routes, migrations, data factories, and tests before changing anything.

---

## Product context

Anshita Makeover is a luxury bridal makeup, hair, draping, nails, and beauty studio. The website should feel like an editorial bridal lookbook combined with a reliable service catalogue and booking experience.

The visual direction is:

- Cinematic.
- Warm.
- Editorial.
- Premium.
- Photography-led.
- Champagne-gold accents on deep charcoal/plum backgrounds.
- Subtle glitter and atmospheric background light.
- Restrained motion inspired by luxury editorial websites such as the Evagher reference shared by the client.
- Original Anshita Makeover branding, imagery, copy, and interaction patterns.

Do not copy Evagher's code, assets, text, layout, or identity. Use only broad visual principles such as spacious composition, cinematic imagery, editorial typography, controlled reveals, and deliberate pacing.

---

# Primary information architecture

The website must be divided into clear page responsibilities.

## Homepage

The homepage is a concise editorial discovery and conversion page. It must not contain the entire service catalogue, package catalogue, comparison matrices, or a full gallery grid.

Required homepage sections:

1. Existing opening animation/preloader.
2. Hero section.
3. Occasion discovery.
4. Featured services edit.
5. Featured gallery/lookbook edit.
6. Trust section.
7. Final conversion CTAs.

## Dedicated pages

```text
/services/
/services/<id>/
/packages/
/packages/<id>/
/gallery/
/cart/
/build-your-look/
/academy/
```

The Academy should remain a Coming Soon experience rather than a full course marketplace.

---

# Homepage requirements

## Hero

Create a strong editorial hero with:

- Bridal-focused positioning.
- Large, high-quality visual.
- Clear headline.
- Short supporting copy.
- Primary CTA to `/services/`.
- Secondary CTA to `/gallery/`.
- Optional Beauty Plan or WhatsApp CTA.

The hero image must use real approved project imagery or an existing project asset. Do not invent fake client claims.

## Opening animation

Preserve the existing architectural opening animation:

- Dark charcoal/plum background.
- Two curtain panels.
- Anshita crest/emblem.
- Subtle champagne glow/glitter.
- `Enter Studio`/skip button.
- Escape-key dismissal.
- Automatic timeout fallback.
- Immediate or nearly immediate experience under `prefers-reduced-motion: reduce`.
- No permanent blocking overlay.

If animation libraries fail, the page must still render and become interactive.

## Occasion discovery

Provide clear occasion pathways:

- Wedding/Bridal.
- Engagement/Roka.
- Reception/Cocktail.
- Haldi/Sangeet.
- Family/Bridesmaids.

Each option should lead to a meaningful filtered service/gallery experience or a clearly labeled dedicated page. Do not automatically hijack native scrolling.

## Featured services

Show only a small curated selection, ideally three cards or another clearly limited edit.

Each card should include:

- Image.
- Category.
- Service name.
- Short description or inclusion summary.
- Starting-from price.
- View details action.
- Optional Add to Beauty Plan action.

Cards must link to `/services/<id>/`.

## Featured lookbook

Show only the strongest three or similarly limited album cards.

Each card should include:

- Approved cover image.
- Album/look name.
- Category.
- Optional client/look information.
- Open album action.

Clicking must open the hybrid album viewer or take the user to `/gallery/`.

## Trust section

Place near the bottom of the homepage. Include:

- Sinha Family Group logo.
- Accurate explanatory context.
- Location/travel positioning.
- Selected reviews or trust proof.
- No fabricated awards or endorsements.

## Homepage exclusions

Do not put these full experiences on the homepage:

- Complete service catalogue.
- Complete package catalogue.
- Large comparison tables.
- All albums/media items.
- Repeated pricing engines.
- Long admin/media management panels for public visitors.

---

# Services page requirements

Route:

```text
/services/
```

The page must be a polished dedicated service catalogue.

## Service categories

Support category filtering for the available database categories, including:

- Bridal.
- Engagement/Roka.
- Reception/Cocktail.
- Haldi/Sangeet.
- Hair/Draping.
- Skin/Pre-bridal.
- Family/Bridesmaids.
- Nails.

## Service cards

Every public service card must use active database records and display:

- Service image.
- Service title.
- Category.
- Short description.
- Inclusions/features.
- Starting-from price.
- View details CTA.
- Add to Beauty Plan CTA.
- WhatsApp enquiry CTA where appropriate.

Only `is_active=True` services may be shown publicly.

## Service detail page

Route:

```text
/services/<id>/
```

Include:

- Large service image.
- Service category.
- Description.
- Inclusions.
- Starting-from price.
- Related services.
- Add to Beauty Plan.
- Direct enquiry CTA.
- Clear back-to-services link.

Invalid or inactive IDs must return a proper 404.

## Pricing

Prices must be admin-controlled and sourced from the database. Use “Starting from” language publicly. Never trust a browser-provided price in booking or recommendations.

---

# Packages page requirements

Routes:

```text
/packages/
/packages/<id>/
```

Packages must be separate from individual services.

Include:

- Bridal suites.
- Engagement/reception combinations.
- Multi-event celebration bundles.
- Inclusions.
- Starting-from prices.
- Database-calculated savings.
- Package detail page.
- Beauty Plan action.
- WhatsApp enquiry action.

Only active/public packages may be shown.

Do not show misleading discounts. All savings must be computed from current database values.

---

# Gallery/lookbook requirements

Route:

```text
/gallery/
```

The gallery must be data-driven from album/lookbook records.

## Album cards

Display:

- Album cover.
- Album name.
- Category.
- Approved client/look name if available.
- Photo count.
- Video count.
- Optional external Instagram/YouTube link.
- Open album CTA.

Only albums that are active and published may be shown.

Only media that is published and approved according to the data model may be exposed.

## Filters

Support meaningful category filters and maintain keyboard focus after filtering. Announce result changes with an accessible status message.

---

# Hybrid album viewer requirements

The album viewer must support all three album types:

## Image-only album

- Main image.
- Thumbnail/position indicator.
- Previous/next.
- Caption.
- Keyboard controls.
- Close button.

## Video-only album

- Video or supported embed.
- Poster/thumbnail.
- Previous/next.
- No unexpected audio autoplay.
- External provider link where configured.

## Mixed album

- Correct image/video rendering per item.
- Directional transitions.
- Caption and metadata.
- Previous/next.
- Touch/swipe support.

## Viewer accessibility

- Escape closes.
- Arrow keys navigate.
- Tab focus is controlled while open.
- Focus returns to the invoking album card.
- Close button has an accessible label.
- `aria-modal="true"` is used where appropriate.
- No nested confusing scrollbar on mobile.
- Native vertical scrolling is not hijacked.

---

# Beauty Plan and booking requirements

The top navigation must include a Beauty Plan/cart action. Avoid presenting it as a generic retail ecommerce cart.

The Beauty Plan must support:

- Multiple services/packages.
- Quantity changes where applicable.
- Name.
- Phone.
- Email.
- City/location.
- Event date.
- Notes.
- Enquiry reference.
- WhatsApp handoff.

API:

```text
POST /api/booking/
```

The server must:

1. Validate required contact fields.
2. Resolve submitted service/package IDs against active database records.
3. Recalculate prices server-side.
4. Ignore or reject invalid/inactive records safely.
5. Never trust `estimated_total` from the browser.
6. Persist a `BookingEnquiry`.
7. Return a safe success/error response.

Admin enquiry management:

```text
/admin-portal/enquiries/
```

Admin must be able to view, update status, and archive enquiries.

---

# Build Your Look requirements

Routes:

```text
/build-your-look/
POST /api/package-builder/
```

The builder may ask questions, but recommendations must remain guarded.

Rules:

- Active database services only.
- Database prices only.
- No invented service names.
- No invented prices.
- No direct database mutation by AI.
- No content publishing by AI.
- Budget filtering server-side.
- Maximum discount enforced server-side.
- Invalid discounts clamped.
- Invalid JSON returns 400.
- Unsupported methods return 405.
- Empty/no-match cases receive useful safe responses.

Recommended test coverage:

- Page access.
- Active filtering.
- Database pricing.
- Budget ceiling.
- Discount clamping.
- Invalid JSON.
- Unsupported methods.
- Empty input.
- Inactive records.

---

# Admin requirements

Admin controls must exist for:

- Service active state.
- Service order.
- Service pricing.
- Discount pricing.
- Minimum negotiated price.
- Maximum discount percentage.
- AI negotiation permission.
- Package active state.
- Package pricing/inclusions.
- Album publication.
- Album featured state.
- Album cover.
- Media type.
- Media publication.
- Consent status.
- External media URLs.
- Booking enquiry status.

Admin mutations require appropriate authentication and authorization. AI-generated actions must be schema-validated and bounded.

---

# Glittery background requirements

The visual background should be elegant and subtle.

## Layers

1. Deep charcoal/plum base.
2. Soft champagne radial glow.
3. Barely visible grain/noise.
4. Sparse glitter particles.
5. Rare soft glints.

Suggested palette:

```css
--dark: #161313;
--dark-2: #201a19;
--dark-3: #2a2220;
--cream: #f5edd6;
--gold: #d4af37;
--gold-light: #ead48a;
```

## Glitter behavior

- Desktop: approximately 35–60 particles maximum.
- Tablet: approximately 20–35.
- Mobile: approximately 8–18.
- Most particles are dim and tiny.
- A few particles softly brighten and fade.
- No synchronized screen-wide flashing.
- No particles over faces or important text.
- No gaming/casino/starfield appearance.
- Glitter is strongest in the hero and preloader.
- Glitter is much lighter on catalogue and form pages.

## Implementation

Use CSS or a lightweight DOM particle layer as the default. Canvas/WebGL may be a decorative hero enhancement only.

Canvas must:

- Pause when offscreen.
- Pause when the tab is hidden.
- Disable under reduced motion.
- Disable/reduce on mobile or low-power devices.
- Have a CSS fallback.
- Never contain essential content.

---

# Animation and Evagher-inspired editorial motion

Use broad editorial principles only:

- Large images.
- Spacious sections.
- Layered typography.
- Controlled reveal masks.
- Soft image crop transitions.
- Occasional full-bleed visual moments.
- Calm page rhythm.
- Strong composition.

Do not copy external code, assets, wording, or layouts.

## Approved motion vocabulary

- Curtain reveal.
- Soft fade and upward reveal.
- Image crop reveal.
- Small horizontal editorial slide.
- Subtle depth layers.
- 4–6px card hover lift.
- Gold rule draw.
- Directional album crossfade/slide.

## Avoid

- Scroll hijacking.
- Excessive parallax.
- Large card rotation.
- Flashing discounts.
- Fake countdown urgency.
- Unpausable autoplay carousels.
- Full-screen WebGL dependence.
- Continuous heavy scroll handlers.
- Motion that hides content.

## Reduced-motion mode

With `prefers-reduced-motion: reduce`:

- Preloader dismisses immediately.
- Glitter becomes static or disappears.
- Parallax is removed.
- Slides become instant/short fades.
- Viewer transitions become simple fades.
- Pinned scenes become normal stacked content.
- All content and buttons remain available.

---

# Accessibility requirements

Verify:

- Semantic headings.
- Image alt text.
- Empty alt for decorative images.
- Keyboard navigation.
- Visible focus indicators.
- Accessible button labels.
- Modal focus handling.
- Escape behavior.
- `aria-expanded` on drawers/dropdowns.
- `aria-live` for status changes.
- No information available only on hover.
- Touch targets large enough for mobile.
- No color-only error states.

---

# Security requirements

Review and fix:

- CSRF exemptions.
- Admin authorization.
- Upload MIME validation.
- Upload size limits.
- Image decoding validation.
- Raw exception leakage.
- Unsafe `|safe` output.
- Hardcoded secrets.
- Production `DEBUG` settings.
- `ALLOWED_HOSTS`.
- Secure cookie flags.
- AI action allowlists.
- Prompt injection protection.

---

# Migration and repository requirements

Before declaring completion:

```bash
python manage.py showmigrations
python manage.py migrate --plan
python manage.py makemigrations --check --dry-run
```

There must be one valid migration sequence. Do not leave duplicate migration numbers or conflicting dependencies.

Check for stale links:

```bash
grep -R 'href="/#services"\|href="/#packages"\|href="/#gallery"' \
  -n django/core/templates
```

Expected result: no stale dedicated-catalogue links.

Check all route imports:

```bash
grep -R "animation_lab\|gallery_page\|services_page\|packages_page" \
  -n django/core
```

Every imported view must exist and every referenced template must exist.

---

# Testing requirements

Run from repository root:

```bash
python testing/run_all.py
```

Expected available-suite result:

- Unit: all pass.
- API: all pass.
- Smoke: pass.
- Performance: pass with zero errors.
- Django system check: no issues.

Run browser tests if dependencies are available:

- Desktop homepage.
- Mobile homepage.
- Services page.
- Service detail.
- Packages page.
- Package detail.
- Gallery.
- Image-only album.
- Video-only album.
- Mixed album.
- Beauty Plan.
- Build Your Look.
- Reduced-motion mode.
- Keyboard-only navigation.

If Chromium or Java/Maven are unavailable, report that clearly rather than claiming full validation.

---

# Final acceptance checklist

The task is complete only when:

- [ ] Homepage is concise and editorial.
- [ ] Homepage has no complete service/package/gallery dump.
- [ ] Hero, buttons, occasion discovery, featured cards, trust, and CTAs work.
- [ ] Opening animation is preserved, reliable, and accessible.
- [ ] Glitter background is subtle, beautiful, and performant.
- [ ] Services catalogue is dedicated and functional.
- [ ] Packages catalogue is dedicated and functional.
- [ ] Gallery is dedicated and data-driven.
- [ ] Image-only albums work.
- [ ] Video-only albums work.
- [ ] Mixed albums work.
- [ ] Album viewer is mobile and keyboard accessible.
- [ ] Beauty Plan booking recalculates prices server-side.
- [ ] Build Your Look obeys all server-side guardrails.
- [ ] Admin controls are functional.
- [ ] No stale catalogue anchors remain.
- [ ] Migration chain is valid.
- [ ] No missing view/template imports remain.
- [ ] Tests pass.
- [ ] Browser visual validation passes.
- [ ] Working tree is clean.
- [ ] Final branch is pushed and PR updated.

Do not declare the work finished if only the unit tests pass while visual/browser acceptance remains unverified.
