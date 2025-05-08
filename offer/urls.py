from django.urls import path
from . import views

urlpatterns = [
    path('upload_vacancies/',views.upload_vacancies, name='upload_vacancies'),
    path('upload_cvs/',views.uploadCVS, name='upload_cvs'),
    path('open_vacancies/<int:vacancy_id>',views.change_state_vacancy, name='change_vacancy_state'),
]