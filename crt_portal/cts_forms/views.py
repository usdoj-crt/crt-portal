from collections import ChainMap

from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404, render_to_response
from django.urls import reverse
from django.views import generic

from formtools.wizard.views import SessionWizardView

from .models import Report, ProtectedClass
from .forms import WhatHappened, Where, Who, Details, Contact

import logging

logger = logging.getLogger(__name__)


class CRTReportWizard(SessionWizardView):
    """Once all the sub-forms are submitted this class will clean data and save."""
    template_name = 'forms/report.html'

    def done(self, form_list, form_dict, **kwargs):
        form_data_dict = self.get_all_cleaned_data()
        m2mfield = form_data_dict.pop('protected_class')
        r = Report.objects.create(**form_data_dict)
        r.save()

        # Many to many fields need to be added or updated to the main model, with a related manager such as add() or update()
        for protected in m2mfield:
            p = ProtectedClass.objects.get(protected_class=protected)
            r.protected_class.add(p)

        r.save()
        # adding this back for the save page results
        form_data_dict['protected_class'] = m2mfield.values()

        return render_to_response('forms/confirmation.html', {'data_dict': form_data_dict})
