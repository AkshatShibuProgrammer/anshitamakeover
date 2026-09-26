# Phase 1 Implementation — Baseline Recovery

## Completed

- Repaired regression seed data to use `display_label` instead of the removed `MakeupPackage.price_label` database field.
- Added a backward-compatible `price_label` property setter that maps legacy form/factory writes to `display_label`.
- Updated AI copilot and admin service pricing paths to write valid `MakeupPackage` fields.
- Standardized protected-route behavior to the existing regression contract: redirect to branded admin login.
- Unified coupon auto-rotation between `core.views.common` and `features.coupon_ops` using day-of-month rotation.
- Restored chatbot token cap to 640 and preserved negotiation guardrail wording.
- Enabled Headroom compression when available, while retaining raw-history fallback.
- Aligned seeded bridal negotiation floor with the existing API contract.

## Validation

Command:

```bash
python testing/run_all.py
```

Result:

```text
unit PASS — 228 tests
api PASS — 28 tests
smoke PASS
perf PASS — 120 requests, p95 594 ms, 0 errors
e2e SKIP — Chromium unavailable locally
bdd SKIP — Java/Maven unavailable locally
coverage 67%
```

The full executed baseline is green. E2E and BDD remain environment skips, not application failures.

## Next phase

Phase 2: album/media model and viewer foundation. Before that phase, install Chromium and Java/Maven in CI/local where possible so browser and BDD validation can be added to the checkpoint.
