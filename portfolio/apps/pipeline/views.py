import json
import random
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .catalogos import PAISES_VALIDOS, TIPO_POR_DEFECTO, TIPOS_VALIDOS
from .models import Deploy, hashear_ip, normalizar_autor

# Cuántos deploys se muestran en el muro
LIMITE_MURO = 12

# Máximo de deploys por huella de IP en la ventana de tiempo
MAX_DEPLOYS_POR_IP = 3
VENTANA_HORAS = 24


def _obtener_ip(request) -> str:
    """Obtiene la IP real del cliente respetando proxies (Railway/AWS)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _limpiar(texto: str, maximo: int) -> str:
    """Normaliza texto libre: recorta, colapsa espacios y limita longitud."""
    if not isinstance(texto, str):
        return ""
    return " ".join(texto.split())[:maximo].strip()


@require_GET
def deploys_recientes(request):
    """Devuelve los últimos deploys y el total acumulado."""
    qs = Deploy.objects.filter(is_visible=True)
    deploys = [d.como_dict() for d in qs[:LIMITE_MURO]]
    return JsonResponse(
        {
            "ok": True,
            "total": qs.count(),
            "deploys": deploys,
        }
    )


@require_POST
def lanzar_deploy(request):
    """
    Registra el deploy de un visitante.

    Protecciones: honeypot (`website`), longitud máxima de campos y límite
    de despliegues por huella de IP.
    """
    try:
        datos = json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "payload_invalido"}, status=400)

    # Honeypot: los bots rellenan campos ocultos
    if _limpiar(datos.get("website", ""), 100):
        return JsonResponse({"ok": False, "error": "rechazado"}, status=400)

    # El autor se normaliza a un identificador (sin espacios ni tildes) en vez
    # de rechazarse: quien escribe "William Andrés" obtiene "William-Andres".
    nombre = normalizar_autor(datos.get("name", ""))
    if len(nombre) < 2:
        return JsonResponse(
            {
                "ok": False,
                "error": "nombre_invalido",
                "detalle": "El autor necesita al menos 2 caracteres válidos (letras o números).",
            },
            status=400,
        )

    # El país viene de un catálogo cerrado: cualquier otra cosa se descarta
    # en silencio en lugar de ensuciar el muro.
    ubicacion = _limpiar(datos.get("location", ""), 32)
    if ubicacion and ubicacion not in PAISES_VALIDOS:
        return JsonResponse(
            {
                "ok": False,
                "error": "pais_invalido",
                "detalle": "Elige un país de la lista.",
            },
            status=400,
        )

    tipo = _limpiar(datos.get("type", ""), 10).lower() or TIPO_POR_DEFECTO
    if tipo not in TIPOS_VALIDOS:
        return JsonResponse(
            {
                "ok": False,
                "error": "tipo_invalido",
                "detalle": "Ese tipo de commit no existe.",
            },
            status=400,
        )

    mensaje = _limpiar(datos.get("message", ""), 80)

    ip_hash = hashear_ip(_obtener_ip(request))
    if ip_hash:
        desde = timezone.now() - timedelta(hours=VENTANA_HORAS)
        recientes = Deploy.objects.filter(ip_hash=ip_hash, created_at__gte=desde).count()
        if recientes >= MAX_DEPLOYS_POR_IP:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "limite_alcanzado",
                    "detalle": (
                        f"Ya lanzaste {MAX_DEPLOYS_POR_IP} deploys en las últimas "
                        f"{VENTANA_HORAS} horas. ¡Gracias por participar!"
                    ),
                },
                status=429,
            )

    deploy = Deploy.objects.create(
        visitor_name=nombre,
        visitor_location=ubicacion,
        commit_type=tipo,
        message=mensaje,
        duration_ms=random.randint(1200, 2600),
        ip_hash=ip_hash,
    )

    return JsonResponse(
        {
            "ok": True,
            "deploy": deploy.como_dict(),
            "total": Deploy.objects.filter(is_visible=True).count(),
        },
        status=201,
    )
