from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Error handlers (no import needed)
#handler404 = 'userprofile.views.handler404'
#handler500 = 'userprofile.views.handler500'
#handler400 = 'userprofile.views.handler400'
#handler403 = 'userprofile.views.handler403'

# Serve static & media files
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]