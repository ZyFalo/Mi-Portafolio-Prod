from django.shortcuts import render

from portfolio.apps.cielo.catalogos import PAISES

from .models import Developer


def home(request):
    developers = Developer.objects.filter(is_active=True).order_by("order", "id")
    return render(request, 'core/home.html', {
        "developers": developers,
        "paises": PAISES,
    })
