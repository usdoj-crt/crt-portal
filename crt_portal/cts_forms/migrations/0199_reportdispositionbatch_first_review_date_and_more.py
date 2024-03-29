# Generated by Django 4.2.3 on 2024-03-22 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0198_reportdispositionbatch_first_reviewer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdispositionbatch',
            name='first_review_date',
            field=models.DateTimeField(blank=True, help_text='Date of the first records team review.', null=True),
        ),
        migrations.AddField(
            model_name='reportdispositionbatch',
            name='second_review_date',
            field=models.DateTimeField(blank=True, help_text='Date of the second records team review.', null=True),
        ),
        migrations.AlterField(
            model_name='reportdispositionbatch',
            name='create_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reportdispositionbatch',
            name='notes',
            field=models.TextField(blank=True, help_text='Internal notes about batch.', max_length=7000, null=True),
        ),
    ]
