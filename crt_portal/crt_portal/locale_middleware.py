from django.utils import translation


class LanguageParamMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.GET.get("lang")
        if not language:
            return self.get_response(request)

        translation.activate(language)
        response = self.get_response(request)
        response.set_cookie('django_language', language)

        return response
