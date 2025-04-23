from django.contrib import admin
from django.urls import path, include
from CVapp import views as cvapp_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', cvapp_views.home, name='home'),
    path('offer/', include('offer.urls'), name='offer'),
    path('user/', include('users.urls'), name='user'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)