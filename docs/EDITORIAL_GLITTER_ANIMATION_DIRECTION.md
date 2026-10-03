# Anshita Makeover — Glitter Background and Evagher-Inspired Editorial Motion Direction

## Purpose

This document captures the specific visual direction discussed for the Anshita Makeover experience:

- A beautiful, subtle, glittering background.
- A cinematic luxury-beauty atmosphere.
- Editorial movement inspired by the mood and pacing of the Evagher website reference shared during planning.
- An original implementation using Anshita Makeover's own brand, images, copy, and interaction patterns.

This is an inspiration and implementation direction, not a request to copy Evagher's code, layout, assets, wording, or identity.

---

# 1. Desired overall feeling

The site should feel like entering a luxury bridal studio after sunset:

- Deep charcoal/plum space.
- Warm champagne light.
- Tiny floating points of reflected light.
- Large, quiet photography.
- Slow editorial transitions.
- Strong typography with generous breathing room.
- Delicate movement around the content, never movement that makes the content difficult to read.

The glitter should feel like:

- Fine cosmetic shimmer.
- Light catching on jewellery.
- Dust suspended in a theatrical beam.
- Champagne particles in the air.
- A soft reflection from a bridal dupatta or sequined fabric.

It must not feel like:

- A gaming particle effect.
- A Christmas sparkle overlay.
- A casino or wedding-template animation.
- A bright starfield behind every section.
- A continuously flashing background.

The guiding rule is:

> The visitor should notice the atmosphere before noticing the effect, and should notice the content before noticing the atmosphere.

---

# 2. Relationship to the Evagher reference

The Evagher reference is useful for broad creative principles:

- Full-bleed cinematic visual compositions.
- Strong editorial typography.
- A sense of moving through a visual story.
- Carefully staged section entrances.
- Large images treated as art direction rather than simple thumbnails.
- Restrained, high-quality transitions.
- Layered depth and spatial composition.
- Intentional pauses between sections.

The Anshita Makeover version should adapt those principles to a bridal beauty studio:

- Replace fashion-editorial abstraction with bridal faces, hair, draping, jewellery, skin texture, and celebration details.
- Replace unfamiliar navigation experiments with clear Services, Packages, Gallery, Beauty Plan, and booking paths.
- Keep the opening animation, but make the rest of the site easy to use and naturally scrollable.
- Use the glitter as an atmospheric studio signature, not as a decorative copy of another site's visual identity.

The result should be:

```text
Evagher-like editorial mood
+ Anshita bridal imagery
+ champagne shimmer atmosphere
+ clear catalogue and booking UX
```

---

# 3. Glitter background concept

## 3.1 Layer structure

The glitter background should be built from several restrained layers rather than one aggressive particle canvas.

### Layer A — base color

A deep, warm charcoal background:

```css
background: #161313;
```

Possible secondary tones:

```css
--ink: #161313;
--plum-black: #21191b;
--warm-brown: #2a2020;
--wine-shadow: #332124;
```

### Layer B — ambient light pools

Large blurred radial gradients create a studio-light feeling:

```css
background:
  radial-gradient(
    circle at 18% 15%,
    rgba(212, 175, 55, 0.12),
    transparent 30%
  ),
  radial-gradient(
    circle at 84% 32%,
    rgba(158, 91, 100, 0.12),
    transparent 34%
  ),
  radial-gradient(
    circle at 52% 100%,
    rgba(235, 203, 142, 0.06),
    transparent 38%
  ),
  #161313;
```

These pools should drift extremely slowly or remain static. They are meant to give depth to the background, not act as a visible animation.

### Layer C — soft grain

A very subtle grain texture can prevent flat digital color.

Options:

1. A small compressed noise image.
2. A CSS-generated low-opacity pattern.
3. A tiny SVG filter used sparingly.

Recommended opacity:

```css
opacity: 0.025 to 0.055;
```

The grain must not make text or faces look dirty.

### Layer D — glitter particles

The glitter particles are tiny, sparse points of warm light.

Recommended appearance:

- 1px to 3px diameter.
- Mostly champagne, ivory, or muted rose-gold.
- Very low opacity at rest.
- Small number of brighter particles.
- No uniform grid.
- No obvious repeated pattern.
- No particle directly over important text where it reduces readability.

Suggested particle distribution:

```text
70% tiny dim points
20% medium soft points
8% small blurred glints
2% rare bright twinkles
```

### Layer E — occasional glints

