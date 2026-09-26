# Anshita Makeover Repository Audit

**Audit date:** 2026-09-25  
**Branch:** `arena/01a0d489-anshitamakeover`  
**Scope:** Django public site, admin portal, AI chatbot/copilot, testing hub, CI, and animation architecture.  
**Method:** command output, failing tests, and source line citations only. No application fixes were made during this audit.

## Executive summary

- **Overall: D (not production-ready)** — public pages and smoke/performance probes work, but the canonical seed command aborts and the full test program is red.
- **Security: D** — hardcoded `SECRET_KEY`, `DEBUG=True`, wildcard hosts, permissive iframe policy, and disabled password validators are evidenced in settings.
- **Correctness: D** — 228-test unit run reports 13 failures and 84 errors; API run reports 8 failures and 8 setup errors; the seed failure is a schema/factory mismatch.
- **Operations/CI: C-** — CI provisions Playwright and Java/Maven, but the master runner's baseline prep failure prevents meaningful downstream validation.
- **UX/animation: C** — the site has a substantial animation stack, but three render-blocking CDN scripts and many simultaneous motion systems require a measured redesign before adding Evagher-style transitions.

## Phase 1 ground truth

### Commands and results

`python testing/run_all.py`:

```text
No Python with Django found — bootstrapping testenv/ …
testenv ready.
... database prep ...
 django.core.exceptions.FieldError: Invalid field name(s) for model MakeupPackage: 'price_label'.
prep FAILED — aborting
```

Evidence:

- `testing/testdata/factories.py:214-216` seeds `price_label`.
- `testing/testdata/factories.py:228-230` passes the row as `update_or_create(... defaults=defaults)`.
- `django/core/models.py:146-160` defines no database field named `price_label`.
- `django/core/models.py:168-172` defines `price_label` only as a property.
- `django/core/migrations/0011_remove_makeuppackage_price_label_and_more.py:12-25` explicitly removes the field and adds `display_label`.

`python testing/run_all.py --skip-prep`:

```text
unit: FAIL
api: FAIL
e2e: SKIP (install browsers: ... playwright install --with-deps chromium)
bdd: SKIP (needs Java 11+ & Maven — runs in CI)
smoke: PASS
perf: PASS
```

Measured metrics from that run:

- Unit: **228 tests**, reported **13 failures + 84 errors**, coverage **45%** (`2031` statements, `1113` missed).
- API: **28 collected**, **12 passed, 8 failed, 8 errors**.
- Smoke: **PASS**, all probes passed.
- Performance: **PASS**, 120 requests, 173 req/s, p50 52 ms, p95 90 ms, 0 errors.
- E2E: skipped because Chromium was not installed in the local environment.
- BDD: skipped because Java/Maven were unavailable in the local environment.

### Manual HTTP baseline

After `migrate --no-input` and starting `runserver 0.0.0.0:8123`:

```text
/                          200 text/html
/academy/                  200 text/html
/chatbot/                  200 text/html
/travel-estimator/         200 text/html
/admin/                    200 text/html
/admin-login/              200 text/html
/api/coupon/               200 application/json
/static/core/css/...       200 text/css
/media/                    404
```

`/admin/` returning 200 is expected from the explicit redirect in `django/anshita_project/urls.py:9`; `/media/` 404 is consistent with no media index resource, not proof that individual media files fail.

## Findings register

