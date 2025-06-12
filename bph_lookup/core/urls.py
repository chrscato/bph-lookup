from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('medicare/', views.rate_lookup, name='rate_lookup'),
    path('workcomp/', views.workers_comp_lookup, name='workers_comp_lookup'),
    path('api/rates/', views.rate_lookup_api, name='rate_lookup_api'),
]
