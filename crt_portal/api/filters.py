# Class to handle filtering data by supplied query params, providing the params are valid.

from cts_forms.models import User
from actstream import registry
from actstream.models import Action, actor_stream
from rest_framework.exceptions import ParseError
import urllib.parse
from datetime import datetime

from utils.datetime_fns import change_datetime_to_end_of_day

# To add a new filter option, add the field name and expected filter behavior
filter_options = {
    'start_date': '__gte',
    'end_date': '__lte'
}


def contacts_filter(querydict, total_emails_counter):
    kwargs = {}
    filters = {}
    action_qs = Action.objects.filter().all()
    contact_qs = Action.objects.filter(verb='Contacted complainant:').all()
    total_actions = len(action_qs)
    total_contacts = len(contact_qs)
    emails_counter_for_date_range = total_emails_counter.copy()

    contacts_payload = {
        "start_date": '',
        "end_date": '',
        'total_actions': total_actions,
        'total_contacts': total_contacts,
        "total_contacts_in_range": 0,
        "total_actions_in_range": 0,
        "total_emails_counter": total_emails_counter,
        "emails_counter_for_date_range": emails_counter_for_date_range
    }

    for field in querydict.keys():
        filter_list = querydict.getlist(field)
        if len(filter_list) > 0:
            filters[field] = filter_list
        if 'date' in field:
            # filters by a start date or an end date expects yyyy-mm-dd
            field_name = 'timestamp'
            encoded_date = filter_list[0]
            contacts_payload[field] = encoded_date
            decoded_date = urllib.parse.unquote(encoded_date)
            try:
                date_obj = datetime.strptime(decoded_date, "%Y-%m-%d")
                date_obj = change_datetime_to_end_of_day(date_obj, field)
                kwargs[f'{field_name}{filter_options[field]}'] = date_obj
            except ValueError:
                # if the date is invalid, we throw an error
                raise ValueError("Incorrect date format, should be YYYY-MM-DD")
    filtered_actions = action_qs.filter(**kwargs).distinct()
    filtered_contacts = contact_qs.filter(**kwargs).distinct()

    for contact in contact_qs:
        try:
            email_title = contact.description.split("'")[1]
            if email_title:
                for key in total_emails_counter:
                    if key == email_title:
                        total_emails_counter[key] += 1
        except IndexError:
            raise ParseError("Request failed due to invalid data")

    for contact in filtered_contacts:
        try:
            email_title = contact.description.split("'")[1]
            if email_title:
                for key in emails_counter_for_date_range:
                    if key == email_title:
                        emails_counter_for_date_range[key] += 1
        except IndexError:
            raise ParseError("Request failed due to invalid data")

    contacts_payload['total_contacts_in_range'] = len(filtered_contacts)
    contacts_payload['total_actions_in_range'] = len(filtered_actions)
    contacts_payload['total_emails_counter'] = total_emails_counter
    contacts_payload['emails_counter_for_date_range'] = emails_counter_for_date_range

    return contacts_payload


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
                        dateObj = change_datetime_to_end_of_day(dateObj, field)
                        kwargs['timestamp__lte'] = dateObj
                    except ValueError:
                        # if the date is invalid, we ignore it.
                        continue
                    reports_accessed_payload["end_date"] = encodedDate
        filtered_actions = actor_stream(intake_specialist).filter(**kwargs)
        reports_accessed_payload["report_count"] = len(filtered_actions)
    return reports_accessed_payload
