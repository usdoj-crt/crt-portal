from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404, render_to_response
from django.urls import reverse
from django.views import generic

from formtools.wizard.views import SessionWizardView

from .models import ViolationReport
from .forms import ContactForm1, ContactForm2


import logging

logger = logging.getLogger(__name__)


### Forms view

class ContactWizard(SessionWizardView):
    """once all the sub-forms are submitted this class will save."""
    template_name = 'forms/report.html'
    def done(self, form_list, form_dict, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        # for debugging
        logger.error(form_data)

        return render_to_response('forms/confirmation.html', {'form_data': form_data})
