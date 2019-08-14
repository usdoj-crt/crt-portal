from collections import ChainMap

from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404, render_to_response
from django.urls import reverse
from django.views import generic

from formtools.wizard.views import SessionWizardView

from .models import Report
from .forms import WhatHappened, Where, Who, Details, Contact


import logging

logger = logging.getLogger(__name__)



class CRTReportWizard(SessionWizardView):
    """once all the sub-forms are submitted this class will clean data and save."""
    template_name = 'forms/report.html'


    def done(self, form_list, form_dict, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        consolidated_data = dict(ChainMap(*form_data))
        logger.error(consolidated_data)
        report_instance = Report(**consolidated_data)
        report_instance.save()

        return render_to_response('forms/confirmation.html', {'data_dict': consolidated_data})
