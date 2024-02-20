"""Automatically refreshes the output of files."""

from typing import Optional, Dict, List
from helpers.table_contents_manager import TableContentsManager
import copy
import datetime
import json
import logging
import os
from nbconvert.preprocessors.execute import ExecutePreprocessor
import nbformat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK_DIR = os.path.join(BASE_DIR)
SCHEDULES_PATH = os.path.join(NOTEBOOK_DIR, 'schedules.json')


def main():
    manager = TableContentsManager()
    schedules = _read(manager)
    results = _execute_all(schedules, manager)
    _write(results, manager)


def _read(manager):
    schedules = json.loads(manager.get('schedules.json').get('content'))

    notebooks = [
        notebook.get('path')
        for notebook
        in manager.get('/assignments/intake-dashboard').get('content', [])
    ]
    missing_from_schedules = [
        found
        for found in notebooks
        if not any(known.get('path') == found for known in schedules)
    ]
    return [
        *schedules,
        *[
            {'path': path, 'interval': {'hours': 1}}
            for path in missing_from_schedules
        ]
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


def _parse_json_date(container, key) -> Optional[datetime.datetime]:
    raw = container.get(key)
    if raw is None:
        return None
    try:
        return datetime.datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        readable_container = json.dumps(container)
        logging.error(f'Expected a date but got: {raw} in {readable_container}')
        return None


def _should_execute(schedule):
    last_executed = _parse_json_date(schedule, 'last_executed')
    if not last_executed:
        return True

    interval = schedule.get('interval')
    try:
        duration = datetime.timedelta(**interval)
    except TypeError as more_detail:
        logging.error(f'Invalid interval: {more_detail}')
        return False

    return last_executed + duration < datetime.datetime.now()


def _execute_one(schedule, manager) -> Dict:
    path = schedule.get('path')
    try:
        source_code = manager.get(path)
    except Exception as e:
        logging.error(f'Failed to execute {path}: {e}')
        return schedule
    if not source_code:
        logging.error(f'Failed to execute {path}: No source code')
        return schedule
    content = source_code.get('content')
    if not content:
        logging.error(f'Failed to execute {path}: No notebook content')
        return schedule

    kernel = content.get('metadata', {}).get('kernelspec', {}).get('name', 'python3')
    processor = ExecutePreprocessor(timeout=600, kernel_name=kernel)
    # Run relative to the jupyterhub/ directory
    # (Any imports, files, etc must exist on disk):
    metadata = {'metadata': {'path': os.path.dirname(os.path.realpath(__file__))}}
    notebook = nbformat.from_dict(content)
    if not isinstance(notebook, nbformat.NotebookNode):
        logging.error(f'Failed to execute {path}: Invalid notebook')
        return schedule
    try:
        result, _ = processor.preprocess(notebook, metadata)

        source_code['content'] = result
        manager.save(source_code, path)
    except Exception as e:
        logging.error(f'Failed to execute {path}: {e}')

    schedule_updates = {'last_executed': datetime.datetime.now().isoformat()}
    return copy.deepcopy(schedule) | schedule_updates


def _execute_all(schedules, manager) -> List[Dict]:
    return [
        _execute_one(schedule, manager)
        if _should_execute(schedule)
        else schedule
        for schedule in schedules
    ]


if __name__ == '__main__':
    main()
