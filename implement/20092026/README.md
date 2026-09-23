# Branch 20092026 — Implementation Planning Hub

> **Branch created:** 20 September 2026
> **Scope:** All pending improvements from the September 2026 design & development review session
> **Rule:** This folder is analysis-only. No source code is modified here. Each sub-folder contains a deep-dive `ANALYSIS.md` with current-state findings, proposed approach, file impact list, risks, and a step-by-step implementation checklist.

---

## Folder Map

| # | Folder | Topic | Priority |
|---|--------|--------|----------|
| 01 | `01_ai_concierge_overhaul` | Fix AI using fallback instead of real Gemini | CRITICAL |
| 02 | `02_package_ux_simplification` | Simplify package cards to Quick-View popup | CRITICAL |
| 03 | `03_admin_customization` | All values editable from Admin Portal | HIGH |
| 04 | `04_security_audit` | Veracode-style security audit and hardening | HIGH |
| 05 | `05_seasonal_discounting` | Indian calendar season-aware auto coupons | MEDIUM |
| 06 | `06_animation_overhaul` | Curtain preloader + Evagher-grade animations | MEDIUM |
| 07 | `07_cart_upselling` | Cart upsell suggestions with combo discounts | MEDIUM |
| 08 | `08_ui_fixes` | Button sizing, AI button visibility, misc UX | LOW |

---

## How To Use This Hub

1. Read the `ANALYSIS.md` in each folder before implementing anything.
2. Each analysis ends with a **Checklist** — tick items as you implement them.
3. After all checklist items in a folder are done, move the folder to `implement/phase_N_name/` (matching the existing phase naming convention).
4. Raise a PR from branch `20092026` to `main` once all 8 areas are complete.

---

## Dependency Order

```
[04] Security Audit   --> must be done before any API changes
[01] AI Overhaul      --> depends on API key being correctly configured
[05] Seasonal Coupons --> depends on [03] Admin Customization
[02] Package UX       --> depends on [03] Admin Customization
[07] Cart Upselling   --> depends on [02] Package UX
[08] UI Fixes         --> independent, can run in parallel
[06] Animations       --> independent, can run in parallel
```
