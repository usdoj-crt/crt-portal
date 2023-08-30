"""
This loops through meaningful permutations of the data and shows the output of the assign_section function.

View expected results: data/section_assignment_expected.csv If section routing rules change you will need to update this document.

The output of this test is saved to data/section_assignment.csv
"""
import csv
import copy
import itertools

from django.test import TestCase

from ..models import Report, ProtectedClass
from ..model_variables import PRIMARY_COMPLAINT_CHOICES, PROTECTED_CLASS_CHOICES, COMMERCIAL_OR_PUBLIC_PLACE_CHOICES, CORRECTIONAL_FACILITY_LOCATION_CHOICES, PUBLIC_OR_PRIVATE_SCHOOL_CHOICES
from .test_data import SAMPLE_REPORT_1


FIELDNAMES = ['Section assignment', 'Primary complaint', 'Protected class', 'Hate crime', 'Place', 'Facility', 'School']


def load_expected_assignment():
    with open('data/section_assignment_expected.csv', 'r') as csv_expected:
        reader = csv.reader(csv_expected)
        next(reader, None)  # Skip the header row.
        return {
            ''.join(line)
            for line in reader
        }


class Ultimate_Section_Assignment_Test(TestCase):
    def setUp(self):
        self.actual = set()
        self.actual_rows = []
        self.expected = load_expected_assignment()

    def tearDown(self):
        rows_by_section = sorted(self.actual_rows,
                                 key=lambda row: row['Section assignment'] + row['Primary complaint'])
        with open('data/section_assignment.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows_by_section)

    def write_and_check(self, row):
        record = ''.join(row.values())
        self.actual_rows.append(row)
        self.actual.add(record)
        self.assertIn(record, self.expected)

    def create_and_check_report(self, *, primary, protected_class):
        class_object = ProtectedClass.objects.get_or_create(protected_class=protected_class)
        if primary[0] not in ['commercial_or_public', 'police', 'education']:
            test_report = Report.objects.create(**SAMPLE_REPORT_1)
            test_report.protected_class.add(class_object[0])
            section = test_report.assign_section()
            self.write_and_check({
                'Section assignment': section,
                'Primary complaint': primary[0],
                'Protected class': str(protected_class),
                'Place': 'n/a',
                'Facility': 'n/a',
                'School': 'n/a',
            })

        if primary[0] == 'commercial_or_public':
            for place in COMMERCIAL_OR_PUBLIC_PLACE_CHOICES:
                data = copy.deepcopy(SAMPLE_REPORT_1)
                data['commercial_or_public_place'] = place[0]
                test_report = Report.objects.create(**data)
                test_report.protected_class.add(class_object[0])
                section = test_report.assign_section()
                self.write_and_check({
                    'Section assignment': section,
                    'Primary complaint': primary[0],
                    'Protected class': str(protected_class),
                    'Place': place[0],
                    'Facility': 'n/a',
                    'School': 'n/a',
                })
        if primary[0] == 'police':
            for facility in CORRECTIONAL_FACILITY_LOCATION_CHOICES:
                data = copy.deepcopy(SAMPLE_REPORT_1)
                data['inside_correctional_facility'] = facility[0]
                test_report = Report.objects.create(**data)
                test_report.protected_class.add(class_object[0])
                section_facility = test_report.assign_section()
                self.write_and_check({
                    'Section assignment': section_facility,
                    'Primary complaint': primary[0],
                    'Protected class': str(protected_class),
                    'Place': 'n/a',
                    'Facility': facility[0],
                    'School': 'n/a',
                })
        if primary[0] == 'education':
            for school in PUBLIC_OR_PRIVATE_SCHOOL_CHOICES:
                data = copy.deepcopy(SAMPLE_REPORT_1)
                data['public_or_private_school'] = school[0]
                test_report = Report.objects.create(**data)
                test_report.protected_class.add(class_object[0])
                section_facility = test_report.assign_section()
                self.write_and_check({
                    'Section assignment': section_facility,
                    'Primary complaint': primary[0],
                    'Protected class': str(protected_class),
                    'Place': 'n/a',
                    'Facility': 'n/a',
                    'School': school[0],
                })

    def test_all_assignments(self):
        for protected_class, primary in itertools.product(PROTECTED_CLASS_CHOICES, PRIMARY_COMPLAINT_CHOICES):
            SAMPLE_REPORT_1['primary_complaint'] = primary[0]
            self.create_and_check_report(primary=primary,
                                         protected_class=protected_class)
        not_in_test = self.actual - self.expected
        self.assertEqual(not_in_test, set())
        missing_value = self.expected - self.actual
        self.assertEqual(missing_value, set())
