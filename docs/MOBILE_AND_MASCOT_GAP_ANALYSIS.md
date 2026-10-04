# Mobile, Navigation, Scroll Motion, and AI Mascot Gap Analysis

**Audit target:** remote branch `arena/01a0d489-anshitamakeover`

**Audited remote commit:** `10ea3328c44acfb66106ee86c71c5cc046d583ae`

**Audit date:** 2026-10-04

## Executive finding

The current remote implementation does **not** yet match the requested 3D mascot behavior.

The requested experience is:

1. A 3D AI character/bunny is hidden initially.
2. As the visitor scrolls down, the character enters the scene smoothly.
3. The character becomes smaller and docks into a chatbot position.
4. It then shows a greeting such as “How may I help you today?”
5. The transition feels like a polished 3D editorial website, with scroll-driven animation rather than a normal floating chat bubble.
6. The navigation bar remains available and does not disappear incorrectly on mobile.

The remote implementation currently provides a conventional fixed chatbot bubble and a draggable chat panel. It does not yet provide the requested scroll-driven mascot transformation.

---

## 1. Current remote behavior

### Chatbot component

The remote `chatbot_modal.html` contains:

- A fixed chat container.
- A chat window.
- An Anshita Concierge header.
- An image avatar using `logo.jpeg`.
- A chat message list.
- A language selection card.
- Text input and send button.
- A fixed `💬` toggle button.
- A pulse ping around the toggle button.

Current welcome content includes a long concierge introduction and language choices. It does not implement a hidden 3D character entering from the page scene.

### Current gap

The current component is a normal chatbot UI. It is not a character animation system.

Missing:

- 3D bunny/mascot asset in the public scene.
- Initial hidden state.
- Scroll progress tracking.
- Character entrance choreography.
- Character scale-down choreography.
- Character docking to chatbot position.
- Character-to-chatbot state transition.
- “How may I help you today?” transition message.
- Scroll-driven interpolation.
- Mobile-specific mascot composition.
- Reduced-motion equivalent.

---

## 2. Requested mascot experience

## State A — Hidden initial state

On first load:

- The mascot should not occupy the main visual composition.
- It may be completely below/behind the hero scene or represented by a subtle hint.
- It must not cover the hero headline, primary CTA, face, or navigation.
- It must not create horizontal overflow.
- The chatbot should not appear as a generic fixed bubble immediately if the planned experience expects the character reveal first.

Suggested initial state:

```text
opacity: 0
scale: 1.12
translate3d(0, 40px, 0)
visibility: hidden or visually concealed
pointer-events: none
```

The initial hidden state must still have a non-animated accessible fallback.

## State B — Scroll entrance

As the user scrolls through the hero/first discovery section:

- The character gradually becomes visible.
- The character can rise from the lower/right visual layer.
- A soft glow or glitter trail may accompany the movement.
- Movement should be tied to scroll progress, not a timer.
- The page must keep native scrolling.
- Scroll must not be prevented, hijacked, or replaced by wheel-event choreography.

Suggested progress range:

```text
0.00–0.25: hidden to partially visible
0.25–0.55: character enters and settles
0.55–0.80: character begins scaling down and moving toward dock position
0.80–1.00: character becomes a compact chatbot assistant
```

## State C — Docked chatbot

After the transition:

- The large mascot becomes small.
- It docks into a fixed chatbot launcher position.
- It remains reachable on every page.
- It does not cover important mobile controls.
- It displays a short greeting bubble:

```text
How may I help you today?
```

Alternative copy may include:

```text
Namaste! How may I help you today?
```

The message should appear once or with a calm reveal, not repeatedly on every scroll.

## State D — Open concierge

When tapped/clicked:

- The docked mascot opens the concierge panel.
- The user can close/dock it again.
- The panel should retain focus behavior.
- The mascot should not jump unexpectedly between positions.
- The panel must remain usable on mobile.

---

## 3. Scroll animation architecture

The desired behavior is scroll-driven, but native scrolling must remain intact.

### Correct approach

Use a passive scroll observer or `IntersectionObserver`/scroll timeline approach to derive a normalized progress value.

Do not use:

```js
preventDefault()
```

on the page wheel or touch scroll path.

Do not replace the page with a manually controlled full-screen scroll engine.

### Recommended structure

```html
<section class="hero-scene" data-mascot-scene>
  <div class="hero-content">...</div>
  <div class="mascot-stage" aria-hidden="true">
    <canvas id="mascot-canvas"></canvas>
    <!-- or a transparent animated 3D/WebGL layer -->
  </div>
</section>

<div class="mascot-dock" id="mascot-dock">
  <button aria-label="Open Anshita AI Concierge">...</button>
  <div class="mascot-greeting">How may I help you today?</div>
</div>
```

