from django.urls import path
from . import views

urlpatterns = [
    path('', views.rate_lookup, name='rate_lookup'),
] 