import os
import urllib.parse

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.generic import FormView, View, TemplateView
from django.views.decorators.cache import cache_control
from formtools.wizard.views import SessionWizardView

from .filters import report_filter
from .forms import (CommentActions, ComplaintActions, ResponseActions,
                    ContactEditForm, Filters, ReportEditForm, Review,
                    add_activity)
from .model_variables import (COMMERCIAL_OR_PUBLIC_PLACE_DICT,
                              CORRECTIONAL_FACILITY_LOCATION_DICT,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_DICT,
                              ELECTION_DICT, EMPLOYER_SIZE_DICT,
                              HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
                              PRIMARY_COMPLAINT_DICT,
                              PRIMARY_COMPLAINT_CHOICES,
                              PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
                              PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
                              LANDING_COMPLAINT_DICT,
                              LANDING_COMPLAINT_CHOICES_TO_EXAMPLES,
                              LANDING_COMPLAINT_CHOICES_TO_HELPTEXT,
                              PUBLIC_OR_PRIVATE_EMPLOYER_DICT,
                              PUBLIC_OR_PRIVATE_SCHOOL_DICT)
from .models import CommentAndSummary, Report, Trends
from .page_through import pagination

SORT_DESC_CHAR = '-'


def error_400(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 400,
            'message': _("Bad request"),
            'helptext': _("It seems your browser is not responding properly. Try refreshing this page.")
        },
        status=400
    )


def error_403(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 403,
            'message': _("Unauthorized"),
            'helptext': _("This page is off limits to unauthorized users.")
        },
        status=403
    )


def error_404(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 404,
            'message': _("We can't find the page you are looking for"),
            'helptext': _("Try returning to the previous page")
        },
        status=404
    )


def error_500(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 500,
            'message': _("There's a problem loading this page"),
            'helptext': _("There's a technical problem loading this page. Try refreshing this page or going to another page. If that doesn't work, try again later.")
        },
        status=500
    )


def error_501(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 501,
            'message': _("Not implemented"),
            'helptext': _("There seems to be a problem with this request. Try refreshing the page.")
        },
        status=501
    )


def error_502(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 502,
            'message': _("Bad gateway"),
            'helptext': _("This problem is due to poor IP communication between back-end computers, possibly including our web server. Try clearing your browser cache completely. You may have a problem with your internal internet connection or firewall.")
        },
        status=502
    )


def error_503(request, exception=None):
    return render(
        request,
        'forms/errors.html', {
            'status': 503,
            'message': _("Service Unavailable"),
            'helptext': _("Our web server is either closed for repair, upgrades or is rebooting. Please try again later.")
        },
        status=503
    )


def csrf_failure(request, reason=""):
    return render(
        request,
        'forms/errors.html', {
            'status': "Problem with security cookie",
            'message': _("Your browser couldn't create a secure cookie"),
            'helptext': _("We use security cookies to protect your information from attackers. Make sure you allow cookies for this site. Having the page open for long periods can also cause this problem. If you know cookies are allowed and you are having this issue, try going to this page in new browser tab or window. That will make you a new security cookie and should resolve the problem.")
        },
        status=403
    )


def format_protected_class(p_class_objects, other_class):
    p_class_list = []
    for p_class in p_class_objects:
        if p_class.value:
            code = p_class.code
            if code != 'Other':
                p_class_list.append(code)
            # If this code is other but there is no other_class description, we want it to say "Other". If there is an other_class that will take the place of "Other"
            elif other_class is None:
                p_class_list.append(code)

    return p_class_list


@login_required
def IndexView(request):
    report_query, query_filters = report_filter(request)

    # Sort data based on request from params, default to `created_date` of complaint
    sort = request.GET.getlist('sort', ['-create_date'])
    per_page = request.GET.get('per_page', 15)
    page = request.GET.get('page', 1)

    # Validate requested sort params
    report_fields = [f.name for f in Report._meta.fields]
    if all(elem.replace("-", '') in report_fields for elem in sort) is False:
        raise Http404(f'Invalid sort request: {sort}')

    requested_reports = report_query.order_by(*sort)
    paginator = Paginator(requested_reports, per_page)
    requested_reports, page_format = pagination(paginator, page, per_page)

    sort_state = {}
    # make sure the links for this page have the same paging, sorting, filtering etc.
    page_args = f'?per_page={per_page}'
    filter_args = ''

    for query_item in query_filters.keys():
        arg = query_item
        for item in query_filters[query_item]:
            filter_args = filter_args + f'&{arg}={item}'

    for sort_item in sort:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_state.update({sort_item[1::]: True})
        else:
            sort_state.update({sort_item: False})

        # all query params except info about what page we are on
        page_args = page_args + f'&sort={sort_item}{filter_args}'

    all_args_encoded = urllib.parse.quote(f'{page_args}&page={page}')

    data = []

    for report in requested_reports:
        p_class_list = format_protected_class(
            report.protected_class.all().order_by('form_order'),
            report.other_class,
        )
        if report.other_class:
            p_class_list.append(report.other_class)
        if len(p_class_list) > 3:
            p_class_list = p_class_list[:3]
            p_class_list[2] = f'{p_class_list[2]}...'

        data.append({
            "report": report,
            "report_protected_classes": p_class_list,
            "url": f'{report.id}?next={all_args_encoded}'

        })

    final_data = {
        'form': Filters(request.GET),
        'data_dict': data,
        'page_format': page_format,
        'page_args': page_args,
        'sort_state': sort_state,
        'filter_state': filter_args,
        'filters': query_filters,
    }

    return render(request, 'forms/complaint_view/index/index.html', final_data)


