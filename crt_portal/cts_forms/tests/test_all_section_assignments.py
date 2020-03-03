"""This is not a test yet, it is looping through meaningful permeations of the data and showing the output of the assign section function."""
import csv
import copy

from django.test import TestCase

from ..models import Report, ProtectedClass, HateCrimesandTrafficking
from ..model_variables import PRIMARY_COMPLAINT_CHOICES, PROTECTED_CLASS_CHOICES, COMMERCIAL_OR_PUBLIC_PLACE_CHOICES, CORRECTIONAL_FACILITY_LOCATION_CHOICES, PUBLIC_OR_PRIVATE_SCHOOL_CHOICES
from .test_data import SAMPLE_REPORT


fieldnames = ['section_assignment_actual', 'primary_complaint', 'protected_class', 'hate_crimes_trafficking', 'place', 'facility', 'school']


class Ultimate_Section_Assignment_Test(TestCase):

    def test_all_assignments(self):
        with open('data/section_assignment.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'section_assignment_actual': 'Section assignment',
                'primary_complaint': 'Primary complaint',
                'protected_class': 'Protected class',
                'hate_crimes_trafficking': 'Hate crimes or trafficking',
                'place': 'Place',
                'facility': 'Facility',
                'school': 'School',
            })
            for protected_class in PROTECTED_CLASS_CHOICES:
                class_object = ProtectedClass.objects.get_or_create(protected_class=protected_class)
                for primary in PRIMARY_COMPLAINT_CHOICES:
                    SAMPLE_REPORT['primary_complaint'] = primary[0]
                    # right now we are not accounting for multiple protected class selections, since we only have routing tied to disability for the moment, we may want to add more permutations as the logic gets more complex.

                    # this is a bisic example, if there is another required question for routing, we don't record this because it can't exist without the required question
                    if primary[0] not in ['commercial_or_public', 'police', 'education']:
                        # create object with required fields
                        test_report = Report.objects.create(**SAMPLE_REPORT)
                        test_report.protected_class.add(class_object[0])
                        # without hate crimes
                        section_no_hc = test_report.assign_section()
                        writer.writerow({
                            'section_assignment_actual': section_no_hc,
                            'primary_complaint': primary[0],
                            'protected_class': protected_class,
                            'hate_crimes_trafficking': 'none',
                            'place': 'n/a',
                            'facility': 'n/a',
                            'school': 'n/a',
                        })

                    # hate crime and trafficking example
                    crime_object = HateCrimesandTrafficking.objects.all()
                    test_report.hatecrimes_trafficking.add(crime_object[0])
                    test_report.hatecrimes_trafficking.add(crime_object[1])
                    test_report.save()
                    section = test_report.assign_section()
                    writer.writerow({
                        'section_assignment_actual': section,
                        'primary_complaint': primary[0],
                        'protected_class': protected_class,
                        'hate_crimes_trafficking': "hate crimes and trafficking",
                        'place': 'n/a',
                        'facility': 'n/a',
                        'school': 'n/a',
                    })

                    if primary[0] == 'commercial_or_public':
                        for place in COMMERCIAL_OR_PUBLIC_PLACE_CHOICES:
                            # create object with required fields
                            data = copy.deepcopy(SAMPLE_REPORT)
                            data['commercial_or_public_place'] = place[0]
                            test_report = Report.objects.create(**data)
                            test_report.protected_class.add(class_object[0])
                            # without hate crimes
                            section_no_hc = test_report.assign_section()
                            writer.writerow({
                                'section_assignment_actual': section_no_hc,
                                'primary_complaint': primary[0],
                                'protected_class': protected_class,
                                'hate_crimes_trafficking': 'none',
                                'place': place[0],
                                'facility': 'n/a',
                                'school': 'n/a',
                            })
                    if primary[0] == 'police':
                        for facility in CORRECTIONAL_FACILITY_LOCATION_CHOICES:
                            data = copy.deepcopy(SAMPLE_REPORT)
                            data['inside_correctional_facility'] = facility[0]
                            test_report = Report.objects.create(**data)
                            test_report.protected_class.add(class_object[0])
                            section_facility = test_report.assign_section()
                            writer.writerow({
                                'section_assignment_actual': section_facility,
                                'primary_complaint': primary[0],
                                'protected_class': protected_class,
                                'hate_crimes_trafficking': 'none',
                                'place': 'n/a',
                                'facility': facility[0],
                                'school': 'n/a',
                            })
                    if primary[0] == 'education':
                        for school in PUBLIC_OR_PRIVATE_SCHOOL_CHOICES:
                            data = copy.deepcopy(SAMPLE_REPORT)
                            data['public_or_private_school'] = school[0]
                            test_report = Report.objects.create(**data)
                            test_report.protected_class.add(class_object[0])
                            section_facility = test_report.assign_section()
                            writer.writerow({
                                'section_assignment_actual': section_facility,
                                'primary_complaint': primary[0],
                                'protected_class': protected_class,
                                'hate_crimes_trafficking': 'none',
                                'place': 'n/a',
                                'facility': 'n/a',
                                'school': school[0],
                            })
