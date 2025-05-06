from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):  # pragma: no cover
    help = "Reverts reported reason's that were updated from a value to null or empty ('')."

    def handle(self, *args, **options):
        try:
            num_reported_reasons_corrected = 0
            reports_corrected_log = {}
            query = ""
            query_params = []
            protected_class_map = {
                "Age": 1,
                "Disability": 2,
                "Family": 3,
                "Gender": 4,
                "Genetic": 5,
                "Immigration/citizenship": 6,
                "Language": 7,
                "National": 8,
                "Pregnancy": 9,
                "Race/color": 10,
                "Religion": 11,
                "Sex": 12,
                "Sexual": 13,
                "None": 14,
                "Other": 16
            }

            cursor = connection.cursor()
            # description is a string containing the list of reported reasons that got removed delimited by commas
            # target_object_id is the report id
            cursor.execute(
                """
                    SELECT description, target_object_id
                    FROM actstream_action
                    WHERE
                        verb like '%Protected%' and
                        description like '%to ""%' and
                        timestamp > '2025-03-04 00:00:00.00+00:00'
                """
            )

            for row in cursor.fetchall():
                # Cleaning up the descriptions so we can map them to the protected class
                affected_reported_reasons = [x.replace('Updated from "', "").strip() for x in row[0].replace("Family, marital, or parental status", "Family").split(',')]
                report_id = row[1]

                for affected_reported_reason in affected_reported_reasons:
                    # Get the first word of the affected reported reason so we can map it to the protected class id
                    first_word = affected_reported_reason.split()[0].strip('"')

                    try:
                        reports_corrected_log[report_id]["ids"].append(protected_class_map[first_word])
                        reports_corrected_log[report_id]["reported_reasons"].append(affected_reported_reason.replace('" to ""', '').replace('Family', '"Family, marital, or parental status"'))
                    except KeyError:
                        reports_corrected_log[report_id] = {
                            "ids": [protected_class_map[first_word]],
                            "reported_reasons": [affected_reported_reason.replace('" to ""', '').replace('Family', '"Family, marital, or parental status"')]
                        }

                    # Try to add the reported reason to the report, if it already exists then we do nothing
                    query += "INSERT INTO cts_forms_report_protected_class (report_id, protectedclass_id) VALUES (%s, %s) ON CONFLICT (report_id, protectedclass_id) DO NOTHING;\n"
                    query_params.append(report_id)
                    query_params.append(protected_class_map[first_word])
                    # Sanity check to keep track of how many reported reasons we are correcting
                    num_reported_reasons_corrected += 1

            cursor.execute(f"BEGIN;\n{query}\nCOMMIT;", query_params)

            print("--------------------------------------")
            print(f"Number of reports corrected: {len(reports_corrected_log)}")
            print(f"Number of reported reasons corrected: {num_reported_reasons_corrected}")
            print("Reports corrected log:")
            [print(f"Report ID: {k}: Reported Reason Data: {reports_corrected_log[k]}") for k in reports_corrected_log]
            print("--------------------------------------")
        except Exception as e:
            print(e)
