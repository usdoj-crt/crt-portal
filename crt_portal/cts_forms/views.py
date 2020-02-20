import urllib.parse
import os

from django.shortcuts import render_to_response, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.http import Http404
from django.views.generic import View
from django import forms

from formtools.wizard.views import SessionWizardView

from actstream import action

from .models import Report, ProtectedClass, HateCrimesandTrafficking
from .model_variables import PROTECTED_CLASS_CODES, PRIMARY_COMPLAINT_CHOICES, HATE_CRIMES_TRAFFICKING_MODEL_CHOICES
from .page_through import pagination
from .filters import report_filter
from .forms import Filters, ComplaintActions

SORT_DESC_CHAR = '-'


def format_protected_class(p_class_objects, other_class):
    p_class_list = []
    for p_class in p_class_objects:
        if p_class.protected_class is not None:
            code = PROTECTED_CLASS_CODES.get(p_class.protected_class, p_class.protected_class)
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

    return render_to_response('forms/complaint_view/index/index.html', final_data)


class ShowView(View):
    def __serialize_data(self, request, report_id):
        report = get_object_or_404(Report.objects, id=report_id)
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
                'status': report.status
            }),
            'activity_stream': report.target_actions.all(),
            'crimes': crimes,
            'data': report,
            'p_class_list': p_class_list,
            'primary_complaint': primary_complaint,
            'return_url_args': request.GET.get('next', ''),
        }

        return output

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, id):
        output = self.__serialize_data(request, id)

        return render(request, 'forms/complaint_view/show/index.html', output)

    def post(self, request, id):
        record = Report.objects.filter(id=id)
        report = record[0]

        updates = {}

        # see custom message options https://django-activity-stream.readthedocs.io/en/latest/data.html
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken' and key != 'next':
                updates[key] = value
                action_verb_target = ' '.join(key.split('_'))
                action_verb = f"updated {action_verb_target}"
                action_description = f"with value {value}"

                action.send(
                    request.user,
                    verb=action_verb,
                    description=action_description,
                    target=report
                )

        record.update(**updates)

        output = self.__serialize_data(request, id)
        output.update({
            'return_url_args': request.POST.get('next', ''),
        })

        return render(request, 'forms/complaint_view/show/index.html', output)


TEMPLATES = [
    # Contact
    'forms/report_grouped_questions.html',
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


def show_location_form_condition(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('1') or {'primary_complaint': 'not yet completed'}

    if not cleaned_data['primary_complaint'] in conditional_location_routings:
        return True
    return False


class CRTReportWizard(SessionWizardView):
    """Once all the sub-forms are submitted this class will clean data and save."""

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
        ordered_step_names = [
            _('Contact'),
            _('Primary Issue'),
            _('Location'),
            _('Protected Class'),
            _('Date'),
            _('Details'),
        ]
        # Name for all forms whether they are skipped or not
        all_step_names = [
            _('Contact'),
            _('Primary Issue'),
            _('Primary Issue'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Location'),
            _('Protected Class'),
            _('Date'),
            _('Details'),
        ]

        current_step_name = all_step_names[int(self.steps.current)]

        # This title appears in large font above the question elements
        ordered_step_titles = [
            _('Contact'),
            _('Primary issue'),
            _('Primary issue'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Location details'),
            _('Please provide details'),
            _('Date'),
            _('Details'),
        ]
        current_step_title = ordered_step_titles[int(self.steps.current)]
        form_autocomplete_off = os.getenv('FORM_AUTOCOMPLETE_OFF', False)

        context.update({
            'ordered_step_names': ordered_step_names,
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
            'form_name': form_name
        })

        if current_step_name == _('Details'):
            context.update({
                'page_note': _('Continued'),
            })
        elif current_step_name == _('Location'):
            context.update({
                'page_note': _('Providing details on where this occurred helps us properly review your issue and get it to the right people within the Civil Rights Division.'),
            })
        elif current_step_name == _('Date'):
            context.update({
                'page_note': _('It is important for us to know how recently this incident happened. Some civil rights violations must be reported within a certain amount of time.')
            })
        elif current_step_name == _('Primary Issue'):
            if all_step_names[int(self.steps.prev)] == current_step_name:
                context.update({
                    'page_note': _('Continued')
                })
            else:
                context.update({
                    'crime_help_text2': _('Please select if any that apply to your situation (optional)'),
                })

        return context

    def done(self, form_list, form_dict, **kwargs):
        form_data_dict = self.get_all_cleaned_data()
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
        r.save()
        # adding this back for the save page results
        form_data_dict['protected_class'] = m2m_protected_class.values()
        form_data_dict['hatecrimes_trafficking'] = m2m_hatecrime.values()

        return render_to_response('forms/confirmation.html', {'data_dict': form_data_dict})
