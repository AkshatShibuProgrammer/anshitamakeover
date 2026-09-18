# Anshita Makeover — testing targets (hub: testing/)
# ─────────────────────────────────────────────
# Uses testenv when present; otherwise the master program bootstraps it.
PY := $(shell if [ -x testenv/bin/python ]; then echo testenv/bin/python; else echo python3; fi)
PORT ?= 8123

.PHONY: help venv test unit api e2e bdd smoke perf seed server list

help:            ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

venv:            ## Create the test virtualenv with all frameworks
	python3 -m venv testenv
	testenv/bin/pip install --upgrade pip
	testenv/bin/pip install "Django>=5.0,<7.0" Pillow requests python-dotenv \
		pytest pytest-playwright playwright pyyaml
	@echo "Install browsers with: testenv/bin/python -m playwright install --with-deps chromium"

test:            ## MASTER: run every kind of testing (unit, api, e2e, bdd, smoke, perf)
	$(PY) testing/run_all.py

list:            ## Show available test suites + runtime availability
	$(PY) testing/run_all.py --list

unit:            ## Unit testing — 221 Django regression tests
	$(PY) testing/run_all.py --suite unit

api:             ## API contract testing — pytest + requests vs live server
	$(PY) testing/run_all.py --suite api

e2e:             ## Browser E2E testing — Playwright chromium
	$(PY) testing/run_all.py --suite e2e

bdd:             ## BDD testing — Karate (needs Java 11+ & Maven + running server)
	cd testing/bdd && BASE_URL=http://127.0.0.1:$(PORT) ./run.sh

smoke:           ## Smoke testing — fast HTTP probes (server must be running)
	$(PY) testing/smoke/smoke_check.py --base-url http://127.0.0.1:$(PORT)

perf:            ## Performance testing — concurrency & latency budgets
	$(PY) testing/perf/load_check.py --base-url http://127.0.0.1:$(PORT)

seed:            ## Migrate + seed the canonical regression dataset
	cd django && $(PY) manage.py migrate --no-input && $(PY) manage.py seed_test_data

server:          ## Run the seeded dev server on 0.0.0.0:PORT
	cd django && $(PY) manage.py runserver 0.0.0.0:$(PORT)
