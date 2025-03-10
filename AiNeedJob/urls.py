from django.contrib import admin
from django.urls import path
from CVapp import views as cvapp_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', cvapp_views.home, name='home'),
    path('upload_cv/', cvapp_views.uploadCV, name='upload_cv')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)