from django.db import migrations


def create_actstream_description_index(apps, schema_editor):
    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #     CREATE INDEX IF NOT EXISTS actstream_action_description_idx
    #         ON public.actstream_action USING btree
    #         (description)
    #     """)
    pass  # Noop - this breaks on dev due to:
    # index row size 3008 exceeds btree version 4 maximum 2704 for index "actstream_action_description_idx"


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0163_crm_form_letters_update'),
    ]
    operations = [
        migrations.RunPython(create_actstream_description_index)
    ]
