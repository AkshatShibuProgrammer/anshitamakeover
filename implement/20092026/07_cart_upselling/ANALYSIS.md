# Analysis 07 — Cart Upselling Suggestions

**Status:** PENDING IMPLEMENTATION
**Branch:** 20092026
**Priority:** MEDIUM

---

## 1. Problem Statement

The user said: *"In cart we can see suggestion to add other makeup at discount price."*
Also: *"Don't put too much detail of wedding production — just mention that in package we can put this add-on."*

When a user adds a service to the cart (e.g. Bridal Makeup), the cart panel should suggest complementary services at a special bundled/discounted rate — similar to Amazon's "Frequently bought together."

---

## 2. Current Cart State

The "Trousseau Cart" is a floating panel rendered in `home.html`. It:
- Shows selected services (name, price)
- Has a total amount
- Has a WhatsApp checkout button
- Currently: no upsell suggestions at all

The cart is JavaScript-driven (client-side only, no cart model in DB).

---

## 3. Upsell Logic Design

### Trigger Rules

| Item in Cart | Suggest | Discount |
|-------------|---------|----------|
| Any Bridal package | "Add Engagement/Roka Makeup" | 15% off (existing combo discount) |
| Bridal package | "Add Side Makeup for Family" | ₹2,500 each (existing offer rate) |
| Bridal package | "Add Royal Photography Package" | Partner add-on (EventPackage) |
| Engagement only | "Add Bridal to complete your look" | 15% combo |
| Reception / Sangeet | "Add Hair Styling upgrade" | 10% off |
| Party Glam | "Add Nails & Extensions" | 10% off |
| Academy course | "Enroll a friend — refer & save" | Referral note |

### Display Location

In the cart panel sidebar, below the items list and above the total:
```
─────────────────────────────────
✦ COMPLETE YOUR BRIDAL JOURNEY
─────────────────────────────────
+ Engagement & Roka Makeup
  Usually ₹18,000 → Add for ₹15,300 (15% combo off)
  [Add to Cart]

+ Side Makeup (per person)
  Special rate: ₹2,500 each
  [Add to Cart]

+ Royal Photography (Partner Add-on)
  Starting ₹68,000 — enquire via WhatsApp
  [Enquire]
─────────────────────────────────
```

---

## 4. Data Source for Suggestions

Suggestions are generated client-side from:
1. **Current cart contents** — check which `package_type` is in cart
2. **Pre-loaded package data** — embedded as JSON in page (same JSON block used for Quick-View modal from task 02)
3. **SiteSettings** — combo discount %, discounted side price (already in page context)

No additional API calls needed. All data is already on the page.

---

## 5. Wedding Production / Event Add-ons

User specified these should NOT appear in the main packages grid, only as cart suggestions.

`EventPackage` model exists for photography, decor, etc. These should appear:
- As suggestion cards in the cart with "Enquire via WhatsApp" CTA (not "Add to Cart" since these are partner services)
- With a short 1-line description only (not full feature list)
- Badge: "Partner Service — Curated by Anshita"

---

## 6. Upsell Card Design

```
.upsell-card {
  background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(212,175,55,0.03));
  border: 1px solid rgba(212,175,55,0.2);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.upsell-card .upsell-name { font-size: 13px; font-weight: 600; color: var(--gold); }
.upsell-card .upsell-price { font-size: 11px; color: rgba(245,237,214,.7); }
.upsell-card .upsell-add-btn { font-size: 11px; padding: 4px 10px; }
```

---

## 7. Trousseau Cart Button Size Fix (Related UI Issue)

The user reported: *"Trousseau Cart button is very big."*

Current: The floating cart toggle button likely has excessive padding or fixed width.
Fix: Reduce to a compact icon-button style (icon + count badge only on mobile).

```css
/* Before (assumed large button) */
#cart-toggle { padding: 12px 24px; font-size: 16px; }

/* After (compact) */
#cart-toggle { 
  width: 48px;
  height: 48px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px; /* just the cart icon */
}
/* Badge for item count */
#cart-toggle .cart-count {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--gold);
  color: #000;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

---

## 8. Files to Modify

| File | Change |
|------|--------|
| `django/core/templates/core/home.html` | Add upsell section in cart panel HTML; add JS upsell logic; fix cart button CSS |
| `django/core/views/public.py` | (if needed) expose EventPackage data for partner add-ons |

---

## 9. Implementation Checklist

- [ ] Audit current cart panel HTML structure in `home.html`
- [ ] Fix Trousseau Cart button to compact icon-button style
- [ ] Build `generateUpsells(cartItems)` JS function with rule table
- [ ] Add upsell section HTML to cart panel (below items, above total)
- [ ] Style upsell cards with luxury gold glassmorphism design
- [ ] Test upsell triggers: bridal → suggests engagement; engagement only → suggests bridal
- [ ] Add EventPackage partner add-ons as "Enquire" cards (NOT add-to-cart)
- [ ] Verify EventPackage data is available in page context
- [ ] Test on mobile — upsell cards should not overflow cart panel
- [ ] Verify AI concierge button is visible (not hidden behind cart toggle)
