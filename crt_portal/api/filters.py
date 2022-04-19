from actstream import registry
from actstream.models import actor_stream
from cts_forms.models import User


def reports_accessed_filter(querydict):
    kwargs = {}
    reports_accessed_payload = {
        "report_count": 0,
        "start_date": "",
        "end_date": "",
        "intake_specialist": "",
    }
    registry.register(User)
    intake_specialist_username = querydict.get("intake_specialist", None)
    intake_specialist = User.objects.filter(username=intake_specialist_username).first()
    if intake_specialist:
        reports_accessed_payload["intake_specialist"] = intake_specialist_username
        filtered_actions = actor_stream(intake_specialist).filter(**kwargs)
        reports_accessed_payload["report_count"] = len(filtered_actions)
        for field in querydict:
            if "date" in field:
                # filters by a start date or an end date expects yyyy-mm-dd
                encoded_date = querydict.getlist(field)[0]
                if field == "start_date":
                    reports_accessed_payload["start_date"] = encoded_date
                elif field == "end_date":
                    reports_accessed_payload["end_date"] = encoded_date
    return reports_accessed_payload
