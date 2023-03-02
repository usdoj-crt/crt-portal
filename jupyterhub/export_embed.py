"""
Places select portions of Jupyter notebook into SQL.

Only converts notebooks with 'export_embed: True' metadata set.
"""

import collections
from typing import Optional, List
import json
import logging
import os
import shutil
import subprocess
import psycopg2
from psycopg2 import sql
import contextlib


@contextlib.contextmanager
def open_transaction():
    dsn = os.environ.get('DATABASE_URL')
    if not dsn:
        raise ValueError('env DATABASE_URL was not specified, and must be.')
    connection = psycopg2.connect(dsn)
    try:
        yield connection.cursor()
        connection.commit()
    except Exception as e:
        logging.exception('Database connection failed', e)
        connection.cancel()
        connection.close()
    finally:
        connection.close()


def main():
    logging.basicConfig(level=logging.INFO)
    with open_transaction() as cursor:
        create_embeds(cursor)


def create_embeds(cursor):
    shutil.rmtree("embeds", ignore_errors=True)
    for root, _, files in os.walk("assignments", followlinks=True):
        outdir = os.path.join("embeds", root)
        os.makedirs(exist_ok=True, name=outdir)
        for file in files:
            notebook_path = os.path.join(root, file)
            converted = convert_notebook(notebook_path, 'html')
            if not converted:
                continue
            save_embed(cursor,
                       filename=notebook_path,
                       content=converted,
                       mimetype="text/html")


def save_embed(cursor, **attrs):
    attrs = collections.OrderedDict(**attrs)
    insert_names = ', '.join(attrs.keys())
    insert_vars = ', '.join(f'{{{key}}}' for key in attrs.keys())
    update_pairs = ',\n'.join([
        f"{key} = {{{key}}}"
        for key in attrs.keys()
    ])
    query_template = sql.SQL(f"""
        INSERT
        INTO "analytics"."dashboard_embed" ({insert_names})
        VALUES ({insert_vars})
        ON CONFLICT (filename) DO UPDATE
            SET {update_pairs};
    """)

    query = query_template.format(**{
        key: sql.Literal(value)
        for key, value in attrs.items()
    }).as_string(cursor)

    printable = query_template.format(**{
        key: sql.Literal(value[:50] + ('...' if len(value) > 50 else ''))
        for key, value in attrs.items()
    }).as_string(cursor)

    logging.info(f"Running SQL: \n\n{printable}\n\n")
    cursor.execute(query)


def run_jupyter(*, args: List[str], to_format: str, notebook_path: str):
    jupyter_args = [
        "jupyter", "nbconvert",
        "--to", to_format,
        *args,
        "--stdout",
        notebook_path,
    ]

    try:
        logging.info(f"Executing notebook: {jupyter_args}")
        return subprocess.run(jupyter_args, stdout=subprocess.PIPE, check=True)
    except ChildProcessError as e:
        logging.exception(f'Something went wrong executing {notebook_path}', e)
        return None


def convert_notebook(notebook_path: str, to_format: str) -> Optional[str]:
    if '.ipynb_checkpoints' in notebook_path:
        return None
    if not notebook_path.endswith(".ipynb"):
        return None
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    if not notebook.get("metadata", {}).get("export_embed", False):
        return None

    run_jupyter(
        to_format=to_format,
        notebook_path=notebook_path,
        args=[
            "--execute", "--ExecutePreprocessor.timeout=600",
        ]
    )

    result = run_jupyter(
        to_format=to_format,
        notebook_path=notebook_path,
        args=[
            "--TagRemovePreprocessor.remove_cell_tags=hide",
            "--TagRemovePreprocessor.remove_input_tags=hide_input",
        ]
    )

    if not result:
        return None
    return result.stdout.decode('utf-8')


if __name__ == "__main__":
    main()
