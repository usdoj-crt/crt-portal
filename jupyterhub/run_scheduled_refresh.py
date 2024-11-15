"""Automatically refreshes the output of files."""

from typing import Optional, List
from helpers.table_contents_manager import TableContentsManager
import datetime
import json
import logging
import os
from nbconvert.preprocessors.execute import ExecutePreprocessor
import nbformat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK_DIR = os.path.join(BASE_DIR)
SCHEDULES_PATH = os.path.join(NOTEBOOK_DIR, 'schedules.json')


def main(dry_run=False):
    manager = TableContentsManager()
    notebooks = manager.list_all_notebooks()
    updated_notebooks = _execute_all(notebooks, manager, dry_run=dry_run)
    updated_pks = [notebook.get(('file', 'id'))
                   for notebook in updated_notebooks
                   if notebook is not None]
    manager.update_fields(
        [id for id in updated_pks if id is not None],
        metadata_fields_and_values={'last_run': datetime.datetime.now()},
    )
    return [
        notebook.get(('file', 'path'))
        for notebook in updated_notebooks
    ]


def _any_to_json(unknown):
    if isinstance(unknown, datetime.datetime):
        return unknown.isoformat()
    return str(unknown)


def _write(schedules, manager):
    jsonified = json.dumps(schedules, default=_any_to_json, indent=2, sort_keys=True)
    with open(SCHEDULES_PATH, 'w') as f:
        f.write(jsonified)

    model = {
        'writable': True,
        'content': jsonified,
        'type': 'file',
        'format': '',
    }
    manager.save(model, 'schedules.json')


def _should_execute(notebook):
    run_frequency = notebook.get(('metadata', 'run_frequency'))
    if not run_frequency:
        return False

    last_run = notebook.get(('metadata', 'last_run'))
    if not last_run:
        return True

    return last_run + run_frequency < datetime.datetime.now(datetime.timezone.utc)


def _execute_one(notebook, manager, dry_run=False) -> Optional[int]:
    path = notebook.get(('file', 'path'))

    if dry_run:
        logging.info(f'Dry run - skipping execution of {path}')
        return notebook

    logging.info(f'Pulling source code for {path}')
    try:
        source_code = manager.get(path)
    except Exception as e:
        logging.warning(f'Failed to execute {path}: {e}')
        return None
    if not source_code:
        logging.warning(f'Failed to execute {path}: No source code')
        return None
    content = source_code.get('content')
    if not content:
        logging.warning(f'Failed to execute {path}: No notebook content')
        return None

    try:
        kernel = content.get('metadata', {}).get('kernelspec', {}).get('name', 'python3')
    except AttributeError:
        kernel = 'python3'
    processor = ExecutePreprocessor(timeout=600, kernel_name=kernel)
    # Run relative to the jupyterhub/ directory
    # (Any imports, files, etc must exist on disk):
    metadata = {'metadata': {'path': os.path.dirname(os.path.realpath(__file__))}}
    notebook = nbformat.from_dict(content)
    if not isinstance(notebook, nbformat.NotebookNode):
        logging.warning(f'Failed to execute {path}: Invalid notebook')
        return None
    try:
        logging.info(f'Executing notebook {path}')
        result, _ = processor.preprocess(notebook, metadata)

        source_code['content'] = result
        logging.info(f'Saving notebook {path}')
        manager.save(source_code, path)
    except Exception as e:
        logging.error(f'Failed to execute {path}: {e}')

    return notebook


def _execute_all(notebooks, manager, dry_run=False) -> List[Optional[int]]:
    return [
        _execute_one(notebook, manager, dry_run=dry_run)
        for notebook in notebooks
        if _should_execute(notebook)
    ]


if __name__ == '__main__':
    logging.info('Updated the following notebooks', main())