```js
const scene = document.querySelector('[data-mascot-scene]');
const mascot = document.querySelector('.mascot-stage');
const dock = document.querySelector('.mascot-dock');

const updateMascotProgress = () => {
  const rect = scene.getBoundingClientRect();
  const travel = Math.max(1, scene.offsetHeight - window.innerHeight);
  const progress = Math.min(1, Math.max(0, -rect.top / travel));

  mascot.style.setProperty('--mascot-progress', progress.toFixed(3));
  dock.classList.toggle('is-docked', progress > 0.8);
};

window.addEventListener('scroll', updateMascotProgress, { passive: true });
```

For better performance, use `requestAnimationFrame` throttling or CSS scroll-driven animation where browser support is acceptable, with a JavaScript fallback.

### Important

The scroll handler should only update transforms/opacity or a CSS custom property. It must not repeatedly force layout by reading many dimensions after writing styles.

---

## 4. 3D mascot implementation options

### Preferred option: transparent 3D/WebGL character

Use a transparent canvas with:

- A lightweight GLB/GLTF mascot.
- Pre-baked or simple idle animation.
- Transparent background.
- Low-poly or optimized materials.
- Soft studio lighting.
- Limited particle/glitter accents.

The mascot should look friendly and premium, not like a generic game avatar.

### Fallback option: pre-rendered transparent image sequence

If a real-time 3D model is too heavy:

- Use a short transparent PNG/WebP sequence or video.
- Map the sequence to scroll progress.
- Use a static poster for reduced motion/mobile.

### Current remote gap

The audited remote chatbot uses a regular image avatar and does not contain a verified 3D character model or scroll-driven render pipeline.

---

## 5. Glitter and background treatment

The mascot scene should use the planned elegant glitter background, not a noisy particle field.

### Background layers

1. Deep charcoal/plum base.
2. Soft champagne radial glow.
3. Very low-opacity grain.
4. Sparse floating glitter particles.
5. Rare soft jewellery-like glints.

### During mascot entrance

- Glitter density can rise slightly around the mascot.
- A soft champagne halo can follow the mascot.
- A few particles can drift upward.
- No screen-wide flash.
- No glitter over faces or text.
- No glitter in form fields or dense catalogue content.

### Mobile

- Reduce particle count significantly.
- Prefer CSS ambient glow over a full WebGL particle field.
- Keep the mascot readable and small.
- Disable the effect on low-power devices if necessary.

---

## 6. Navigation audit

### Current risk

The remote header uses Headroom-style classes:

```text
headroom--pinned
headroom--unpinned
headroom--top
```

It also contains a hide-on-scroll behavior. This can cause the navigation bar to disappear while the visitor is scrolling, which conflicts with the reported requirement that the navigation should remain available.

### Required behavior

On mobile:

- Navigation must remain visible or reappear quickly after a small scroll reversal.
- It must not disappear while the mascot animation is running.
- It must not be covered by the mascot or chat panel.
- It must respect safe-area insets.
- It must not cause horizontal overflow.
- The menu button must remain reachable.

Recommended mobile behavior:

```css
@media (max-width: 760px) {
  nav#mnav {
    position: fixed;
    top: 0;
    transform: translateY(0) !important;
  }
}
```

If hide-on-scroll is retained on desktop, disable it on mobile or use only a very small compact transition.

Recommended safer rule:

- Desktop: allow subtle hide/reveal only after the hero.
- Mobile: keep navigation pinned.
- During modal/chat/mascot transitions: keep navigation pinned.

### Navigation content

The current header still contains legacy homepage-anchor links such as:

```text
/#services
/#packages
/#gallery
```

These should use:

```text
/services/
/packages/
/gallery/
```

unless the link intentionally targets a section that genuinely exists on the homepage.

---

## 7. Mobile audit findings

### A. Mascot positioning

Risk:

- Mascot can overlap the bottom mobile bar.
- Mascot can overlap the navigation.
- Mascot can cover WhatsApp or cart actions.
- Mascot can cause horizontal overflow.

Required:

```css
.mascot-dock {
  right: max(16px, env(safe-area-inset-right));
  bottom: calc(78px + env(safe-area-inset-bottom));
}
```

The bottom position must account for the existing mobile navigation bar.

### B. Chat panel

The chat panel must:

- Fit within the viewport width.
- Respect safe-area insets.
- Avoid being taller than the usable viewport.
- Keep the input above the mobile keyboard.
- Avoid nested scroll confusion.
- Provide a large close button.
- Avoid blocking the entire navigation unless intentionally maximized.

### C. Header

The navigation bar must:

- Stay visible on mobile.
- Have a clear stacking order above the background canvas.
- Have a clear stacking order below/above the chatbot according to the intended interaction.
- Never disappear permanently after a downward scroll.

### D. Hero and scroll scene

