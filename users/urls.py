from django.urls import path
from . import views

urlpatterns = [
    #path('', views.offer, name='offer'),
    path('login/',views.login, name='login'),
    path('signup/',views.signup, name='signup'),
    path('logout/',views.logout, name='logout'),
    path('history/',views.history, name='history'),
]