A few particles may briefly brighten and fade:

```text
fade from 0.15 opacity to 0.75 opacity and back
800–1600 ms duration
long random delay
```

There should never be a simultaneous flash across the screen.

---

# 4. Glitter implementation options

## Option A — CSS-only glitter for the base experience

Use pseudo-elements or a repeated radial-gradient background for a lightweight effect.

Advantages:

- No JavaScript dependency.
- Works if all animation libraries fail.
- Easy to disable with reduced motion.
- Low CPU cost.

Limitations:

- Less natural random movement.
- Harder to make particles feel organic.

Good for:

- Services page.
- Packages page.
- Footer/trust section.
- Mobile devices.

## Option B — DOM particle layer

Create a small number of absolutely positioned particles with CSS animation.

Recommended maximum:

- Desktop: 35–60 particles.
- Tablet: 20–35 particles.
- Mobile: 8–18 particles.

Each particle should receive randomized:

- Position.
- Size.
- Opacity.
- Delay.
- Duration.
- Blur.
- Drift direction.

Use transforms only:

```css
transform: translate3d(x, y, 0) scale(s);
```

Do not animate layout properties such as `top`, `left`, `width`, or `height` continuously.

## Option C — Canvas glitter enhancement

A canvas can render the hero-only glitter field when the device supports it.

Rules:

- Canvas is decorative only.
- HTML content remains fully visible without it.
- Pause it when the hero leaves the viewport.
- Disable it for `prefers-reduced-motion: reduce`.
- Disable or reduce it on small/low-power devices.
- Use device-pixel-ratio limits to avoid expensive rendering.
- Keep particle count low.
- Stop animation when the tab is hidden.

The fallback must be the CSS-only background.

---

# 5. Glitter movement behavior

The glitter should not move as a flat swarm.

Use three movement families:

## Family 1 — suspended drift

Particles move 4–16px over 8–22 seconds.

```text
slow diagonal movement
small opacity variation
no sharp direction changes
```

## Family 2 — gentle rise

A few particles move upward like dust in a light beam.

```text
movement: 10–30px upward
opacity: 0 → 0.4 → 0
duration: 10–24 seconds
```

## Family 3 — stationary twinkle

Most particles barely move and only change brightness.

```text
scale: 0.85 → 1.15 → 0.85
opacity: 0.15 → 0.55 → 0.15
duration: 1.2–2.4 seconds
```

Use random delays so the effect does not appear synchronized.

---

# 6. Section-specific visual treatment

## 6.1 Opening/preloader

The preloader should use the most controlled version of the atmosphere.

Sequence:

1. Deep charcoal background appears.
2. A very faint central champagne glow expands.
3. Two curtain panels cover the frame.
4. The Anshita crest appears.
5. A handful of glitter points become visible around the crest.
6. A few points brighten like reflected jewellery.
7. Curtains open.
8. Glitter density reduces as the homepage becomes interactive.

Do not keep the preloader waiting for glitter or remote assets.

## 6.2 Homepage hero

The hero can contain the richest background treatment:

- Large warm radial glow behind the image/copy.
- 20–40 subtle particles in the negative space.
- Two or three slow brighter glints.
- A barely perceptible light sweep across a gold rule.
- Background glow moves slower than foreground image movement.

The face, hair, jewellery, and text must remain the visual priority.

## 6.3 Occasion discovery

Reduce glitter density here.

Use:

- Static soft glow.
- Thin gold dividers.
- Small hover shimmer on the selected card border.

Avoid putting moving particles inside every occasion card.

## 6.4 Services catalogue

Use a calm, mostly static background.

Cards should feel like editorial catalogue plates:

- Image crop reveal.
- Soft border transition.
- Tiny gold arrow movement.
- No continuous card animation.

Glitter should remain behind the catalogue and not interfere with price/inclusion scanning.

## 6.5 Packages catalogue

Use slightly warmer ambient light because packages represent complete celebration planning.

Allowed:

- A slow background glow.
- Small gold divider shimmer on section entry.
- Subtle package-card border highlight.

Do not use fake urgency or rapidly flashing savings labels.

## 6.6 Gallery/lookbook

The gallery should feel like a dark exhibition room.

Use:

- Deeper background.
- Slightly brighter image frames.
- Sparse glitter only in empty space.
- Soft image hover zoom.
- A restrained gold line around focus/hover.

The viewer overlay may use a very faint blurred version of the current image behind the main media, provided it does not reduce contrast.

