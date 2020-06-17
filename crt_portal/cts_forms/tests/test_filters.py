from django.test import SimpleTestCase

from cts_forms.filters import _get_date_field_from_param


class FilterTests(SimpleTestCase):
    def test_get_date_field_from_param(self):
        """truncate `_start` and `_end` from incoming parameters"""
        self.assertEquals(_get_date_field_from_param('create_date_start'), 'create_date')
        self.assertEquals(_get_date_field_from_param('closed_date_end'), 'closed_date')
        self.assertEquals(_get_date_field_from_param('modified_date_start'), 'modified_date')
