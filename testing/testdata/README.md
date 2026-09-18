# 📦 Test Data

Canonical, deterministic dataset shared by **every** suite in `testing/`.

| File | Purpose |
|---|---|
| `factories.py` | Builder functions per model + `build_full_dataset()` — no randomness, no network, idempotent (`update_or_create`) |
| `fixtures/regression_dataset.json` | Serialised snapshot (79 objects) loadable via `manage.py loaddata regression_dataset` |
| `generate_fixture.py` | Rebuilds the snapshot from the factories using a throwaway test DB |

## Dataset contents

* **Users** — `regadmin` + `akshat` (staff superusers), `client_user` (non-staff)
* **SiteSettings** — coupons GLAMOUR30 / SECRET10 / TODAYVIP, offer rules,
  travel zones, AI-negotiation guardrails (floor 75 %, max discount 20 %)
* **3 artists** · **2 courses + 6 modules** · **12 packages** (incl. NULL-price
  "On Request" and one inactive) · **5 studio services** · **12 service prices**
* **5 event packages** with vendor-cost/quote pairs for commission math
* **10 reviews** (9 active + 1 hidden) · **2 look groups + 5 media items**
  (image/Instagram/YouTube) · **5 media items** · **4 gallery images**
  (cover vs non-cover grouping) · **3 chat messages**

## Where it is consumed

* `unit/` — factories in `TestCase.setUp` (`seed_dataset = True`)
* `api/` & `e2e/` — `testing/conftest.py` seeds the live server's DB on demand
* `bdd/` / `smoke/` / `perf/` — server seeded via `manage.py seed_test_data`
  (management command wrapping these factories)

## Regenerate

```bash
python testing/testdata/generate_fixture.py     # rewrite the JSON snapshot
cd django && python manage.py seed_test_data --wipe   # reseed a dev DB
```
