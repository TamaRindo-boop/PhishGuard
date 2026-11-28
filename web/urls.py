from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login, name='login'),
    path('salir/', views.salir, name='salir'),
    path('panel/', views.panel, name='panel'),
    path('detector/', views.detector_urls, name='detector'), 
    path('registro/', views.registro, name='registro'),
]