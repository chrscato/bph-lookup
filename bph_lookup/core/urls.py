from django.urls import path
from . import views

urlpatterns = [
    path('', views.rate_lookup, name='rate_lookup'),
    path('api/rates/', views.rate_lookup_api, name='rate_lookup_api'),
]
