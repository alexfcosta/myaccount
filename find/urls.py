from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='find-home'),
    path('about/', views.about, name='find-about'),
]
