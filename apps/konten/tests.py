from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class KontenMigrationRegressionTests(SimpleTestCase):
    def test_missing_konten_migration_file_is_restored(self):
        migration_path = Path(settings.BASE_DIR) / "apps" / "konten" / "migrations" / "0002_initial.py"
        self.assertTrue(migration_path.exists())
