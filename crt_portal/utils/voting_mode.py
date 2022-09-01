from cts_forms.models import VotingMode


def is_voting_mode():
    try:
        voting_mode = VotingMode.objects.first()
        return voting_mode.toggle
    except AttributeError:
        VotingMode.objects.create(toggle=False)
        return False

