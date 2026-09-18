# Karate API Contract Suite (BDD) — Anshita Makeover

Behaviour-driven API contract tests for the Django backend, written with
[Karate 1.5](https://github.com/karate-netty/karate). Every scenario mirrors a
test in `testing/api/test_api_contract.py` (same TC ids), so the
identical contract is validated by **two independent frameworks**.

## Layout

```
testing/bdd/
├── pom.xml                       # Maven build (karate-junit5 + JUnit5)
├── run.sh                        # one-command runner (health-checks server first)
└── src/test/java/
    ├── karate-config.js          # baseUrl + single sign-in (callSingle)
    ├── anshita/KarateRunner.java # JUnit5 entry point
    ├── helpers/admin-login.feature
    ├── public_pages.feature      # TC-KRT-PUB-001..006
    ├── chatbot.feature           # TC-KRT-CHT-001..005
    ├── reviews.feature           # TC-KRT-REV-001..004
    ├── admin-crud.feature        # TC-KRT-ADM-001..006
    └── pricing-auth.feature      # TC-KRT-PRC-001..003, TC-KRT-AUTH-001..003
```

## Running

Requirements: **Java 11+**, **Maven**, and a seeded server:

```bash
cd django
python manage.py migrate && python manage.py seed_test_data
python manage.py runserver 0.0.0.0:8123

cd ../testing/bdd
BASE_URL=http://127.0.0.1:8123 ./run.sh
```

HTML report lands in `testing/bdd/target/karate-reports/karate-summary.html`.

## Notes

* Admin scenarios reuse a **single authenticated session** (`callSingle` in
  `karate-config.js`) and replay Django's CSRF handshake (`csrftoken` cookie +
  `X-CSRFToken` header) exactly like the browser does.
* Mutating scenarios clean up after themselves so the suite is re-runnable.
* CI runs this suite automatically — see `.github/workflows/regression.yml`.
