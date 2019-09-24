from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='find-home'),
    path('register2/<str:surname>/<str:postcode>/', views.register2, name='find-register2'),
    path('about/', views.about, name='find-about'),
]
