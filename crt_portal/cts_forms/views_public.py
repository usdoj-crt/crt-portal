"""
These are the views that are available to the public.
 - All public copy needs to be available for translation
 - URLs for public pages need to be declared in the settings
"""
import os
import logging

from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from formtools.wizard.views import SessionWizardView
from tms.models import TMSEmail

from .model_variables import (COMMERCIAL_OR_PUBLIC_PLACE_DICT,
                              CORRECTIONAL_FACILITY_LOCATION_DICT,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_DICT,
                              ELECTION_DICT, EMPLOYER_SIZE_DICT,
                              LANDING_COMPLAINT_CHOICES_TO_EXAMPLES,
                              LANDING_COMPLAINT_CHOICES_TO_HELPTEXT,
                              LANDING_COMPLAINT_CHOICES_TO_HELPLINK,
                              LANDING_COMPLAINT_CHOICES_TO_NOTE,
                              LANDING_COMPLAINT_CHOICES_TO_PREAMBLE,
                              LANDING_COMPLAINT_CHOICES_TO_LEARNMORE,
                              LANDING_COMPLAINT_DICT,
                              PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
                              PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES_VOTING,
                              PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
                              PRIMARY_COMPLAINT_DICT,
                              PRIMARY_COMPLAINT_DICT_VOTING,
                              PUBLIC_OR_PRIVATE_EMPLOYER_DICT,
                              PUBLIC_OR_PRIVATE_SCHOOL_DICT)
from .models import Report, ResponseTemplate, EmailReportCount, Campaign
from .forms import save_form, Review
from .mail import mail_to_complainant
from utils.voting_mode import is_voting_mode


logger = logging.getLogger(__name__)


class LandingPageView(TemplateView):
    """Homepage"""
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        primary_complaint_dictionary = PRIMARY_COMPLAINT_DICT_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_DICT
        all_complaints = {
            **primary_complaint_dictionary,
            **LANDING_COMPLAINT_DICT,
        }
        complaint_choices_examples = PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES
        all_examples = {
            **complaint_choices_examples,
            **LANDING_COMPLAINT_CHOICES_TO_EXAMPLES,
        }
        all_helptext = {
            **PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
            **LANDING_COMPLAINT_CHOICES_TO_HELPTEXT,
        }
        all_helplinks = {
            **LANDING_COMPLAINT_CHOICES_TO_HELPLINK,
        }
        all_learnmore = {
            **LANDING_COMPLAINT_CHOICES_TO_LEARNMORE,
        }
        all_note = {
            **LANDING_COMPLAINT_CHOICES_TO_NOTE,
        }
        all_preamble = {
            **LANDING_COMPLAINT_CHOICES_TO_PREAMBLE,
        }
        choices = [
            {
                'key': key,
                'description': description,
                'examples': all_examples.get(key, []),
                'helptext': all_helptext.get(key, ''),
                'helplink': all_helplinks.get(key, {}),
                'learnmore': all_learnmore.get(key, ''),
                'preamble': all_preamble.get(key, ''),
                'note': all_note.get(key, ''),
            }
            for key, description in all_complaints.items()
            if key != 'something_else'  # exclude because this choice has no examples
        ]
        return {'choices': choices}


# Public form view starts here #
TEMPLATES = [
    # Contact
    'forms/report_contact_info.html',
    # Primary reason
    'forms/report_primary_complaint.html',
    # Voting + location
    'forms/report_location.html',
    # Workplace + location
    'forms/report_location.html',
    # Police + location
    'forms/report_location.html',
    # Commercial/Public + location
    'forms/report_location.html',
    # Education + location
    'forms/report_location.html',
    # Location
    'forms/report_location.html',
    # Protected Class
    'forms/report_class.html',
    # Date
    'forms/report_date.html',
    # Details
    'forms/report_details.html',
    # Review page
    'forms/report_review.html',
]

conditional_location_routings = ['voting', 'workplace', 'police', 'commercial_or_public', 'education']


def is_routable_complaint(wizard, primary_complaint):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('1') or {'primary_complaint': 'not yet completed'}
    if cleaned_data['primary_complaint'] == primary_complaint:
        return True
    return False


def show_election_form_condition(wizard):
    return is_routable_complaint(wizard, 'voting')


def show_workplace_form_condition(wizard):
    return is_routable_complaint(wizard, 'workplace')


def show_police_form_condition(wizard):
    return is_routable_complaint(wizard, 'police')


def show_commercial_public_form_condition(wizard):
    return is_routable_complaint(wizard, 'commercial_or_public')


def show_education_form_condition(wizard):
    return is_routable_complaint(wizard, 'education')


def data_decode(form_data_dict, decoder_dict, value):
    return decoder_dict.get(
        form_data_dict.get(value)
    )


