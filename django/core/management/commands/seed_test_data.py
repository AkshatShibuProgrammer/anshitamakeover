"""
Management command: populate the current database with the canonical
regression dataset (the same data that backs the automated test suite).

Usage::

    python manage.py seed_test_data           # idempotent seed
    python manage.py seed_test_data --wipe    # delete existing rows first

Admin logins created by the seed:

* ``regadmin`` / ``RegTest@2026``  (regression-suite admin)
* ``akshat``   / ``Anshita@2026``  (canonical studio admin)
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    SiteSettings, Artist, AcademyCourse, CourseModule, MakeupPackage,
    GalleryImage, MediaItem, ServicePrice, EventPackage, ChatMessage,
    AdminProfile, CustomerReview, StudioService, LookGroup, LookMediaItem,
)


class Command(BaseCommand):
    help = 'Seed the canonical regression test dataset into the current database.'

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true',
                            help='Delete existing domain rows before seeding.')

    @transaction.atomic
    def handle(self, *args, **options):
        # The factories live with the test suite (testing/testdata); make
        # them importable even when manage.py is invoked from elsewhere.
        import sys
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[4]
        sys.path.insert(0, str(repo_root / 'testing'))

        from testdata.factories import build_full_dataset

        if options['wipe']:
            self.stdout.write('Wiping existing domain rows…')
            for model in [ChatMessage, LookMediaItem, LookGroup, MediaItem,
                          GalleryImage, CustomerReview, EventPackage,
                          ServicePrice, StudioService, MakeupPackage,
                          CourseModule, AcademyCourse, Artist, AdminProfile,
                          SiteSettings]:
                model.objects.all().delete()

        counts = build_full_dataset()
        self.stdout.write(self.style.SUCCESS('Regression dataset seeded:'))
        for model, count in counts.items():
            self.stdout.write(f'  {model:<16} {count}')
        self.stdout.write(self.style.SUCCESS(
            '\nAdmin logins: regadmin/RegTest@2026 · akshat/Anshita@2026'
        ))
