# Class to handle filtering data by supplied query params, providing the params are valid.

from actstream.models import Action
import urllib.parse
from datetime import datetime

from utils.datetime_fns import _change_datetime_to_end_of_day

# To add a new filter option, add the field name and expected filter behavior
filter_options = {
  'start_date': '__gte',
  'end_date': '__lte'
}

def contacts_filter(querydict):
  kwargs = {}
  filters = {}
  action_qs = Action.objects.filter().all()
  contact_qs = Action.objects.filter(verb='Contacted complainant:').all()
  total_actions = len(action_qs)
  total_contacts = len(contact_qs)
  total_emails_counter = {'CRM - R1 Form Letter': 0,
          'CRM - R2 Form Letter': 0,
          'CRM - Referral to FBI': 0,
          'CRT - Comments & Opinions': 0,
          'CRT - Constant Writer': 0,
          'CRT - EEOC Referral Letter': 0,
          'CRT - No capacity': 0,
          'CRT - Non-Actionable': 0,
          'CRT - Request for Agency Review': 0,
          'DRS - Dept of Ed Referral Form Letter': 0,
          'DRS - DOT Referral Letter': 0,
          'DRS - EEOC Referral Letter': 0,
          'DRS - HHS Referral Form Letter': 0,
          'HCE - Referral for Housing/Lending/Public Accomodation': 0,
          'IER - Form Letter': 0,
          'EOS - EEOC Referral Form Letter': 0,
          'EOS - Department of Ed OCR Referral Form Letter': 0,
          'SPL - Referral for PREA Issues': 0,
          'SPL - Standard Form Letter': 0,
          'Trending - Arbery Inquiries': 0,
          'Trending - Floyd Inquiries': 0,
          'Trending - General COVID Inquiries': 0}
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
            date_obj = _change_datetime_to_end_of_day(date_obj, field)
            kwargs[f'{field_name}{filter_options[field]}'] = date_obj
        except ValueError:
            # if the date is invalid, we ignore it.
            continue
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
          print("oh my, it is not an email")

  for contact in filtered_contacts:
      try:
          email_title = contact.description.split("'")[1]
          if email_title:
              for key in emails_counter_for_date_range:
                  if key == email_title:
                      emails_counter_for_date_range[key] += 1
      except IndexError:
          print("oh my, it is not an email")

  contacts_payload['total_contacts_in_range'] = len(filtered_contacts)
  contacts_payload['total_actions_in_range'] = len(filtered_actions)
  contacts_payload['total_emails_counter'] = total_emails_counter
  contacts_payload['emails_counter_for_date_range'] = emails_counter_for_date_range

  return contacts_payload