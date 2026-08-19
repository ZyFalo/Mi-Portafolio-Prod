from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from portfolio.apps.pipeline.catalogos import PAISES, TIPOS_COMMIT

from . import estado
from .models import Developer


def home(request):
    developers = Developer.objects.filter(is_active=True).order_by("order", "id")
    return render(request, 'core/home.html', {
        "developers": developers,
        "estado": estado.recolectar(),
        "paises": PAISES,
        "tipos_commit": TIPOS_COMMIT,
    })


@require_GET
def estado_sistema(request):
    """Estado en vivo del sitio para el panel del portafolio."""
    return JsonResponse(estado.recolectar())
