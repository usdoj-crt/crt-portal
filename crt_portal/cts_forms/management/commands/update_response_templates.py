import os
import frontmatter
from django.conf import settings
from django.core.management.base import BaseCommand
from cts_forms.models import ResponseTemplate


class Command(BaseCommand):
    help = 'Adds new response templates or updates existing ones'

    templates_dir = os.path.join(settings.BASE_DIR, 'cts_forms', 'response_templates')

    def handle(self, *args, **options):
        templates = os.scandir(self.templates_dir)
        for template in templates:
            if template.is_file() and template.name.endswith('.md'):
                with open(template, 'r') as f:
                    content = frontmatter.load(f)

                    letter_id = content['title']
                    letter_data = {
                        'subject': content['subject'],
                        'language': content['language'],
                        'body': content,
                    }
                    letter, created = ResponseTemplate.objects.update_or_create(title=letter_id, defaults=letter_data)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created response template: {letter_id}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated response template: {letter_id}'))
