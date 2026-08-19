from django.urls import path

from . import views

app_name = 'pipeline'

urlpatterns = [
    path('deploys/', views.deploys_recientes, name='deploys'),
    path('deploy/', views.lanzar_deploy, name='lanzar'),
]
