# Anshita Makeover — Animation, Background, and Interaction Specification

## Purpose

This document is the implementation contract for the visual motion system. It describes the animation style, background behavior, page transitions, gallery motion, accessibility requirements, and performance boundaries that the website must follow.

The visual direction is **editorial bridal couture**: cinematic, warm, refined, tactile, and spacious. Motion should make the website feel like a luxury lookbook, not like an entertainment dashboard.

The reference direction borrows broad editorial principles from luxury fashion and beauty websites—large imagery, controlled reveals, quiet transitions, layered typography, and intentional pacing—but must use Anshita Makeover's own content, brand, and implementation.

---

## 1. Core creative direction

### Desired feeling

The animation system should feel:

- Cinematic but calm.
- Premium but not slow.
- Feminine without becoming sugary.
- Editorial rather than commercial.
- Tactile, like turning pages in a couture lookbook.
- Warm, with champagne-gold accents on deep charcoal/plum backgrounds.
- Image-led, with typography supporting the photography.

### Motion vocabulary

Use a small, consistent set of motion behaviors:

1. **Curtain reveal** — the existing opening animation uses two architectural curtains that part to reveal the studio.
2. **Soft opacity reveal** — text and cards fade in with a short upward movement.
3. **Image crop reveal** — images enter through an overflow-hidden frame while their scale settles from approximately 1.04 to 1.
4. **Editorial slide** — hero content or gallery media moves a short distance horizontally, never a large carousel swipe across the page.
5. **Layered depth** — foreground image, background wash, and decorative line move at different very small rates.
6. **Hover lift** — cards rise by a few pixels and brighten their border; no aggressive 3D rotation.
7. **Viewer transition** — album images use a directional crossfade/slide when changing media.
8. **Progressive line drawing** — thin champagne rules or small decorative vector marks draw in once, then remain static.

Do not introduce a new animation style for every section.

---

## 2. Color and background system

### Primary background

The primary page background should be a deep editorial neutral:

```css
--dark: #161313;
--dark-2: #201a19;
--dark-3: #2a2220;
```

The exact existing variables may be retained if they already match the design system, but all new sections must use the same palette rather than introducing unrelated colors.

### Text

```css
--cream: #f5edd6;
--text-sub: rgba(245, 237, 214, 0.68);
--text-muted: rgba(245, 237, 214, 0.45);
```

### Accent

Champagne gold should be used sparingly:

```css
--gold: #d4af37;
--gold-light: #ead48a;
```

Gold is for:

- Small section labels.
- Focus/hover borders.
- Rules and dividers.
- Key prices.
- Primary CTA emphasis.
- Progress indicators.

Gold must not be used as a full-screen flashing background or behind large quantities of text.

### Background texture

The site may use a subtle atmospheric background layer:

- A very low-opacity radial champagne glow.
- A barely visible grain/noise layer.
- A soft vignette around the edge of large image sections.
- Optional blurred color wash derived from the current hero image.

Recommended implementation:

```css
.page-atmosphere {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background:
    radial-gradient(circle at 18% 18%, rgba(212,175,55,.08), transparent 32%),
    radial-gradient(circle at 82% 70%, rgba(125,72,70,.10), transparent 38%),
    #161313;
}
```

Constraints:

- No rapidly moving particle field behind text.
- No heavy full-page video background.
- No animated background that reduces text contrast.
- No WebGL dependency for essential content.
- If Three.js is retained, it must remain a decorative enhancement and be disabled on reduced-motion/mobile/low-power conditions.

---

## 3. Opening animation / preloader

The opening animation is a signature element and should be preserved, not replaced by a generic spinner.

### Sequence

1. Page loads with a dark charcoal background.
2. Two vertical architectural curtain panels cover the viewport.
3. The Anshita crest/emblem appears in the center.
4. The crest fades or softly scales into place.
5. A thin gold rule or small decorative mark draws in.
6. The `Enter Studio`/skip control becomes visible.
7. Curtains part from the center toward the sides.
8. Main page content becomes visible.
9. Preloader is removed from the accessibility tree and does not block interaction.

### Timing target

- Fast path: approximately 900–1400 ms.
- Maximum automatic wait: approximately 2500 ms.
- If assets or animation libraries fail, the page must still become usable.

### Required controls

- Visible `Enter Studio` button.
- Escape key dismisses the preloader.
- Clicking the skip button dismisses the preloader.
- A fallback timeout dismisses it automatically.
- Session storage may prevent replay on every page load, but the user must be able to see it again after a new session if desired.

### Reduced motion

When `prefers-reduced-motion: reduce` is active:

- Do not part curtains with animated transforms.
- Show the crest with an immediate or very short opacity change.
- Remove all decorative motion.
- Make the page available immediately.
- Do not hide content behind a long preloader.

### Failure behavior

If any of the following fails:

- GSAP unavailable.
- Three.js unavailable.
- Crest asset unavailable.
- JavaScript error.
- Slow network.

The page must still dismiss the preloader using a simple CSS fallback or timeout.

---