def serialize_data(report, request, report_id):
    primary_complaint = [choice[1] for choice in PRIMARY_COMPLAINT_CHOICES if choice[0] == report.primary_complaint]
    crimes = {
        'physical_harm': False,
        'trafficking': False
    }

    # for archival data
    for crime in report.hatecrimes_trafficking.all():
        for choice in HATE_CRIMES_TRAFFICKING_MODEL_CHOICES:
            if crime.value == choice[0]:
                crimes[choice[0]] = True

    p_class_list = format_protected_class(
        report.protected_class.all().order_by('form_order'),
        report.other_class,
    )

    output = {
        'actions': ComplaintActions(instance=report),
        'responses': ResponseActions(instance=report),
        'comments': CommentActions(),
        'activity_stream': report.target_actions.all(),
        'crimes': crimes,
        'data': report,
        'p_class_list': p_class_list,
        'primary_complaint': primary_complaint,
        'return_url_args': request.GET.get('next', ''),
        'summary': report.get_summary,
    }

    return output


class ResponseView(LoginRequiredMixin, View):

    def post(self, request, id):
        report = get_object_or_404(Report, pk=id)
        form = ResponseActions(request.POST, instance=report)

        if form.is_valid() and form.has_changed():
            template_name = form.cleaned_data['templates'].title
            button_type = request.POST['type']
            action = "Copied" if button_type == "copy" else "Printed"
            description = f"{action} '{template_name}' template"
            add_activity(request.user, "Contacted complainant:", description, report)
            messages.add_message(request, messages.SUCCESS, description)

        # preserve the query that got the user to this page
        return_url_args = request.POST.get('next', '')
        next_page = urllib.parse.quote(return_url_args)
        url = f'{report.get_absolute_url()}?next={next_page}'
        return redirect(url)


class ShowView(LoginRequiredMixin, View):
    forms = {
        form.CONTEXT_KEY: form
        for form in [ContactEditForm, ComplaintActions, ReportEditForm]
    }

    def get(self, request, id):
        report = get_object_or_404(Report, pk=id)
        output = serialize_data(report, request, id)
        contact_form = ContactEditForm(instance=report)
        details_form = ReportEditForm(instance=report)

        output.update({
            'contact_form': contact_form,
            'details_form': details_form,
        })

        return render(request, 'forms/complaint_view/show/index.html', output)

    def get_form(self, request, report):
        form_type = request.POST.get('type')
        if not form_type:
            raise SuspiciousOperation("Invalid form data")
        return self.forms[form_type](request.POST, instance=report), form_type

    def post(self, request, id):
        """
        Multiple forms are provided on the page
        Accept only the submitted form and discard any other inbound changes
        """
        report = get_object_or_404(Report, pk=id)

        form, inbound_form_type = self.get_form(request, report)
        if form.is_valid() and form.has_changed():
            report = form.save(commit=False)

            # district and location are on different forms so handled here.
            # If the incident location changes, update the district.
            # District can be overwritten in the drop down.
            # If there was a location change but no new match for district, don't override.
            if 'district' not in form.changed_data:
                current_district = report.district
                assigned_district = report.assign_district()
                if assigned_district and current_district != assigned_district:
                    report.district = assigned_district
                    description = f'Updated from "{current_district}" to "{report.district}"'
                    add_activity(request.user, "District:", description, report)

            report.save()
            form.update_activity_stream(request.user)
            messages.add_message(request, messages.SUCCESS, form.success_message())
            #  preserve the query that got the user to this page
            return_url_args = request.POST.get('next', '')
            next_page = urllib.parse.quote(return_url_args)
            url = f'{report.get_absolute_url()}?next={next_page}'
            return redirect(url)
        else:
            output = serialize_data(report, request, id)
            output.update({inbound_form_type: form})

            try:
                fail_message = form.FAIL_MESSAGE
            except AttributeError:
                fail_message = 'No updates applied'
            messages.add_message(request, messages.ERROR, fail_message)

            # provide new forms for those not submitted
            for form_type, form in self.forms.items():
                if form_type != inbound_form_type:
                    output.update({form_type: form(instance=report)})

            return render(request, 'forms/complaint_view/show/index.html', output)


