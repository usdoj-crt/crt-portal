# Generated by Django 4.2.11 on 2024-10-08 19:02

import textwrap
from django.db import migrations
from cts_forms.models import AddConfigurableContentMigration
from cts_forms.model_variables import STATES_AND_TERRITORIES

_DEFAULT_CONTENT = textwrap.dedent("""
    <div data-state="default" class='state-hide-show'>
        Select a state to see state-specific resources.
    </div>
""")

_STATES_CONTENT = [
    textwrap.dedent(f"""
    <div data-state="{state_key}" class='state-hide-show'>
        There are no state-specific resources for {state_name}.
    </div>
    """)
    for state_key, state_name in STATES_AND_TERRITORIES
]

_CONTENT = _DEFAULT_CONTENT + ''.join(_STATES_CONTENT)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0220_add_vot_form_content'),
    ]

    operations = [
        AddConfigurableContentMigration('vot-form-states', content=_CONTENT),
    ]