## 6.7 Trust section

Use almost no glitter. Trust content needs clarity.

Use:

- Static warm glow.
- Logo reveal.
- Soft rule draw.
- Slow fade-in only.

## 6.8 Beauty Plan/cart

The cart drawer should prioritize usability over spectacle.

- Background scrim fades in.
- Drawer slides in.
- No particle movement inside form fields.
- Gold highlight only for selected items and totals.

---

# 7. Evagher-like transition language

The site can feel more like the shared Evagher reference through composition and pacing rather than copying its implementation.

## 7.1 Full-bleed image moments

Use occasional large image sections with:

- Strong crop.
- Minimal copy.
- Large type.
- Plenty of empty space.
- A clear next action.

Do not make every section full-screen; use full-bleed moments as punctuation.

## 7.2 Editorial reveal masks

Images can be revealed through a mask or clipped frame:

```text
initial state: image clipped to a narrow or offset frame
final state: frame expands to full card/section bounds
```

Duration target:

```text
600–900 ms
```

Use only on initial entry, not every time a user scrolls back and forth.

## 7.3 Layered typography

Use hierarchy:

- Small uppercase section label.
- Large serif/editorial heading.
- Short supporting paragraph.
- One or two clear actions.

Text should arrive in groups, not every word separately.

Avoid overly theatrical text animations that slow reading.

## 7.4 Pinned editorial scenes

If a pinned scene is used, it must be limited to one intentional section, such as:

- A three-look service story.
- A three-frame bridal transformation.
- A short “from consultation to final look” sequence.

Rules:

- Pin only within the section bounds.
- Do not hijack the entire page scroll.
- Provide natural mobile fallback: stacked cards.
- Respect reduced motion.
- Ensure keyboard users can reach all content without scroll choreography.

## 7.5 Horizontal visual sequence

A horizontal gallery sequence may be used only inside a controlled component.

It must:

- Work with drag/swipe.
- Have previous/next buttons.
- Have visible progress.
- Allow keyboard navigation.
- Fall back to a vertical list on mobile.
- Never convert the whole page into a horizontal scroll trap.

## 7.6 Soft scene changes

Between major sections, use:

- Background color shift.
- Thin divider line.
- Image overlap.
- Short opacity reveal.

Avoid dramatic page wipes for ordinary links.

---

# 8. Buttons and interactive accents

Buttons are part of the motion language.

## Primary button

Use a champagne fill or strong outlined gold treatment.

Hover:

- Background shifts slightly warmer.
- Arrow moves 3–5px.
- Shadow increases subtly.

Focus:

- Clear high-contrast outline.
- No reliance on hover-only color.

## Secondary button

Use transparent background with a fine champagne border.

Hover:

- Border brightens.
- Background receives a low-opacity gold wash.
- Text remains readable.

## Gallery open button

Use a small arrow or “Open album” label.

On hover:

- Arrow translates slightly.
- A short underline or rule expands.

Do not make the entire button flash.

## Beauty Plan button

When adding an item:

- Badge count updates.
- Button may briefly brighten once.
- Use an accessible status message.
- Do not use a shaking cart icon.

---

# 9. Image treatment

Photography is more important than the glitter.

Use:

- High-quality crops that protect faces.
- Object positioning controlled per image where needed.
- Soft overlay gradients only where text sits over images.
- `aspect-ratio` containers to prevent layout shifts.
- Lazy loading below the fold.
- Eager/preloaded hero image where appropriate.

Avoid:

- Heavy filters that alter makeup colors.
- Excessive blur.
- Glitter over faces.
- Aggressive zoom that cuts off hair, jewellery, or clothing details.
- Fake before/after effects unless real approved media is available.

---

# 10. Responsive behavior

## Desktop

- Richest hero atmosphere.
- 20–60 particles depending on performance.
- Large editorial image compositions.
- Hover interactions enabled.
- Optional light canvas enhancement.

## Tablet

- Reduce particle count by approximately half.
- Simplify layered movement.
- Keep cards readable in two-column layouts.
- Disable expensive effects if frame rate falls.

## Mobile

- CSS ambient glow rather than a large particle canvas.
- Approximately 8–18 glitter particles maximum if performance allows.
- No hover-only behavior.
- Stacked services/gallery cards.
- Native vertical scroll.
- Viewer controls fixed within reachable areas.
- No full-screen pinned scroll scenes.

---

