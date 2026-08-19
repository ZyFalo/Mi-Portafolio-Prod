from django.urls import path

from .views import estado_sistema, home

urlpatterns = [
    path('', home, name='home'),
    path('estado/', estado_sistema, name='estado'),
]
