import os
import urllib.parse

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, FormView
from formtools.wizard.views import SessionWizardView

from .filters import report_filter
from .forms import ComplaintActions, CommentActions, Filters, Review
from .model_variables import (COMMERCIAL_OR_PUBLIC_PLACE_DICT,
                              CORRECTIONAL_FACILITY_LOCATION_DICT,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_DICT,
                              ELECTION_DICT, EMPLOYER_SIZE_DICT,
                              HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
                              PRIMARY_COMPLAINT_CHOICES,
                              PRIMARY_COMPLAINT_DICT,
                              PUBLIC_OR_PRIVATE_EMPLOYER_DICT,
                              PUBLIC_OR_PRIVATE_SCHOOL_DICT)
from .models import HateCrimesandTrafficking, ProtectedClass, Report, CommentAndSummary
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
            'helptext': _("Try retuning to the previous page")
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
        }
    )


def format_protected_class(p_class_objects, other_class):
    p_class_list = []
    for p_class in p_class_objects:
        if p_class.protected_class is not None:
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
        'auth': 'DJFKDSFJSD'
    }

    return render(request, 'forms/complaint_view/index/index.html', final_data)


def serialize_data(report, request, report_id):
    primary_complaint = [choice[1] for choice in PRIMARY_COMPLAINT_CHOICES if choice[0] == report.primary_complaint]
    crimes = {
        'physical_harm': False,
        'trafficking': False
    }

    for crime in report.hatecrimes_trafficking.all():
        for choice in HATE_CRIMES_TRAFFICKING_MODEL_CHOICES:
            if crime.hatecrimes_trafficking_option == choice[1]:
                crimes[choice[0]] = True

    p_class_list = format_protected_class(
        report.protected_class.all().order_by('form_order'),
        report.other_class,
    )

    output = {
        'actions': ComplaintActions(initial={
            'assigned_section': report.assigned_section,
            'status': report.status,
            'primary_statute': report.primary_statute,
            'district': report.district,
        }),
        'comments': CommentActions(),
        'activity_stream': report.target_actions.all(),
        'crimes': crimes,
        'data': report,
        'p_class_list': p_class_list,
        'primary_complaint': primary_complaint,
        'return_url_args': request.GET.get('next', ''),
    }

    return output


class ShowView(LoginRequiredMixin, View):
    def get(self, request, id):
        report = get_object_or_404(Report, pk=id)
        output = serialize_data(report, request, id)

        return render(request, 'forms/complaint_view/show/index.html', output)

    def post(self, request, id):
        report = get_object_or_404(Report, pk=id)
        action_form = ComplaintActions(request.POST, instance=report)
        if action_form.is_valid() and action_form.has_changed():
            action_form.update_activity_stream(request.user)
            action_form.save()

        output = serialize_data(report, request, id)
        output.update({
            'return_url_args': request.POST.get('next', ''),
        })

        return render(self.request, 'forms/complaint_view/show/index.html', output)


class SaveCommentView(LoginRequiredMixin, FormView):
    """Can be used for saving comments or summaries for a report"""
    form_class = CommentActions

    def post(self, request, report_id):
        report = get_object_or_404(Report, pk=report_id)
        if request.POST.__getitem__('note'):
            comment = CommentAndSummary.objects.create(
                note=request.POST.__getitem__('note'),
                is_summary=request.POST.__getitem__('is_summary'),
            )
            report.internal_comments.add(comment)
            CommentActions.update_activity_stream(request.user, report, comment.note)
        output = serialize_data(report, request, report_id)
        output.update({
            'return_url_args': request.POST.get('next', ''),
        })
        return render(request, 'forms/complaint_view/show/index.html', output)


def save_form(form_data_dict):
    m2m_protected_class = form_data_dict.pop('protected_class')
    m2m_hatecrime = form_data_dict.pop('hatecrimes_trafficking')
    r = Report.objects.create(**form_data_dict)

    # add a save feature for hatecrimes and trafficking question on primary reason page
    # Many to many fields need to be added or updated to the main model, with a related manager such as add() or update()
    for protected in m2m_protected_class:
        p = ProtectedClass.objects.get(protected_class=protected)
        r.protected_class.add(p)

    for option in m2m_hatecrime:
        o = HateCrimesandTrafficking.objects.get(hatecrimes_trafficking_option=option)
        r.hatecrimes_trafficking.add(o)

    r.assigned_section = r.assign_section()
    r.district = r.assign_district()
    r.save()
    # adding this back for the save page results
    form_data_dict['protected_class'] = m2m_protected_class.values()
    form_data_dict['hatecrimes_trafficking'] = m2m_hatecrime.values()
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
            'Follow up',
            'Incident location',
            'Personal characteristics',
            'Date',
            'Summary',
        ]

        context.update({
            'field_errors': field_errors,
            'page_errors': page_errors,
            'num_page_errors': len(list(page_errors)),
            'page_errors_desc': ','.join([f'"{error_desc}"' for error_desc in page_errors]),
            'word_count_text': {
                'wordRemainingText': _('word remaining'),
                'wordsRemainingText': _(' words remaining'),
                'wordLimitReachedText': _(' word limit reached'),
            },
            'ordered_step_names': ordered_step_names,
            'stage_link': True,
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
    # Hate crimes and trafficking
    'forms/report_grouped_questions.html',
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
            _('Review your concern'),
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

            # Get values for M2M fields destined for association with this Report instance
            hatecrimes = [crime.hatecrimes_trafficking_option for crime in form_data_dict.pop('hatecrimes_trafficking')]
            protected_class = [choice.protected_class for choice in form_data_dict.pop('protected_class')]

            context.update({
                'report': Report(**form_data_dict),
                'hatecrimes': hatecrimes,
                'protected_classes': protected_class,
                'question': form.question_text,
            })

        return context

    def done(self, form_list, form_dict, **kwargs):
        form_data_dict = self.get_all_cleaned_data()
        _, report = save_form(form_data_dict)
        return render(self.request, 'forms/confirmation.html', {'report': report, 'questions': Review.question_text,
                                                                'ordered_step_names': self.ORDERED_STEP_NAMES})
