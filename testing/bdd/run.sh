#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# Karate runner for the Anshita Makeover contract suite.
#
# Usage:
#   ./run.sh                      # run against http://127.0.0.1:8111
#   BASE_URL=http://x:8000 ./run.sh
#
# Requirements: Java 11+ and Maven. The Django server must already be
# running with the regression dataset seeded:
#   python manage.py migrate && python manage.py seed_test_data
#   python manage.py runserver 0.0.0.0:8111
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

BASE_URL="${BASE_URL:-http://127.0.0.1:8111}"

command -v mvn >/dev/null 2>&1 || { echo "ERROR: Maven is required (https://maven.apache.org)"; exit 1; }
command -v java >/dev/null 2>&1 || { echo "ERROR: Java 11+ is required"; exit 1; }

# Health-check the target server first
if ! curl -sf "${BASE_URL}/api/coupon/" >/dev/null; then
  echo "ERROR: no Anshita server responding at ${BASE_URL}"
  echo "Start one with: python manage.py seed_test_data && python manage.py runserver 0.0.0.0:8111"
  exit 1
fi

echo "[*] Running Karate contract suite against ${BASE_URL}"
mvn -q test -DbaseUrl="${BASE_URL}"

echo "[*] Karate report: target/karate-reports/karate-summary.html"
