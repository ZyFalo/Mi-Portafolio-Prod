from django.urls import path

from . import views

app_name = "cielo"

urlpatterns = [
    path("estrellas/", views.estrellas, name="estrellas"),
    path("encender/", views.encender, name="encender"),
]
