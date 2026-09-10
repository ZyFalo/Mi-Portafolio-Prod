"""
Pruebas de la redirección al dominio canónico.

No renderizan plantillas, así que también corren fuera del contenedor.
"""

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from .middleware import DominioCanonicoMiddleware

ANTIGUO = "dev-william-pena.up.railway.app"
CANONICO = "wpena.dev"


def _vista(request):
    return HttpResponse("servido")


@override_settings(CANONICAL_HOST=CANONICO, REDIRECT_HOSTS=[ANTIGUO])
class RedireccionTests(SimpleTestCase):
    def setUp(self):
        self.fabrica = RequestFactory()
        self.middleware = DominioCanonicoMiddleware(_vista)

    def _get(self, ruta, host):
        return self.middleware(self.fabrica.get(ruta, HTTP_HOST=host))

    def test_el_dominio_antiguo_redirige_de_forma_permanente(self):
        respuesta = self._get("/", ANTIGUO)

        self.assertEqual(respuesta.status_code, 301)
        self.assertEqual(respuesta["Location"], "https://wpena.dev/")

    def test_conserva_la_ruta_y_los_parametros(self):
        """Un enlace compartido a un gadget debe llegar al mismo gadget."""
        respuesta = self._get("/open/macbook-air-m4/?utm_source=linkedin", ANTIGUO)

        self.assertEqual(
            respuesta["Location"],
            "https://wpena.dev/open/macbook-air-m4/?utm_source=linkedin",
        )

    def test_el_dominio_canonico_se_sirve_sin_redirigir(self):
        self.assertEqual(self._get("/", CANONICO).status_code, 200)

    def test_otros_hosts_no_se_tocan(self):
        self.assertEqual(self._get("/", "localhost").status_code, 200)

    def test_ignora_el_puerto_y_las_mayusculas(self):
        respuesta = self._get("/fyq/", "DEV-William-Pena.up.railway.app:443")

        self.assertEqual(respuesta["Location"], "https://wpena.dev/fyq/")

    def test_un_post_conserva_el_metodo(self):
        """Con 301 el navegador reenviaría el POST como GET."""
        peticion = self.fabrica.post(
            "/cielo/encender/", data="{}", content_type="application/json", HTTP_HOST=ANTIGUO
        )

        respuesta = self.middleware(peticion)

        self.assertEqual(respuesta.status_code, 308)
        self.assertEqual(respuesta["Location"], "https://wpena.dev/cielo/encender/")


class ActivacionTests(SimpleTestCase):
    def test_sin_configuracion_el_middleware_se_retira(self):
        with override_settings(CANONICAL_HOST="", REDIRECT_HOSTS=[]):
            with self.assertRaises(MiddlewareNotUsed):
                DominioCanonicoMiddleware(_vista)

    def test_sin_hosts_antiguos_no_hace_nada(self):
        with override_settings(CANONICAL_HOST=CANONICO, REDIRECT_HOSTS=[]):
            with self.assertRaises(MiddlewareNotUsed):
                DominioCanonicoMiddleware(_vista)

    def test_el_canonico_en_la_lista_no_provoca_un_bucle(self):
        with override_settings(CANONICAL_HOST=CANONICO, REDIRECT_HOSTS=[CANONICO, ANTIGUO]):
            middleware = DominioCanonicoMiddleware(_vista)

        respuesta = middleware(RequestFactory().get("/", HTTP_HOST=CANONICO))

        self.assertEqual(respuesta.status_code, 200)

    def test_solo_el_canonico_en_la_lista_equivale_a_apagado(self):
        with override_settings(CANONICAL_HOST=CANONICO, REDIRECT_HOSTS=[CANONICO]):
            with self.assertRaises(MiddlewareNotUsed):
                DominioCanonicoMiddleware(_vista)
