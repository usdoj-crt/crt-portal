import os
import frontmatter
import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from cts_forms.models import ResponseTemplate, ReferralContact


class Command(BaseCommand):  # pragma: no cover
    help = 'Adds new response templates or updates existing ones'

    templates_dir = os.path.join(settings.BASE_DIR, 'cts_forms', 'response_templates')
    template_ids = []

    def handle(self, *args, **options):
        templates = os.scandir(self.templates_dir)
        environment = os.environ.get('ENV', 'UNDEFINED')
        for template in templates:
            if template.is_file() and template.name.endswith('.md'):
                with open(template, 'r') as f:
                    try:
                        content = frontmatter.load(f)
                    except yaml.scanner.ScannerError:
                        self.stdout.write(self.style.ERROR(f'Response template {template.name} front-matter could not be parsed. Skipping it!'))
                        continue

                    try:
                        letter_id = content['title']
                    except KeyError:
                        self.stdout.write(self.style.ERROR(f'Response template {template.name} is missing required `title` property. Skipping it!'))
                        continue

                    if letter_id.startswith('(TEST)') and environment == 'PRODUCTION':
                        self.stdout.write(self.style.SUCCESS(f'Ignoring response template in production: {letter_id}'))
                        continue

                    if content.get('ignore') is True:
                        self.stdout.write(self.style.SUCCESS(f'Ignoring response template: {letter_id}'))
                        continue

                    try:
                        letter_data = {
                            'subject': content['subject'],
                            'language': content['language'],
                            'body': content,
                        }
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Response template {template.name} is missing required `{e.args[0]}` property. Skipping it!'))
                        continue

                    referral_contact_machine_name = content.get('referral_contact')
                    if referral_contact_machine_name:
                        maybe_referral_contact = ReferralContact.objects.filter(machine_name=referral_contact_machine_name).first()
                        if maybe_referral_contact:
                            letter_data['referral_contact'] = maybe_referral_contact
                        else:
                            self.stdout.write(self.style.ERROR(f'Response template {template.name} has an unknown referral_contact {referral_contact_machine_name}'))

                    self.template_ids.append(letter_id)
                    # Mark if a letter should be processed from Markdown to HTML.
                    # This is optional. Default value is false
                    # Note: this does not catch errors or typos in values.
                    letter_data['is_html'] = content.get('is_html', False)
                    letter_data['show_in_dropdown'] = content.get('show_in_dropdown', True)
                    letter_data['is_user_created'] = False

                    letter, created = ResponseTemplate.objects.update_or_create(title=letter_id, defaults=letter_data)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created response template: {letter.title}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated response template: {letter.title}'))

        for object in ResponseTemplate.objects.filter(is_user_created=False).exclude(title__in=self.template_ids):
            letter_id = object.title
            letter_data = {
                'show_in_dropdown': False,
            }
            letter = ResponseTemplate.objects.update_or_create(title=letter_id, defaults=letter_data)
            self.stdout.write(self.style.SUCCESS(f'Updated response template: {object.title}'))
