from django.urls import path
from . import views


urlpatterns = [
    path('ipn/', views.pesapal_ipn), 
]