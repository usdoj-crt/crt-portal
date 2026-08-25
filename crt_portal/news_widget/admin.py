from datetime import datetime

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from utils.admin import CrtModelAdmin
from .models import NewsWidgetColumnData
from .widgets import NewsColumnWidget


_validate_link = URLValidator(schemes=['http', 'https'])


def _normalize_date(value):
    """Return an ISO 'YYYY-MM-DD' date string, or None if unparseable.

    Accepts ISO input as well as the legacy display format (e.g. 'Feb 26,
    2026') so records saved before the editor existed still validate.
    """
    value = (value or '').strip()
    for date_format in ('%Y-%m-%d', '%b %d, %Y'):
        try:
            return datetime.strptime(value, date_format).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


class NewsWidgetColumnDataForm(forms.ModelForm):
    class Meta:
        model = NewsWidgetColumnData
        fields = '__all__'
        widgets = {'data': NewsColumnWidget}

    def clean_data(self):
        articles = self.cleaned_data.get('data')
        if not articles:
            return []
        if not isinstance(articles, list):
            raise ValidationError('The article data must be a list of articles.')

        cleaned = []
        for position, article in enumerate(articles, start=1):
            if not isinstance(article, dict):
                raise ValidationError(f'Article {position} must be an object with a date, title, and link.')

            title = (article.get('title') or '').strip()
            link = (article.get('link') or '').strip()

            if not title:
                raise ValidationError(f'Article {position} is missing a title.')
            if not link:
                raise ValidationError(f'Article {position} is missing a link.')
            try:
                _validate_link(link)
            except ValidationError:
                raise ValidationError(f'Article {position} has an invalid link (it must be a full http(s) URL).')

            date = _normalize_date(article.get('date'))
            if date is None:
                raise ValidationError(f'Article {position} is missing a valid date.')

            cleaned.append({'date': date, 'title': title, 'link': link})
        return cleaned


class NewsWidgetColumnAdmin(CrtModelAdmin):
    form = NewsWidgetColumnDataForm
    list_display = ('pk', 'name')
    search_fields = ('name',)


admin.site.register(NewsWidgetColumnData, NewsWidgetColumnAdmin)