| ID | Severity | Dimension | Evidence | Reproduction | Small fix | Regression test |
|---|---|---|---|---|---|---|
| AUD-001 | 🔴 Critical | Test/data correctness | `factories.py:214-216,228-230`; `models.py:146-172`; migration `0011...:12-25` | `python testing/run_all.py` | Replace seed `price_label` writes with `display_label`/`price`; regenerate fixture and verify idempotence | Seed command test: two consecutive runs complete and counts remain stable |
| AUD-002 | 🔴 Critical | Production security | `settings.py:6-8` | Inspect settings or run deployment check | Load `SECRET_KEY`, `DEBUG`, and hosts from environment; fail closed in production | `manage.py check --deploy` plus settings security test |
| AUD-003 | 🟠 High | API contract/auth UX | `common.py:17-21`; API output: anonymous admin calls return `401`; existing tests expect `302` | `python testing/run_all.py --skip-prep` | Decide one contract; preferably return JSON 401 for API and update tests/clients, or preserve redirect consistently | Anonymous and non-staff matrix test for every admin endpoint |
| AUD-004 | 🟠 High | AI copilot correctness | `chatbot.py:474-477`, `493-510`, `513-522` write/read `price_label` on `MakeupPackage`, but model exposes it only as a property | Trigger `update_package` or `modify_booking_offers` with Gemini action | Use `price` plus `display_label`; never assign computed property | AI copilot package CRUD test after seeding |
| AUD-005 | 🟠 High | Unit baseline | Unit output: 13 failures, 84 errors; first common error is AUD-001 | `python testing/run_all.py --skip-prep` | Fix seed/schema drift before interpreting secondary failures | Full unit suite green |
| AUD-006 | 🟠 High | Coupon correctness | Unit output: expected `GLAMOUR30/GLAM50/ANSHITA10`, received `NAVRATRI15`; `common.py:28-41` gives seasonal month precedence over day logic | Run coupon tests | Make date-rotation contract explicit and test seasonal mode separately, or update expected contract | `test_coupons.py` day/month tests |
| AUD-007 | 🟠 High | AI history correctness | Unit output: expected compressed history but raw history reached Gemini; `chatbot.py:270-271` sends result of `headroom_compress_history` | Run `TC-CHT-026` | Fix compressor contract/patch target and assert compressed turns are used | Existing `TC-CHT-026` |
| AUD-008 | 🟠 High | Secrets/configuration | `settings.py:91-92` permits `django/gemini_api_key.txt`; `settings.py:6` hardcodes key material-like secret; grep found Gemini integration | Scan repo and deployment settings | Keep only environment/secret-manager values; ignore local key file; rotate any exposed credential | Secret scanning CI + configuration test |
| AUD-009 | 🟠 High | Clickjacking/security headers | `settings.py:10-12` sets `X_FRAME_OPTIONS='ALLOWALL'` | Inspect response headers | Restrict framing to trusted preview origins or remove in production | Security header test in production settings |
| AUD-010 | 🟡 Medium | CSRF policy | `chatbot.py:71-72` exempts public chatbot POST; `public.py:58-59` exempts language endpoint; multiple admin APIs use `@csrf_exempt` (`grep` evidence) | POST without CSRF token | Keep exemption only for intentionally stateless public endpoint with origin/rate limits; use CSRF tokens for authenticated admin mutations | CSRF matrix tests |
| AUD-011 | 🟡 Medium | Upload validation | `models.py:258-259,539-540` accept `FileField`; `media.py:134-145` proceeds from request metadata; no MIME/size validation is visible in cited upload path | Submit arbitrary file under image/video action | Validate MIME, extension, size, image decode, and store outside executable/static paths | Upload tests for invalid type, oversized file, and valid image |
| AUD-012 | 🟡 Medium | AI execution safety | `chatbot.py:456-480` executes model-produced JSON actions; `chatbot.py:635-636` returns raw exception text; no approval/dry-run step is visible | Staff submits prompt causing action JSON | Add allowlisted schema validation, audit log, preview/confirmation, and generic errors; bound numeric fields server-side | Copilot prompt-injection and approval tests |
| AUD-013 | 🟡 Medium | AI external-call resilience | `chatbot.py:293-308` makes multiple Gemini requests with 15-second timeouts; `chatbot.py:446` uses 12 seconds for copilot; no retry budget/circuit breaker is visible | Gemini slow/error path | Add total request deadline, bounded retry/backoff, provider error mapping, and rate limits | Mock timeout/500 test with elapsed-time bound |
| AUD-014 | 🟡 Medium | Frontend performance | `base.html:9-11` loads Three.js, GSAP, and Headroom synchronously in `<head>` without `defer`/`async` | View source/network waterfall | Use `defer`, self-host/pin with SRI where appropriate, and lazy-load decorative WebGL after first content paint | Lighthouse budget and template assertion |
| AUD-015 | 🟡 Medium | Animation UX | Evidence: `base.html:155-156`, preloader/curtain block around `base.html:230+`, Three.js loop around `base.html:5393+`, hero slider `home.html:780+`, plus scroll skew selectors in base CSS | Load home on mobile/reduced-motion and scroll rapidly | Consolidate to one scroll timeline, remove scroll hijacking, add `prefers-reduced-motion`, and provide preloader skip/failsafe | Playwright 360px + reduced-motion test |
| AUD-016 | 🔵 Low | Dead/shadow code | `django/core/views_monolithic_backup.py` contains duplicate legacy view implementations and is not imported by `django/core/urls.py` or `views/__init__.py` | `grep` route imports; file contains old decorators/routes | Archive outside runtime or delete after dependency verification | Import graph check and repository clean-up review |
| AUD-017 | 🔵 Low | Test/plan drift | `docs/testing/REGRESSION_TEST_PLAN.md` says branch `arena/01a0b103-anshitamakeover` and 228 unit tests; current branch is `arena/01a0d489-anshitamakeover`; catalog lists KD-001–KD-004 as known defects while its header and implementation claims overlap | Compare `git branch --show-current` and plan header | Update document metadata and reconcile fixed/open defects | Documentation consistency check |

