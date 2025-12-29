# Django imports
from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.http import HttpResponse, HttpResponseRedirect

class AllowAllHostsMiddleware:
    """
    Custom middleware to allow Render domains and custom domain
    Bypasses ALLOWED_HOSTS check for Render subdomains
    Also redirects Render URLs to custom domain for branding
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.custom_domain = 'shivorganicdairyfarms.com'

    def __call__(self, request):
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # PERMANENT FIX: ALWAYS redirect Render URLs to custom domain
        # This ensures your domain always shows in browser, not Render URL
        # Works in both DEBUG and production mode
        if host.endswith('.onrender.com'):
            # Redirect to custom domain (preserve path and query string)
            protocol = 'https' if request.is_secure() else 'http'
            path = request.get_full_path()
            redirect_url = f'{protocol}://{self.custom_domain}{path}'
            return HttpResponseRedirect(redirect_url)
        
        # Allow any Render subdomain (for development/debugging)
        if host.endswith('.onrender.com'):
            # Add to ALLOWED_HOSTS if not already there
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
        
        # Allow custom domain
        if host in ['shivorganicdairyfarms.com', 'www.shivorganicdairyfarms.com']:
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
        
        response = self.get_response(request)
        return response
