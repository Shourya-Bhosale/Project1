from django.http import HttpResponse
from django.conf import settings

class AllowAllHostsMiddleware:
    """
    Custom middleware to allow all hosts and bypass ALLOWED_HOSTS check
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Override the host validation
        request.META['HTTP_HOST'] = request.get_host()
        response = self.get_response(request)
        return response
