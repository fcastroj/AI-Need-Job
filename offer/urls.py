from django.urls import path
from . import views

urlpatterns = [
    #path('', views.offer, name='offer'),
    path('',views.uploadCVS, name='upload_cvs'),
]