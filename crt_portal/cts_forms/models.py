from django.db import models
from django.forms import ModelForm
from django.utils import timezone

from .model_variables import *



class InternalHistory(models.Model):
    note = models.CharField(max_length=500, null=False, blank=False,)
    create_date = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    primary_complaint = models.CharField(max_length=100, choices=PRIMARY_COMPLAINT_CHOICES)
    protected_class = models.CharField(max_length=100, null=True, blank=True, choices=PROTECTED_CLASS_CHOICES)
    place = models.CharField(max_length=100, null=True, blank=True, choices=PLACE_CHOICES)
    public_or_private_employer = models.CharField(max_length=100, null=True, blank=True, choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES)
    # location_details to come after user testing
    employer_size = models.CharField(max_length=100, null=True, blank=True, choices=EMPLOYER_SIZE_CHOICES)
    public_or_private_school = models.CharField(max_length=100, null=True, blank=True, choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES)
    public_or_private_facility = models.CharField(max_length=100, null=True, blank=True, choices=PUBLIC_OR_PRIVATE_FACILITY_CHOICES)
    public_or_private_healthcare = models.CharField(max_length=100, null=True, blank=True, choices=PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES)
    respondent_type = models.CharField(max_length=100, null=True, blank=True, choices=RESPONDENT_TYPE_CHOICES)
    respondent_contact_ask = models.BooleanField(null=True)
    respondent_name = models.CharField(max_length=225, null=True, blank=True)
    respondent_city = models.CharField(max_length=700, null=True, blank=True)
    respondent_state =  models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    violation_summary = models.TextField()
    when = models.CharField(max_length=700, null=True, blank=True, choices=WHEN_CHOICES)
    how_many = models.CharField(max_length=700, null=True, blank=True, choices=HOW_MANY_CHOICES)
    who_reporting_for= models.CharField(max_length=100, null=True, blank=True, choices=WHO_CHOICES)
    relationship = models.CharField(max_length=100, null=True, blank=True, choices=RELATIONSHIP_CHOICES)
    do_not_contact = models.BooleanField(null=True)
    contact_given_name = models.CharField(max_length=225, null=True, blank=True)
    contact_family_name = models.CharField(max_length=225, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    # TODO, upgrade to add validation https://pypi.org/project/django-phone-field/
    contact_phone = models.CharField(max_length=200, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.violation_summary

    def was_published_recently(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days=1)