The hero must not lock the page into an animation stage that prevents natural scrolling. If a pinned scene is used:

- It must have a bounded height.
- It must release into normal content.
- It must fall back to a stacked hero on mobile.
- It must be disabled or simplified under reduced motion.

### E. Touch interactions

- Buttons should be at least approximately 44px high.
- Swiping the gallery must not accidentally scroll the entire page sideways.
- Mascot tap target must be obvious.
- Chat controls must not rely on hover.

---

## 8. Mobile breakpoint plan

### Large desktop: 1200px and above

- Full 3D mascot entrance.
- Richest glitter/background treatment.
- Hero scene may use layered depth.
- Header can use compact editorial transitions.

### Tablet: 768–1199px

- Reduce mascot scale and particle count.
- Simplify hero depth.
- Keep navigation pinned when necessary.
- Use two-column service/gallery layouts where space allows.

### Mobile: below 768px

- Use lightweight mascot renderer or poster/sequence fallback.
- Pin navigation.
- Remove heavy pinned scenes.
- Stack hero content.
- Keep glitter sparse.
- Keep mascot dock above bottom navigation.
- Keep chat panel within viewport.
- Preserve native vertical scrolling.

### Small mobile: below 390px

- Reduce decorative elements further.
- Hide nonessential nav labels while retaining accessible labels.
- Ensure the mascot does not cover the primary CTA.
- Use a compact greeting bubble.
- Test on 320px–390px widths.

---

## 9. Reduced-motion behavior

When `prefers-reduced-motion: reduce` is active:

- Do not animate the mascot through the full scroll scene.
- Show the mascot as a static small docked assistant or static hero illustration.
- Do not move particles.
- Remove parallax.
- Do not hide the navigation.
- Use immediate/short fades only.
- Keep the greeting visible and accessible.
- Keep the chatbot fully usable.

---

## 10. Gap table

| Planned behavior | Current remote state | Gap | Priority |
|---|---|---|---|
| Hidden AI character initially | Conventional fixed chat bubble | 3D scene state missing | Critical |
| Character enters on scroll | No scroll-driven mascot animation | Full choreography missing | Critical |
| Character scales down | No mascot scaling transition | Dock transition missing | Critical |
| Character becomes chatbot | Chatbot exists independently | Mascot/chat integration missing | Critical |
| Greeting after dock | Long chatbot intro exists | Add short docked greeting state | High |
| Smooth 3D movement | Standard CSS chat panel animation | WebGL/sequence/scroll interpolation missing | Critical |
| Native scroll retained | Some Headroom/scroll behavior exists | Need verify no scroll hijack | Critical |
| Mobile nav stays available | Headroom can unpin/hide nav | Mobile pinned-nav rule required | Critical |
| Mobile chat fits viewport | Existing chat CSS needs browser test | Keyboard/safe-area testing missing | High |
| Glitter atmosphere | Some background/canvas infrastructure exists | Mascot-linked glitter scene missing | High |
| Reduced motion | Some CSS support exists | Mascot fallback not implemented | High |
| Browser validation | E2E previously unavailable | Install/run Chromium | Critical |

---

## 11. Recommended implementation sequence

1. Create a dedicated `mascot-scene` component and state machine.
2. Add an optimized transparent mascot asset or approved fallback.
3. Implement hidden → entering → docked states.
4. Drive the state with passive, rAF-throttled scroll progress.
5. Keep native scroll untouched.
6. Add the docked greeting: “How may I help you today?”
7. Connect docked mascot click to the existing chatbot panel.
8. Keep the navigation pinned on mobile.
9. Add safe-area and z-index rules.
10. Add glitter only to the hero/mascot scene.
11. Add reduced-motion fallback.
12. Test image/video/gallery interactions after the mascot work.
13. Run browser tests at 320px, 375px, 768px, and desktop widths.
14. Run the full Django test suite.
15. Update the PR only after the working tree and remote branch are synchronized.

---

## 12. Definition of done

The requested mascot/scroll experience is complete only when:

- [ ] The 3D character is hidden initially.
- [ ] The character enters smoothly as the user scrolls.
- [ ] The character scales down during the transition.
- [ ] The character docks into the chatbot position.
- [ ] The docked greeting says “How may I help you today?” or an approved equivalent.
- [ ] Clicking the mascot opens the concierge panel.
- [ ] Native scroll remains natural.
- [ ] The page does not use wheel/touch `preventDefault()` for the animation.
- [ ] The navigation remains visible and usable on mobile.
- [ ] The mascot does not overlap the mobile bottom bar or important buttons.
- [ ] The glitter background is subtle, warm, and performant.
- [ ] Reduced-motion users receive a complete static alternative.
- [ ] The experience works on desktop, tablet, and small mobile widths.
- [ ] Browser tests confirm no console errors, overflow, stuck navigation, or broken chatbot state.
