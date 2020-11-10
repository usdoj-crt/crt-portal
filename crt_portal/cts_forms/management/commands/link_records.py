import pandas as pd
import recordlinkage
from cts_forms.models import Report
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create N reports with randomly generated data'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Linking reports...'))

        # Load Reports into dataframe
        fields = ["id", "contact_first_name", "contact_last_name", "contact_email", "location_name", "violation_summary"]
        queryset = Report.objects.values_list(*fields)
        df = pd.DataFrame.from_records(queryset, columns=fields, index='id')
        indexer = recordlinkage.Index()
        # indexer.block('contact_last_name')
        indexer.full()

        print(df)

        candidate_links = indexer.index(df)

        print(len(df), len(candidate_links))

        # Let's find similar records!
        compare_cl = recordlinkage.Compare()

        compare_cl.string('contact_last_name', 'contact_last_name', method='jarowinkler', threshold=0.85, label="contact_last_name")
        compare_cl.string('contact_first_name', 'contact_first_name', method='jarowinkler', threshold=0.85, label="contact_first_name")
        compare_cl.string('location_name', 'location_name', method='jarowinkler', threshold=0.85, label="location_name")

        features = compare_cl.compute(candidate_links, df)

        print(features.head(10))

        print(features.describe())

        features.sum(axis=1).value_counts().sort_index(ascending=False)

        matches = features[features.sum(axis=1) > 2]

        print(len(matches))
        print(matches.head(10))
