# Class to handle filtering data by supplied query params, providing the params are valid.

from cts_forms.models import User, Report, FormLettersSent
from actstream import registry
from actstream.models import actor_stream
from cts_forms.models import User, Report
from django.utils.datastructures import MultiValueDictKeyError
import urllib.parse
from datetime import datetime

from utils.datetime_fns import change_datetime_to_end_of_day


def autoresponses_filter(querydict):
    kwargs = {}
    autoresponse_qs = Report.objects.filter().all()

    if "assigned_section" not in querydict.keys():
        return 0

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
            elif field == "end_date":
                try:
                    date_obj = datetime.strptime(decoded_date, "%Y-%m-%d")
                    date_obj = change_datetime_to_end_of_day(date_obj, field)
                    kwargs["create_date__lte"] = date_obj
                except ValueError:
                    # if the date is invalid, we throw an error
                    raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        elif field == "assigned_section":
            kwargs["assigned_section"] = querydict.getlist(field)[0]
    filtered_autoresponses = autoresponse_qs.filter(**kwargs)
    return len(filtered_autoresponses)


def form_letters_filter(querydict):
    kwargs = {}
    form_letters_counter = {}

    form_letters_payload = {
        "start_date": "",
        "end_date": "",
        "assigned_section": "",
        "total_form_letters": 0,
        "form_letters_counter": {}
    }

    try:
        section = querydict["assigned_section"]
        form_letters_payload["assigned_section"] = section
        form_letters_by_section = FormLettersSent.objects.filter(assigned_section=section)
    except MultiValueDictKeyError:
        return form_letters_payload

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
                    # if the date is invalid, we throw an error
                    raise ValueError("Incorrect date format, should be YYYY-MM-DD")
                form_letters_payload["start_date"] = encodedDate
            elif field == "end_date":
                try:
                    dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
                    dateObj = change_datetime_to_end_of_day(dateObj, field)
                    kwargs['timestamp__lte'] = dateObj
                except ValueError:
                    # if the date is invalid, we throw an error
                    raise ValueError("Incorrect date format, should be YYYY-MM-DD")
                form_letters_payload["end_date"] = encodedDate
    filtered_form_letters = form_letters_by_section.filter(**kwargs)
    form_letters_payload["total_form_letters"] = len(filtered_form_letters)

    for form_letter in filtered_form_letters:
        email_title = form_letter.description.split("'")[1]
        try:
            form_letters_counter[email_title] += 1
        except KeyError:
            form_letters_counter[email_title] = 1

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

def related_reports_filter(email_address, data):
    related_reports_payload = []
    related_reports_dict = {}
    for field in data:
        related_reports_dict["pk"] = field.pk
        related_reports_dict["viewed"] = field.viewed
        related_reports_dict["public_id"] = field.public_id
        related_reports_dict["assigned_section"] = field.assigned_section
        related_reports_dict["recent_email_sent"] = field.recent_email_sent
        related_reports_dict["create_date"] = field.create_date
        related_reports_dict["email"] = email_address
        related_reports_payload.append(related_reports_dict)

    return related_reports_payload

