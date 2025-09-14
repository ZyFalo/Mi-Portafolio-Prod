from django.urls import path
from .views import fyq

urlpatterns = [
    path('', fyq, name='fyq'),
]

