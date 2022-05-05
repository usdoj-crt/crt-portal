# from django.db import migrations, connection

# def create_materialize_action_section_view():
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             CREATE MATERIALIZED VIEW action_section AS
#             SELECT (id, public_id, contact_email, section)
#             FROM cts_forms_report
#             JOIN cts_forms_report on cts_form_report.public_id = actstream_actions.public_object_id
#         """)

#         SELECT (id, verb, description, target_object_id) FROM actstream_actions
