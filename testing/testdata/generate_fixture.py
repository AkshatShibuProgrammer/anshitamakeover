"""
Regenerate ``testing/testdata/fixtures/regression_dataset.json`` from the
canonical test-data factories.

The script spins up a throw-away test database (the dev ``db.sqlite3`` is
never touched), seeds the full dataset and serialises every row to the JSON
fixture.  Run from anywhere::

    python testing/testdata/generate_fixture.py

The resulting fixture is loadable into any database with::

    python manage.py loaddata regression_dataset
"""
import os
import sys
from pathlib import Path

TESTDATA_DIR = Path(__file__).resolve().parent
TESTING_DIR = TESTDATA_DIR.parent
REPO_ROOT = TESTING_DIR.parent
DJANGO_DIR = REPO_ROOT / 'django'

sys.path.insert(0, str(DJANGO_DIR))
sys.path.insert(0, str(TESTING_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anshita_project.settings')

import django  # noqa: E402

django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.core import serializers  # noqa: E402
from django.test.runner import DiscoverRunner  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402

FIXTURE_PATH = TESTDATA_DIR / 'fixtures' / 'regression_dataset.json'


def main():
    setup_test_environment()
    runner = DiscoverRunner(verbosity=0, interactive=False)
    old_config = runner.setup_databases()
    try:
        from testdata.factories import build_full_dataset
        counts = build_full_dataset()

        # Serialise users first (FK targets), then everything else.
        objects = list(User.objects.all().order_by('id'))
        from core.models import (
            SiteSettings, AdminProfile, Artist, AcademyCourse, CourseModule,
            MakeupPackage, StudioService, ServicePrice, EventPackage,
            CustomerReview, LookGroup, LookMediaItem, MediaItem, GalleryImage,
            ChatMessage,
        )
        for model in [SiteSettings, AdminProfile, Artist, AcademyCourse, CourseModule,
                      MakeupPackage, StudioService, ServicePrice, EventPackage,
                      CustomerReview, LookGroup, LookMediaItem, MediaItem,
                      GalleryImage, ChatMessage]:
            objects.extend(model.objects.all().order_by('id'))

        payload = serializers.serialize('json', objects, indent=2)
        FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE_PATH.write_text(payload, encoding='utf-8')

        print(f'[+] Wrote {FIXTURE_PATH}')
        print(f'[+] {len(objects)} objects serialised.')
        for model, count in counts.items():
            print(f'    {model:<16} {count}')
    finally:
        runner.teardown_databases(old_config)


if __name__ == '__main__':
    main()
