/* =========================================================================
   PIPELINE COLABORATIVO
   Cada visitante lanza un deploy que recorre las etapas del pipeline y queda
   registrado en el muro. La animación corre en el cliente; la persistencia
   ocurre en Django (POST /pipeline/deploy/).
   ========================================================================= */
(function () {
    'use strict';

    const raiz = document.getElementById('pipeline-app');
    if (!raiz) return;

    const URL_LISTA = raiz.dataset.urlDeploys;
    const URL_DEPLOY = raiz.dataset.urlLanzar;

    const form = document.getElementById('pipeline-form');
    const consola = document.getElementById('console-output');
    const muro = document.getElementById('deploy-wall');
    const contador = document.getElementById('deploy-counter');
    const barra = document.getElementById('stage-progress');
    const etapas = Array.from(document.querySelectorAll('.stage'));
    const boton = document.getElementById('btn-deploy');

    const ETAPAS = [
        { clave: 'checkout', etiqueta: 'Clonando repositorio…', detalle: 'git checkout -b visitante/{hash}' },
        { clave: 'build', etiqueta: 'Construyendo imagen…', detalle: 'docker build -t portafolio:{hash} .' },
        { clave: 'test', etiqueta: 'Ejecutando pruebas…', detalle: '5 passed in 0.06s' },
        { clave: 'deploy', etiqueta: 'Desplegando…', detalle: 'kubectl rollout status deploy/portafolio' }
    ];

    const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

    const reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* --------------------------------------------------------------------
       Utilidades
       -------------------------------------------------------------------- */
    function obtenerCookie(nombre) {
        const partes = document.cookie.split(';');
        for (const parte of partes) {
            const limpio = parte.trim();
            if (limpio.startsWith(nombre + '=')) {
                return decodeURIComponent(limpio.slice(nombre.length + 1));
            }
        }
        return '';
    }

    function tiempoRelativo(iso) {
        const delta = (Date.now() - new Date(iso).getTime()) / 1000;
        if (delta < 60) return 'ahora';
        if (delta < 3600) return Math.floor(delta / 60) + 'm';
        if (delta < 86400) return Math.floor(delta / 3600) + 'h';
        return Math.floor(delta / 86400) + 'd';
    }

    // Inserta texto siempre con textContent: nada de HTML de terceros.
    function escribirLinea(partes) {
        const linea = document.createElement('span');
        linea.className = 'console-line';
        partes.forEach(([texto, clase]) => {
            const trozo = document.createElement('span');
            if (clase) trozo.className = clase;
            trozo.textContent = texto;
            linea.appendChild(trozo);
        });
        consola.appendChild(linea);
        consola.scrollTop = consola.scrollHeight;
    }

    function limpiarConsola() {
        consola.replaceChildren();
    }

    function empujarEvento(nombre, extra) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push(Object.assign({
            event: nombre,
            timestamp: new Date().toISOString()
        }, extra || {}));
    }

    /* --------------------------------------------------------------------
       Muro de deploys
       -------------------------------------------------------------------- */
    function construirFila(deploy, esNuevo) {
        const fila = document.createElement('div');
        fila.className = 'deploy-row' + (esNuevo ? ' is-new' : '');

        const hash = document.createElement('span');
        hash.className = 'deploy-hash';
        hash.textContent = deploy.commit;

        const actor = document.createElement('span');
        actor.className = 'deploy-actor';
        actor.textContent = deploy.actor;

        const estado = document.createElement('span');
        estado.className = 'deploy-status';
        estado.textContent = '✓ ' + tiempoRelativo(deploy.created_at);

        fila.append(hash, actor);

        if (deploy.message) {
            const msg = document.createElement('span');
            msg.className = 'deploy-msg';

            // El tipo va aparte para poder colorearlo por categoría
            const tipo = document.createElement('span');
            tipo.className = 'commit-tag commit-tag-' + (deploy.type || 'feat');
            tipo.textContent = (deploy.type || 'feat') + ':';
            msg.appendChild(tipo);
            msg.appendChild(document.createTextNode(' ' + deploy.message));

            fila.appendChild(msg);
        }

        fila.appendChild(estado);
        return fila;
    }

    function pintarMuro(deploys) {
        muro.replaceChildren();
        if (!deploys.length) {
            const vacio = document.createElement('p');
            vacio.className = 'text-muted small mb-0 py-3 text-center';
            vacio.textContent = 'Aún no hay deploys. ¡Sé quien lance el primero!';
            muro.appendChild(vacio);
            return;
        }
        deploys.forEach((d, i) => {
            const fila = construirFila(d, false);
            fila.style.animationDelay = (i * 0.05) + 's';
            muro.appendChild(fila);
        });
    }

    function actualizarContador(total) {
        if (contador) contador.textContent = total.toLocaleString('es-CO');
    }

    async function cargarDeploys() {
        try {
            const respuesta = await fetch(URL_LISTA, { headers: { 'Accept': 'application/json' } });
            if (!respuesta.ok) throw new Error('HTTP ' + respuesta.status);
            const datos = await respuesta.json();
            pintarMuro(datos.deploys || []);
            actualizarContador(datos.total || 0);
        } catch (error) {
            muro.replaceChildren();
            const aviso = document.createElement('p');
            aviso.className = 'text-muted small mb-0 py-3 text-center';
            aviso.textContent = 'No se pudo cargar el historial de deploys.';
            muro.appendChild(aviso);
        }
    }

    /* --------------------------------------------------------------------
       Animación del pipeline
       -------------------------------------------------------------------- */
    function reiniciarEtapas() {
        etapas.forEach((e) => e.classList.remove('is-running', 'is-done'));
        if (barra) barra.style.width = '0';
    }

    async function correrEtapas(hashProvisional) {
        const paso = reducirMovimiento ? 120 : 620;

        for (let i = 0; i < ETAPAS.length; i++) {
            const etapa = ETAPAS[i];
            const nodo = etapas[i];
            if (nodo) nodo.classList.add('is-running');

            escribirLinea([
                ['▸ ', 'c-accent'],
                [etapa.etiqueta, '']
            ]);

            await esperar(paso);

            escribirLinea([
                ['  ' + etapa.detalle.replace('{hash}', hashProvisional), 'c-dim']
            ]);

            if (nodo) {
                nodo.classList.remove('is-running');
                nodo.classList.add('is-done');
                nodo.querySelector('.stage-node').textContent = '✓';
            }
            if (barra) barra.style.width = (((i + 1) / ETAPAS.length) * 84) + '%';

            await esperar(paso / 2);
        }
    }

    /* --------------------------------------------------------------------
       Envío
       -------------------------------------------------------------------- */
    async function lanzarDeploy(evento) {
        evento.preventDefault();

        const nombre = form.elements.name.value.trim();
        if (!nombre) {
            form.elements.name.focus();
            return;
        }

        boton.disabled = true;
        boton.textContent = 'Desplegando…';
        reiniciarEtapas();
        limpiarConsola();

        const hashProvisional = Math.random().toString(16).slice(2, 9);

        escribirLinea([['$ ', 'c-accent'], ['git commit -m "' + form.elements.type.value + ': …" && deploy --author ' + nombre, '']]);

        const carga = {
            name: nombre,
            location: form.elements.location.value,
            type: form.elements.type.value,
            message: form.elements.message.value.trim(),
            website: form.elements.website.value
        };

        // La animación y la petición corren en paralelo: el pipeline se ve
        // fluido y el resultado real llega antes de escribir el desenlace.
        const peticion = fetch(URL_DEPLOY, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(carga)
        });

        await correrEtapas(hashProvisional);

        try {
            const respuesta = await peticion;
            const datos = await respuesta.json();

            if (!respuesta.ok || !datos.ok) {
                const mensaje = datos.detalle || 'El deploy fue rechazado.';
                escribirLinea([['✗ ', 'c-accent'], [mensaje, '']]);
                etapas.forEach((e) => e.classList.remove('is-done', 'is-running'));
                if (barra) barra.style.width = '0';
                empujarEvento('pipeline_deploy_rechazado', { motivo: datos.error || 'desconocido' });
                return;
            }

            const deploy = datos.deploy;

            if (barra) barra.style.width = '100%';
            escribirLinea([
                ['✓ ', 'c-ok'],
                ['Deploy ', ''],
                [deploy.commit, 'c-accent'],
                [' completado en ' + (deploy.duration_ms / 1000).toFixed(2) + 's', '']
            ]);
            escribirLinea([['  ¡Gracias por dejar tu huella en este portafolio!', 'c-ok']]);

            // Insertar el nuevo deploy al principio del muro
            const primero = muro.querySelector('.deploy-row');
            const fila = construirFila(deploy, true);
            if (primero) {
                muro.insertBefore(fila, primero);
            } else {
                muro.replaceChildren(fila);
            }
            actualizarContador(datos.total);

            form.reset();
            empujarEvento('pipeline_deploy_exitoso', {
                commit: deploy.commit,
                has_message: Boolean(deploy.message)
            });
        } catch (error) {
            escribirLinea([['✗ ', 'c-accent'], ['Error de red: no se pudo registrar el deploy.', '']]);
            empujarEvento('pipeline_deploy_error');
        } finally {
            boton.disabled = false;
            boton.textContent = 'Lanzar mi deploy';
        }
    }

    /* --------------------------------------------------------------------
       Arranque
       -------------------------------------------------------------------- */
    // --- Ayudas del formulario -------------------------------------------

    // El autor se escribe como un identificador de git: se corrige mientras
    // el visitante teclea, en vez de rechazarlo al enviar.
    function limpiarAutor(texto) {
        return texto
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')  // quita tildes
            .replace(/\s+/g, '-')
            .replace(/[^a-zA-Z0-9._-]/g, '')
            .replace(/-{2,}/g, '-')
            .slice(0, 24);
    }

    function iniciarAyudasFormulario() {
        if (!form) return;

        const campoAutor = form.elements.name;
        const campoTipo = form.elements.type;
        const campoMensaje = form.elements.message;
        const vistaPrevia = document.getElementById('preview-commit');

        if (campoAutor) {
            campoAutor.addEventListener('input', function () {
                const cursor = this.selectionStart;
                const antes = this.value;
                const despues = limpiarAutor(antes);
                if (antes !== despues) {
                    this.value = despues;
                    // Mantiene el cursor donde estaba pese a la corrección
                    const ajuste = despues.length - antes.length;
                    this.setSelectionRange(cursor + ajuste, cursor + ajuste);
                }
                refrescarVistaPrevia();
            });
        }

        function refrescarVistaPrevia() {
            if (!vistaPrevia) return;
            const tipo = campoTipo ? campoTipo.value : 'feat';
            const texto = campoMensaje ? campoMensaje.value.trim() : '';
            vistaPrevia.textContent = texto ? tipo + ': ' + texto : tipo + ': …';
        }

        if (campoTipo) campoTipo.addEventListener('change', refrescarVistaPrevia);
        if (campoMensaje) campoMensaje.addEventListener('input', refrescarVistaPrevia);
        refrescarVistaPrevia();
    }

    cargarDeploys();
    iniciarAyudasFormulario();
    if (form) form.addEventListener('submit', lanzarDeploy);

    // Evento de visualización de la sección
    const seccion = document.getElementById('pipeline');
    if (seccion && 'IntersectionObserver' in window) {
        const observador = new IntersectionObserver((entradas) => {
            entradas.forEach((entrada) => {
                if (entrada.isIntersecting) {
                    empujarEvento('pipeline_section_view');
                    observador.disconnect();
                }
            });
        }, { threshold: 0.4 });
        observador.observe(seccion);
    }
})();
