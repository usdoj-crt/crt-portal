from django.shortcuts import redirect


class PortalAccessRequiredMixin():
    """Verify that the current user is has portal access."""
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        if not hasattr(user, 'profile'):
            return redirect('/form/landing')

        if not user.profile.has_portal_access:
            return redirect('/form/landing')

        return super().dispatch(request, *args, **kwargs)
