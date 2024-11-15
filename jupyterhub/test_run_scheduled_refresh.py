import datetime
import dotenv
import os
import pytest
import run_scheduled_refresh
from helpers import table_contents_manager

dotenv.load_dotenv()


@pytest.fixture()
def manager():
    user = os.environ.get('POSTGRES_ANALYTICS_USER')
    password = os.environ.get('POSTGRES_ANALYTICS_PASSWORD')
    os.environ['DATABASE_URL'] = f'postgresql://{user}:{password}@localhost:5432/postgres'
    return table_contents_manager.TableContentsManager()


def test_updates_notebooks(manager):
    notebooks_before = manager.list_all_notebooks()
    assert len(notebooks_before) > 2, 'Did not find enough notebooks to test. Try running update_ipynb_examples.'
    ids = [
        notebook.get(('file', 'id'))
        for notebook in notebooks_before
    ]
    should_run_id = ids[0]
    should_not_run_id = ids[1]

    now = datetime.datetime.now(datetime.timezone.utc)
    past_due = now - datetime.timedelta(days=4)
    run_every = datetime.timedelta(days=3)
    not_yet_due = now - datetime.timedelta(days=2)

    manager.update_fields(
        [should_run_id], metadata_fields_and_values={
            'last_run': past_due,
            'run_frequency': run_every,
        }
    )
    manager.update_fields(
        [should_not_run_id], metadata_fields_and_values={
            'last_run': not_yet_due,
            'run_frequency': run_every,
        }
    )

    updated = run_scheduled_refresh.main(dry_run=True)

    notebooks_after = manager.list_all_notebooks()
    should_run_after = next(notebook
                            for notebook
                            in notebooks_after
                            if notebook.get(('file', 'id')) == should_run_id)
    should_not_run_after = next(notebook
                                for notebook
                                in notebooks_after
                                if notebook.get(('file', 'id')) == should_not_run_id)

    assert len(updated) >= 2
    assert should_not_run_after.get(('metadata', 'last_run')) == not_yet_due
    assert should_run_after.get(('metadata', 'last_run')) > past_due
