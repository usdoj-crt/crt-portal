from datetime import datetime
import json
import os
import sys
import traceback
import uuid

from analytics.models import AnalyticsFile

from django.conf import settings
from django.core.management.base import BaseCommand
import nbconvert
import nbformat
import pytz

notebook_dir = os.path.join(settings.BASE_DIR, '..', 'jupyterhub')


def _simplify_path(path) -> str:
    return path.replace(notebook_dir, '')


def _is_in_git(path: str) -> bool:
    return os.system(f'git ls-files --error-unmatch "{path}" > /dev/null 2>&1') == 0


def _build_error_notebook(error: Exception):
    return json.dumps({
        "cells": [
            {
                "cell_type": "markdown",
                "id": str(uuid.uuid4()),
                "metadata": {},
                "source": [
                    "# Something went wrong on import\n",
                    "\n",
                    "We were unable to import this notebook:"
                    "\n",
                    "```",
                    *traceback.format_exception(error),
                    "```",
                ]
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": '.'.join(str(i) for i in sys.version_info[:3])
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    })


class Command(BaseCommand):  # pragma: no cover
    help = 'Adds new response templates or updates existing ones'

    def _build_notebook(self, notebook_path: str) -> dict:
        local_tz = pytz.timezone('US/Eastern')
        simple_path = _simplify_path(notebook_path)
        return {
            'name': os.path.basename(simple_path).strip('/'),
            'path': simple_path.strip('/'),
            'type': 'notebook',
            'format': 'json',
            'mimetype': 'application/json',
            'created': datetime.fromtimestamp(os.path.getctime(notebook_path), tz=local_tz),
            'last_modified': datetime.fromtimestamp(os.path.getmtime(notebook_path), tz=local_tz),
            'from_command': True
        }

    def _load_notebook(self, notebook_path: str) -> AnalyticsFile:
        with open(notebook_path, 'r') as f:
            node = nbformat.read(f, as_version=nbformat.NO_CONVERT)

        # We don't want to show output from runs in other environments.
        nbconvert.preprocessors.ClearOutputPreprocessor().preprocess(node, {})
        notebook_content = json.dumps(node)
        return AnalyticsFile(
            content=notebook_content,
            **self._build_notebook(notebook_path),
        )

    def _safe_load_notebook(self, notebook_path: str) -> AnalyticsFile:
        try:
            return self._load_notebook(notebook_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading notebook {notebook_path}: {e}'))
            return AnalyticsFile(
                content=_build_error_notebook(e),
                **self._build_notebook(notebook_path),
            )

    def _safe_load_directory(self, directory_path: str) -> AnalyticsFile:
        return AnalyticsFile(
            type='directory',
            format='json',
            **self._build_filesystem_object(directory_path),
        )

    def _safe_load_file(self, file_path: str) -> AnalyticsFile:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            content = str(e)

        return AnalyticsFile(
            content=content,
            type='file',
            **self._build_filesystem_object(file_path),
        )

    def _build_filesystem_object(self, directory_path: str) -> dict:
        local_tz = pytz.timezone('US/Eastern')
        simple_path = _simplify_path(directory_path)
        return {
            'name': os.path.basename(simple_path).strip('/'),
            'path': simple_path.strip('/'),
            'created': datetime.fromtimestamp(os.path.getctime(directory_path), tz=local_tz),
            'last_modified': datetime.fromtimestamp(os.path.getmtime(directory_path), tz=local_tz),
            'from_command': True
        }

    def handle(self, *args, **options):
        del args, options  # Unused

        AnalyticsFile.objects.filter(from_command=True).delete()

        files = []
        for (dirpath, dirnames, filenames) in os.walk(notebook_dir):
            for filename in filenames:
                if not filename.endswith('.ipynb'):
                    continue
                notebook_path = os.path.join(dirpath, filename)
                if not _is_in_git(notebook_path):
                    continue
                files.append(self._safe_load_notebook(notebook_path))
            for dirname in dirnames:
                directory_path = os.path.join(dirpath, dirname)
                if not _is_in_git(directory_path):
                    continue
                files.append(self._safe_load_directory(directory_path))
            for filename in filenames:
                if filename.endswith('.ipynb'):
                    continue
                file_path = os.path.join(dirpath, filename)
                if not _is_in_git(file_path):
                    continue
                files.append(self._safe_load_file(file_path))

        files.append(self._safe_load_directory('/'))
        preview = len(files)
        self.stdout.write(self.style.SUCCESS(f'Loading {preview} Jupyter objects from filesystem:\n'))

        AnalyticsFile.objects.bulk_create(files)

        self.stdout.write(self.style.SUCCESS(f'Loaded {preview} Jupyter objects from filesystem'))
