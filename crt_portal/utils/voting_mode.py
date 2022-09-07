# from cts_forms.models import VotingMode
from django.conf import settings


def is_voting_mode():
    return settings.VOTING_MODE
    # Leaving this here in case we can get past circleci's build errors.  If this code is used instead of the env
    # variable, the updates would be in real time, and admins could do them.  To update to voting mode now, we need to
    # run cf set-env crt-portal-django VOTING_MODE True (see documentation)
    # try:
    #     voting_mode = VotingMode.objects.first()
    #     return voting_mode.toggle
    # except AttributeError:
    #     VotingMode.objects.create(toggle=False)
    #     return False
