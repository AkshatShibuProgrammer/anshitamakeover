#!/usr/bin/env python3
"""
UNIT TESTING PROGRAM — Django unit & regression suite (221 tests).

Runs the ``regression`` package through Django's own test runner against an
isolated test database, emits JUnit XML + an HTML coverage report into
``testing/reports/``, and is aggregated into the master report.

Usage:
    python testing/unit/run.py
    python testing/unit/run.py test_coupons
    python testing/unit/run.py test_coupons.AutoRotationCouponTests.test_tc_cpn_001_days_1_to_10
    python testing/unit/run.py -v 2 --no-coverage
"""
import argparse
import os
import sys
from pathlib import Path

UNIT_DIR = Path(__file__).resolve().parent
TESTING_DIR = UNIT_DIR.parent
REPO_ROOT = TESTING_DIR.parent
DJANGO_DIR = REPO_ROOT / 'django'
REPORTS_DIR = TESTING_DIR / 'reports'

# Make both the Django project and the testing hub (for ``testdata``) importable.
sys.path.insert(0, str(DJANGO_DIR))
sys.path.insert(0, str(TESTING_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')

import django  # noqa: E402
from django.conf import settings  # noqa: E402
from django.test.runner import DiscoverRunner  # noqa: E402

try:
    import xmlrunner  # unittest-xml-reporting
    HAS_XMLRUNNER = True
except ImportError:
    HAS_XMLRUNNER = False

COVERAGE_SOURCES = [str(DJANGO_DIR / 'core'), str(DJANGO_DIR / 'features')]
# Dead code / generated code that would only dilute the numbers.
COVERAGE_OMIT = [
    str(DJANGO_DIR / 'core' / 'views_monolithic_backup.py'),
    '*/migrations/*', '*/management/*', '*/templatetags/*',
]


class XmlDjangoRunner(DiscoverRunner):
    """Django runner that writes JUnit XML via unittest-xml-reporting."""

    def __init__(self, *args, xml_output=None, **kwargs):
        self.xml_output = xml_output
        super().__init__(*args, **kwargs)

    def get_test_runner_kwargs(self):
        if self.xml_output and HAS_XMLRUNNER:
            self.test_runner = xmlrunner.XMLTestRunner
            return {
                'output': self.xml_output,
                'verbosity': self.verbosity,
                'failfast': self.failfast,
                'buffer': self.buffer,
            }
        return super().get_test_runner_kwargs()


def main():
    ap = argparse.ArgumentParser(description='Anshita Makeover unit/regression runner')
    ap.add_argument('labels', nargs='*',
                    help='optional test labels inside the regression package '
                         '(e.g. test_coupons or test_coupons.AutoRotationCouponTests)')
    ap.add_argument('-v', '--verbosity', type=int, default=1)
    ap.add_argument('--failfast', action='store_true')
    ap.add_argument('--no-coverage', action='store_true', help='skip coverage measurement')
    ap.add_argument('--no-junit', action='store_true', help='skip JUnit XML output')
    args = ap.parse_args()

    django.setup()

    junit_dir = REPORTS_DIR / 'junit'
    junit_dir.mkdir(parents=True, exist_ok=True)
    if not args.no_junit:
        # xmlrunner writes one file per test class — drop stale ones from
        # previous runs so the master report never counts tests twice.
        for stale in junit_dir.glob('TEST-regression*.xml'):
            stale.unlink()
    xml_output = None if args.no_junit else str(junit_dir)

    runner = XmlDjangoRunner(verbosity=args.verbosity, interactive=False,
                             failfast=args.failfast, xml_output=xml_output)
    labels = [f'regression.{l}' if not l.startswith('regression') else l
              for l in args.labels] or ['regression']

    # Optional coverage instrumentation around the whole run.
    cov = None
    if not args.no_coverage:
        try:
            import coverage
            cov_dir = REPORTS_DIR / 'coverage'
            cov_dir.mkdir(parents=True, exist_ok=True)
            cov = coverage.Coverage(source=COVERAGE_SOURCES, omit=COVERAGE_OMIT, branch=False,
                                    data_file=str(cov_dir / '.coverage'))
            cov.start()
        except ImportError:
            print('[unit] coverage.py not installed — continuing without coverage')

    failures = runner.run_tests(labels)

    if cov:
        cov.stop()
        cov.save()
        cov_dir = REPORTS_DIR / 'coverage'
        cov.html_report(directory=str(cov_dir))
        cov.xml_report(outfile=str(cov_dir / 'coverage.xml'))
        print('\n[unit] coverage summary:')
        cov.report(show_missing=True)

    if not args.no_junit:
        print(f'[unit] JUnit XML written to {junit_dir}/')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
