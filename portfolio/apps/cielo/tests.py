"""
Pruebas del cielo de visitantes.

El foco está en lo que separa un cielo de un vertedero: nombres que se leen
como nombres, lugares de un catálogo cerrado, coordenadas dentro del lienzo
y estrellas que no se pisan entre sí.
"""

import json
import math
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .models import Star, limpiar_nombre


class LimpiarNombreTests(TestCase):
    def test_conserva_nombres_humanos(self):
        """El cielo lo firma cualquiera: no se exige un identificador de git."""
        self.assertEqual(limpiar_nombre("Ana Mar\u00eda"), "Ana Mar\u00eda")
        self.assertEqual(limpiar_nombre("O'Brien"), "O'Brien")
        self.assertEqual(limpiar_nombre("Jean-Luc"), "Jean-Luc")
        self.assertEqual(limpiar_nombre("William Andrés Peña"), "William Andrés Peña")

    def test_colapsa_espacios_y_recorta(self):
        self.assertEqual(limpiar_nombre("  Ana    María  "), "Ana María")
        self.assertEqual(limpiar_nombre("a" * 60), "a" * 32)

    def test_descarta_caracteres_invisibles(self):
        # Se escriben con su escape a propósito: pegados en el literal no se
        # ven al leer el test y cualquiera los borraría sin darse cuenta.
        self.assertEqual(limpiar_nombre("An\u200ba"), "Ana")   # ancho cero
        self.assertEqual(limpiar_nombre("Ana\u202e"), "Ana")   # invierte el texto
        self.assertEqual(limpiar_nombre("A\x00na"), "Ana")     # byte nulo

    def test_descarta_marcado(self):
        self.assertEqual(limpiar_nombre("<script>"), "script")

    def test_texto_sin_letras_queda_vacio(self):
        self.assertEqual(limpiar_nombre("!!!"), "")
        self.assertEqual(limpiar_nombre(None), "")


class EncenderTests(TestCase):
    def setUp(self):
        self.url = reverse("cielo:encender")

    def _enviar(self, **campos):
        cuerpo = {"name": "Ana", "location": "Colombia", "x": 0.5, "y": 0.5}
        cuerpo.update(campos)
        return self.client.post(
            self.url, data=json.dumps(cuerpo), content_type="application/json"
        )

    def test_enciende_una_estrella(self):
        respuesta = self._enviar()

        self.assertEqual(respuesta.status_code, 201)
        datos = respuesta.json()
        self.assertTrue(datos["ok"])
        self.assertEqual(datos["estrella"]["name"], "Ana")
        self.assertEqual(datos["estrella"]["label"], "Ana · Colombia")
        self.assertEqual(Star.objects.count(), 1)

    def test_el_honeypot_rechaza_a_los_bots(self):
        respuesta = self._enviar(website="https://spam.example")

        self.assertEqual(respuesta.status_code, 400)
        self.assertFalse(Star.objects.exists())

    def test_nombre_demasiado_corto(self):
        respuesta = self._enviar(name="A")

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["error"], "nombre_invalido")

    def test_lugar_fuera_del_catalogo(self):
        respuesta = self._enviar(location="Narnia")

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["error"], "pais_invalido")

    def test_se_permite_no_decir_el_lugar(self):
        respuesta = self._enviar(location="")

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["estrella"]["label"], "Ana")

    def test_sin_coordenadas_no_hay_estrella(self):
        respuesta = self._enviar(x=None, y=None)

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["error"], "posicion_invalida")

    def test_las_coordenadas_se_encajan_en_el_lienzo(self):
        """Nadie debe poder colocar su estrella fuera del cuadro."""
        respuesta = self._enviar(x=-5, y=99)

        self.assertEqual(respuesta.status_code, 201)
        estrella = Star.objects.get()
        self.assertGreaterEqual(estrella.x, views.MARGEN)
        self.assertLessEqual(estrella.y, 1 - views.MARGEN)

    def test_rechaza_coordenadas_no_numericas(self):
        for valor in ("hola", float("nan"), float("inf")):
            with self.subTest(valor=valor):
                respuesta = self._enviar(x=valor)
                self.assertEqual(respuesta.status_code, 400)

    def test_dos_estrellas_en_el_mismo_punto_no_se_pisan(self):
        self._enviar(name="Ana")
        self._enviar(name="Beto")

        a, b = Star.objects.order_by("id")
        distancia = math.hypot(a.x - b.x, a.y - b.y)
        self.assertGreaterEqual(distancia, views.SEPARACION_MINIMA)

    def test_limite_por_huella_de_ip(self):
        for i in range(views.MAX_ESTRELLAS_POR_IP):
            self.assertEqual(self._enviar(name=f"Visitante{i}").status_code, 201)

        respuesta = self._enviar(name="UnoDeMas")

        self.assertEqual(respuesta.status_code, 429)
        self.assertEqual(respuesta.json()["error"], "limite_alcanzado")
        self.assertEqual(Star.objects.count(), views.MAX_ESTRELLAS_POR_IP)

    def test_el_limite_caduca_con_la_ventana(self):
        for i in range(views.MAX_ESTRELLAS_POR_IP):
            self._enviar(name=f"Visitante{i}")

        antiguo = timezone.now() - timedelta(hours=views.VENTANA_HORAS + 1)
        Star.objects.update(created_at=antiguo)

        self.assertEqual(self._enviar(name="Nuevo").status_code, 201)

    def test_solo_acepta_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)


class ListadoTests(TestCase):
    def setUp(self):
        self.url = reverse("cielo:estrellas")

    def test_cielo_vacio(self):
        datos = self.client.get(self.url).json()

        self.assertTrue(datos["ok"])
        self.assertEqual(datos["total"], 0)
        self.assertEqual(datos["estrellas"], [])

    def test_las_estrellas_ocultas_no_se_publican(self):
        Star.objects.create(name="Visible", x=0.3, y=0.3)
        Star.objects.create(name="Retirada", x=0.6, y=0.6, is_visible=False)

        datos = self.client.get(self.url).json()

        self.assertEqual(datos["total"], 1)
        self.assertEqual(datos["estrellas"][0]["name"], "Visible")

    def test_se_devuelven_de_mas_antigua_a_mas_nueva(self):
        """Orden estable: si baila, las constelaciones se redibujan solas."""
        vieja = Star.objects.create(name="Primera", x=0.2, y=0.2)
        Star.objects.filter(pk=vieja.pk).update(
            created_at=timezone.now() - timedelta(days=2)
        )
        Star.objects.create(name="Segunda", x=0.8, y=0.8)

        nombres = [e["name"] for e in self.client.get(self.url).json()["estrellas"]]

        self.assertEqual(nombres, ["Primera", "Segunda"])
