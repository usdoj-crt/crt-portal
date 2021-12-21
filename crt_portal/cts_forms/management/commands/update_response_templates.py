import os
import frontmatter
import yaml
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
                    try:
                        content = frontmatter.load(f)
                    except yaml.scanner.ScannerError:
                        self.stdout.write(self.style.ERROR(
                            f'Response template {template.name} front-matter could not be parsed. Skipping it!'))
                        continue

                    try:
                        letter_id = content['title']
                    except KeyError:
                        self.stdout.write(self.style.ERROR(
                            f'Response template {template.name} is missing required `title` property. Skipping it!'))
                        continue

                    if content.get('ignore', False):
                        self.stdout.write(self.style.SUCCESS(f'Ignoring response template: {letter_id}'))
                        continue

                    try:
                        letter_data = {
                            'subject': content['subject'],
                            'language': content['language'],
                            'body': content,
                        }
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(
                            f'Response template {template.name} is missing required `{e.args[0]}` property. Skipping it!'))
                        continue

                    letter, created = ResponseTemplate.objects.update_or_create(title=letter_id, defaults=letter_data)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created response template: {letter.title}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated response template: {letter.title}'))