## Security review summary

### Admin protection

`admin_required` permits either authenticated staff or `request.session['artist_verified']` (`django/core/views/common.py:8-21`). The custom portal itself checks staff only (`django/core/views/auth.py:42-47`). Admin API behavior is therefore broader than portal behavior and depends on the artist session flag; this requires an explicit threat model and tests for session fixation/verification lifecycle.

### CSRF

CSRF middleware is installed (`settings.py:25-33`), but public chatbot and language endpoints are explicitly exempt. Admin APIs also contain several `@csrf_exempt` decorators according to repository grep output. The audit found no evidence that all such exemptions are justified by a stateless authentication design.

### Injection and unsafe rendering

`base.html:6798` uses `|safe` for server-provided `look_groups_json`; this is an injection review point. Admin AI also converts model output directly into database actions. No raw SQL usage was found in the initial grep, but AI action validation needs defense-in-depth.

### Sessions/passwords

`settings.py:67` sets `AUTH_PASSWORD_VALIDATORS = []`. Secure cookie flags are not explicitly configured in settings. These must be added for production deployment behind HTTPS.

## Phase 4 coverage and test quality

Coverage baseline from unit run: **45% overall**.

Important low-covered files from the measured report:

1. `django/core/models.py` — 16%
2. `django/features/auth_ops/auth_service.py` — 39%
3. `django/core/views/media.py` — 36%
4. `django/features/public_ops/public_service.py` — 42%
5. `django/core/views/services_pricing.py` — 46%
6. `django/features/artist_ops/artist_service.py` — 63%
7. `django/core/views/public.py` — 61%
8. `django/core/views/reviews.py` — 64%
9. `django/core/views/chatbot.py` — 55%
10. `django/core/views/artists.py` — 55%

Existing catalog evidence says some business paths have tests, but they cannot be trusted as a green baseline until AUD-001 is fixed. Critical additional tests should cover upload validation, AI approval/prompt injection, exact admin session authorization, security settings, and reduced-motion/browser behavior.

## CI review

`.github/workflows/regression.yml` provisions:

- Python 3.11.
- Django, Pillow, requests, dotenv.
- pytest and pytest-html for API.
- pytest-playwright plus Chromium and system dependencies for E2E.
- Temurin Java 17 with Maven cache for BDD.

