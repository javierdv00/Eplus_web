from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import upload_and_process

urlpatterns = [
    path('', upload_and_process, name='upload_and_process'),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
