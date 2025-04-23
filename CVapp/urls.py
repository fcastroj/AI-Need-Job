from django.urls import path
from . import views   

urlpatterns = [
    path('', views.home, name='home'),
    path('upload_cv/', views.uploadCV, name='upload_cv'),
    path('feed/', views.feed, name='feed'),
    path('apply/<int:vacancy_id>/', views.apply_vacancy, name='apply'),

    path('process_cv/', views.download_cv_generated, name='process_cv'),
]