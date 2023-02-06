from django.core.management.commands import makemigrations
from django.conf import settings
import os
import uuid


class Command(makemigrations.Command):
    def write_migration_files(self, changes):
        marker_path = os.path.join(settings.SITE_ROOT, '.migration_conflict_marker')
        with open(marker_path, 'w') as f:
            print("DO NOT EDIT: Re-run makemigrations to regenerate this file.", file=f)
            print("Conflicts here mean another developer merged migrations first.", file=f)
            print("To fix, delete and regenerate your new migrations to depend on theirs.", file=f)
            print(str(uuid.uuid4()), file=f)
        super(Command, self).write_migration_files(changes)
