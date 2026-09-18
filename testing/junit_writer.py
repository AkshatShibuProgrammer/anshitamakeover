"""Tiny JUnit-XML writer shared by the script-based suites (smoke, perf).

Lets the master report builder treat every suite uniformly — unit, api, e2e,
smoke and perf all drop a ``testing/reports/junit/<suite>.xml``.
"""
import xml.etree.ElementTree as ET
from pathlib import Path


def write_junit(path, suite_name, cases, timestamp=None):
    """Write JUnit XML.

    cases: list of dicts {name, passed, seconds, message (optional on failure)}
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tests = len(cases)
    failures = sum(1 for c in cases if not c['passed'])
    total_time = sum(c.get('seconds', 0.0) for c in cases)

    suite = ET.Element('testsuite', {
        'name': suite_name,
        'tests': str(tests),
        'failures': str(failures),
        'errors': '0',
        'skipped': '0',
        'time': f'{total_time:.3f}',
    })
    if timestamp:
        suite.set('timestamp', timestamp)

    for case in cases:
        el = ET.SubElement(suite, 'testcase', {
            'classname': suite_name,
            'name': case['name'],
            'time': f"{case.get('seconds', 0.0):.3f}",
        })
        if not case['passed']:
            fail = ET.SubElement(el, 'failure', {'message': case.get('message', 'failed')})
            fail.text = case.get('message', 'failed')

    ET.ElementTree(suite).write(path, encoding='utf-8', xml_declaration=True)
    return path
