import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import ViolationReport


def create_question(description_text, days):
    """
    Create a question with the given `description_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return ViolationReport.objects.create(description_text=description_text, create_date=time)

class QuestionDetailViewTests(TestCase):
    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(description_text='Past Question.', days=-5)
        url = reverse('crt_forms:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.description_text)