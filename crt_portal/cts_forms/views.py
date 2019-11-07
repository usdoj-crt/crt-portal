from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from formtools.wizard.views import SessionWizardView

from .models import Report, ProtectedClass
from .model_variables import PROTECTED_CLASS_CODES


@login_required
def IndexView(request):
    latest_reports = Report.objects.order_by('-create_date')
    data = []
    # formatting protected class
    for report in latest_reports:
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
            "report_protected_classes": p_class_list
        })

    return render_to_response('forms/index.html', {'data_dict': data})


TEMPLATES = [
    # Contact
    'forms/report_grouped_questions.html',
    # Primary reason
    'forms/report_multiple_questions.html',
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
            'Contact',
            'Primary Issue',
            'Protected Class',
            'Details',
        ]
        current_step_name = ordered_step_names[int(self.steps.current)]

        # This title appears in large font above the question elements
        ordered_step_titles = [
            'Contact',
            'What is your primary reason for contacting the Civil Rights Division?',
            'Please provide details',
            'Details'
        ]
        current_step_title = ordered_step_titles[int(self.steps.current)]

        context.update({
            'ordered_step_names': ordered_step_names,
            'current_step_title': current_step_title,
            'current_step_name': current_step_name,
            'page_errors': page_errors,
        })

        if current_step_name == 'Details':
            context.update({
                'page_note': 'Continued'
            })
        elif current_step_name == 'Primary Issue':
            # Disable default client-side validation to roll our own.
            # Roll this out incrementally page-by-page.
            context.update({
                'form_novalidate': True
            })

        return context

    def done(self, form_list, form_dict, **kwargs):
        form_data_dict = self.get_all_cleaned_data()
        m2mfield = form_data_dict.pop('protected_class')
        r = Report.objects.create(**form_data_dict)

        # Many to many fields need to be added or updated to the main model, with a related manager such as add() or update()
        for protected in m2mfield:
            p = ProtectedClass.objects.get(protected_class=protected)
            r.protected_class.add(p)

        r.save()
        # adding this back for the save page results
        form_data_dict['protected_class'] = m2mfield.values()

        return render_to_response('forms/confirmation.html', {'data_dict': form_data_dict})