class SaveCommentView(LoginRequiredMixin, FormView):
    """Can be used for saving comments or summaries for a report"""
    form_class = CommentActions

    def post(self, request, report_id):
        """Update or create inbound comment"""
        report = get_object_or_404(Report, pk=report_id)
        comment_id = request.POST.get('comment_id')
        if comment_id:
            instance = get_object_or_404(CommentAndSummary, id=comment_id)
        else:
            instance = None

        comment_form = CommentActions(request.POST, instance=instance)

        if comment_form.is_valid() and comment_form.has_changed():
            comment = comment_form.save()
            report.internal_comments.add(comment)
            verb = 'Updated comment: ' if instance else 'Added comment: '

            messages.add_message(request, messages.SUCCESS, f'Successfully {verb[:-2].lower()}.')
            comment_form.update_activity_stream(request.user, report, verb)

            #  preserve the query that got the user to this page
            return_url_args = request.POST.get('next', '')
            next_page = urllib.parse.quote(return_url_args)
            url = f'{report.get_absolute_url()}?next={next_page}'
            return redirect(url)
        else:
            # TODO handle form validation failures
            output = serialize_data(report, request, report_id)
            output.update({
                'return_url_args': request.POST.get('next', ''),
            })

            return render(request, 'forms/complaint_view/show/index.html', output)


def save_form(form_data_dict, **kwargs):
    m2m_protected_class = form_data_dict.pop('protected_class')
    r = Report.objects.create(**form_data_dict)

    # Many to many fields need to be added or updated to the main model, with a related manager such as add() or update()
    for protected in m2m_protected_class:
        r.protected_class.add(protected)

    r.assigned_section = r.assign_section()
    r.district = r.assign_district()
    if kwargs.get('intake_format'):
        r.intake_format = kwargs.get('intake_format')
    r.save()
    # adding this back for the save page results
    form_data_dict['protected_class'] = m2m_protected_class.values()
    return form_data_dict, r


class ProFormView(LoginRequiredMixin, SessionWizardView):
    def get_template_names(self):
        return 'forms/pro_template.html'

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        field_errors = list(map(lambda field: field.errors, context['form']))
        page_errors = [error for field in field_errors for error in field]

        # internal use only
        ordered_step_names = [
            'Intake',
            'Contact',
            'Service member',
            'Primary concern',
            'Incident location',
            'Personal characteristics',
            'Date',
            'Summary',
        ]

        context.update({
            'field_errors': field_errors,
            'page_errors': page_errors,
            'num_page_errors': len(list(page_errors)),
            'word_count_text': {
                'wordRemainingText': _('word remaining'),
                'wordsRemainingText': _(' words remaining'),
                'wordLimitReachedText': _(' word limit reached'),
            },
            'ordered_step_names': ordered_step_names,
            'stage_link': True,
            'submit_button': True,
        })

        return context

    def done(self, form_list, form_dict, **kwargs):
        data, report = save_form(self.get_all_cleaned_data())

        return redirect(reverse('crt_forms:crt-forms-show', kwargs={'id': report.pk}))


TEMPLATES = [
    # Contact
    'forms/report_contact_info.html',
    # Primary reason
    'forms/report_primary_complaint.html',
    # Hate crimes
    'forms/report_hate_crime.html',
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


class LandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        all_complaints = {
            **PRIMARY_COMPLAINT_DICT,
            **LANDING_COMPLAINT_DICT,
        }
        all_examples = {
            **PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
            **LANDING_COMPLAINT_CHOICES_TO_EXAMPLES,
        }
        all_helptext = {
            **PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
            **LANDING_COMPLAINT_CHOICES_TO_HELPTEXT,
        }
        choices = {
            key: {
                'description': description,
                'examples': all_examples.get(key, []),
                'helptext': all_helptext.get(key, ''),
            }
            for key, description in all_complaints.items()
            if key != 'something_else'  # exclude because this choice has no examples
        }
        return {'choices': choices}


@method_decorator(cache_control(private=True), name='dispatch')
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
        return form_class(**kwargs)

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
            # unpack values in data for display
            form_data_dict['primary_complaint'] = data_decode(
                form_data_dict, PRIMARY_COMPLAINT_DICT, 'primary_complaint'
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
                'question': form.question_text
            })

        return context

    def done(self, form_list, form_dict, **kwargs):
        form_data_dict = self.get_all_cleaned_data()
        _, report = save_form(form_data_dict, intake_format='web')
        return render(
            self.request, 'forms/confirmation.html',
            {
                'report': report, 'questions': Review.question_text,
                'ordered_step_names': self.ORDERED_STEP_NAMES
            },
        )


class TrendView(LoginRequiredMixin, TemplateView):
    template_name = "forms/complaint_view/trends.html"

    def get_context_data(self, **kwargs):
        return {
            'this_week': Trends.objects.filter(record_type='this_week'),
            'last_week': Trends.objects.filter(record_type='last_week'),
            'four_weeks': Trends.objects.filter(record_type='four_weeks'),
            'year': Trends.objects.filter(record_type='year'),
        }
