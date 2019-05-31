from django.db import models
from django.utils import timezone

# Create your models here.

class ViolationReport(models.Model):
    description_text = models.CharField(max_length=200)
    create_date = models.DateTimeField('date published')

    def __str__(self):
        return self.description_text

    def was_published_recently(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(ViolationReport, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