# 11. Reduced-motion design

When reduced motion is enabled:

- Remove glitter drift.
- Remove particle twinkles or leave only static dots.
- Remove parallax.
- Remove image scale transitions.
- Remove pinned scenes.
- Replace slide transitions with immediate or short fades.
- Make the preloader dismiss immediately.
- Keep focus, hierarchy, and visual styling intact.

The reduced-motion page should still look premium; it should not look broken or empty.

---

# 12. Performance requirements

The glitter system must never become the reason the site feels slow.

Requirements:

- Use transforms and opacity for animation.
- Avoid layout-triggering animation.
- Pause canvas when offscreen.
- Pause animation when the tab is hidden.
- Use `IntersectionObserver` for section entry effects.
- Limit device pixel ratio for canvas.
- Avoid loading large animation libraries before content.
- Ensure the hero remains usable if scripts fail.
- Keep background layers pointer-events disabled.
- Do not use a high-frequency scroll listener for every section.

Suggested limits:

```text
Desktop particles: 35–60
Tablet particles: 20–35
Mobile particles: 8–18
Hero continuous animations: maximum 1–2
Section entry duration: 250–900 ms
```

---

# 13. Implementation architecture

Recommended components:

```text
motion/
├── preloader.js
├── glitter-background.js
├── reveal-observer.js
├── viewer-motion.js
└── motion-preferences.js
```

The implementation can remain within the current Django templates if that matches the repository architecture, but responsibilities should remain separated.

### `motion-preferences.js`

Expose:

```js
const motionReduced = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;
```

All animation modules should check this value before starting.

### `glitter-background.js`

Responsibilities:

- Create a limited number of particles.
- Randomize position and timing.
- Pause when hidden/offscreen.
- Fall back safely.
- Remove or freeze on reduced motion.

### `reveal-observer.js`

Responsibilities:

- Observe sections/cards.
- Add a single `is-visible` class.
- Avoid repeatedly replaying animation unless intentionally requested.

### `viewer-motion.js`

Responsibilities:

- Directional image transitions.
- Video cleanup before changing media.
- Reduced-motion fallback.
- Focus/keyboard integration.

---

# 14. Visual QA checklist

## Background

- [ ] Glitter is visible but subtle.
- [ ] Glitter never covers important text.
- [ ] Glitter does not cover faces.
- [ ] Background contrast remains accessible.
- [ ] No obvious repeated particle pattern.
- [ ] No flashing or distracting synchronization.
- [ ] Mobile particle count is reduced.
- [ ] Reduced-motion background is static.

## Homepage

- [ ] Preloader can always be dismissed.
- [ ] Hero feels cinematic but loads quickly.
- [ ] Hero buttons remain visible and usable.
- [ ] Occasion cards reveal cleanly.
- [ ] Featured services remain a small curated edit.
- [ ] Featured gallery remains a small curated edit.
- [ ] Trust content remains readable.

## Services and packages

- [ ] Cards animate only on entry/hover.
- [ ] Pricing and inclusions remain readable.
- [ ] Filters do not cause jarring layout shifts.
- [ ] No catalogue page feels like a particle demo.

## Gallery

- [ ] Album cards feel like a visual exhibition.
- [ ] Viewer opens quickly.
- [ ] Image transitions are directional and soft.
- [ ] Video transitions do not autoplay unexpected audio.
- [ ] Mixed albums work correctly.
- [ ] Mobile viewer does not trap vertical scrolling.

## Evagher-inspired mood

- [ ] Large imagery is given room to breathe.
- [ ] Typography creates a clear editorial rhythm.
- [ ] Full-bleed moments are used selectively.
- [ ] Motion supports the visual story.
- [ ] The result remains recognizably Anshita Makeover.
- [ ] No external site's assets, code, copy, or identity are copied.

---

# 15. Definition of done

The glitter and editorial animation direction is complete when:

1. The opening animation is reliable and accessible.
2. The background has a warm, subtle, champagne-glitter atmosphere.
3. The glitter is strongest in the hero and restrained elsewhere.
4. Services, packages, and gallery use one consistent motion language.
5. The gallery viewer has polished image/video/mixed-media transitions.
6. Mobile uses a simpler, lighter version of the effect.
7. Reduced-motion users receive a complete static alternative.
8. The site remains usable if animation JavaScript fails.
9. Native scrolling is never hijacked.
10. Browser testing confirms the result feels cinematic, premium, and original rather than copied.
