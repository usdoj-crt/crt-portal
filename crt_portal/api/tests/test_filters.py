
from actstream.models import Action
from urllib import request
from django.http import QueryDict

from django.test import TestCase
from api.tests.test_data import SAMPLE_ACTION_1, SAMPLE_ACTION_2, SAMPLE_ACTION_3
from ..filters import contacts_filter


class ContactsFilterTests(TestCase):
  def setUp(self):
    action_1 = Action.objects.create(**SAMPLE_ACTION_1)
    action_2 = Action.objects.create(**SAMPLE_ACTION_2)
    action_3 = Action.objects.create(**SAMPLE_ACTION_3)
  
  def test_date_filter(self):
    request_one_day = QueryDict(mutable=True)
    request_one_day.update({
      'start_date': '2022-04-12',
      'end_date': '2022-04-12'
    })
    request_multi_day = QueryDict(mutable=True)
    request_multi_day.update({
      'start_date': '2022-04-12',
      'end_date': '2022-04-15'
    })
    result_one_day = contacts_filter(request_one_day)
    result_multi_day = contacts_filter(request_multi_day)

    self.assertEqual(result_one_day['total_contacts_in_range'], 2)
    self.assertEqual(result_multi_day['total_contacts_in_range'], 3)
  
  def test_result_without_date_filter(self):
    request = {}
    result = contacts_filter(request)
    
    self.assertEqual(result['total_emails_counter'], result['emails_counter_for_date_range'])
    self.assertEqual(result['total_actions'], result['total_actions_in_range'])
    self.assertEqual(result['total_contacts'], result['total_contacts_in_range'])
  
  def test_date_filter_no_results(self):
    request = QueryDict(mutable=True)
    request.update({'start_date': '2022-04-1', 'end_date': '2022-04-11'})
    result = contacts_filter(request)

    self.assertEqual(result['total_contacts_in_range'], 0)
    self.assertEqual(result['total_actions_in_range'], 0)
