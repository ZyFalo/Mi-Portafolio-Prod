from django.urls import path
from .views import contactame

urlpatterns = [
    path('', contactame, name='contactame'),
]

