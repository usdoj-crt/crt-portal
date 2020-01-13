import csv

from django.test import TestCase

from .models import Report, ProtectedClass, HateCrimesandTrafficking
from .model_variables import PRIMARY_COMPLAINT_CHOICES, PROTECTED_CLASS_CHOICES
from .test_data import SAMPLE_REPORT


hate_crime_choices = {
    'physical harm': ['Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability'],
    'trafficking': ['Coerced or forced to do work or perform a commercial sex act'],
    'physical harm and trafficking': ['Physical harm or threats of violence based on race, color, national origin, religion, gender, sexual orientation, gender identity, or disability', 'Coerced or forced to do work or perform a commercial sex act'],
    'none': [],
}

fieldnames = ['section_assignment_actual', 'primary_complaint', 'protected_class', 'hate_crimes_trafficking']


csvfile = open('section_assignment.csv', 'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)


class Ultimate_Section_Assignment_Test(TestCase):

    def test_all_assignments(self):
        with open('section_assignment.csv', 'w', newline='') as csvfile:
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

                    for crime in hate_crime_choices:
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
                        # hate crime combinations
                        for crime_choice in hate_crime_choices:
                            crime_object = HateCrimesandTrafficking.objects.get_or_create(hatecrimes_trafficking_option=hate_crime_choices[crime])
                            test_report.hatecrimes_trafficking.add(crime_object[0])
                            test_report.save()
                            section = test_report.assign_section()
                            writer.writerow({
                                'section_assignment_actual': section,
                                'primary_complaint': primary[0],
                                'protected_class': protected_class,
                                'hate_crimes_trafficking': crime,
                            })

csvfile.close()







