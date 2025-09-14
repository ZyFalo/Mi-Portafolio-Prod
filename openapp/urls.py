from django.urls import path
from .views import open_list, open_detail

urlpatterns = [
    path('', open_list, name='open_list'),
    path('<slug:slug>/', open_detail, name='open_detail'),
]

