import logging
import json
from typing import Optional
from contextlib import contextmanager
from datetime import datetime
import os
from urllib.parse import urlencode

from django.conf import settings
from django.db import models
from django.apps import apps
from django.db.migrations import RunSQL
from django.db.migrations.operations import special
from django.forms import model_to_dict
from nbconvert.preprocessors.execute import ExecutePreprocessor
import nbconvert
import nbformat
import pytz

from cts_forms.models import RoutingSection


class RunSQLIgnoringErrors(RunSQL):
    """RunSQL, but don't raise exceptions.

    Useful, for example, to perform operations that don't support IF NOT EXISTS.
    """

    def database_forwards(self, *args, **kwargs):
        try:
            super().database_forwards(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Ignoring error in RunSQL (this message can probably be ignored): {e}")

    def database_backwards(self, *args, **kwargs):
        try:
            super().database_backwards(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Ignoring error in RunSQL (this message can probably be ignored): {e}")


def make_analytics_user():
    """Use as the `operations` variable in a migration."""
    user = settings.DATABASES['analytics']['USER']
    db = settings.DATABASES['analytics']['NAME']
    password = settings.DATABASES['analytics']['PASSWORD']
    superuser = settings.DATABASES['default']['USER']

    return [
        RunSQLIgnoringErrors(
            f"CREATE USER {user};",
            reverse_sql=f"""
                REASSIGN OWNED BY {user} TO {superuser};
                DROP OWNED BY {user};
                DROP ROLE {user};
            """,
        ),
        RunSQLIgnoringErrors(
            f"GRANT CONNECT ON DATABASE {db} TO {user};",
            reverse_sql=special.RunSQL.noop,
        ),
        RunSQLIgnoringErrors(
            f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {user};",
            reverse_sql=special.RunSQL.noop,
        ),
        RunSQLIgnoringErrors(
            f"ALTER DEFAULT PRIVILEGES FOR USER {superuser} IN SCHEMA public GRANT SELECT ON TABLES TO {user};",
            reverse_sql=special.RunSQL.noop,
        ),
        RunSQLIgnoringErrors(
            f"""
            GRANT ALL PRIVILEGES ON SCHEMA analytics TO {user};
            GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO {user};
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO {user};
            GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA analytics TO {user};
            """,
            reverse_sql=special.RunSQL.noop,
        ),
        RunSQLIgnoringErrors(
            f"""
            ALTER DEFAULT PRIVILEGES FOR USER {superuser} IN SCHEMA analytics GRANT ALL PRIVILEGES ON TABLES TO {user};
            ALTER DEFAULT PRIVILEGES FOR USER {superuser} IN SCHEMA analytics GRANT ALL PRIVILEGES ON SEQUENCES TO {user};
            ALTER DEFAULT PRIVILEGES FOR USER {superuser} IN SCHEMA analytics GRANT ALL PRIVILEGES ON FUNCTIONS TO {user};
            """,
            reverse_sql=special.RunSQL.noop,
        ),
        RunSQLIgnoringErrors(
            f"ALTER USER {user} PASSWORD '{password}';",
            reverse_sql=special.RunSQL.noop,
        ),
    ]


@contextmanager
def _readonly_database_env():
    db = settings.DATABASES['default']
    name = db['NAME']
    user = db['USER']
    password = db['PASSWORD']
    host = db['HOST']
    port = db['PORT']
    port_str = f":{port}" if port else ""
    attrs = urlencode({
        'options': " ".join([
            "-c default_transaction_read_only=on",
            "-c default_transaction_isolation=serializable",
            "-c default_transaction_deferrable=on",
        ]),
        'target_session_attrs': 'read-only'
    })
    uri = f'postgresql://{user}:{password}@{host}{port_str}/{name}?{attrs}'
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


def _keep_only_code(notebook_content: Optional[str]) -> str:
    if not notebook_content:
        return ''

    preprocessors = [
        nbconvert.preprocessors.ClearOutputPreprocessor(),
        nbconvert.preprocessors.ClearMetadataPreprocessor(),
    ]
    node = nbformat.reads(notebook_content, as_version=nbformat.NO_CONVERT)

    for preprocessor in preprocessors:
        preprocessor.preprocess(node, {})

    return node


class AnalyticsFile(models.Model):
    """Stores Jupyter notebooks in the database.

    Extends the File spec from
    jupyter_server.services.contents.manager.ContentsManager
    """
    class Meta:
        db_table = 'analytics"."analyticsfile'
        managed = True
        permissions = (
            ("jupyter_editor", "Can access and edit Jupyter Notebooks"),
            ("jupyter_superuser", "Can use Jupyter admin features"),
        )

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

    @classmethod
    def get_existing(cls, other):
        try:
            return AnalyticsFile.objects.get(name=other.name, path=other.path)
        except AnalyticsFile.DoesNotExist:
            return None

    def has_same_source_as(self, other) -> bool:
        """Ignoring outputs, etc, whether this has the same code as `other`.

        Used, for example, in determining whether to reload a file.
        """
        self_attrs = {
            'name': self.name,
            'path': self.path,
            'type': self.path,
            'format': self.path,
            'mimetype': self.mimetype,
        }
        other_attrs = {
            'name': self.name,
            'path': self.path,
            'type': self.path,
            'format': self.path,
            'mimetype': self.mimetype,
        }
        if self_attrs != other_attrs:
            return False

        if self.type == 'notebook':
            return _keep_only_code(self.content) == _keep_only_code(other.content)

        return self.content == other.content

    def as_notebook(self) -> nbformat.NotebookNode:
        loaded = nbformat.reads(self.content, as_version=4)
        if self.type != 'notebook':
            raise ValueError(f"Can't create a notebook node from a {self.type}")
        if not isinstance(loaded, nbformat.NotebookNode):
            raise ValueError(f"Notebook is not a valid ipynb: {loaded}")
        return loaded

    def __str__(self):
        return self.path

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

            try:
                notebook, _ = processor.preprocess(
                    self.as_notebook(),
                    km=kernel_manager,
                )
            finally:
                if processor.kc:
                    processor.kc.stop_channels()

        self.content = json.dumps(notebook)
        local_tz = pytz.timezone('US/Eastern')
        self.last_run = datetime.now(local_tz)
        self.last_modified = datetime.now(local_tz)

        if run_only_cell is None:
            return None
        if run_only_cell + 1 >= len(notebook['cells']):
            kernel_manager.shutdown_kernel()
            return None
        return run_only_cell + 1

    def to_html(self) -> str:
        """Runs the notebook and returns rendered HTML as a string."""
        if self.type != 'notebook':
            raise ValueError(f"Can't HTML-ify a {self.type}")
        exporter = nbconvert.HTMLExporter()
        exporter.exclude_input = True
        exporter.exclude_input_prompt = True
        exporter.exclude_output_prompt = True
        exporter.exclude_output_stdin = True
        exporter.exclude_raw = True
        html, _ = exporter.from_notebook_node(self.as_notebook())
        return html


class DashboardGroup(models.Model):
    """Organizes notebooks for display in the Portal's intake section."""
    header = models.CharField(max_length=256, blank=True, null=False, help_text="A human-readable header for the group")
    notebooks = models.ManyToManyField(AnalyticsFile, through='FileGroupAssignment', blank=True, help_text="The notebooks to display in this group")
    order = models.IntegerField(default=0, help_text="The order in which to display this group, lower numbers first")

    def __str__(self):
        return self.header


class FileGroupAssignment(models.Model):
    analytics_file = models.ForeignKey(AnalyticsFile, on_delete=models.DO_NOTHING)
    dashboard_group = models.ForeignKey(DashboardGroup, on_delete=models.DO_NOTHING)
    show_only_for_sections = models.ManyToManyField(RoutingSection, blank=True, help_text="If set, the notebook will only be displayed for the given section(s). If unset, the notebook will be displayed for all sections.")


def get_dashboard_structure():
    assignments = FileGroupAssignment.objects.all().prefetch_related('analytics_file', 'dashboard_group')
    groups = {}
    for assignment in assignments:
        group_id = assignment.dashboard_group.pk
        if group_id not in groups:
            groups[group_id] = {
                **model_to_dict(assignment.dashboard_group),
                'notebooks': [],
                'show_only_for_sections': [],
            }
        groups[group_id]['notebooks'].append(assignment.analytics_file.to_html())
    return sorted(groups.values(), key=lambda g: g['order'])
