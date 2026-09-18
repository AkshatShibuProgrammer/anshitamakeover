# Django Regression Suite (unit layer)

221 `django.test.TestCase` tests organised in 14 functional areas
(`REG-AREA-01` … `REG-AREA-14`). Full catalogue: [`docs/testing/REGRESSION_TEST_PLAN.md`](../../../docs/testing/REGRESSION_TEST_PLAN.md).

## Running

```bash
python testing/unit/run.py                    # whole suite
python testing/unit/run.py -v 2               # verbose
python testing/unit/run.py test_coupons       # one area
python testing/unit/run.py test_coupons.AutoRotationCouponTests.test_tc_cpn_001_days_1_to_10
```

No network access is required — Gemini is mocked (`test_ai_copilot.py`),
oEmbed calls are mocked, and date-dependent coupon logic is frozen with fake
dates. The suite creates its own test database and never touches `db.sqlite3`.

## Test data

* `testing/testdata/factories.py` — deterministic factories used by every test
  class (`seed_dataset = True` builds the full canonical dataset in `setUp`).
* `testing/testdata/generate_fixture.py` — rewrites
  `testing/testdata/fixtures/regression_dataset.json` (79 objects).
* The identical dataset can be loaded into any DB with
  `python manage.py seed_test_data`.

## Conventions

* Every test method name starts with its catalogue id: `test_tc_xxx_NNN_*`.
* Assertions that lock a known defect reference `KD-xxx` in the docstring.
* New tests: take the next TC id, add factories if needed, update the plan doc.
