from django.shortcuts import redirect


def active_user_required(func):
    def wrapper(request, *args, **kwargs):
        print("Active User Required Decorator is called!")
        user = request.user
        if not user.is_active:
            print("User is not active, redirecting to landing.")
            return redirect('/form/landing')
        func(request, *args, **kwargs)
    return wrapper
