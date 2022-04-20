from actstream import registry
from actstream.models import actor_stream
from cts_forms.models import User
import urllib.parse
from datetime import datetime


def _change_datetime_to_end_of_day(dateObj, field):
    """
    Takes a datetime and field param to ensure an end_date
    field has time moved to end of day (23:59:59)
    """
    if 'end' in field:
        return dateObj.replace(hour=23, minute=59, second=59)
    else:
        return dateObj


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

        for field in querydict:
            if "date" in field:
                # filters by a start date or an end date expects yyyy-mm-dd
                encodedDate = querydict.getlist(field)[0]
                decodedDate = urllib.parse.unquote(encodedDate)
                if field == "start_date":
                    try:
                        dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
                        kwargs['timestamp__gte'] = dateObj
                    except ValueError:
                        # if the date is invalid, we ignore it.
                        continue
                    reports_accessed_payload["start_date"] = encodedDate
                elif field == "end_date":
                    try:
                        dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
                        dateObj = _change_datetime_to_end_of_day(dateObj, field)
                        kwargs['timestamp__lte'] = dateObj
                    except ValueError:
                        # if the date is invalid, we ignore it.
                        continue
                    reports_accessed_payload["end_date"] = encodedDate
        filtered_actions = actor_stream(intake_specialist).filter(**kwargs)
    reports_accessed_payload["report_count"] = len(filtered_actions)
    return reports_accessed_payload
