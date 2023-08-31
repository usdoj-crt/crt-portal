"""
This loops through meaningful permutations of the data and shows the output of the assign_section function.

View expected results: data/section_assignment_expected.csv If section routing rules change you will need to update this document.

The output of this test is saved to data/section_assignment.csv
"""
from typing import List
import csv
import copy
import itertools

from django.test import TestCase

from ..models import Report, ProtectedClass
from ..model_variables import PRIMARY_COMPLAINT_CHOICES, PROTECTED_CLASS_CHOICES, COMMERCIAL_OR_PUBLIC_PLACE_CHOICES, CORRECTIONAL_FACILITY_LOCATION_CHOICES, PROTECTED_CLASS_DICT, PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, PRIMARY_COMPLAINT_DICT
from .test_data import SAMPLE_REPORT_1


FIELDNAMES = ['Section assignment', 'Primary complaint', 'Protected class', 'Hate crime', 'Place', 'Facility', 'School']


def translate_edge_cases(cases):
    return [
        (
            (primary, PRIMARY_COMPLAINT_DICT[primary]),
            [
                PROTECTED_CLASS_DICT[protected_class]
                for protected_class in protected_classes
            ]
        ) for primary, protected_classes in cases
    ]


# See #1612
IER_EDGE_CASES = [
    ('workplace', ('Immigration', 'National origin', 'Language')),
    ('workplace', ('Immigration', 'National origin', 'Disability')),
    ('workplace', ('National origin', 'Language', 'Genetic')),
    ('workplace', ('Immigration', 'Language', 'Religion')),
    ('workplace', ('National origin', 'Age', 'Sex')),
    ('workplace', ('Immigration', 'Gender', 'Orientation')),
    ('workplace', ('Language', 'Pregnancy', 'Other')),
    ('voting', ('Immigration', 'National origin', 'Language')),
    ('voting', ('Immigration', 'Gender', 'Orientation')),
    ('commercial_or_public', ('Immigration', 'National origin', 'Language')),
    ('commercial_or_public', ('Immigration', 'Gender', 'Orientation')),
]

# Protected class is a checkbox, not radio button, so users can select multiple.
# That's too many combinations, though, so we only look at the subset we've added special logic for:
COMPLEX_EDGE_CASES = translate_edge_cases([
    *IER_EDGE_CASES,
])


def load_expected_assignment():
    with open('data/section_assignment_expected.csv', 'r') as csv_expected:
        reader = csv.reader(csv_expected)
        next(reader, None)  # Skip the header row.
        return {
            ''.join(line)
            for line in reader
        }


def classes_to_string(protected_classes: List[ProtectedClass]) -> str:
    return '|'.join(str(c.protected_class) for c in protected_classes)


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

    def create_and_check_report(self, *, primary, protected_classes):
        if primary[0] not in ['commercial_or_public', 'police', 'education']:
            test_report = Report.objects.create(**SAMPLE_REPORT_1)
            test_report.protected_class.set(protected_classes)
            section = test_report.assign_section()
            self.write_and_check({
                'Section assignment': section,
                'Primary complaint': primary[0],
                'Protected class': classes_to_string(protected_classes),
                'Place': 'n/a',
                'Facility': 'n/a',
                'School': 'n/a',
            })

        if primary[0] == 'commercial_or_public':
            for place in COMMERCIAL_OR_PUBLIC_PLACE_CHOICES:
                data = copy.deepcopy(SAMPLE_REPORT_1)
                data['commercial_or_public_place'] = place[0]
                test_report = Report.objects.create(**data)
                test_report.protected_class.set(protected_classes)
                section = test_report.assign_section()
                self.write_and_check({
                    'Section assignment': section,
                    'Primary complaint': primary[0],
                    'Protected class': classes_to_string(protected_classes),
                    'Place': place[0],
                    'Facility': 'n/a',
                    'School': 'n/a',
                })
        if primary[0] == 'police':
            for facility in CORRECTIONAL_FACILITY_LOCATION_CHOICES:
                data = copy.deepcopy(SAMPLE_REPORT_1)
                data['inside_correctional_facility'] = facility[0]
                test_report = Report.objects.create(**data)
                test_report.protected_class.set(protected_classes)
                section_facility = test_report.assign_section()
                self.write_and_check({
                    'Section assignment': section_facility,
                    'Primary complaint': primary[0],
                    'Protected class': classes_to_string(protected_classes),
                    'Place': 'n/a',
                    'Facility': facility[0],
                    'School': 'n/a',
                })
        if primary[0] == 'education':
            for school in PUBLIC_OR_PRIVATE_SCHOOL_CHOICES:
                data = copy.deepcopy(SAMPLE_REPORT_1)
                data['public_or_private_school'] = school[0]
                test_report = Report.objects.create(**data)
                test_report.protected_class.set(protected_classes)
                section_facility = test_report.assign_section()
                self.write_and_check({
                    'Section assignment': section_facility,
                    'Primary complaint': primary[0],
                    'Protected class': classes_to_string(protected_classes),
                    'Place': 'n/a',
                    'Facility': 'n/a',
                    'School': school[0],
                })

    def test_all_assignments(self):
        protected_class_selections = [
            *itertools.combinations(PROTECTED_CLASS_CHOICES, 1),
        ]

        selections = [
            *COMPLEX_EDGE_CASES,
            *itertools.product(PRIMARY_COMPLAINT_CHOICES, protected_class_selections),
        ]

        import pprint
        pprint.pprint(selections)

        models = (
            (
                primary,
                [
                    ProtectedClass.objects.get_or_create(protected_class=selection)[0]
                    for selection in protected_class_selection
                ]
            )
            for primary, protected_class_selection in selections
        )

        for primary, protected_class_set in models:
            SAMPLE_REPORT_1['primary_complaint'] = primary[0]
            self.create_and_check_report(primary=primary,
                                         protected_classes=protected_class_set)
        self.assertEqual(self.actual, self.expected)
