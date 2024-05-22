import traceback
from django.core.management.base import BaseCommand
from datetime import datetime

from cts_forms.models import SavedSearch, ScheduledNotification, NotificationPreference
from cts_forms.filters import get_report_filter_from_search


def _maybe_schedule_for(preference: NotificationPreference, search: SavedSearch):
    queryset, _ = get_report_filter_from_search(search)
    last_checked = datetime.fromisoformat(preference.saved_searches_last_checked[str(search.id)])
    new_reports = queryset.filter(create_date__gt=last_checked).count()

    if not new_reports:
        return

    frequency = preference.saved_searches.get(str(search.pk), 'none')
    if frequency == 'none':
        return

    key = f'saved_search_{search.pk}'
    scheduled = ScheduledNotification.find_for(preference.user, frequency)
    if key not in scheduled.notifications:
        scheduled.notifications[key] = {
            'name': search.name,
            'new_reports': 0,
        }
    scheduled.notifications[key]['new_reports'] += new_reports
    scheduled.save()


def _process_preference(preference: NotificationPreference):
    search_ids = preference.saved_searches.keys()
    searches = SavedSearch.objects.filter(id__in=search_ids).all()

    for search in searches:
        _maybe_schedule_for(preference, search)
        preference.saved_searches_last_checked[str(search.id)] = datetime.now()
    preference.save()


class Command(BaseCommand):
    help = 'Sends any scheduled digest notifications'

    def handle(self, *args, **options):

        preferences = NotificationPreference.objects.exclude(saved_searches__exact={}).all()

        for preference in preferences.all():
            try:
                _process_preference(preference)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing preference {preference.pk}: {e}\n\n{traceback.format_exc()}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Post-processed report {preference.pk}'))
