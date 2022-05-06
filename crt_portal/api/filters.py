# Class to handle filtering data by supplied query params, providing the params are valid.

from cts_forms.models import User, FormLettersSent, Report
from actstream import registry
from actstream.models import Action, actor_stream
from rest_framework.exceptions import ParseError
import urllib.parse
from datetime import datetime

from utils.datetime_fns import change_datetime_to_end_of_day

# To add a new filter option, add the field name and expected filter behavior
filter_options = {
    "assigned_section": "assigned_section",
    "start_date": "__gte",
    "end_date": "__lte"
}

def autoresponses_filter(querydict):
    kwargs = {}
    autoresponse_qs = Report.objects.filter().all()

    autoresponses_payload = {
        "start_date": "",
        "end_date": "",
        "total_autoresponses": 0
    }
    for field in querydict.keys():
        if "date" in field:
            # filters by a start date or an end date expects yyyy-mm-dd
            encoded_date = querydict.getlist(field)[0]
            decoded_date = urllib.parse.unquote(encoded_date)
            if field == "start_date":
                try:
                    date_obj = datetime.strptime(decoded_date, "%Y-%m-%d")
                    kwargs["create_date__gte"] = date_obj                    
                except ValueError:
                    # if the date is invalid, we throw an error
                    raise ValueError("Incorrect date format, should be YYYY-MM-DD")
                autoresponses_payload["start_date"] = encoded_date
            elif field == "end_date":
                try:
                    date_obj = datetime.strptime(decoded_date, "%Y-%m-%d")
                    date_obj = change_datetime_to_end_of_day(date_obj, field)
                    kwargs["create_date__lte"] = date_obj
                except ValueError:
                    # if the date is invalid, we throw an error
                    raise ValueError("Incorrect date format, should be YYYY-MM-DD")
                autoresponses_payload["end_date"] = encoded_date
        elif field == "assigned_section":
            kwargs["assigned_section"] = querydict.getlist(field)[0]
    filtered_autoresponses = autoresponse_qs.filter(**kwargs)
    autoresponses_payload["total_autoresponses"] = len(filtered_autoresponses)
    return autoresponses_payload            
           

def form_letters_filter(querydict):
    kwargs = {}
    filters = {}
    form_letter_qs = Action.objects.filter(verb="Contacted complainant:").all()
    form_letters_counter = {}

    form_letters_payload = {
        "start_date": "",
        "end_date": "",
        "assigned_section": "",
        "total_form_letters": 0,
        "form_letters_counter": form_letters_counter
    }
    section_filter = False
    section = ""
    for field in querydict.keys():
        filter_list = querydict.getlist(field)
        if len(filter_list) > 0:
            filters[field] = filter_list
        if "date" in field:
            # filters by a start date or an end date expects yyyy-mm-dd
            field_name = "timestamp"
            encoded_date = filter_list[0]
            form_letters_payload[field] = encoded_date
            decoded_date = urllib.parse.unquote(encoded_date)
            try:
                date_obj = datetime.strptime(decoded_date, "%Y-%m-%d")
                date_obj = change_datetime_to_end_of_day(date_obj, field)
                kwargs[f'{field_name}{filter_options[field]}'] = date_obj
            except ValueError:
                # if the date is invalid, we throw an error
                raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        elif "assigned_section" in field:
            section_filter = True
            section = filter_list[0]
    filtered_form_letters = form_letter_qs.filter(**kwargs)

    if section_filter and section:
        filtered_by_section_form_letters = []
        for form_letter in filtered_form_letters:
            form_letters_sent = FormLettersSent.objects.filter(report_id=form_letter.target_object_id).first()
            if form_letters_sent and form_letters_sent.assigned_section == section:
                filtered_by_section_form_letters.append(form_letter)
        filtered_form_letters = filtered_by_section_form_letters

    for form_letter in filtered_form_letters:
        try:
            email_title = form_letter.description.split("'")[1]
            if email_title:
                for key in form_letters_counter:
                    if key == email_title:
                        form_letters_counter[key] += 1
                    else:
                        form_letters_counter[key] = 1
        except IndexError:
            raise ParseError("Request failed due to invalid data")

    form_letters_payload["form_letters_counter"] = form_letters_counter
    form_letters_payload["total_form_letters"] = len(filtered_form_letters)

    return form_letters_payload


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
