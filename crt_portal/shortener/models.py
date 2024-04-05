from django.db import models
import string
import re


class ShortenedURL(models.Model):
    shortname = models.CharField(max_length=255, unique=True, help_text="The url the user will type in. For example, putting campaign-1 here would make the URL civilrights.justice.gov/link/campaign-1). Use only letters, numbers, or dashes here.", primary_key=True)
    destination = models.TextField(help_text="The destination path, for example /form/view, or /report?utm_campaign=asdf")
    enabled = models.BooleanField(default=True, help_text="If not enabled, the link will result in a 404 - Not Found")

    def __str__(self):
        return self.shortname

    def get_short_url(self):
        return f"/link/{self.shortname}"

    def get_absolute_url(self):
        return self.destination

    @classmethod
    def urlify(self, text, *, prefix=''):
        text = ''.join([
            c
            if c in string.ascii_letters + string.digits
            else ' '
            for c in text
        ]).lower()

        text = re.sub(r'\s+', '-', text).strip('-')

        suffix = 0
        if prefix:
            prefix = f'{prefix}-'
        match = f"{prefix}{text}"
        while ShortenedURL.objects.filter(shortname=match).exists():
            suffix += 1
            match = f"{prefix}{text}-{suffix}"

        return match
