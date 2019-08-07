from django.db import models
from django.utils import timezone


# TODO, add person and case classes

class State(models.Model):
    """State or territory, we can hard code but this allows for flexibility in the admin"""
    state_name = models.CharField(max_length=200)

    def __str__(self):
        return self.state_name

class InternalHistory(models.Model):
    note = models.CharField(max_length=500, null=False, blank=False,)
    create_date = models.DateTimeField(auto_now_add=True)


class ViolationReport(models.Model):
    email = models.EmailField(max_length=254, null=True, blank=True)
    # TODO, upgrade to add validation https://pypi.org/project/django-phone-field/
    phone = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state =  models.ManyToManyField(State, null=True, blank=True)
    first_date_of_incident = models.DateField(null=True, blank=True)
    description_text = models.CharField(max_length=500, null=False, blank=False,)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description_text

    def was_published_recently(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    """ This is a throwaway class to test some functionality """
    question = models.ForeignKey(ViolationReport, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
