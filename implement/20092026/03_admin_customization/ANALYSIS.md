# Analysis 03 — Admin Customization

**Status:** PENDING IMPLEMENTATION
**Branch:** 20092026
**Priority:** HIGH

---

## 1. Problem Statement

The user requested: *"We should have option to customize all values and details from admin section."*

While the Admin Portal panel (floating sidebar in `home.html`) already covers coupons, booking offers, AI settings, and media — several important areas are NOT yet editable from the frontend admin UI and require either a Django admin login or direct code changes.

---

## 2. Current Admin Coverage Audit

### Covered in Frontend Admin Panel (✅ already working)

| Setting | Admin Tab | DB Field |
|---------|-----------|----------|
| Coupon code + % | Coupon tab | `SiteSettings.coupon_code/discount_percent` |
| Auto date coupon | Coupon tab | `SiteSettings.coupon_auto_by_date` |
| Exit/secret coupon | Coupon tab | `SiteSettings.exit_coupon_*` |
| Free side makeups | Booking Offers | `SiteSettings.offer_bridal_free_sides` |
| Side makeup discounted rate | Booking Offers | `SiteSettings.offer_next_sides_discounted_price` |
| Combo discount % | Booking Offers | `SiteSettings.offer_combo_discount_percent` |
| Grand bundle flat price | Booking Offers | `SiteSettings.offer_grand_combo_bundle_price` |
| AI negotiation toggle | AI Copilot | `SiteSettings.ai_negotiation_enabled` |
| AI max discount % | AI Copilot | `SiteSettings.ai_max_discount_percent` |
| AI strategy | AI Copilot | `SiteSettings.ai_negotiation_strategy` |
| AI instructions | AI Copilot | `SiteSettings.ai_negotiation_instructions` |
| Package price edit | Studio Services tab | Via `update_price` API |
| Media embeds | Media & Reels tab | Via `add_media` API |
| Reviews | Reviews tab | (check implementation) |

### NOT Covered — Missing from Frontend Admin (gaps)

| Missing Setting | Current Method | Impact |
|----------------|---------------|--------|
| Package `display_label` | Only via Django /admin/ | Blocks 02_package_ux |
| Package `tagline` edit | Only via Django /admin/ | Can't update card copy from panel |
| Package `features` text edit | Only via Django /admin/ | Dense text blob, no UI |
| Package `is_featured` toggle | Only via Django /admin/ | Can't promote packages from panel |
| Travel widget on/off | Only via Django /admin/ | Needs a toggle in Travel tab |
| Travel zone labels & fees | Stored in `SiteSettings` | Travel tab exists but may not save |
| WhatsApp number | Only via Django /admin/ | Critical — no frontend edit |
| Instagram URL | Only via Django /admin/ | No frontend edit |
| VIP coupon generation | Partial (AI Copilot tab) | Check if VIP code generator works |
| Auto-coupon badge text | Only via Django /admin/ | Banner text not changeable from panel |
| StudioService individual prices | Via `update_price` action | Verify all service slugs are mapped |

---

## 3. Gap Analysis by Admin Tab

### Tab: Coupon
- **Missing:** WhatsApp number edit, banner badge text edit
- **Add:** `whatsapp_number` input field, `default_auto_coupon_badge` textarea

### Tab: Studio Services
- **Missing:** Package tagline edit, features edit, display label, is_featured toggle
- **Add:** An expandable package editor per package with all editable fields

### Tab: Travel
- **Verify:** Does the "Save Travel Settings" button actually persist to DB?
- **Add if missing:** Toggle for `travel_widget_active`, all zone label/fee fields

### Tab: AI Copilot
- **Missing:** AI model selector (flash vs pro), thinking budget toggle
- **Add:** Dropdown for `GEMINI_MODEL`, checkbox for thinking budget

### New Tab: Site Info
- **Add new tab** for: studio name, WhatsApp, Instagram URL, footer text

---

## 4. Backend API Gaps

The frontend admin panel sends commands to `/api/admin/ai-command/` (natural language → AI-parsed JSON action). This covers packages and coupons. Missing direct REST endpoints:

| Endpoint Needed | Purpose |
|----------------|---------|
| `POST /api/admin/site-settings/` | Save WhatsApp, Instagram, travel fields directly |
| `POST /api/admin/package/<id>/edit/` | Edit tagline/features/display_label directly without AI parsing |
| `GET /api/admin/status/` | Return Gemini live/fallback status |

---

## 5. Security Consideration

All admin API endpoints must be protected with `@login_required` decorator. Verify every `/api/admin/*` view has this. Cross-reference with Security Audit (folder 04).

---

## 6. Files to Modify

| File | Change |
|------|--------|
| `django/core/templates/core/home.html` | Add new Site Info tab; extend Coupon/Travel/Services tabs with missing fields |
| `django/core/views/services_pricing.py` | Add `save_site_settings` view for direct (non-AI) field saves |
| `django/core/views/__init__.py` | Register new views |
| `django/core/urls.py` | Add URL patterns for new endpoints |
| `django/core/models.py` | Add `display_label` to `MakeupPackage` (shared with task 02) |

---

## 7. Implementation Checklist

- [ ] Audit every `SiteSettings` field — confirm which are reachable from frontend panel
- [ ] Audit every `MakeupPackage` field — confirm which are reachable
- [ ] Add "Site Info" admin tab with WhatsApp, Instagram, badge text fields
- [ ] Add direct package editor section in "Studio Services" tab
- [ ] Verify "Travel" tab save functionality end-to-end
- [ ] Create `POST /api/admin/site-settings/` endpoint (direct field save, no AI)
- [ ] Create `POST /api/admin/package/<id>/edit/` endpoint
- [ ] Add `GET /api/admin/ai-status/` endpoint
- [ ] Add Gemini model selector in AI Copilot tab
- [ ] Run through all tabs after changes and verify saves persist on page reload
