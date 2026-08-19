/* =========================================================================
   MOVIMIENTO Y ATMÓSFERA
   Scroll suave (Lenis), revelados al hacer scroll (GSAP + ScrollTrigger),
   interruptor de tema y botón de volver arriba.
   Todo degrada con elegancia: si una librería no carga, el sitio funciona.
   ========================================================================= */
(function () {
    'use strict';

    const prefiereMenosMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* --------------------------------------------------------------------
       1. Interruptor de tema
       -------------------------------------------------------------------- */
    function iniciarTema() {
        const boton = document.getElementById('theme-toggle');
        if (!boton) return;

        const icono = boton.querySelector('i');

        function pintarIcono() {
            const oscuro = document.documentElement.getAttribute('data-theme') === 'dark';
            if (icono) icono.className = oscuro ? 'bi bi-sun' : 'bi bi-moon-stars';
            boton.setAttribute('aria-pressed', String(oscuro));
        }

        pintarIcono();

        boton.addEventListener('click', function () {
            const actual = document.documentElement.getAttribute('data-theme');
            const nuevo = actual === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', nuevo);
            try { localStorage.setItem('tema', nuevo); } catch (e) {}
            pintarIcono();

            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ event: 'theme_toggle', theme: nuevo });
        });
    }

    /* --------------------------------------------------------------------
       2. Navbar al hacer scroll + botón de volver arriba
       -------------------------------------------------------------------- */
    function iniciarScrollUI() {
        const navbar = document.querySelector('.navbar');
        const botonArriba = document.getElementById('back-to-top');

        function alDesplazar() {
            const y = window.pageYOffset;
            if (navbar) navbar.classList.toggle('is-scrolled', y > 20);
            if (botonArriba) botonArriba.classList.toggle('is-visible', y > 400);
        }

        window.addEventListener('scroll', alDesplazar, { passive: true });
        alDesplazar();

        if (botonArriba) {
            botonArriba.addEventListener('click', function () {
                if (window.lenisInstancia) {
                    window.lenisInstancia.scrollTo(0);
                } else {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        }
    }

    /* --------------------------------------------------------------------
       3. Scroll suave con Lenis
       -------------------------------------------------------------------- */
    // El trackpad de macOS ya aplica su propia inercia; Lenis encima suma un
    // segundo suavizado y el scroll se siente pesado. La rueda de un ratón,
    // en cambio, sí gana con la interpolación.
    //
    // Por eso arrancamos SIN Lenis y solo lo activamos si aparece una rueda.
    // Encenderlo de entrada y apagarlo al detectar el trackpad cancelaba la
    // animación del primer gesto a media ejecución: ese scroll se perdía y
    // se sentía como un tirón. Empezando en nativo, el trackpad nunca lo sufre.
    //
    // Heurística: la rueda manda deltas grandes y enteros (100, 120, 53…);
    // el trackpad, deltas pequeños y a menudo fraccionarios (4.5, 12.3…).
    function crearLenis() {
        const lenis = new Lenis({
            duration: 0.9,
            easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
            smoothWheel: true
        });

        function bucle(tiempo) {
            lenis.raf(tiempo);
            requestAnimationFrame(bucle);
        }
        requestAnimationFrame(bucle);

        window.lenisInstancia = lenis;

        // ScrollTrigger debe seguir el scroll de Lenis una vez activo
        if (typeof ScrollTrigger !== 'undefined' && typeof gsap !== 'undefined') {
            lenis.on('scroll', ScrollTrigger.update);
            gsap.ticker.lagSmoothing(0);
            ScrollTrigger.refresh();
        }

        return lenis;
    }

    function observarDispositivo() {
        if (prefiereMenosMovimiento || typeof Lenis === 'undefined') return;

        function alGirar(evento) {
            const delta = Math.abs(evento.deltaY);
            const esRueda = evento.deltaMode !== 0 ||
                (delta >= 50 && Number.isInteger(evento.deltaY));

            // Sea rueda o trackpad, la decisión se toma una sola vez.
            window.removeEventListener('wheel', alGirar);

            // Trackpad: nos quedamos con el scroll nativo del sistema.
            if (esRueda) crearLenis();
        }

        window.addEventListener('wheel', alGirar, { passive: true });
    }

    /* --------------------------------------------------------------------
       3b. Enlaces internos
       Funciona con Lenis o sin él, según lo que haya en ese momento.
       -------------------------------------------------------------------- */
    function iniciarAnclas() {
        document.querySelectorAll('a[href^="#"]').forEach(function (ancla) {
            const destino = ancla.getAttribute('href');
            if (!destino || destino === '#') return;

            ancla.addEventListener('click', function (evento) {
                const objetivo = document.querySelector(destino);
                if (!objetivo) return;
                evento.preventDefault();

                if (window.lenisInstancia) {
                    window.lenisInstancia.scrollTo(objetivo, { offset: -90 });
                } else {
                    const arriba = objetivo.getBoundingClientRect().top + window.pageYOffset - 90;
                    window.scrollTo({ top: arriba, behavior: 'smooth' });
                }
            });
        });
    }

    /* --------------------------------------------------------------------
       4. Revelados al hacer scroll
       -------------------------------------------------------------------- */
    // Muestra de inmediato cualquier elemento que ya esté dentro de la pantalla
    // pero siga invisible. Se ejecuta con moderación para no castigar el scroll.
    let ultimoRepaso = 0;
    function revelarLoVisible() {
        const ahora = Date.now();
        if (ahora - ultimoRepaso < 250) return;
        ultimoRepaso = ahora;

        const alto = window.innerHeight;
        document.querySelectorAll('.reveal:not(.is-visible)').forEach(function (el) {
            const caja = el.getBoundingClientRect();
            if (caja.top < alto * 0.95 && caja.bottom > 0) {
                el.classList.add('is-visible');
                if (typeof gsap !== 'undefined') {
                    gsap.set(el, { opacity: 1, y: 0 });
                }
            }
        });
    }

    function iniciarRevelados() {
        const elementos = document.querySelectorAll('.reveal');
        if (!elementos.length) return;

        // Sin movimiento: se muestra todo de inmediato.
        if (prefiereMenosMovimiento) {
            elementos.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }

        // Camino preferente: GSAP + ScrollTrigger (escalonado por grupo).
        if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);

            document.querySelectorAll('[data-reveal-group]').forEach(function (grupo) {
                const hijos = grupo.querySelectorAll('.reveal');
                if (!hijos.length) return;

                gsap.to(hijos, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: 'power3.out',
                    stagger: 0.09,
                    scrollTrigger: {
                        trigger: grupo,
                        start: 'top 82%',
                        once: true
                    },
                    onStart: function () {
                        hijos.forEach(function (h) { h.classList.add('is-visible'); });
                    }
                });
            });

            // Elementos sueltos (fuera de cualquier grupo)
            document.querySelectorAll('.reveal:not([data-reveal-group] .reveal)').forEach(function (el) {
                gsap.to(el, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: 'power3.out',
                    scrollTrigger: { trigger: el, start: 'top 88%', once: true },
                    onStart: function () { el.classList.add('is-visible'); }
                });
            });

            // Las posiciones se calculan antes de que carguen las fuentes web:
            // recalcularlas evita que un trigger quede desfasado.
            if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
            }
            window.addEventListener('load', function () { ScrollTrigger.refresh(); });

            // Salvavidas: ante un salto brusco (barra de scroll, Cmd+Fin, anclas)
            // nada debe quedarse invisible dentro de la pantalla.
            revelarLoVisible();
            window.addEventListener('scroll', revelarLoVisible, { passive: true });

            return;
        }

        // Reserva: IntersectionObserver con las transiciones del CSS.
        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada, indice) {
                if (entrada.isIntersecting) {
                    setTimeout(function () {
                        entrada.target.classList.add('is-visible');
                    }, indice * 70);
                    observador.unobserve(entrada.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        elementos.forEach(function (el) { observador.observe(el); });
    }

    /* --------------------------------------------------------------------
       5. Entrada del hero
       -------------------------------------------------------------------- */
    function iniciarHero() {
        const piezas = document.querySelectorAll('[data-hero-in]');
        if (!piezas.length) return;

        if (prefiereMenosMovimiento || typeof gsap === 'undefined') return;

        function animar() {
            gsap.from(piezas, {
                opacity: 0,
                y: 26,
                duration: 0.95,
                ease: 'power3.out',
                stagger: 0.11,
                delay: 0.12,
                // Al terminar se retiran los estilos inline: el hero queda
                // gobernado por el CSS y nunca atrapado en un estado a medias.
                clearProps: 'opacity,transform'
            });
        }

        // gsap.from() deja el elemento invisible de entrada y lo revela con
        // requestAnimationFrame. En una pestaña en segundo plano rAF se
        // congela, así que la animación jamás correría y el hero quedaría
        // vacío: se espera a que la pestaña sea visible antes de animar.
        if (document.hidden) {
            document.addEventListener('visibilitychange', function alVerse() {
                if (document.hidden) return;
                document.removeEventListener('visibilitychange', alVerse);
                animar();
            });
            return;
        }

        animar();

        // Red de seguridad: si algo interrumpe la animación, el contenido
        // debe terminar visible pase lo que pase.
        setTimeout(function () {
            piezas.forEach(function (pieza) {
                if (parseFloat(getComputedStyle(pieza).opacity) < 0.9) {
                    gsap.set(pieza, { clearProps: 'opacity,transform' });
                }
            });
        }, 2600);
    }

    /* --------------------------------------------------------------------
       6. Contadores animados
       -------------------------------------------------------------------- */
    function iniciarContadores() {
        const contadores = document.querySelectorAll('[data-contador]');
        if (!contadores.length || !('IntersectionObserver' in window)) return;

        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (!entrada.isIntersecting) return;

                const el = entrada.target;
                const destino = parseFloat(el.dataset.contador) || 0;
                const decimales = (el.dataset.contador.split('.')[1] || '').length;

                if (prefiereMenosMovimiento) {
                    el.textContent = destino.toFixed(decimales);
                } else {
                    const inicio = performance.now();
                    const duracion = 1300;

                    function paso(ahora) {
                        const avance = Math.min((ahora - inicio) / duracion, 1);
                        const suave = 1 - Math.pow(1 - avance, 3);
                        el.textContent = (destino * suave).toFixed(decimales);
                        if (avance < 1) requestAnimationFrame(paso);
                    }
                    requestAnimationFrame(paso);
                }

                observador.unobserve(el);
            });
        }, { threshold: 0.6 });

        contadores.forEach(function (c) { observador.observe(c); });
    }

    /* --------------------------------------------------------------------
       Arranque
       -------------------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', function () {
        iniciarTema();
        iniciarScrollUI();
        iniciarAnclas();
        // Los revelados arrancan sobre el scroll nativo; si más tarde entra
        // Lenis, crearLenis() se encarga de sincronizar ScrollTrigger.
        iniciarRevelados();
        observarDispositivo();
        iniciarHero();
        iniciarContadores();
    });
})();
