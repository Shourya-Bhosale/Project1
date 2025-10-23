"""
URL configuration for shivdairy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.http import require_GET
import os

@require_GET
def sitemap_xml(request):
    """Serve sitemap.xml"""
    sitemap_path = os.path.join(os.path.dirname(__file__), '..', 'sitemap.xml')
    try:
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/xml')
    except FileNotFoundError:
        return HttpResponse('Sitemap not found', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('sitemap.xml', sitemap_xml, name='sitemap'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
