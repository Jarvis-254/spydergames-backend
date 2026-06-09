from django.urls import path
from . import views
# Write your urls here

urlpatterns = [
    path('create/', views.create_match_api),
    path('join/', views.join_match_api),
    path('game/<str:code>/', views.game_room_api),
    path('submit/<str:code>/', views.submit_answer_api),
    path('results/<str:code>/', views.results_api),
    path('waiting/<str:code>/', views.waiting_room_api),
    path('payment', views.payment_api),
    path('pesapal_callback', views.pesapal_callback_api),
    path('deposit', views.deposit_api),
    
]