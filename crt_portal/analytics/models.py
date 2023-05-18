from typing import Optional
from contextlib import contextmanager
from datetime import datetime
import os
from urllib.parse import urlencode

from django.conf import settings
from django.db import models
from django.apps import apps
from nbconvert.preprocessors.execute import ExecutePreprocessor
import nbconvert
import nbformat
import pytz


@contextmanager
def _readonly_database_env():
    db = settings.DATABASES['default']
    name = db['NAME']
    user = db['USER']
    password = db['PASSWORD']
    host = db['HOST']
    port = db['PORT']
    attrs = urlencode({
        'options': " ".join([
            "-c default_transaction_read_only=on",
            "-c default_transaction_isolation=serializable",
            "-c default_transaction_deferrable=on",
        ]),
        'target_session_attrs': 'read-only'
    })
    uri = f'postgresql://{user}:{password}@{host}:{port}/{name}?{attrs}'
    clean_env = os.environ.copy()
    os.environ['DATABASE_URL'] = uri
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(clean_env)


class ExecuteCellPreprocessor(ExecutePreprocessor):
    """A special ExecutePreprocessor that only runs one step."""

    def __init__(self, *args, **kwargs):
        self._run_only_cell = kwargs.pop('run_only_cell', 0)
        super().__init__(*args, **kwargs)

    def preprocess_cell(self, cell, resources, index):
        if self._run_only_cell != index:
            return cell, resources
        return super().preprocess_cell(cell, resources, index)


class AnalyticsFile(models.Model):
    """Stores Jupyter notebooks in the database.

    Extends the File spec from
    jupyter_server.services.contents.manager.ContentsManager
    """
    class Meta:
        db_table = 'analytics"."analyticsfile'
        managed = True

    name = models.CharField(max_length=1024, blank=True, null=False, help_text="A human-readable name for the notebook")
    content = models.TextField(blank=True, null=True, help_text="The file contents (not human readable, do not edit)")
    path = models.CharField(max_length=2048, blank=True, null=False, help_text="The full path (including filename) to the file", unique=True)
    type = models.CharField(max_length=32, choices=[("notebook", "notebook"), ("file", "file"), ("directory", "directory")])
    format = models.CharField(max_length=1024, blank=True)
    mimetype = models.CharField(max_length=1024, blank=True, null=True)
    created = models.DateTimeField(null=True, blank=True, help_text="When this was created")
    last_modified = models.DateTimeField(null=True, blank=True, help_text="When this was last modified")

    from_command = models.BooleanField(default=False, help_text="If true, the notebook was loaded from a command, and should not be modified (e.g., examples)")
    last_run = models.DateTimeField(null=True, blank=True, help_text="The last time this notebook was run from the Portal admin panel")

    def as_notebook(self) -> nbformat.NotebookNode:
        loaded = nbformat.reads(self.content, as_version=4)
        if self.type != 'notebook':
            raise ValueError(f"Can't create a notebook node from a {self.type}")
        if not isinstance(loaded, nbformat.NotebookNode):
            raise ValueError(f"Notebook is not a valid ipynb: {loaded}")
        return loaded

    def refresh(self, *, run_only_cell: Optional[int] = None) -> Optional[int]:
        """Re-runs the associated ipynb.

        Returning the next unexecuted cell or None."""
        if self.type != 'notebook':
            raise ValueError(f"Can't refresh a {self.type}")

        if run_only_cell is not None:
            processor = ExecuteCellPreprocessor(timeout=600,
                                                kernel_name='python3',
                                                run_only_cell=run_only_cell)
        else:
            processor = ExecutePreprocessor(timeout=600, kernel_name='python3')

        with _readonly_database_env():
            kernel_manager = apps.get_app_config('analytics').kernel_manager

            notebook, _ = processor.preprocess(
                self.as_notebook(),
                km=kernel_manager,
            )

        self.content = nbformat.writes(notebook)
        local_tz = pytz.timezone('US/Eastern')
        self.last_run = datetime.now(local_tz)
        self.last_modified = datetime.now(local_tz)

        if run_only_cell is None:
            return None
        if run_only_cell + 1 >= len(notebook['cells']):
            return None
        return run_only_cell + 1

    def to_html(self) -> str:
        """Runs the notebook and returns rendered HTML as a string."""
        if self.type != 'notebook':
            raise ValueError(f"Can't HTML-ify a {self.type}")
        exporter = nbconvert.HTMLExporter()
        exporter.exclude_input = True
        html, _ = exporter.from_notebook_node(self.as_notebook())
        return html
