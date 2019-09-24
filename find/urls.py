from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='find-home'),
    path('register2/<str:forename>/<str:surname>/<str:postcode>/<str:email>/', views.register2, name='find-register2'),
    path('dashboard/<str:gid>/<str:forename>/<str:surname>/<str:postcode>/<str:email>/', views.dashboard, name='find-dashboard'),
    path('about/', views.about, name='find-about'),
]