## 4. Homepage animation plan

The homepage is a discovery page and should not behave like a long animation demo.

### Hero

The hero uses a restrained cinematic composition:

- Large bridal image on one side.
- Editorial copy on the other side.
- Slow image crop settlement on first load.
- Headline reveals line by line or as one controlled block.
- Gold rule draws once.
- CTA buttons fade in after the headline.

Suggested sequence:

```text
0 ms       hero image visible at scale 1.03
120 ms     section label fades in
260 ms     headline rises 16px and fades in
430 ms     supporting copy appears
560 ms     CTA buttons appear
```

No continuous hero zoom should run forever. If an idle effect is used, keep it below a 1% scale movement over 12–20 seconds and disable it on reduced motion.

### Occasion discovery

Occasion cards should reveal as a staggered row/grid:

- Each card enters with opacity and a 12px upward movement.
- Stagger: approximately 60–90 ms.
- Hover: gold border and small lift.
- Active selection: gold border, subtle background wash, and a short status message.

Do not automatically scroll the user aggressively when selecting an occasion. If filtering is used, update the relevant content and provide a clearly labeled optional link to explore it.

### Featured services

Service cards should use:

- Image crop reveal on initial appearance.
- Text appearing after the image is visible.
- A small hover lift of 4–6px.
- A gold border transition.
- No card rotation.
- No infinite floating animation.

Only the strongest three or a small curated selection should appear on the homepage. The full catalogue belongs on `/services/`.

### Featured lookbook

Lookbook cards should feel like printed editorial plates:

- Image frame with `overflow: hidden`.
- Caption below or over a controlled gradient.
- Small category label.
- `Open album` affordance.
- Hover image scale no greater than approximately 1.04.
- Optional gold line that expands from 0 to a short width.

Cards must open the album viewer, not navigate to an inaccessible or placeholder page.

### Trust section

Trust content should use no dramatic animation. Use only:

- Fade-in of the heading.
- A short gold rule draw.
- Gentle reveal of logo/testimonial blocks.

The Sinha Family Group logo must be presented with accurate context and must not imply awards, ownership, or endorsement that is not true.

---

## 5. Services page animation plan

The services page is a catalogue, so motion must support scanning and comparison.

### Page entry

- Header enters immediately.
- Catalogue heading fades in.
- Filter controls appear without delay.
- Cards reveal in a stagger of no more than 50 ms each.

### Filter transitions

When filtering categories:

- Do not animate height for a large number of cards if it causes layout jumps.
- Use CSS opacity/transform for a short transition.
- Maintain keyboard focus on the selected filter.
- Announce the updated result count with an `aria-live` status.

### Card hover

Allowed:

- 4–6px lift.
- Image scale up to 1.04.
- Border color transition.
- CTA underline or arrow movement.

Not allowed:

- Large card rotation.
- Cursor-following distortions.
- Unreadable text overlays.
- Motion that moves the card under the pointer.

### Detail page

Service detail page may use:

- Image reveal.
- Small inclusion list stagger.
- Price fade-in.
- Sticky Beauty Plan CTA on mobile only if it does not cover content.

---

## 6. Packages page animation plan

Packages should feel more composed and premium than individual service cards.

Allowed effects:

- Wide image crop reveal.
- Small package number/label reveal.
- Gold divider drawing.
- Inclusion list appearing in short groups.
- Hover transition on package comparison cards.

Avoid:

- Flashing discount badges.
- Fake countdown urgency.
- Excessive confetti or particles.
- Auto-rotating package carousels that cannot be paused.

All prices should continue to be presented as admin-controlled starting prices, with savings calculated from database values.

---

## 7. Gallery and lookbook animation plan

### Gallery page

The gallery should feel like an editorial archive:

- Album cards load in a quiet stagger.
- Category filtering crossfades the grid.
- Cover images use a restrained crop settlement.
- Album metadata remains readable without hover.

### Album opening

When an album opens:

1. The selected card may briefly transition toward the viewer position.
2. The overlay fades in.
3. Viewer panel settles from 98% scale to 100%.
4. Main media becomes visible.
5. Caption and controls appear.

The viewer must open immediately enough that users do not think the click failed.

### Previous/next

For image changes:

- Directional slide of approximately 20–36px.
- Crossfade at the same time.
- Duration approximately 240–420 ms.
- No full-screen page transition.

For video changes:

- Stop/unload previous media.
- Show the next poster or player.
- Do not autoplay audio unexpectedly.

### Mobile

- Viewer occupies the viewport without nested confusing scrollbars.
- Controls remain reachable with one hand.
- Swipe changes media only when the gesture is clearly horizontal.
- Native vertical page scroll must remain available.
- Close button remains fixed and visible.

### Keyboard

- `Escape`: close viewer.
- `ArrowLeft`: previous media.
- `ArrowRight`: next media.
- `Tab`: stays within the viewer while open.
- Focus returns to the album button after close.

---

## 8. Beauty Plan and booking animation plan

Booking actions should communicate confidence and progress, not urgency.

### Cart drawer

