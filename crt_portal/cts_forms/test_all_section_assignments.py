"""This is not a test yet, it is looping through meaningful permeations of the data and showing the output of the assign section function."""
import csv

from django.test import TestCase

from .models import Report, ProtectedClass, HateCrimesandTrafficking
from .model_variables import PRIMARY_COMPLAINT_CHOICES, PROTECTED_CLASS_CHOICES
from .test_data import SAMPLE_REPORT


fieldnames = ['section_assignment_actual', 'primary_complaint', 'protected_class', 'hate_crimes_trafficking']

csvfile = open('section_assignment.csv', 'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)


class Ultimate_Section_Assignment_Test(TestCase):

    def test_all_assignments(self):
        with open('data/section_assignment.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'section_assignment_actual': 'Section assignment',
                'primary_complaint': 'Primary complaint',
                'protected_class': 'Protected class',
                'hate_crimes_trafficking': 'Hate crimes trafficking',
            })

            for primary in PRIMARY_COMPLAINT_CHOICES:
                # right now we are not accounting for multiple protected class selections, since we only have routing tied to disability for the moment, we may want to add more permutations as the logic gets more complex.
                for protected_class in PROTECTED_CLASS_CHOICES:
                    class_object = ProtectedClass.objects.get_or_create(protected_class=protected_class)

                    # create object with required fields
                    SAMPLE_REPORT['primary_complaint'] = primary[0]
                    test_report = Report.objects.create(**SAMPLE_REPORT)
                    test_report.protected_class.add(class_object[0])
                    # without hate crimes
                    section_no_hc = test_report.assign_section()
                    writer.writerow({
                        'section_assignment_actual': section_no_hc,
                        'primary_complaint': primary[0],
                        'protected_class': protected_class,
                        'hate_crimes_trafficking': 'none',
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
                    })


csvfile.close()
