import json
import math
import random
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .catalogos import PAISES_VALIDOS
from .models import LARGO_MINIMO, Star, hashear_ip, limpiar_nombre

# El cielo se dibuja entero: son puntos, no filas de texto, y verlo poblado
# es justamente la gracia. El tope evita que una campaña de spam lo reviente.
LIMITE_CIELO = 600

# Máximo de estrellas por huella de IP en la ventana de tiempo. No es una por
# persona porque una oficina o una universidad comparten salida: sería
# bloquear a los compañeros de quien llegó primero.
MAX_ESTRELLAS_POR_IP = 3
VENTANA_HORAS = 24

# Separación mínima entre estrellas, en coordenadas normalizadas. Por debajo
# de esto los puntos se pisan y el cielo se lee como una mancha.
SEPARACION_MINIMA = 0.025

# Margen para que ninguna estrella nazca pegada al borde del lienzo
MARGEN = 0.035


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


def _dentro_del_lienzo(valor) -> float:
    """Encaja una coordenada dentro del área dibujable."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if math.isnan(numero) or math.isinf(numero):
        return None
    return min(max(numero, MARGEN), 1 - MARGEN)


def _hueco_libre(x, y, ocupadas):
    """
    Busca el punto libre más cercano al que pidió el visitante.

    Se aparta en espiral en lugar de rechazar la petición: quien toca el
    cielo no tiene por qué saber que ahí ya había alguien, y ver su estrella
    aparecer un pelo más allá se entiende solo.
    """

    def libre(px, py):
        return all(
            math.hypot(px - ox, py - oy) >= SEPARACION_MINIMA for ox, oy in ocupadas
        )

    if libre(x, y):
        return x, y

    for vuelta in range(1, 13):
        radio = SEPARACION_MINIMA * vuelta
        for paso in range(8):
            angulo = (math.pi / 4) * paso + vuelta
            px = _dentro_del_lienzo(x + math.cos(angulo) * radio)
            py = _dentro_del_lienzo(y + math.sin(angulo) * radio)
            if px is not None and py is not None and libre(px, py):
                return px, py

    # Cielo muy poblado en esa zona: se cede a la suerte antes que fallar
    return (
        random.uniform(MARGEN, 1 - MARGEN),
        random.uniform(MARGEN, 1 - MARGEN),
    )


@require_GET
def estrellas(request):
    """Devuelve el cielo completo y el total acumulado."""
    qs = Star.objects.filter(is_visible=True)
    total = qs.count()
    # Se envían de más antigua a más nueva: así el trazado de constelaciones
    # es estable y no baila cada vez que alguien enciende una.
    cielo = [e.como_dict() for e in qs.order_by("created_at", "id")[:LIMITE_CIELO]]
    return JsonResponse({"ok": True, "total": total, "estrellas": cielo})


@require_POST
def encender(request):
    """
    Enciende la estrella de un visitante.

    Protecciones: honeypot (`website`), catálogo cerrado de lugares,
    coordenadas dentro del lienzo y límite por huella de IP.
    """
    try:
        datos = json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "payload_invalido"}, status=400)

    # Honeypot: los bots rellenan campos ocultos
    if _limpiar(datos.get("website", ""), 100):
        return JsonResponse({"ok": False, "error": "rechazado"}, status=400)

    nombre = limpiar_nombre(datos.get("name", ""))
    if len(nombre) < LARGO_MINIMO:
        return JsonResponse(
            {
                "ok": False,
                "error": "nombre_invalido",
                "detalle": "Escribe al menos 2 letras para firmar tu estrella.",
            },
            status=400,
        )

    # El lugar viene de un catálogo cerrado: cualquier otra cosa se rechaza
    # en lugar de ensuciar el cielo.
    lugar = _limpiar(datos.get("location", ""), 32)
    if lugar and lugar not in PAISES_VALIDOS:
        return JsonResponse(
            {"ok": False, "error": "pais_invalido", "detalle": "Elige un lugar de la lista."},
            status=400,
        )

    x = _dentro_del_lienzo(datos.get("x"))
    y = _dentro_del_lienzo(datos.get("y"))
    if x is None or y is None:
        return JsonResponse(
            {
                "ok": False,
                "error": "posicion_invalida",
                "detalle": "Toca el cielo para elegir dónde va tu estrella.",
            },
            status=400,
        )

    ip_hash = hashear_ip(_obtener_ip(request))
    if ip_hash:
        desde = timezone.now() - timedelta(hours=VENTANA_HORAS)
        recientes = Star.objects.filter(ip_hash=ip_hash, created_at__gte=desde).count()
        if recientes >= MAX_ESTRELLAS_POR_IP:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "limite_alcanzado",
                    "detalle": (
                        f"Ya encendiste {MAX_ESTRELLAS_POR_IP} estrellas en las últimas "
                        f"{VENTANA_HORAS} horas. ¡Gracias por iluminar esto!"
                    ),
                },
                status=429,
            )

    ocupadas = list(Star.objects.filter(is_visible=True).values_list("x", "y"))
    x, y = _hueco_libre(x, y, ocupadas)

    estrella = Star.objects.create(
        name=nombre,
        location=lugar,
        x=x,
        y=y,
        ip_hash=ip_hash,
    )

    return JsonResponse(
        {
            "ok": True,
            "estrella": estrella.como_dict(),
            "total": Star.objects.filter(is_visible=True).count(),
        },
        status=201,
    )