- Drawer slides in from the appropriate edge.
- Background scrim fades in.
- Focus moves into the drawer.
- Close returns focus to the cart button.
- The drawer must not create a second confusing page scrollbar on mobile.

### Add-to-plan feedback

When a service is added:

- Update the badge immediately.
- Use a short non-blocking status message.
- Do not use a disruptive alert for normal additions.
- Keep the service card in place.

### Booking submission

- Disable the submit button while sending.
- Show a clear loading state.
- Show success/error message in the form.
- Never rely solely on color.
- Preserve entered form data after validation errors.

---

## 9. Build Your Look animation plan

The builder should feel like a guided consultation.

- Questions appear one step at a time only if that improves clarity.
- Step changes use short opacity/slide transitions.
- Users can go back without losing answers.
- Recommendation results use a calm reveal.
- Budget/discount messages remain visible and understandable.
- No fake AI typing delay is required.
- If no service matches the budget, show a useful empty state with a contact CTA.

---

## 10. Background/WebGL rules

Three.js or canvas may be used only for decorative enhancement.

### Allowed

- Very slow abstract gold dust or light field.
- Low-opacity blurred shapes.
- Static or slowly shifting ambient gradient.
- Decorative background behind the hero.

### Not allowed

- Essential content rendered only in canvas.
- High-density particles on mobile.
- Continuous expensive render loops when the canvas is not visible.
- Full-screen WebGL that prevents text selection.
- Motion that competes with faces or makeup details.
- Scroll-linked WebGL that hijacks scrolling.

### Disable conditions

Disable canvas/WebGL when:

- `prefers-reduced-motion: reduce` is active.
- The device appears low-power or mobile, unless the effect is proven lightweight.
- The tab is hidden.
- The canvas is outside the viewport.
- WebGL initialization fails.

Use `IntersectionObserver` and `visibilitychange` to pause expensive effects.

---

## 11. Accessibility contract

Every motion component must have a non-animated equivalent.

Required:

- `prefers-reduced-motion` support.
- Visible focus styles.
- Keyboard operation for menus, cards, drawers, and viewer.
- `aria-expanded` for drawers/dropdowns.
- `aria-modal="true"` for modal viewers.
- `aria-live` for filter and booking status updates.
- No essential information available only on hover.
- No flashing above safe thresholds.
- No automatic carousel that cannot be paused.
- No focus trapped in a closed modal.

---

## 12. Performance budget

Targets:

- First content visible without waiting for animation libraries.
- Hero image is prioritized and appropriately sized.
- Below-the-fold images use lazy loading.
- Decorative scripts use `defer` where compatible.
- No continuous scroll event handler that performs layout work.
- Use CSS transforms and opacity for transitions.
- Avoid animating `top`, `left`, `width`, `height`, or large box shadows repeatedly.
- Pause offscreen animation.
- Avoid layout shift when images load by reserving aspect-ratio boxes.

Suggested budgets:

- No more than one major continuous decorative animation at a time.
- Entry transition duration: generally 250–700 ms.
- Page should be usable if all optional animation JavaScript fails.
- Motion should not delay access to any CTA beyond the preloader maximum.

---

## 13. Validation checklist

### Desktop

- [ ] Opening curtains dismiss correctly.
- [ ] Hero buttons work.
- [ ] Occasion cards work.
- [ ] Featured service cards open details.
- [ ] Featured albums open viewer.
- [ ] Services catalogue filters work.
- [ ] Package cards open details.
- [ ] Gallery opens image-only albums.
- [ ] Gallery opens video-only albums.
- [ ] Gallery opens mixed albums.
- [ ] Beauty Plan drawer opens and closes correctly.

### Mobile

- [ ] No horizontal overflow.
- [ ] No nested confusing scrollbars.
- [ ] Viewer controls are reachable.
- [ ] Swipe does not hijack vertical scrolling.
- [ ] Navigation drawer works.
- [ ] CTA buttons have adequate touch targets.
- [ ] Hero image and text remain readable.

### Accessibility

- [ ] Keyboard-only navigation works.
- [ ] Escape closes preloader, drawer, and viewer.
- [ ] Focus returns to invoking control.
- [ ] Reduced-motion mode removes nonessential motion.
- [ ] Status messages are announced.

### Performance

- [ ] Canvas pauses offscreen.
- [ ] Decorative animation can fail without breaking the page.
- [ ] Images reserve layout space.
- [ ] No blocking console errors.
- [ ] No long-running scroll handler.

---

## 14. Definition of done

The animation and background work is complete only when:

1. The existing opening animation is preserved and reliable.
2. The homepage uses restrained editorial reveals rather than a collection of unrelated effects.
3. Services, packages, and gallery use consistent motion language.
4. The album viewer works for images, videos, and mixed albums.
5. Background effects remain decorative and performant.
6. Native scrolling is never hijacked.
7. Reduced-motion behavior is complete.
8. Mobile and keyboard behavior are verified.
9. No animation route/template/import is broken.
10. Browser-level validation confirms the intended result visually.
