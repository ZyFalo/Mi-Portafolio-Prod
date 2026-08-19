"""
Pruebas del panel de estado.

Lo que se comprueba aquí es de quién habla el panel: la versión en producción
y su antigüedad deben salir del pipeline colaborativo —los deploys que dejan
los visitantes— y no del repositorio de este portafolio.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from portfolio.apps.pipeline.models import Deploy

from . import estado


class RevisionEnProduccionTests(TestCase):
    def _deploy(self, nombre, minutos_atras=0, **extra):
        return Deploy.objects.create(
            visitor_name=nombre,
            visitor_location=extra.pop("pais", "Colombia"),
            commit_type=extra.pop("tipo", "feat"),
            message=extra.pop("mensaje", "mi primer commit"),
            created_at=timezone.now() - timedelta(minutes=minutos_atras),
            **extra,
        )

    def test_sin_deploys_manda_el_commit_inicial(self):
        revision = estado._revision_en_produccion()

        self.assertTrue(revision["inicial"])
        self.assertEqual(revision["commit"], estado.VERSION.get("commit", ""))

    def test_el_deploy_de_un_visitante_pasa_a_produccion(self):
        deploy = self._deploy("cata-dev")

        revision = estado._revision_en_produccion()

        self.assertFalse(revision["inicial"])
        self.assertEqual(revision["commit"], deploy.commit_hash)
        self.assertEqual(revision["autor"], "cata-dev@Colombia")
        self.assertEqual(revision["asunto"], "feat: mi primer commit")
        self.assertAlmostEqual(revision["momento"], deploy.created_at.timestamp(), places=3)

    def test_manda_siempre_el_deploy_mas_reciente(self):
        self._deploy("will-dev", minutos_atras=480)
        reciente = self._deploy("cata-dev", minutos_atras=20)

        self.assertEqual(estado._revision_en_produccion()["commit"], reciente.commit_hash)

    def test_un_deploy_oculto_no_llega_a_produccion(self):
        visible = self._deploy("will-dev", minutos_atras=60)
        self._deploy("spam-bot", minutos_atras=1, is_visible=False)

        self.assertEqual(estado._revision_en_produccion()["commit"], visible.commit_hash)

    def test_el_reloj_cuenta_desde_el_ultimo_deploy(self):
        self._deploy("cata-dev", minutos_atras=20)

        datos = estado.recolectar()

        # 20 minutos, con holgura para el tiempo que tarda la prueba
        self.assertAlmostEqual(datos["desplegado_segundos"], 20 * 60, delta=5)

    def test_los_dos_relojes_son_independientes(self):
        """
        'En producción' mide el último deploy; 'proceso activo', el arranque
        del contenedor. Antes ambos salían del build y marcaban casi lo mismo.
        """
        self._deploy("cata-dev", minutos_atras=180)

        datos = estado.recolectar()

        self.assertGreater(datos["desplegado_segundos"], datos["uptime_segundos"])


class FormatoTests(TestCase):
    def test_formatear_uptime_coincide_con_el_navegador(self):
        # Mismos cortes que formatearUptime() en efectos.js
        self.assertEqual(estado.formatear_uptime(45), "45s")
        self.assertEqual(estado.formatear_uptime(3 * 60 + 7), "3m 7s")
        self.assertEqual(estado.formatear_uptime(2 * 3600 + 5 * 60 + 9), "2h 5m 9s")
        self.assertEqual(estado.formatear_uptime(3 * 86400 + 4 * 3600), "3d 4h 0m")
        self.assertEqual(estado.formatear_uptime(-10), "0s")


class RecolectarTests(TestCase):
    def test_publica_lo_que_espera_la_portada(self):
        datos = estado.recolectar()

        self.assertTrue(datos["operativo"])
        for clave in ("uptime", "desplegado", "despliegue", "arranque", "version"):
            self.assertIn(clave, datos)
        for clave in ("commit", "rama", "autor", "asunto"):
            self.assertIn(clave, datos["version"])
