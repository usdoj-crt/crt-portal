import base64
import contextlib
from datetime import datetime
import logging
import json
import os

from jupyter_server.services.contents.checkpoints import Checkpoints
from jupyter_server.services.contents.manager import ContentsManager
from nbformat import from_dict
from psycopg2 import sql
import psycopg2


@contextlib.contextmanager
def _open_transaction():
    dsn = os.environ.get('DATABASE_URL')
    if not dsn:
        raise ValueError('env DATABASE_URL was not specified, and must be.')
    connection = psycopg2.connect(dsn)
    try:
        yield connection, connection.cursor()
        connection.commit()
    except Exception as e:
        logging.exception('Database cursor failed', e)
        connection.cancel()
        connection.close()
        raise
    finally:
        connection.close()


FILE_FIELDS = [
    'name',
    'content',
    'path',
    'type',
    'format',
    'mimetype',
    'created',
    'last_modified'
]


def _get_path_literals(path):
    path = path.strip('/')
    return {
        'is_in_path':
            sql.SQL(
                "path NOT LIKE '%/%'" if path == ''
                else f"path LIKE '{path}/%' AND path NOT LIKE '{path}/%/%'"
            ),
        'is_in_path_recursive':
            sql.SQL(
                "true" if path == ''
                else f"path LIKE '{path}/%'"
            ),
        'full_path': sql.Literal(path),
        'name': sql.Literal(os.path.basename(path).strip('/')),
    }


def _make_file(fields, row, content=True):
    file = {
        'writable': True,
        **dict(zip(fields, row)),
    }

    if not content:
        file['content'] = None
        file['format'] = None
        file['mimetype'] = None
        return file

    if file['type'] == 'notebook':
        file['format'] = 'json'
        file['mimetype'] = None
        file['content'] = json.loads(file['content'] or '{}')

    if file['type'] == 'file':
        file.setdefault('format', 'text')
        file.setdefault('mimetype', 'text/plain')

    if file['type'] == 'directory':
        file['format'] = 'json'
        file['mimetype'] = None

    return file


class NoopCheckpoints(Checkpoints):
    empty = {
        "id": '0',
        "last_modified": datetime.fromtimestamp(0),
    }

    def create_checkpoint(self, contents_mgr, path):
        return self.empty.copy()

    def restore_checkpoint(self, contents_mgr, checkpoint_id, path):
        pass

    def rename_checkpoint(self, checkpoint_id, old_path, new_path):
        pass

    def delete_checkpoint(self, checkpoint_id, path):
        pass

    def list_checkpoints(self, path):
        return [self.empty.copy()]

    def rename_all_checkpoints(self, old_path, new_path):
        pass

    def delete_all_checkpoints(self, path):
        pass


