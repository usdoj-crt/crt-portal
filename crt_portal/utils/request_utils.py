from crequest.middleware import CrequestMiddleware


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_section():
    current_request = CrequestMiddleware.get_request()
    user = current_request.user
    if hasattr(user, 'profile'):
        return current_request.user.profile.section
    return None