The local runner is designed to skip E2E when Chromium is unavailable and BDD when Java/Maven are unavailable (`testing/run_all.py` runtime detection). CI supplies those dependencies, but CI still invokes the same database prep and therefore will fail at AUD-001 before meaningful suites can establish a green baseline.

## Known-issue register reconciliation

The repository register in `docs/testing/REGRESSION_TEST_PLAN.md` lists:

- **KD-001:** event-package form POST defect — still listed as locked/open; audit did not change it.
- **KD-002:** AI copilot photo service naming no-op — still listed as locked/open; audit did not change it.
- **KD-003:** `admin_ai_command` not wired — appears stale/inconsistent because `django/core/urls.py` currently wires both `/api/admin/ai/` and `/api/admin/ai-command/` to the view. The register should be updated and a regression test should confirm both routes.
- **KD-004:** hardcoded `SECRET_KEY`/`DEBUG=True` — confirmed open by `settings.py:6-8`.
- **KD-005–KD-007:** marked fixed in the register; the current API contract mismatch in AUD-003 shows their redirect assumptions need revalidation, even though staff gating exists.

## Prioritized remediation backlog

### P0 — Critical

1. **Repair seed/schema contract — M**
   - Acceptance: `migrate`, `seed_test_data`, and a second idempotent seed all pass; `python testing/run_all.py` reaches every suite.
2. **Production configuration hardening — M**
   - Acceptance: no repository secret, `DEBUG=False` in production, explicit allowed hosts, secure cookies, password validators, deployment checks pass.
3. **AI copilot safe execution — L**
   - Acceptance: schema allowlist, field-level bounds, approval preview, audit log, generic errors, prompt-injection tests, and no computed-property writes.

### P1 — High

4. **Reconcile API auth contract — S**
   - Acceptance: anonymous/non-staff/staff matrix is documented and green for every `/api/admin/*` route.
5. **Fix chatbot history compression — S/M**
   - Acceptance: compressed history reaches provider and fallback behavior remains green.
6. **Resolve coupon semantics — S**
   - Acceptance: seasonal and day-based rotation have separate explicit tests and UI labels.
7. **Harden uploads — M**
   - Acceptance: MIME/decode/size validation, safe file names, invalid upload tests, and no executable media path.

### P2 — Medium

8. **External provider resilience — M**
   - Acceptance: bounded total latency, retries/circuit breaker, rate limiting, and provider-neutral errors.
9. **Static asset performance — M**
   - Acceptance: deferred/pinned third-party scripts, lazy WebGL, image dimensions/WebP, Lighthouse budgets.
10. **Admin content architecture — L**
    - Acceptance: all public claims, services, pricing, look groups, content blocks, animation toggles, and social links are controlled through validated admin fields, not inline template constants.

### P3 — UX/animation redesign

11. **Evagher-inspired scroll system — L**
    - Acceptance: section transitions use one coordinated timeline; no scroll hijacking; keyboard/touch work; reduced-motion fallback; mobile maintains 60fps target where measurable.
12. **Service discovery redesign — M**
    - Acceptance: each service has finish, ceremony, duration, starting price, inclusions, location/travel info, and one clear availability CTA.

Recommended animation direction: retain the luxury editorial tone but use fewer effects—one pinned scene with image displacement/mask reveal, a restrained gold particle layer, and sequential section reveal. Avoid stacking preloader + cursor + skew + slider + particle + multiple scroll transforms on every card.

## Audit artifact status

- `docs/AUDIT_REPORT.md`: this report.
- `testing/reports/`: generated baseline reports from the executed test runs.
- No application fixes were made during this audit phase.
- The pre-existing `WEBSITE_AUDIT_AND_RECOMMENDATIONS.md` and base-template motion accessibility changes remain separate from this audit report and should not be treated as fixes for the findings above.
