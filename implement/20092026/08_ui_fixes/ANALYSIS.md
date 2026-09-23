# Analysis 08 — UI Fixes

**Status:** PENDING IMPLEMENTATION
**Branch:** 20092026
**Priority:** LOW

---

## 1. Problem Statement

Multiple small UI issues reported during the review session:
1. *"Trousseau Cart button is very big"* — oversized floating cart toggle
2. *"I can't see AI button as well"* — AI concierge chat button not visible
3. *"Current reception makeup looks good for side makeup"* — potential image placement issue
4. General pricing display verification in Services section

---

## 2. Issue Inventory

### 2.1 Trousseau Cart Button — Too Large

**Expected:** A compact circular floating button with cart icon + count badge
**Likely cause:** Button has explicit large padding or `min-width` set
**Selector to find:** `#cart-toggle`, `.cart-btn`, `.trousseau-btn`, or similar

**Fix approach:**
- Reduce to 48×48px circular icon button
- Show only bag icon (🛍 or SVG) + count badge
- Detailed analysis and CSS fix are in `07_cart_upselling/ANALYSIS.md` section 7

### 2.2 AI Concierge Button Not Visible

**Expected:** A floating AI chat button (sparkle icon / "AI Concierge" label) visible on every scroll position
**Likely cause:**
- Hidden behind the cart button (z-index conflict)
- Opacity/display set to 0 by a conflicting CSS rule
- Button exists in DOM but its positioning puts it off-screen on certain viewport sizes

**Steps to diagnose:**
1. Open browser DevTools → Elements tab → find `#ai-btn` or `.ai-concierge-btn`
2. Check `display`, `visibility`, `opacity`, `z-index`, `position`, `top`/`bottom`/`right`/`left`
3. Check if cart button covers it: both are likely `position: fixed; bottom: Xpx; right: Xpx`

**Fix approach:**
- Give AI button a higher `z-index` than the cart button
- If they overlap: offset AI button (`bottom: 100px`) vs cart button (`bottom: 40px`)
- Ensure AI button is always rendered (not conditionally hidden)

### 2.3 Service Pricing Display Verification

Previous session fixed the pricing logic. Verify the following display elements are working:
- Original (crossed-out) price shown
- Offer price shown in gold/highlight
- Discount percentage badge (e.g. "26% OFF")
- No "NaN" or "undefined" in price display

**Template location:** `home.html` services section — look for `svc.has_offer`, `svc.offer_price`, `svc.discount_percent`

### 2.4 Reception Image Used for Side Makeup

User noted an image that appears in the wrong section. This is a content/data issue, not a code issue.
**Fix:** Update the relevant `MediaItem` or `GalleryImage` record via Django admin to assign correct `category`.
No code change needed — pure admin action.

---

## 3. Z-Index Audit for Floating Elements

The site likely has multiple `position: fixed` elements competing for space:

| Element | Expected Z-Index | Expected Position |
|---------|-----------------|------------------|
| Admin panel overlay | 10000 | Fullscreen |
| Modal overlays | 9999 | Fullscreen |
| Curtain panels | 9998 | Fullscreen |
| Nav bar | 1000 | Top |
| AI Concierge button | 500 | Bottom-right |
| Cart button | 499 | Bottom-right (offset from AI) |
| WhatsApp button | 498 | Bottom-left or bottom-right (different side) |
| Cookie/coupon banner | 100 | Bottom |

**Rule:** WhatsApp button should be on bottom-LEFT; AI + Cart on bottom-RIGHT, stacked vertically.

---

## 4. Mobile Responsiveness Quick Audit

Issues to check on mobile (375px viewport):
- [ ] Nav hamburger menu opens correctly
- [ ] Service cards stack to single column
- [ ] Cart panel is full-width and scrollable
- [ ] AI concierge chat window doesn't overflow screen
- [ ] Gallery modal fills screen properly
- [ ] Package Quick-View modal (task 02) scrolls correctly on iOS Safari

---

## 5. Light Theme Verification

Previous session added light theme CSS to `base.html`. Verify:
- [ ] All nav elements readable in light theme
- [ ] Price text visible (gold on white = poor contrast → use dark text in light mode)
- [ ] Form inputs have correct border/background in light theme
- [ ] Theme toggle button is accessible

---

## 6. Files to Modify

| File | Change |
|------|--------|
| `django/core/templates/core/base.html` | Fix z-index stack for floating buttons; fix AI button visibility |
| `django/core/templates/core/home.html` | Fix cart button sizing; verify pricing display |
| Django admin (runtime) | Reassign reception image to correct category (no code change) |

---

## 7. Implementation Checklist

- [ ] Locate AI concierge button selector in `home.html` / `base.html`
- [ ] Diagnose why AI button is not visible (z-index, opacity, positioning)
- [ ] Fix AI button: ensure it is always on top with correct position
- [ ] Audit cart button size — reduce to 48×48px circle
- [ ] Establish z-index hierarchy for all floating elements
- [ ] Verify WhatsApp button does not overlap with AI/Cart buttons
- [ ] Verify service pricing display: offer price, strikethrough, % badge
- [ ] Fix reception image category via Django admin
- [ ] Run mobile viewport test at 375px and 414px widths
- [ ] Verify light theme contrast for price text and buttons
