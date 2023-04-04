from typing import Optional

from django.core.management.commands import makemigrations
import uuid

import pathlib


def find_upwards(cwd: pathlib.Path, filename: str) -> Optional[pathlib.Path]:
    if cwd == pathlib.Path(cwd.root) or cwd == cwd.parent:
        return None

    fullpath = cwd / filename
    return fullpath if fullpath.exists() else find_upwards(cwd.parent, filename)


class Command(makemigrations.Command):
    def write_migration_files(self, changes):
        if self.dry_run:
            super(Command, self).write_migration_files(changes)
            return

        cwd = pathlib.Path(__file__).parent
        marker = find_upwards(cwd, ".migration_conflict_marker")
        if not marker:
            raise RuntimeError("Could not find .migration_conflict_marker")

        with marker.open('w') as f:
            print("DO NOT EDIT: Re-run makemigrations to regenerate this file.", file=f)
            print("Conflicts here mean another developer merged migrations first.", file=f)
            print("To fix, delete and regenerate your new migrations to depend on theirs.", file=f)
            print(str(uuid.uuid4()), file=f)
        super(Command, self).write_migration_files(changes)
