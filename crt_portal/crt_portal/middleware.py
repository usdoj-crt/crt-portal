from django_auth_adfs.middleware import LoginRequiredMiddleware


class CRTLoginRequiredMiddleware(LoginRequiredMiddleware):
    """
    Override django_auth_adfs LoginRequiredMiddleware to avoid authentication checks
    for 404 responses
    """

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return response
        return super().__call__(request)
