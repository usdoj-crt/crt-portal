from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from formtools.wizard.views import SessionWizardView

from .models import Report, ProtectedClass

import logging

logger = logging.getLogger(__name__)


@login_required
def IndexView(request):
    latest_reports = Report.objects.order_by('-create_date')
    return render_to_response('forms/index.html', {'data_dict': latest_reports})


TEMPLATES = [
    # Contact
    'forms/report_grouped_questions.html',
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

        # This name appears in the progress bar wizard
        ordered_step_names = [
            'Contact',
            'Protected Class',
            'Details',
            # 'What Happened',
            # 'Where',
            # 'Who',
        ]
        current_step_name = ordered_step_names[int(self.steps.current)]

        # This title appears in large font above the question elements
        ordered_step_titles = [
            'Contact',
            'Please provide details',
            'Details'
        ]
        current_step_title = ordered_step_titles[int(self.steps.current)]

        context.update({
            'ordered_step_names': ordered_step_names,
            'current_step_title': current_step_title,
            'current_step_name': current_step_name
        })

        if current_step_name == 'Details':
            context.update({
                'page_subtitle': 'Please describe what happened in your own words',
                'page_note': 'Continued'
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
