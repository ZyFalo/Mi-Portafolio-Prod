from django.test import TestCase
from django.urls import reverse

from .models import Deploy


class DeployAPITests(TestCase):
    def test_lanzar_deploy_crea_registro(self):
        respuesta = self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': 'Ana', 'location': 'España', 'message': 'Suerte!'},
            content_type='application/json',
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Deploy.objects.count(), 1)
        self.assertEqual(Deploy.objects.first().actor, 'Ana@España')

    def test_honeypot_rechaza_bots(self):
        respuesta = self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': 'Bot', 'website': 'spam.example'},
            content_type='application/json',
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(Deploy.objects.count(), 0)

    def test_nombre_es_obligatorio(self):
        respuesta = self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': '   '},
            content_type='application/json',
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_limite_por_ip(self):
        for _ in range(3):
            self.client.post(
                reverse('pipeline:lanzar'),
                data={'name': 'Ana'},
                content_type='application/json',
            )
        respuesta = self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': 'Ana'},
            content_type='application/json',
        )
        self.assertEqual(respuesta.status_code, 429)
        self.assertEqual(Deploy.objects.count(), 3)

    def test_listado_devuelve_total(self):
        Deploy.objects.create(visitor_name='Luis')
        respuesta = self.client.get(reverse('pipeline:deploys'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['total'], 1)


class ValidacionesTests(TestCase):
    """Validaciones del formulario: autor, país y tipo de commit."""

    def _lanzar(self, **campos):
        datos = {'name': 'ana'}
        datos.update(campos)
        return self.client.post(
            reverse('pipeline:lanzar'),
            data=datos,
            content_type='application/json',
        )

    def test_nombre_con_espacios_se_normaliza(self):
        respuesta = self._lanzar(name='William Andrés Peña')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Deploy.objects.first().visitor_name, 'William-Andres-Pena')

    def test_nombre_sin_caracteres_utiles_se_rechaza(self):
        respuesta = self._lanzar(name='!!! ???')
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['error'], 'nombre_invalido')

    def test_nombre_no_admite_espacios_en_el_resultado(self):
        self._lanzar(name='mi nombre largo')
        self.assertNotIn(' ', Deploy.objects.first().visitor_name)

    def test_pais_fuera_del_catalogo_se_rechaza(self):
        respuesta = self._lanzar(location='Narnia')
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['error'], 'pais_invalido')
        self.assertEqual(Deploy.objects.count(), 0)

    def test_pais_valido_guarda_bandera(self):
        respuesta = self._lanzar(location='Colombia')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()['deploy']['flag'], '🇨🇴')

    def test_tipo_de_commit_invalido_se_rechaza(self):
        respuesta = self._lanzar(type='explotar')
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['error'], 'tipo_invalido')

    def test_tipo_por_defecto_es_feat(self):
        self._lanzar()
        self.assertEqual(Deploy.objects.first().commit_type, 'feat')

    def test_mensaje_se_compone_en_formato_convencional(self):
        self._lanzar(type='fix', message='arreglado el pipeline')
        self.assertEqual(
            Deploy.objects.first().mensaje_convencional,
            'fix: arreglado el pipeline',
        )


class PrefijoDuplicadoTests(TestCase):
    """El tipo vive en su campo: el mensaje nunca debe repetirlo."""

    def test_prefijo_escrito_a_mano_se_elimina(self):
        self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': 'ana', 'type': 'feat', 'message': 'feat: hola mundo'},
            content_type='application/json',
        )
        deploy = Deploy.objects.first()
        self.assertEqual(deploy.message, 'hola mundo')
        self.assertEqual(deploy.mensaje_convencional, 'feat: hola mundo')

    def test_prefijo_de_otro_tipo_tambien_se_elimina(self):
        self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': 'ana', 'type': 'fix', 'message': 'CHORE: limpieza'},
            content_type='application/json',
        )
        self.assertEqual(Deploy.objects.first().message, 'limpieza')

    def test_mensaje_normal_no_se_altera(self):
        self.client.post(
            reverse('pipeline:lanzar'),
            data={'name': 'ana', 'message': 'hola: esto no es un prefijo'},
            content_type='application/json',
        )
        self.assertEqual(
            Deploy.objects.first().message, 'hola: esto no es un prefijo'
        )
