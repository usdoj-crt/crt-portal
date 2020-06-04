from django.db import connection
from django.db import migrations


# Dictionary is used to find common stop words without returing stemmed results https://dba.stackexchange.com/questions/145016/finding-the-most-commonly-used-non-stop-words-in-a-column
sql_create_statement = """
CREATE TEXT SEARCH DICTIONARY english_simple_dict (
    TEMPLATE = pg_catalog.simple
  , STOPWORDS = english
);

CREATE TEXT SEARCH CONFIGURATION english_simple (COPY = simple);
ALTER  TEXT SEARCH CONFIGURATION english_simple
ALTER MAPPING FOR asciiword WITH english_simple_dict;

CREATE VIEW trends AS
    -- get this week's data
    (SELECT
        word,
        ndoc as document_count,
        nentry as word_count,
        date_trunc('week', CURRENT_TIMESTAMP - interval '1 week') as start_date,
        CURRENT_TIMESTAMP as end_date,
        'this_week' as record_type,
        row_number() OVER (PARTITION BY true) as id
    FROM ts_stat($$
        SELECT to_tsvector('english_simple', violation_summary)
        FROM cts_forms_report
        where
            (create_date >= date_trunc('week', CURRENT_TIMESTAMP - interval '1 week'))
    $$)
    ORDER BY document_count DESC
    LIMIT  10)
    UNION
    -- get last week's data
    (SELECT
        word,
        ndoc as document_count,
        nentry as word_count,
        date_trunc('week', CURRENT_TIMESTAMP - interval '2 week') as start_date,
        date_trunc('week', CURRENT_TIMESTAMP - interval '1 week') as end_date,
        'last_week' as record_type,
        row_number() OVER (PARTITION BY true) as id
    FROM ts_stat($$
        SELECT to_tsvector('english_simple', violation_summary)
        FROM cts_forms_report
        WHERE (
            create_date >= date_trunc('week', CURRENT_TIMESTAMP - interval '2 week') and
            create_date < date_trunc('week', CURRENT_TIMESTAMP - interval '1 week')
        )
    $$)
    ORDER BY document_count DESC
    LIMIT  10)
    UNION
    -- get last 4 weeks
    (SELECT
        word,
        ndoc as document_count,
        nentry as word_count,
        date_trunc('week', CURRENT_TIMESTAMP - interval '4 week') as start_date,
        CURRENT_TIMESTAMP as end_date,
        'four_weeks' as record_type,
        row_number() OVER (PARTITION BY true) as id
    FROM ts_stat($$
        SELECT to_tsvector('english_simple', violation_summary)
        FROM cts_forms_report
        WHERE (
            create_date >= date_trunc('week', CURRENT_TIMESTAMP - interval '4 week')
        )
    $$)
    ORDER BY document_count DESC
    LIMIT  10)
    UNION
    -- get this year
    (SELECT
        word,
        ndoc as document_count,
        nentry as word_count,
        date_trunc('year', CURRENT_TIMESTAMP) as start_date,
        CURRENT_TIMESTAMP as end_date,
        'year' as record_type,
        row_number() OVER (PARTITION BY true) as id
    FROM ts_stat($$
        SELECT to_tsvector('english_simple', violation_summary)
        FROM cts_forms_report
        WHERE (create_date >= date_trunc('year', CURRENT_TIMESTAMP))
    $$)
    ORDER BY document_count DESC
    LIMIT  10)
    ORDER BY start_date, document_count DESC
;
"""

def make_view(apps,schema_editor):
   with connection.cursor() as cursor:
      cursor.execute(sql_create_statement)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0072_contact_phone_message'),
    ]

    operations = [
       migrations.RunPython(make_view)

    ]