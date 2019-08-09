from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404, render_to_response
from django.urls import reverse
from django.views import generic

from formtools.wizard.views import SessionWizardView

from .models import ViolationReport, Choice
from .forms import ContactForm1, ContactForm2


import logging

logger = logging.getLogger(__name__)


# import logging


class IndexView(generic.ListView):
    template_name = 'forms/index.html'
    context_object_name = 'latest_report_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return ViolationReport.objects.order_by('-create_date')[:5]

class ResultsView(generic.DetailView):
    model = ViolationReport
    template_name = 'forms/results.html'

# dummy view used in prototyping
def VoteView(request, violationreport_id):
    report = get_object_or_404(ViolationReport, pk=violationreport_id)
    try:
        selected_choice = report.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'forms/detail.html', {
            'violationreport': report,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('crt_forms:results', args=(report.id,)))

class DetailView(generic.DetailView):
    model = ViolationReport
    template_name = 'forms/detail.html'


class ResultsView(generic.DetailView):
    model = ViolationReport
    template_name = 'forms/results.html'


### Forms view
FORMS = [
    ("ContactForm1", ContactForm1),
    ("ContactForm2", ContactForm2),
]


class ContactWizard(SessionWizardView):
    """once all the sub-forms are submitted this class will save."""
    template_name = 'forms/report.html'
    def done(self, form_list, form_dict, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        logger.error(form_data)
        return render_to_response('forms/confirmation.html', {'form_data': form_data})

