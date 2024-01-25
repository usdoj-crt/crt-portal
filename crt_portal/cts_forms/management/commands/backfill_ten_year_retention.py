import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):  # pragma: no cover
    help = "Apply ten year labels to records that need them"

    def add_arguments(self, parser):
        parser.add_argument('batch_size', help='Number of records to process at a time. Larger batches are faster, but run the risk of running out of RAM. If unsure, 2000 is a sensible default.')
        parser.add_argument('number_of_batches', help='The number of batches to process. Specify "0" to process all records at once. If unsure, 1 is a sensible default')

    def handle(self, *args, **options):
        del args  # unused
        batch_size = int(options['batch_size'])
        number_of_batches = int(options['number_of_batches'])
        backfill_ten_year_retention(batch_size=batch_size,
                                    number_of_batches=number_of_batches)


def backfill_ten_year_retention(*, number_of_batches: int, batch_size: int):
    RetentionSchedule = apps.get_model('cts_forms', 'RetentionSchedule')
    Report = apps.get_model('cts_forms', 'Report')
    User = get_user_model()
    Action = apps.get_model('actstream', 'Action')

    ten_year = RetentionSchedule.objects.get(retention_years=10)
    report_type_id = ContentType.objects.get_for_model(Report).pk
    user_type_id = ContentType.objects.get_for_model(User).pk
    system_user_id = User.objects.get(username='system.user').pk

    reports = Report.objects.filter(
        Q(dj_number__isnull=True) | Q(dj_number='') | Q(dj_number='--'),
        retention_schedule__isnull=True,
        status='closed',
    ).exclude(
        litigation_hold=True,
    )

    paginator = Paginator(reports.order_by('id').values_list('id', flat=True),
                          batch_size)
    for page_number in range(paginator.num_pages):
        if number_of_batches and page_number >= number_of_batches:
            break

        logging.info(f'Applying {page_number + 1} of {paginator.num_pages}')
        page = paginator.get_page(page_number + 1)
        Action.objects.bulk_create([
            Action(verb='Retention schedule:',
                   description='Migrated from "None" to "10 Year"',
                   target_object_id=report_id,
                   actor_object_id=system_user_id,
                   actor_content_type_id=user_type_id,
                   target_content_type_id=report_type_id)
            for report_id
            in page
        ])

        reports.filter(pk__in=page).update(retention_schedule=ten_year)
