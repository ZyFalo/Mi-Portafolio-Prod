/* =========================================================================
   EL CIELO DE LOS VISITANTES
   Cada persona que pasa enciende una estrella y elige dónde va. Las que
   quedan cerca se unen en constelaciones.

   El gesto va primero: se toca el cielo y el formulario nace en ese punto,
   no al revés. Así lo que se pide no es rellenar unos campos sino elegir un
   sitio, que es lo que de verdad se recuerda.

   La animación corre en el cliente; la persistencia, en Django
   (POST /cielo/encender/). Las coordenadas viajan normalizadas entre 0 y 1
   para que el mismo cielo se vea igual en cualquier pantalla.
   ========================================================================= */
(function () {
    'use strict';

    const raiz = document.getElementById('cielo-app');
    if (!raiz) return;

    const URL_ESTRELLAS = raiz.dataset.urlEstrellas;
    const URL_ENCENDER = raiz.dataset.urlEncender;

    const svg = document.getElementById('cielo-svg');
    const capaLineas = document.getElementById('cielo-lineas');
    const capaEstrellas = document.getElementById('cielo-estrellas');
    const capaFantasma = document.getElementById('cielo-fantasma');
    const lienzo = document.getElementById('cielo-lienzo');
    const globo = document.getElementById('cielo-globo');
    const aviso = document.getElementById('cielo-aviso');
    const llamada = document.getElementById('cielo-llamada');
    const contador = document.getElementById('cielo-contador');
    const total = document.getElementById('cielo-total');

    const panel = document.getElementById('cielo-panel');
    const cerrarBoton = document.getElementById('cielo-cerrar');
    const form = document.getElementById('cielo-form');
    const campoNombre = document.getElementById('cielo-nombre');
    const campoLugar = document.getElementById('cielo-lugar');
    const campoTrampa = document.getElementById('cielo-website');
    const boton = document.getElementById('cielo-boton');
    const nota = document.getElementById('cielo-nota');

    const NS = 'http://www.w3.org/2000/svg';
    const ANCHO = 1000;
    const ALTO = 560;

    // Radio de cada estrella según su magnitud. Un cielo donde todas miden
    // igual se lee como una cuadrícula, no como un cielo.
    const RADIOS = { 1: 2.2, 2: 3.3, 3: 4.6 };

    // Distancia máxima, en unidades del lienzo, para unir dos estrellas.
    // Más allá las líneas dejan de sugerir una constelación y parecen ruido.
    const ALCANCE = 165;

    // Por debajo de este ancho el panel no cabe flotando: el CSS lo ancla al
    // pie del lienzo y aquí se deja de posicionar a mano.
    const ANCHO_ANCLADO = 576;

    const reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let estrellas = [];
    let elegida = null;      // {x, y} normalizado, aún sin confirmar
    let enviando = false;

    /* --------------------------------------------------------------------
       Utilidades
       -------------------------------------------------------------------- */
    function obtenerCookie(nombre) {
        for (const parte of document.cookie.split(';')) {
            const [clave, valor] = parte.trim().split('=');
            if (clave === nombre) return decodeURIComponent(valor);
        }
        return '';
    }

    function crear(etiqueta, atributos) {
        const el = document.createElementNS(NS, etiqueta);
        for (const clave in atributos) el.setAttribute(clave, atributos[clave]);
        return el;
    }

    function aLienzo(estrella) {
        return { x: estrella.x * ANCHO, y: estrella.y * ALTO };
    }

    function tiempoRelativo(iso) {
        const minutos = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
        if (minutos < 1) return 'ahora mismo';
        if (minutos < 60) return 'hace ' + minutos + ' min';
        const horas = Math.floor(minutos / 60);
        if (horas < 24) return 'hace ' + horas + 'h';
        const dias = Math.floor(horas / 24);
        return dias === 1 ? 'ayer' : 'hace ' + dias + ' días';
    }

    function empujarEvento(nombre, extra) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push(Object.assign({ event: nombre }, extra || {}));
    }

    /* --------------------------------------------------------------------
       Constelaciones
       Cada estrella se une con su vecina más próxima dentro del alcance.
       Es el grafo del vecino más cercano: agrupa sin cruces enredados y sin
       dejar puntos sueltos por el cielo.
       -------------------------------------------------------------------- */
    function calcularEnlaces(lista) {
        const puntos = lista.map(aLienzo);
        const enlaces = [];
        const vistos = new Set();

        for (let i = 0; i < puntos.length; i++) {
            let mejor = -1;
            let menor = Infinity;

            for (let j = 0; j < puntos.length; j++) {
                if (i === j) continue;
                const dx = puntos[i].x - puntos[j].x;
                const dy = puntos[i].y - puntos[j].y;
                const distancia = Math.sqrt(dx * dx + dy * dy);
                if (distancia < menor) { menor = distancia; mejor = j; }
            }

            if (mejor < 0 || menor > ALCANCE) continue;

            // El vecino más cercano suele ser recíproco: sin esto la misma
            // línea se dibujaría dos veces, una por cada extremo.
            const clave = i < mejor ? i + '-' + mejor : mejor + '-' + i;
            if (vistos.has(clave)) continue;
            vistos.add(clave);

            enlaces.push({ a: puntos[i], b: puntos[mejor] });
        }

        return enlaces;
    }

    function pintarLineas(lista) {
        const fragmento = document.createDocumentFragment();
        calcularEnlaces(lista).forEach(function (enlace) {
            fragmento.appendChild(crear('line', {
                x1: enlace.a.x.toFixed(1), y1: enlace.a.y.toFixed(1),
                x2: enlace.b.x.toFixed(1), y2: enlace.b.y.toFixed(1)
            }));
        });
        capaLineas.replaceChildren(fragmento);
    }

    /* --------------------------------------------------------------------
       Dibujo de estrellas
       -------------------------------------------------------------------- */
    function crearEstrella(estrella, recienNacida) {
        const punto = aLienzo(estrella);
        const radio = RADIOS[estrella.magnitud] || RADIOS[1];

        const grupo = crear('g', {
            class: 'cielo-estrella' + (recienNacida ? ' es-nueva' : ''),
            tabindex: '0',
            role: 'listitem',
            'aria-label': estrella.label
        });

        // El halo da profundidad y, sobre todo, agranda el área sensible:
        // acertarle a un punto de 2px con el ratón sería una crueldad.
        grupo.appendChild(crear('circle', {
            class: 'cielo-halo', cx: punto.x, cy: punto.y, r: radio * 4.5
        }));
        grupo.appendChild(crear('circle', {
            class: 'cielo-nucleo', cx: punto.x, cy: punto.y, r: radio
        }));

        // El parpadeo se desfasa por estrella; si todas latieran a la vez
        // parecería un cartel de neón, no un cielo.
        if (!reducirMovimiento) {
            grupo.style.setProperty('--retardo', (estrella.id % 47) / 10 + 's');
        }

        grupo.addEventListener('mouseenter', function () { mostrarGlobo(estrella, punto); });
        grupo.addEventListener('focus', function () { mostrarGlobo(estrella, punto); });
        grupo.addEventListener('mouseleave', ocultarGlobo);
        grupo.addEventListener('blur', ocultarGlobo);

        if (esMia(estrella.id)) grupo.classList.add('es-mia');

        return grupo;
    }

    function pintarCielo(lista, nueva) {
        estrellas = lista;
        const fragmento = document.createDocumentFragment();
        lista.forEach(function (estrella) {
            fragmento.appendChild(crearEstrella(estrella, nueva && estrella.id === nueva.id));
        });
        capaEstrellas.replaceChildren(fragmento);
        pintarLineas(lista);

        if (total) total.textContent = lista.length;
        if (contador) contador.hidden = false;
        if (aviso) aviso.hidden = lista.length > 0;
    }

    /* --------------------------------------------------------------------
       Globo informativo
       -------------------------------------------------------------------- */
    function mostrarGlobo(estrella, punto) {
        if (!globo || !panel.hidden) return;   // con el formulario abierto, estorba

        const caja = lienzo.getBoundingClientRect();
        const escalaX = caja.width / ANCHO;
        const escalaY = caja.height / ALTO;

        globo.replaceChildren();
        const titulo = document.createElement('strong');
        titulo.textContent = (estrella.flag ? estrella.flag + ' ' : '') + estrella.name;
        const pie = document.createElement('span');
        pie.textContent = [estrella.location, tiempoRelativo(estrella.created_at)]
            .filter(Boolean).join(' · ');

        globo.appendChild(titulo);
        globo.appendChild(pie);
        globo.hidden = false;

        // Se mantiene dentro del lienzo aunque la estrella esté en un borde
        const ancho = globo.offsetWidth;
        const izquierda = Math.min(Math.max(punto.x * escalaX - ancho / 2, 6), caja.width - ancho - 6);
        globo.style.left = izquierda + 'px';
        globo.style.top = (punto.y * escalaY + 18) + 'px';
    }

    function ocultarGlobo() {
        if (globo) globo.hidden = true;
    }

    /* --------------------------------------------------------------------
       Reconocer la propia estrella al volver
       -------------------------------------------------------------------- */
    function misEstrellas() {
        try {
            return JSON.parse(localStorage.getItem('mis-estrellas') || '[]');
        } catch (e) { return []; }
    }

    function esMia(id) {
        return misEstrellas().indexOf(id) !== -1;
    }

    function recordarEstrella(id) {
        try {
            const mias = misEstrellas();
            mias.push(id);
            localStorage.setItem('mis-estrellas', JSON.stringify(mias.slice(-20)));
        } catch (e) { /* modo privado: se pierde el recuerdo, nada más */ }
    }

    /* --------------------------------------------------------------------
       Elegir sitio en el cielo
       -------------------------------------------------------------------- */
    // getScreenCTM traduce de píxeles de pantalla a unidades del lienzo sin
    // que importe cómo haya escalado el SVG: más fiable que dividir por el
    // ancho del contenedor.
    function coordenadasDelEvento(evento) {
        const punto = svg.createSVGPoint();
        punto.x = evento.clientX;
        punto.y = evento.clientY;
        const dentro = punto.matrixTransform(svg.getScreenCTM().inverse());
        return {
            x: Math.min(Math.max(dentro.x / ANCHO, 0), 1),
            y: Math.min(Math.max(dentro.y / ALTO, 0), 1)
        };
    }

    function marcarSitio(coordenadas) {
        elegida = coordenadas;
        const punto = aLienzo(coordenadas);

        const grupo = crear('g', { class: 'cielo-fantasma' });
        grupo.appendChild(crear('circle', { cx: punto.x, cy: punto.y, r: 14, class: 'cielo-fantasma-aro' }));
        grupo.appendChild(crear('circle', { cx: punto.x, cy: punto.y, r: 3.4, class: 'cielo-fantasma-nucleo' }));
        capaFantasma.replaceChildren(grupo);

        return punto;
    }

    /* --------------------------------------------------------------------
       El formulario, anclado al punto elegido
       -------------------------------------------------------------------- */
    function colocarPanel(punto) {
        const caja = lienzo.getBoundingClientRect();

        // En pantallas estrechas el panel va anclado abajo por CSS: cualquier
        // posición que se calcule aquí lo sacaría de sitio.
        if (caja.width < ANCHO_ANCLADO) {
            panel.style.left = '';
            panel.style.top = '';
            return;
        }

        const px = punto.x * (caja.width / ANCHO);
        const py = punto.y * (caja.height / ALTO);
        const ancho = panel.offsetWidth;
        const alto = panel.offsetHeight;
        const aire = 18;

        // Se abre hacia el lado con sitio, para no taparle al visitante el
        // punto que acaba de elegir.
        let izquierda = px + aire;
        if (izquierda + ancho > caja.width - 10) izquierda = px - ancho - aire;
        izquierda = Math.max(10, Math.min(izquierda, caja.width - ancho - 10));

        const arriba = Math.max(10, Math.min(py - alto / 2, caja.height - alto - 10));

        panel.style.left = izquierda + 'px';
        panel.style.top = arriba + 'px';
    }

    function abrirPanel(punto) {
        ocultarGlobo();
        panel.hidden = false;
        if (llamada) llamada.hidden = true;
        lienzo.classList.add('es-eligiendo');

        colocarPanel(punto);

        // El foco entra en el campo, pero sin arrastrar la página: el cielo
        // ya está donde el visitante lo estaba mirando.
        campoNombre.focus({ preventScroll: true });
    }

    function cerrarPanel() {
        panel.hidden = true;
        lienzo.classList.remove('es-eligiendo');
        capaFantasma.replaceChildren();
        elegida = null;
        mostrarNota('');
        if (llamada) llamada.hidden = false;
    }

    function alTocarCielo(evento) {
        if (enviando) return;
        const punto = marcarSitio(coordenadasDelEvento(evento));
        if (panel.hidden) {
            abrirPanel(punto);
        } else {
            // Ya estaba abierto: solo se muda al punto nuevo
            colocarPanel(punto);
        }
    }

    function mostrarNota(texto, tono) {
        nota.textContent = texto || '';
        nota.className = 'cielo-nota mb-0' + (tono ? ' es-' + tono : '');
    }

    /* --------------------------------------------------------------------
       Encender
       -------------------------------------------------------------------- */
    async function enviar(evento) {
        evento.preventDefault();
        if (enviando || !elegida) return;

        if (campoNombre.value.trim().length < 2) {
            mostrarNota('Escribe al menos 2 letras para firmar tu estrella.', 'error');
            campoNombre.focus();
            return;
        }

        enviando = true;
        boton.disabled = true;
        boton.textContent = 'Encendiendo…';
        mostrarNota('');

        try {
            const respuesta = await fetch(URL_ENCENDER, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': obtenerCookie('csrftoken')
                },
                body: JSON.stringify({
                    name: campoNombre.value,
                    location: campoLugar.value,
                    website: campoTrampa ? campoTrampa.value : '',
                    x: elegida.x,
                    y: elegida.y
                })
            });

            const datos = await respuesta.json();

            if (!datos.ok) {
                mostrarNota(datos.detalle || 'No se pudo encender tu estrella.', 'error');
                empujarEvento('cielo_error', { motivo: datos.error });
                return;
            }

            // El servidor puede haber corrido la estrella para que no se pise
            // con otra: se dibuja donde ella dice, no donde se tocó.
            const nueva = datos.estrella;
            recordarEstrella(nueva.id);

            form.reset();
            cerrarPanel();

            pintarCielo(estrellas.concat([nueva]), nueva);
            if (total) total.textContent = datos.total;

            if (llamada) {
                llamada.innerHTML = '<i class="bi bi-check2"></i> Tu estrella ya está en el cielo. Gracias por pasar.';
                llamada.classList.add('es-ok');
            }

            empujarEvento('cielo_estrella_encendida', { total: datos.total });

            // El panel de estado lleva la cuenta de estrellas encendidas
            const marcador = document.getElementById('status-estrellas');
            if (marcador) marcador.textContent = datos.total;
        } catch (error) {
            mostrarNota('Error de red: no se pudo encender tu estrella.', 'error');
            empujarEvento('cielo_error', { motivo: 'red' });
        } finally {
            enviando = false;
            boton.disabled = false;
            boton.innerHTML = '<i class="bi bi-brightness-high me-1"></i>Encender mi estrella';
        }
    }

    /* --------------------------------------------------------------------
       Arranque
       -------------------------------------------------------------------- */
    async function cargar() {
        try {
            const respuesta = await fetch(URL_ESTRELLAS, { headers: { Accept: 'application/json' } });
            const datos = await respuesta.json();
            const lista = datos.estrellas || [];

            pintarCielo(lista);
            if (total) total.textContent = datos.total || 0;

            if (aviso && !lista.length) {
                aviso.textContent = 'Este cielo está vacío. La primera estrella puede ser la tuya.';
                aviso.hidden = false;
            }
            if (llamada) llamada.hidden = false;
        } catch (error) {
            if (aviso) aviso.textContent = 'No se pudo cargar el cielo.';
        }
    }

    svg.addEventListener('click', alTocarCielo);
    form.addEventListener('submit', enviar);
    cerrarBoton.addEventListener('click', cerrarPanel);

    document.addEventListener('keydown', function (evento) {
        if (evento.key === 'Escape' && !panel.hidden) cerrarPanel();
    });

    // Al cambiar el tamaño de la ventana el punto sigue donde estaba, pero su
    // sitio en pantalla no: el panel tiene que recalcularse.
    window.addEventListener('resize', function () {
        if (!panel.hidden && elegida) colocarPanel(aLienzo(elegida));
    });

    cargar();
})();
