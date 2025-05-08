from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from CVapp.views import resume_history

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('CVapp.urls'), name='jobseeker'),
    path('offer/', include('offer.urls'), name='offer'),
    path('user/', include('users.urls'), name='user'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)