from django.shortcuts import redirect


def portal_access_required(func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_staff:
            return func(request, *args, **kwargs)

        if not hasattr(user, 'profile'):
            return redirect('/form/landing')

        if not user.profile.has_portal_access:
            return redirect('/form/landing')
        return func(request, *args, **kwargs)
    return wrapper
