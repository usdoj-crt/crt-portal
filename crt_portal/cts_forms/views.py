import urllib.parse
import os

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.core import serializers
from django.conf import settings

from formtools.wizard.views import SessionWizardView

from .models import Report, ProtectedClass, HateCrimesandTrafficking
from .model_variables import PROTECTED_CLASS_CODES
from .page_through import pagination


SORT_DESC_CHAR = '-'


@login_required
def IndexView(request):
    # Sort data based on request from params, default to `created_date` of complaint
    sort = request.GET.getlist('sort', ['-create_date'])
    per_page = request.GET.get('per_page', 15)
    page = request.GET.get('page', 1)

    # Validate requested sort params
    report_fields = [f.name for f in Report._meta.fields]
    if all(elem.replace("-", '') in report_fields for elem in sort) is False:
        raise Http404(f'Invalid sort request: {sort}')

    requested_reports = Report.objects.order_by(*sort)
    paginator = Paginator(requested_reports, per_page)
    requested_reports, page_format = pagination(paginator, page, per_page)

    sort_state = {}
    # make sure the links for this page have the same paging, sorting, filtering etc.
    page_args = f'?per_page={per_page}'
    for sort_item in sort:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_state.update({sort_item[1::]: True})
        else:
            sort_state.update({sort_item: False})

        page_args = page_args + f'&sort={sort_item}'

    all_args_encoded = urllib.parse.quote(f'{page_args}&page={page}')

    data = []
    # formatting protected class
    for report in requested_reports:
        p_class_list = []
        for p_class in report.protected_class.all().order_by('form_order'):
            if p_class.protected_class is not None:
                code = PROTECTED_CLASS_CODES.get(p_class.protected_class, p_class.protected_class)
                if code != 'Other':
                    p_class_list.append(code)
                # If this code is other but there is no other_class description, we want it to say "Other". If there is an other_class that will take the place of "Other"
                elif report.other_class is None:
                    p_class_list.append(code)

        if report.other_class:
            p_class_list.append(report.other_class)
        if len(p_class_list) > 3:
            p_class_list = p_class_list[:3]
            p_class_list[2] = f'{p_class_list[2]}...'
        data.append({
            "report": report,
            "report_protected_classes": p_class_list,
            "url": f'{report.id}/?next={all_args_encoded}'
        })

    return render_to_response('forms/complaint_view/index.html', {
        'data_dict': data,
        'page_format': page_format,
        'page_args': page_args,
        'sort_state': sort_state
    })


@login_required
def ShowView(request, id):
    report = get_object_or_404(Report.objects, id=id)
    output = {
        'data': report,
        'return_url_args': request.GET.get('next', ''),
    }

    if settings.DEBUG:
        output.update({
            'debug_data': serializers.serialize('json', [report, ])
        })

    return render_to_response('forms/complaint_view/show.html', output)


TEMPLATES = [
    # Contact
    'forms/report_grouped_questions.html',
    # Primary reason
    'forms/report_multiple_questions.html',
    # Location
    'forms/report_location.html',
    # Protected Class
    'forms/report_class.html',
    # Details
    'forms/report_details.html',
]


class CRTReportWizard(SessionWizardView):
    """Once all the sub-forms are submitted this class will clean data and save."""
    def get_template_names(self):
        return [TEMPLATES[int(self.steps.current)]]

    def get_context_data(self, form, **kwargs):
        context = super(CRTReportWizard, self).get_context_data(form=form, **kwargs)

        field_errors = list(map(lambda field: field.errors, context['form']))
        page_errors = [error for field in field_errors for error in field]

        # This name appears in the progress bar wizard
        ordered_step_names = [
            _('Contact'),
            _('Primary Issue'),
            _('Location'),
            _('Protected Class'),
            _('Details'),
        ]
        current_step_name = ordered_step_names[int(self.steps.current)]

        # This title appears in large font above the question elements
        ordered_step_titles = [
            _('Contact'),
            _('What is your primary reason for contacting the Civil Rights Division?'),
            _('Location details'),
            _('Please provide details'),
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
                'finishSummaryText': _('Please finish your summary -- '),
            },
        })

        if current_step_name == _('Details'):
            context.update({
                'page_note': _('Continued'),
            })
        elif current_step_name == _('Location'):
            context.update({
                'page_note': _('Providing details on where this occurred helps us properly review your issue and get it to the right people within the Civil Rights Division.'),
            })
        elif current_step_name == _('Primary Issue'):
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
