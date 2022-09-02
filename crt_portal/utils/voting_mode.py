# from cts_forms.models import VotingMode
from django.conf import settings


def is_voting_mode():
    return settings.VOTING_MODE
    # try:
    #     voting_mode = VotingMode.objects.first()
    #     return voting_mode.toggle
    # except AttributeError:
    #     VotingMode.objects.create(toggle=False)
    #     return False
