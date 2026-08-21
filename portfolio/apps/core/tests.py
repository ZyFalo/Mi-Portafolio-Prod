"""
Pruebas de la portada.

El panel de estado en vivo se retiró junto con el pipeline: lo que queda por
comprobar es que la home sirve lo que sus plantillas esperan.
"""

from django.test import TestCase
from django.urls import reverse

from portfolio.apps.cielo.models import Star

from .models import Developer


class HomeTests(TestCase):
    def test_la_portada_responde(self):
        respuesta = self.client.get(reverse("home"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "core/home.html")

    def test_publica_el_catalogo_de_lugares(self):
        """El formulario del cielo se rellena con él: sin catálogo, no hay select."""
        contexto = self.client.get(reverse("home")).context

        self.assertIn("paises", contexto)
        self.assertGreater(len(contexto["paises"]), 1)

    def test_solo_lista_desarrolladores_activos(self):
        Developer.objects.create(
            name="Visible", role="Dev", bio="…", portfolio_url="https://ejemplo.test",
            skills="Python", is_active=True,
        )
        Developer.objects.create(
            name="Retirado", role="Dev", bio="…", portfolio_url="https://ejemplo.test",
            skills="Python", is_active=False,
        )

        nombres = [d.name for d in self.client.get(reverse("home")).context["developers"]]

        self.assertEqual(nombres, ["Visible"])

    def test_la_portada_carga_con_el_cielo_poblado(self):
        Star.objects.create(name="Ana", location="Colombia", x=0.3, y=0.4)

        self.assertEqual(self.client.get(reverse("home")).status_code, 200)


class DeveloperTests(TestCase):
    def test_el_nombre_de_banner_se_genera_solo(self):
        dev = Developer.objects.create(
            name="Ana María", role="Dev", bio="…",
            portfolio_url="https://ejemplo.test", skills="Python",
        )

        self.assertEqual(dev.banner_name, "developer_ana-maria")

    def test_la_url_del_portafolio_lleva_utm(self):
        dev = Developer.objects.create(
            name="Ana", role="Dev", bio="…",
            portfolio_url="https://ejemplo.test", skills="Python",
        )

        self.assertIn("utm_source=william_portfolio", dev.tracked_url)
        self.assertIn("utm_content=developer_ana", dev.tracked_url)

    def test_sin_utm_automatico_la_url_no_se_toca(self):
        dev = Developer.objects.create(
            name="Ana", role="Dev", bio="…", portfolio_url="https://ejemplo.test",
            skills="Python", auto_utm=False,
        )

        self.assertEqual(dev.tracked_url, "https://ejemplo.test")
