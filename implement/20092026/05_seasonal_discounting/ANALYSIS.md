# Analysis 05 — Indian Calendar Seasonal Discounting

**Status:** PENDING IMPLEMENTATION
**Branch:** 20092026
**Priority:** MEDIUM

---

## 1. Problem Statement

The user asked: *"Check the Indian calendar and see which months we have weddings and makeup — and which have the least. For the least-demand month we will generate the coupon for more discount."*

This requires mapping Indian wedding seasonality, identifying slow months, and creating an automated or semi-automated coupon generation system that offers deeper discounts in off-peak months to drive bookings.

---

## 2. Indian Wedding Season Analysis

### Peak Wedding / Makeup Demand Months

Based on the Hindu calendar (auspicious muhurtas, festivals, and weather):

| Period | Months | Reason | Demand Level |
|--------|--------|--------|-------------|
| Winter Wedding Season | November – February | Most auspicious muhurtas; cool weather; Diwali season | PEAK |
| Spring Season | March – April | Holi season; Vasant Panchami | HIGH |
| Early Summer | May | Last weddings before heat; school year ends | MODERATE |
| Monsoon (inauspicious) | June – August (Ashadh Maas) | No muhurtas; Chaturmas begins after Devshayani Ekadashi | LOW |
| Pre-Vivah Autumn | Sept (early-bird) | Pre-wedding prep & early bookings for winter | MODERATE |
| Navratri & Karwa Chauth | Oct (early) | High festive demand; Karwa Chauth glow | HIGH |
| Diwali to Dev Uthani | Oct–Nov | Picks up sharply after Dev Uthani Ekadashi | HIGH → PEAK |

### Slow Months (Coupon Opportunity)

| Month | Typical Demand | Suggested Auto-Coupon |
|-------|--------------|----------------------|
| June | Low (Monsoon begins) | MONSOON15 — 15% extra |
| July | Off-Peak (Monsoon) | MONSOON20 — 20% extra |
| August | Pre-Season | GLAM20 — 20% extra |
| September | Pre-Season Early-Bird | ROYAL25 — 25% extra |

### Semi-Peak Months (Moderate discount to fill gaps)

| Month | Demand | Suggested Coupon |
|-------|--------|-----------------|
| March | Moderate | SPRING15 — 15% extra |
| April | Moderate | SPRING15 — 15% extra |
| May | Moderate | SUMMER10 — 10% extra |
| October | Moderate/High | NAVRATRI15 — 15% extra |

---

## 3. Current Coupon System

The existing `SiteSettings` coupon system is date-of-month-based (days 1-10, 11-20, 21-31) rather than calendar-month-based. It does not understand seasonality at all.

**Current logic (SiteSettings):**
- `coupon_auto_by_date` flag
- Codes: GLAMOUR30 (days 1-10), GLAM50 (days 11-20), ANSHITA10 (days 21-31)

This is a flat rotation — unrelated to Indian wedding seasons.

---

## 4. Proposed Solution

### Option A: Hardcoded Season-Month Map (Simple, Recommended)

    9:  ('PITRU25',  25, 'Book Now, Celebrate Later — 25% Advance Offer'),  # Sep
    10: ('NAVRATRI10', 10, 'Navratri Celebration — 10% Festive Offer'),    # Oct
    11: ('SHAADI30', 30, 'Wedding Season is Here — 30% Grand Offer'),       # Nov
    12: ('WINTER30', 30, 'Winter Wedding Season — 30% Bridal Privilege'),   # Dec
}
```

This map drives the auto-coupon without any admin input needed monthly.

### Option B: Admin-Configurable Season Table (Complex, Flexible)

Create a new `SeasonalCoupon` model:
```python
class SeasonalCoupon(models.Model):
    month = models.IntegerField(choices=[(i, calendar.month_name[i]) for i in range(1,13)])
    coupon_code = models.CharField(max_length=50)
    discount_percent = models.IntegerField()
    label = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
```

Admin can override any month's coupon from the Admin Portal or Django admin.

**Recommendation: Start with Option A (hardcoded map) and add Option B admin overrides later.**

---

## 5. Integration with Existing Coupon Logic

The current `get_active_coupon()` function in `common.py` drives the coupon banner. Modify it to:
1. First check `SiteSettings.coupon_auto_by_date` — if True, check seasonal map by current month.
2. If month maps to a high-discount code (20%+), prefer seasonal over date-based.
3. Admin manual override always wins.

---

## 6. VIP Code Generation for Low-Demand Months

Add a "Generate VIP Code" button in the Admin Portal that:
1. Detects current month
2. Looks up seasonal discount rate
3. Generates a unique code like `VIP-SEP-XXXX` using `secrets.token_hex(4).upper()`
4. Saves it to `SiteSettings.vip_generated_codes` (already a JSON list field)
5. Shows it to admin to share on WhatsApp/Instagram

---

## 7. Files to Modify

| File | Change |
|------|--------|
| `django/core/views/common.py` | Update `get_active_coupon()` with seasonal logic |
| `django/core/models.py` | Add `SeasonalCoupon` model (Option B) or `seasonal_coupon_map` JSON field to `SiteSettings` |
| `django/core/templates/core/home.html` | Add "Generate VIP Seasonal Code" button in Admin Coupon tab |
| New: `django/core/season_config.py` | Hardcoded `SEASONAL_COUPON_MAP` constant (Option A) |

---

## 8. Implementation Checklist

- [ ] Create `SEASONAL_COUPON_MAP` dict with all 12 months mapped
- [ ] Update `get_active_coupon()` to use seasonal map by current month (when `coupon_auto_by_date` enabled)
- [ ] Test that banner changes correctly when current month is in a low-demand period
- [ ] Add "Generate VIP Seasonal Code" button in Admin Coupon tab
- [ ] Implement VIP code generator (unique code + save to `vip_generated_codes`)
- [ ] Add display of generated codes in admin panel
- [ ] (Optional Phase 2) Create `SeasonalCoupon` model for admin overrides
- [ ] Update AI concierge to mention seasonal codes naturally in conversation
