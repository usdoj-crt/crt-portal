from django.db import models


class ShortenedURL(models.Model):
    shortname = models.CharField(max_length=255, unique=True, help_text="The url the user will type in. For example, putting campaign-1 here would make the URL civilrights.justice.gov/link/campaign-1). Use only letters, numbers, or dashes here.", primary_key=True)
    destination = models.TextField(help_text="The destination path, for example /form/view, or /report?utm_campaign=asdf")
    enabled = models.BooleanField(default=True, help_text="If not enabled, the link will result in a 404 - Not Found")

    def __str__(self):
        return self.shortname

    def get_absolute_url(self):
        return self.destination
