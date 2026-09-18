#!/usr/bin/env bash
# Convenience wrapper — the master test program lives in testing/run_all.py
# and bootstraps its own environment when needed.
#
#   ./run_all_tests.sh                    # run every suite
#   ./run_all_tests.sh --suite unit api   # run selected suites
#   PYTHON=/path/to/python ./run_all_tests.sh   # force an interpreter
set -uo pipefail
cd "$(dirname "$0")"
exec python3 testing/run_all.py "$@"
