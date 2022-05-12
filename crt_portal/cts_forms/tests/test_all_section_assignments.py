"""
This loops through meaningful permutations of the data and shows the output of the assign_section function.

View expected results: data/section_assignment_expected.csv If section routing rules change you will need to update this document.

The output of this test is saved to data/section_assignment.csv
"""
import csv
import copy

from django.test import TestCase

from ..models import Report, ProtectedClass
from ..model_variables import PRIMARY_COMPLAINT_CHOICES, PROTECTED_CLASS_CHOICES, COMMERCIAL_OR_PUBLIC_PLACE_CHOICES, CORRECTIONAL_FACILITY_LOCATION_CHOICES, PUBLIC_OR_PRIVATE_SCHOOL_CHOICES
from .test_data import SAMPLE_REPORT_1


fieldnames = ['section_assignment_actual', 'primary_complaint', 'protected_class', 'hate_crime', 'place', 'facility', 'school']


def load_expected_assignment():
    expected_assignments = set()
    with open('data/section_assignment_expected.csv', 'r') as csv_expected:
        reader = csv.reader(csv_expected)
        for line in reader:
            record = ''.join(line)
            expected_assignments.add(record)
    return expected_assignments


def write_and_check(self, writer, expected, actual, row):
    writer.writerow(row)
    record = ''.join(row.values())
    actual.add(record)
    self.assertTrue(record in expected)


class Ultimate_Section_Assignment_Test(TestCase):
    def test_all_assignments(self):
        expected = load_expected_assignment()
        actual = set()

        with open('data/section_assignment.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            write_and_check(self, writer, expected, actual, {
                'section_assignment_actual': 'Section assignment',
                'primary_complaint': 'Primary complaint',
                'protected_class': 'Protected class',
                'place': 'Place',
                'facility': 'Facility',
                'school': 'School',
            })
            for protected_class in PROTECTED_CLASS_CHOICES:
                class_object = ProtectedClass.objects.get_or_create(protected_class=protected_class)
                for primary in PRIMARY_COMPLAINT_CHOICES:
                    SAMPLE_REPORT_1['primary_complaint'] = primary[0]
                    # right now we are not accounting for multiple protected class selections, since we only have routing tied to disability for the moment, we may want to add more permutations as the logic gets more complex.

                    # this is a basic example, if there is another required question for routing, we don't record this because it can't exist without the required question
                    if primary[0] not in ['commercial_or_public', 'police', 'education']:
                        # create object with required fields
                        test_report = Report.objects.create(**SAMPLE_REPORT_1)
                        test_report.protected_class.add(class_object[0])
                        section = test_report.assign_section()
                        write_and_check(self, writer, expected, actual, {
                            'section_assignment_actual': section,
                            'primary_complaint': primary[0],
                            'protected_class': str(protected_class),
                            'place': 'n/a',
                            'facility': 'n/a',
                            'school': 'n/a',
                        })

                    if primary[0] == 'commercial_or_public':
                        for place in COMMERCIAL_OR_PUBLIC_PLACE_CHOICES:
                            # create object with required fields
                            data = copy.deepcopy(SAMPLE_REPORT_1)
                            data['commercial_or_public_place'] = place[0]
                            test_report = Report.objects.create(**data)
                            test_report.protected_class.add(class_object[0])
                            section = test_report.assign_section()
                            write_and_check(self, writer, expected, actual, {
                                'section_assignment_actual': section,
                                'primary_complaint': primary[0],
                                'protected_class': str(protected_class),
                                'place': place[0],
                                'facility': 'n/a',
                                'school': 'n/a',
                            })
                    if primary[0] == 'police':
                        for facility in CORRECTIONAL_FACILITY_LOCATION_CHOICES:
                            data = copy.deepcopy(SAMPLE_REPORT_1)
                            data['inside_correctional_facility'] = facility[0]
                            test_report = Report.objects.create(**data)
                            test_report.protected_class.add(class_object[0])
                            section_facility = test_report.assign_section()
                            write_and_check(self, writer, expected, actual, {
                                'section_assignment_actual': section_facility,
                                'primary_complaint': primary[0],
                                'protected_class': str(protected_class),
                                'place': 'n/a',
                                'facility': facility[0],
                                'school': 'n/a',
                            })
                    if primary[0] == 'education':
                        for school in PUBLIC_OR_PRIVATE_SCHOOL_CHOICES:
                            data = copy.deepcopy(SAMPLE_REPORT_1)
                            data['public_or_private_school'] = school[0]
                            test_report = Report.objects.create(**data)
                            test_report.protected_class.add(class_object[0])
                            section_facility = test_report.assign_section()
                            write_and_check(self, writer, expected, actual, {
                                'section_assignment_actual': section_facility,
                                'primary_complaint': primary[0],
                                'protected_class': str(protected_class),
                                'place': 'n/a',
                                'facility': 'n/a',
                                'school': school[0],
                            })
        # exists in actual but not expected
        not_in_test = actual.difference(expected)
        self.assertEqual(len(not_in_test), 0)
        # exists in expected but not actual
        missing_value = expected.difference(actual)
        self.assertEqual(len(missing_value), 0)