def show_location_form_condition(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('1') or {'primary_complaint': 'not yet completed'}

    if not cleaned_data['primary_complaint'] in conditional_location_routings:
        return True
    return False


def send_autoresponse_mail(report):
    # Guaranteed to find only one email template, or set to None. If the letter template
    # template in the report's language is not found, default to sending the English letter
    template = ResponseTemplate.objects.filter(title='CRT Auto response', language=report.language).first() or ResponseTemplate.objects.filter(title='CRT Auto response', language='en').first()

    # Skip automated response if complainant doesn't provide an email
    # or if the auto response template doesn't exist
    if report.contact_email and template:
        try:
            sent = mail_to_complainant(report, template, TMSEmail.AUTO_EMAIL)
            if sent:
                description = f"Automated response email sent: '{template.title}' to {report.contact_email} for report {report.public_id}"
            else:
                description = f"{report.contact_email} not in allowed domains, not attempting to deliver {template.title}."

            # Log this activity to server output.
            # This is not being logged in actstream because it is an autonomous activity,
            # and there's no authenticated user attached to this action.
            # When sending email through TMS, a record will automatically be logged in "Tms emails"
            logger.info(description)
        except Exception as e:  # catch *all* exceptions
            logger.warning({'message': f"Automated response email failed to send: {e}", 'report': report.id})
    else:
        logger.info("Report has no contact email, or autoresponse template not found. No automated response email will be sent.")


@method_decorator(never_cache, name='dispatch')
class CRTReportWizard(SessionWizardView):
    """Once all the sub-forms are submitted this class will clean data and save."""

    ORDERED_STEP_NAMES = [
        _('Contact'),
        _('Primary concern'),
        _('Location'),
        _('Personal characteristics'),
        _('Date'),
        _('Personal description'),
        _('Review'),
    ]

    def get_campaign_initial(self):
        campaign_id = self.request.GET.get('utm_campaign')
        if not campaign_id:
            return {}
        try:
            exists = Campaign.objects.filter(uuid=campaign_id).exists()
        except ValidationError:
            return {'unknown_origination_utm_campaign': campaign_id}
        if not exists:
            return {'unknown_origination_utm_campaign': campaign_id}
        return {'origination_utm_campaign': campaign_id}

    def get_form_initial(self, step):
        initial_dict = super().get_form_initial(step)
        campaign_initial = self.get_campaign_initial()

        return {
            **initial_dict,
            **campaign_initial,
            'origination_utm_source': self.request.GET.get('utm_source'),
            'origination_utm_medium': self.request.GET.get('utm_medium'),
            'origination_utm_term': self.request.GET.get('utm_term'),
            'origination_utm_content': self.request.GET.get('utm_content'),
        }

    def form_refreshed(self):
        """
        True if the form and associated session data have been refreshed and cleared
        which invalidates the submission and requires a user to restart the form.
        """
        form_current_step = self.request.POST.get('crt_report_wizard-current_step', None)
        return (form_current_step != self.steps.current and self.storage.current_step is not None)

    def post(self, *args, **kwargs):
        """
        Prior to handling the inbound request, check for and handle
        session data which has been cleared while someone is progressing through
        the form
        """
        if self.form_refreshed():
            return error_422(self.request)
        return super().post(*args, **kwargs)

    def get(self, request):
        if settings.MAINTENANCE_MODE:
            return render(self.request, 'forms/report_maintenance.html', status=503)
        return super().get(request)

    # overriding the get form to add checks to the hidden field and avoid 500s
    def get_form(self, step=None, data=None, files=None):
        """
        Constructs the form for a given `step`. If no `step` is defined, the
        current step will be determined automatically.
        The form will be initialized using the `data` argument to prefill the
        new form. If needed, instance or queryset (for `ModelForm` or
        `ModelFormSet`) will be added too.
        """
        if step is None:
            step = self.steps.current
        # added check to see if people are messing with the form
        elif not step.isdigit() or int(step) > len(TEMPLATES):
            raise PermissionDenied

        form_class = self.form_list[step]
        # prepare the kwargs for the form instance.
        kwargs = self.get_form_kwargs(step)
        kwargs.update({
            'data': data,
            'files': files,
            'prefix': self.get_form_prefix(step, form_class),
            'initial': self.get_form_initial(step),
        })
        if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
            # If the form is based on ModelForm or InlineFormSet,
            # add instance if available and not previously set.
            kwargs.setdefault('instance', self.get_form_instance(step))
        elif issubclass(form_class, forms.models.BaseModelFormSet):
            # If the form is based on ModelFormSet, add queryset if available
            # and not previous set.
            kwargs.setdefault('queryset', self.get_form_instance(step))
        result = form_class(**kwargs)
        setattr(result, 'request', self.request)
        return result

    def get_template_names(self):
        return [TEMPLATES[int(self.steps.current)]]

    def get_context_data(self, form, **kwargs):
        context = super(CRTReportWizard, self).get_context_data(form=form, **kwargs)
        field_errors = list(map(lambda field: field.errors, context['form']))
        page_errors = [error for field in field_errors for error in field]
        form_name = form.name if hasattr(form, 'name') else ''

        # This name appears in the progress bar wizard

        # Name for all forms whether they are skipped or not
        all_step_names = [
            _('Contact'),
            _('Primary concern'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Personal characteristics'),
            _('Date'),
            _('Personal description'),
            _('Review'),
        ]

        current_step_name = all_step_names[int(self.steps.current)]

        # This title appears in large font above the question elements
        ordered_step_titles = [
            _('Contact'),
            _('Primary concern'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Personal characteristics'),
            _('Date'),
            _('Personal description'),
            _('Review your report'),
        ]
        current_step_title = ordered_step_titles[int(self.steps.current)]
        form_autocomplete_off = os.getenv('FORM_AUTOCOMPLETE_OFF', False)

        context.update({
            'ordered_step_names': self.ORDERED_STEP_NAMES,
            'current_step_title': current_step_title,
            'current_step_name': current_step_name,
            'page_errors': page_errors,
            'num_page_errors': len(list(page_errors)),
            'page_errors_desc': ','.join([f'"{error_desc}"' for error_desc in page_errors]),
            # Disable default client-side validation
            'form_novalidate': True,
            'form_autocomplete_off': form_autocomplete_off,
            'word_count_text': {
                'wordRemainingText': _('word remaining'),
                'wordsRemainingText': _(' words remaining'),
                'wordLimitReachedText': _(' word limit reached'),
            },
            'form_name': form_name,
            'stage_number': self.ORDERED_STEP_NAMES.index(current_step_name) + 1,
            'total_stages': len(self.ORDERED_STEP_NAMES),
        })

        if current_step_name == _('Primary concern'):
            if all_step_names[int(self.steps.prev)] != current_step_name:
                context.update({
                    'crime_help_text2': _('Please select if any that apply to your situation (optional)'),
                })
        elif current_step_name == _('Review'):
            form_data_dict = self.get_all_cleaned_data()
            # remember primary complaint key (it's overwritten in the next step)
            # this variable improves some conditional display logic in templates
            primary_complaint_key = form_data_dict['primary_complaint']
            # unpack values in data for display
            primary_complaint_dictionary = PRIMARY_COMPLAINT_DICT_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_DICT
            form_data_dict['primary_complaint'] = data_decode(
                form_data_dict, primary_complaint_dictionary, 'primary_complaint'
            )
            form_data_dict['election_details'] = data_decode(
                form_data_dict, ELECTION_DICT, 'election_details'
            )
            form_data_dict['public_or_private_employer'] = data_decode(
                form_data_dict, PUBLIC_OR_PRIVATE_EMPLOYER_DICT, 'public_or_private_employer'
            )
            form_data_dict['employer_size'] = data_decode(
                form_data_dict, EMPLOYER_SIZE_DICT, 'employer_size'
            )
            form_data_dict['inside_correctional_facility'] = data_decode(
                form_data_dict, CORRECTIONAL_FACILITY_LOCATION_DICT, 'inside_correctional_facility'
            )
            form_data_dict['correctional_facility_type'] = data_decode(
                form_data_dict, CORRECTIONAL_FACILITY_LOCATION_TYPE_DICT, 'correctional_facility_type'
            )
            form_data_dict['commercial_or_public_place'] = data_decode(
                form_data_dict, COMMERCIAL_OR_PUBLIC_PLACE_DICT, 'commercial_or_public_place'
            )
            form_data_dict['public_or_private_school'] = data_decode(
                form_data_dict, PUBLIC_OR_PRIVATE_SCHOOL_DICT, 'public_or_private_school'
            )

            context.update({
                'protected_classes': form_data_dict.pop('protected_class'),
                'report': Report(**form_data_dict),
                'question': form.question_text,
                'primary_complaint_key': primary_complaint_key
            })

        return context

    def done(self, form_list, form_dict, **kwargs):
        form_data_dict = self.get_all_cleaned_data()
        _, report = save_form(form_data_dict, intake_format='web')

        if settings.EMAIL_AUTORESPONSE_ENABLED:
            send_autoresponse_mail(report)
        EmailReportCount.refresh_view()
        return render(
            self.request, 'forms/confirmation.html',
            {
                'report': report,
                'questions': Review.question_text,
                'ordered_step_names': self.ORDERED_STEP_NAMES
            },
        )


# Error pages start here #
def error_400(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 400,
        },
        status=400
    )


def error_403(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 403,
        },
        status=403
    )


def error_404(request, exception=None):
    return render(
        request,
        'forms/errors_heading.html', {
            'status': _("404 | Page not found"),
            'message': _("We can't find the page you are looking for")
        },
        status=404
    )


def error_422(request):
    return render(
        request,
        'forms/error_422.html',
        status=422
    )


def error_500(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 500
        },
        status=500
    )


def error_501(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 501,
        },
        status=501
    )


def error_502(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 502,
        },
        status=502
    )


def error_503(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 503,
        },
        status=503
    )


def csrf_failure(request, reason=""):
    return render(
        request,
        'forms/errors_heading.html', {
            'status': "Problem with security cookie",
            'message': _("Your browser couldn't create a secure cookie"),
            'helptext': _("We use security cookies to protect your information from attackers. Make sure you allow cookies for this site. Having the page open for long periods can also cause this problem. If you know cookies are allowed and you are having this issue, try going to this page in new browser tab or window. That will make you a new security cookie and should resolve the problem.")
        },
        status=403
    )
