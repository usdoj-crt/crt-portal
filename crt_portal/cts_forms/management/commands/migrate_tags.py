import logging

from typing import List
from django.core.management.base import BaseCommand
from cts_forms.models import Tag, Report, CommentAndSummary
from django.db.models import Q
from operator import or_, and_
from django.core.paginator import Paginator
from functools import reduce

_ReportTags = Report.tags.through


class Command(BaseCommand):  # pragma: no cover
    help = "Load and migrate section tags"

    def _fetch_tags(self) -> List[Tag]:
        return list(Tag.objects.all().only('name', 'pk'))

    def handle(self, *args, **options):
        del args, options  # unused
        tags = self._fetch_tags()
        self._match_tags_from_summary(tags)

    def _match_tags_from_summary(self, tags: List[Tag]):

        comments_with_tags = CommentAndSummary.objects.filter(
            and_(
                Q(is_summary=True),
                reduce(or_, [
                    Q(note__contains=tag.name)
                    for tag
                    in tags
                ])
            )
        )

        reports_with_tags = Report.objects.filter(
            internal_comments__in=comments_with_tags,
            tags=None,
        ).order_by('pk').only('pk', 'tags', 'internal_comments').prefetch_related('tags', 'internal_comments')

        logging.info(f'Found {reports_with_tags.count()} reports with no tags on report, but with tags in summary')

        changes = 0
        paginator = Paginator(reports_with_tags, 2000)
        for page_number in range(paginator.num_pages):
            assignments = [
                assignment
                for report in paginator.get_page(page_number + 1)
                for assignment in _get_new_tag_assignments(report, tags)
            ]
            changes += len(assignments)
            _ReportTags.objects.bulk_create(assignments)

        self.stdout.write(self.style.SUCCESS(f'Added {changes} tags to reports'))


def _get_new_tag_assignments(report, tags):
    logging.info(f'Processing report id {report.id}')
    summary = report.summary
    report_tag_ids = [tag.pk for tag in report.tags.all()]
    return [
        _ReportTags(report_id=report.pk, tag_id=tag.pk)
        for tag in tags
        if tag.name in summary.note and tag.pk not in report_tag_ids
    ]
