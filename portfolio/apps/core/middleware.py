"""
Redirección al dominio canónico.

El portafolio vivió en dev-william-pena.up.railway.app y ahora se sirve en
wpena.dev. Los enlaces antiguos siguen repartidos por LinkedIn, el CV y donde
se hayan compartido: en lugar de romperlos, se redirigen de forma permanente
al dominio nuevo conservando la ruta y los parámetros.

Solo actúa cuando CANONICAL_HOST y REDIRECT_HOSTS están definidos. Así el
código puede desplegarse antes de que el dominio nuevo tenga certificado sin
mandar a nadie a un dominio que todavía no responde por HTTPS (y un .dev no
admite otra cosa).
"""

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponsePermanentRedirect


class RedireccionPermanenteConMetodo(HttpResponsePermanentRedirect):
    """
    308: permanente como el 301, pero repite la petición con el mismo método.

    Ante un 301 los navegadores reenvían un POST como GET, y lo que llega al
    destino ya no es la petición original. El 308 conserva método y cuerpo.
    """

    status_code = 308


class DominioCanonicoMiddleware:
    """Redirige los dominios antiguos al canónico, conservando ruta y parámetros."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.canonico = (getattr(settings, "CANONICAL_HOST", "") or "").strip().lower()
        self.antiguos = {
            host.strip().lower()
            for host in getattr(settings, "REDIRECT_HOSTS", [])
            if host.strip()
        }
        # Un error de configuración que incluyera el canónico en la lista lo
        # redirigiría a sí mismo en bucle: se descarta antes de empezar.
        self.antiguos.discard(self.canonico)

        # Sin configuración completa, Django retira el middleware de la cadena
        # y no cuesta nada en cada petición.
        if not self.canonico or not self.antiguos:
            raise MiddlewareNotUsed

    def __call__(self, request):
        # Se lee la cabecera Host tal cual en lugar de request.get_host(), que
        # exige que el host figure en ALLOWED_HOSTS: si algún día se retira de
        # la lista el dominio antiguo, respondería 400 en vez de redirigir. El
        # destino es un valor fijo de configuración, así que no abre ninguna
        # redirección arbitraria.
        host = request.META.get("HTTP_HOST", "").split(":", 1)[0].lower()

        if host not in self.antiguos:
            return self.get_response(request)

        destino = f"https://{self.canonico}{request.get_full_path()}"
        if request.method in ("GET", "HEAD"):
            return HttpResponsePermanentRedirect(destino)
        return RedireccionPermanenteConMetodo(destino)
