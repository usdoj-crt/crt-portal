from actstream import action


def send_action(user, verb, description, target):
    """Send all actions to activity stream"""
    action.send(
        user,
        verb,
        description,
        target,
    )