class TableContentsManager(ContentsManager):
    """Reads content from our notebooks table.

    See: https://jupyter-notebook.readthedocs.io/en/stable/extending/contents.html#required-methods
    """

    checkpoints_class = NoopCheckpoints
    files_handler_params = {
        'path': '/'
    }

    def get(self, path, content=True, type=None, format=None):
        fields = FILE_FIELDS.copy()
        if not content:
            fields.remove('content')

        fields_sql = sql.SQL(', ').join(sql.Identifier(field) for field in fields)
        query = sql.SQL("""
            SELECT {fields}, id
            FROM analytics.analyticsfile
            WHERE path = {full_path}
        """).format(fields=fields_sql, **_get_path_literals(path))
        result = None
        with _open_transaction() as (connection, cursor):
            cursor.execute(query.as_string(connection))
            result = cursor.fetchone()
        if not result:
            if not path:
                raise ValueError('No root directory found - did you run update_ipynb_examples?')
            return None

        file = _make_file([*fields, 'id'], result, content=content)

        if type == 'notebook' or file['type'] == 'notebook':
            file['content'] = from_dict(file['content'])

        if not content or file['type'] != 'directory':
            return file

        fields = FILE_FIELDS.copy()
        fields.remove('content')
        fields_sql = sql.SQL(', ').join(sql.Identifier(field) for field in fields)
        query = sql.SQL("""
            SELECT {fields_sql}, id
            FROM analytics.analyticsfile
            WHERE id != {id}
              AND ({is_in_path});
        """).format(fields_sql=fields_sql,
                    id=sql.Literal(file['id']),
                    **_get_path_literals(path))
        with _open_transaction() as (connection, cursor):
            cursor.execute(query.as_string(connection))
            result = cursor.fetchall()
        file['content'] = [
            _make_file([*fields, 'id'], row, content=False)
            for row in result
        ]

        return file

    def save(self, model, path):
        self.run_pre_save_hooks(model=model, path=path)
        fields = FILE_FIELDS.copy()
        if model['format'] == 'base64':
            model['content'] = base64.b64decode(model['content']).decode('utf-8')
            model['format'] = 'text'
        if model['type'] == 'notebook':
            model.setdefault('format', 'json')
            model.setdefault('mimetype', 'application/json')
        elif model['type'] == 'directory':
            model.setdefault('format', 'json')
            model.setdefault('mimetype', None)
        else:
            model.setdefault('mimetype', 'text/plain')
        name = os.path.basename(path)
        model.setdefault('path', path)
        model.setdefault('name', name)
        now = datetime.now()
        model.setdefault('created', now)
        model['last_modified'] = now
        model.setdefault('content', None)
        if model.get('content') and type(model['content']) is not str:
            model['content'] = json.dumps(model['content'])

        formatted_keys = sql.SQL(', ').join(sql.Identifier(key) for key in fields)
        formatted_values = sql.SQL(', ').join(sql.Literal(model[key]) for key in fields)
        query = sql.SQL("""
            INSERT INTO analytics.analyticsfile ({formatted_keys}, from_command)
            VALUES ({formatted_values}, false)
            ON CONFLICT (path) DO UPDATE
            SET
                ({formatted_keys}) = ({formatted_values})
                WHERE
                    analytics.analyticsfile.path = EXCLUDED.path AND
                    analytics.analyticsfile.name = EXCLUDED.name
            RETURNING {formatted_keys}
        """).format(formatted_keys=formatted_keys, formatted_values=formatted_values)
        result = None
        with _open_transaction() as (connection, cursor):
            cursor.execute(query.as_string(connection))
            result = cursor.fetchone()
        saved_model = _make_file(fields, result, content=False)

        # Jupyter expects a contentless model returned:
        saved_model['content'] = None
        saved_model['format'] = None

        self.run_post_save_hooks(model=model, os_path='.')
        return saved_model

    def delete_file(self, path):
        query = sql.SQL("""
            DELETE FROM analytics.analyticsfile
            WHERE
                path = {full_path} OR ({is_in_path_recursive})
        """).format(**_get_path_literals(path))
        with _open_transaction() as (connection, cursor):
            cursor.execute(query.as_string(connection))

    def rename_file(self, old_path, new_path):
        old = _get_path_literals(old_path)
        new = _get_path_literals(new_path)

        object_query = sql.SQL("""
            UPDATE analytics.analyticsfile
            SET name = {new_name}, path = {new_full_path}
            WHERE path = {old_full_path}
        """).format(new_name=new['name'],
                    new_full_path=new['full_path'],
                    old_full_path=old['full_path'])

        new_directory = sql.Literal(new_path.strip('/'))
        trim_start = sql.Literal(len(old_path.strip('/')) + 1)
        contents_query = sql.SQL("""
            UPDATE analytics.analyticsfile
            SET path = CONCAT(
                {new_directory},
                SUBSTRING(path FROM {trim_start})
            )
            WHERE {is_in_path_recursive}
        """).format(new_name=new['name'],
                    new_directory=new_directory,
                    trim_start=trim_start,
                    is_in_path_recursive=old['is_in_path_recursive'])

        with _open_transaction() as (connection, cursor):
            cursor.execute(object_query.as_string(connection))
            cursor.execute(contents_query.as_string(connection))

    def _exists(self, path="", where=""):
        query = sql.SQL("""
            SELECT 1
            FROM analytics.analyticsfile
            WHERE
                {where} AND
                path={full_path}
        """).format(**_get_path_literals(path), where=sql.SQL(where))
        result = None
        with _open_transaction() as (connection, cursor):
            cursor.execute(query.as_string(connection))
            result = cursor.fetchone()
        return result is not None

    def file_exists(self, path=""):
        if not path:
            return False
        return self._exists(path=path, where="(type='file' OR type='notebook')")

    def dir_exists(self, path):
        if not path:
            return True
        return self._exists(path=path, where="type='directory'")

    def is_hidden(self, path):
        return os.path.basename(path).startswith('.')
