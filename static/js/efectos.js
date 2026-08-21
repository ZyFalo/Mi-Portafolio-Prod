/* =========================================================================
   EFECTOS Y DETALLES
   Terminal del hero, panel de estado en vivo, diagrama de arquitectura que
   se traza al entrar en pantalla, títulos que se descifran, inclinación 3D
   y barra de progreso de lectura.

   Todo es progresivo: si algo falla o el usuario pide menos movimiento, el
   contenido queda legible y estático.
   ========================================================================= */
(function () {
    'use strict';

    const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

    /* --------------------------------------------------------------------
       1. Terminal del hero
       -------------------------------------------------------------------- */
    const GUION = [
        { orden: 'whoami', salida: ['William Andrés Peña Vargas', 'Ingeniero de Software · DevOps & Cloud AWS'] },
        { orden: 'cat stack.txt', salida: ['AWS · Docker · CI/CD · Linux · Python · PHP/Symfony'] },
        { orden: 'git log -1 --oneline', salida: ['feat: lideré la adopción de IA agéntica en el equipo'] },
        { orden: 'terraform plan', salida: ['~ aprendiendo… (en formación, aún no en producción)'] }
    ];

    async function iniciarTerminal() {
        const caja = document.getElementById('hero-terminal');
        if (!caja) return;

        // Sin animación: se vuelca el guion completo de una vez.
        if (quieto) {
            GUION.forEach(function (paso) {
                caja.appendChild(crearLinea('$ ' + paso.orden, 'term-cmd'));
                paso.salida.forEach(function (s) {
                    caja.appendChild(crearLinea(s, 'term-out'));
                });
            });
            return;
        }

        for (const paso of GUION) {
            const linea = crearLinea('$ ', 'term-cmd');
            const cursor = document.createElement('span');
            cursor.className = 'term-cursor';
            linea.appendChild(cursor);
            caja.appendChild(linea);

            // Teclear el comando carácter a carácter
            for (const letra of paso.orden) {
                cursor.insertAdjacentText('beforebegin', letra);
                await esperar(38 + Math.round(Math.sin(letra.charCodeAt(0)) * 12));
            }
            cursor.remove();
            await esperar(230);

            for (const salida of paso.salida) {
                caja.appendChild(crearLinea(salida, 'term-out'));
                await esperar(90);
            }
            await esperar(700);
        }

        // Deja el prompt latiendo al final
        const final = crearLinea('$ ', 'term-cmd');
        const cursorFinal = document.createElement('span');
        cursorFinal.className = 'term-cursor';
        final.appendChild(cursorFinal);
        caja.appendChild(final);
    }

    function crearLinea(texto, clase) {
        const linea = document.createElement('div');
        linea.className = 'term-line ' + clase;
        linea.textContent = texto;
        return linea;
    }

    /* --------------------------------------------------------------------
       2. Diagrama de arquitectura que se traza solo
       -------------------------------------------------------------------- */
    function iniciarArquitectura() {
        const svg = document.getElementById('arquitectura');
        if (!svg || !('IntersectionObserver' in window)) return;

        const trazos = svg.querySelectorAll('.arq-trazo');
        const nodos = svg.querySelectorAll('.arq-nodo');

        if (quieto) {
            trazos.forEach(function (t) { t.style.strokeDashoffset = '0'; });
            nodos.forEach(function (n) { n.style.opacity = '1'; });
            return;
        }

        // Preparar cada trazo con su propia longitud. El camino de vuelta ya
        // es discontinuo por diseño, así que se revela con opacidad en vez de
        // con dasharray, que le borraría el punteado.
        trazos.forEach(function (trazo) {
            if (trazo.classList.contains('arq-trazo-vuelta')) {
                trazo.style.opacity = '0';
                trazo.style.transition = 'opacity 0.9s cubic-bezier(0.33, 1, 0.68, 1)';
                return;
            }
            const largo = trazo.getTotalLength();
            trazo.style.strokeDasharray = largo;
            trazo.style.strokeDashoffset = largo;
            trazo.style.transition = 'stroke-dashoffset 1.1s cubic-bezier(0.33, 1, 0.68, 1)';
        });

        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (!entrada.isIntersecting) return;

                nodos.forEach(function (nodo, i) {
                    setTimeout(function () { nodo.style.opacity = '1'; }, i * 170);
                });
                trazos.forEach(function (trazo, i) {
                    setTimeout(function () {
                        if (trazo.classList.contains('arq-trazo-vuelta')) {
                            trazo.style.opacity = '0.75';
                        } else {
                            trazo.style.strokeDashoffset = '0';
                        }
                    }, 240 + i * 170);
                });

                observador.disconnect();
            });
        }, { threshold: 0.35 });

        observador.observe(svg);

        // Red de seguridad: los nodos parten de opacidad 0, así que si el
        // observador no llega a dispararse el diagrama quedaría invisible.
        setTimeout(function () {
            nodos.forEach(function (n) { n.style.opacity = '1'; });
            trazos.forEach(function (t) {
                if (t.classList.contains('arq-trazo-vuelta')) {
                    t.style.opacity = '0.75';
                } else {
                    t.style.strokeDashoffset = '0';
                }
            });
        }, 6000);
    }

    /* --------------------------------------------------------------------
       3. Revelado del título
       Una cortina descubre el texto de izquierda a derecha. Sustituye al
       efecto de letras desordenadas, que distraía de la lectura.

       El estado inicial lo pone el propio script: si el JavaScript no
       llegara a ejecutarse, el título se ve normal desde el primer momento
       en lugar de quedarse oculto por el recorte.
       -------------------------------------------------------------------- */
    function iniciarRevelarTitulos() {
        const titulos = document.querySelectorAll('[data-revelar-titulo]');
        if (!titulos.length || quieto || !('IntersectionObserver' in window)) return;

        titulos.forEach(function (titulo) { titulo.classList.add('titulo-cortina'); });

        function abrir(titulo) { titulo.classList.add('is-revelado'); }

        // Umbral bajo: un titular alto en pantalla pequeña puede no llegar
        // nunca a estar visible en su mayor parte.
        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (!entrada.isIntersecting) return;
                abrir(entrada.target);
                observador.unobserve(entrada.target);
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -5% 0px' });

        titulos.forEach(function (titulo) { observador.observe(titulo); });

        // Red de seguridad: un título recortado que no se abra queda
        // invisible, así que nada puede quedarse a medias.
        function abrirLoVisible() {
            document.querySelectorAll('[data-revelar-titulo]:not(.is-revelado)')
                .forEach(function (titulo) {
                    const caja = titulo.getBoundingClientRect();
                    if (caja.top < window.innerHeight && caja.bottom > 0) abrir(titulo);
                });
        }

        window.addEventListener('scroll', abrirLoVisible, { passive: true });
        window.addEventListener('resize', abrirLoVisible);
        abrirLoVisible();

        // Último recurso: pasados unos segundos, ningún título sigue oculto.
        setTimeout(function () {
            document.querySelectorAll('[data-revelar-titulo]').forEach(abrir);
        }, 6000);
    }

    /* --------------------------------------------------------------------
       4. Inclinación 3D en tarjetas
       -------------------------------------------------------------------- */
    function iniciarInclinacion() {
        if (quieto || window.matchMedia('(hover: none)').matches) return;

        document.querySelectorAll('[data-tilt]').forEach(function (tarjeta) {
            let pendiente = false;

            tarjeta.addEventListener('mousemove', function (evento) {
                if (pendiente) return;
                pendiente = true;

                requestAnimationFrame(function () {
                    const caja = tarjeta.getBoundingClientRect();
                    const x = (evento.clientX - caja.left) / caja.width - 0.5;
                    const y = (evento.clientY - caja.top) / caja.height - 0.5;

                    tarjeta.style.transform =
                        'perspective(900px) rotateX(' + (-y * 5).toFixed(2) + 'deg) ' +
                        'rotateY(' + (x * 5).toFixed(2) + 'deg) translateY(-4px)';
                    pendiente = false;
                });
            });

            tarjeta.addEventListener('mouseleave', function () {
                tarjeta.style.transform = '';
            });
        });
    }

    /* --------------------------------------------------------------------
       5. Barra de progreso de lectura
       -------------------------------------------------------------------- */
    function iniciarProgreso() {
        const barra = document.getElementById('read-progress');
        if (!barra) return;

        function actualizar() {
            const alcance = document.documentElement.scrollHeight - window.innerHeight;
            const avance = alcance > 0 ? (window.pageYOffset / alcance) * 100 : 0;
            barra.style.width = Math.min(100, Math.max(0, avance)) + '%';
        }

        window.addEventListener('scroll', actualizar, { passive: true });
        window.addEventListener('resize', actualizar);
        actualizar();
    }


    /* --------------------------------------------------------------------
       6. Revelado del texto en el FAQ
       Equivale al "BlurredStagger" de framer-motion, pero con CSS puro y
       por PALABRAS en vez de por letras: una respuesta larga generaría
       cientos de nodos por letra, y además romper palabra a palabra
       estropea la lectura y los lectores de pantalla.
       -------------------------------------------------------------------- */
    function trocearEnPalabras(elemento) {
        if (elemento.dataset.troceado === '1') return;
        elemento.dataset.troceado = '1';

        const bloques = elemento.querySelectorAll('p');
        const destino = bloques.length ? bloques : [elemento];

        destino.forEach(function (bloque) {
            const palabras = bloque.textContent.split(/(\s+)/);
            const fragmento = document.createDocumentFragment();
            let indice = 0;

            palabras.forEach(function (parte) {
                if (!parte.trim()) {
                    fragmento.appendChild(document.createTextNode(parte));
                    return;
                }
                const span = document.createElement('span');
                span.className = 'palabra-revelada';
                span.textContent = parte;
                span.style.animationDelay = (indice * 0.022) + 's';
                fragmento.appendChild(span);
                indice++;
            });

            bloque.replaceChildren(fragmento);
        });
    }

    function reiniciarAnimacion(elemento) {
        elemento.querySelectorAll('.palabra-revelada').forEach(function (palabra) {
            palabra.style.animation = 'none';
            void palabra.offsetWidth;   // fuerza el reflujo para poder repetirla
            palabra.style.animation = '';
        });
    }

    function iniciarRevelarTexto() {
        const respuestas = document.querySelectorAll('[data-revelar-texto]');
        if (!respuestas.length) return;

        // Sin animación no se toca el DOM: el texto queda tal cual.
        if (quieto) return;

        respuestas.forEach(function (respuesta) {
            const panel = respuesta.closest('.accordion-collapse');
            if (!panel) {
                trocearEnPalabras(respuesta);
                return;
            }

            panel.addEventListener('show.bs.collapse', function () {
                trocearEnPalabras(respuesta);
                reiniciarAnimacion(respuesta);
            });
        });
    }

    /* --------------------------------------------------------------------
       Arranque
       -------------------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', function () {
        iniciarTerminal();
        iniciarArquitectura();
        iniciarRevelarTitulos();
        iniciarInclinacion();
        iniciarProgreso();
        iniciarRevelarTexto();
    });
})();
