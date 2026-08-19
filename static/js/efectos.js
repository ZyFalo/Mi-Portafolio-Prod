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
       2. Panel de estado en vivo
       -------------------------------------------------------------------- */
    function iniciarEstado() {
        const panel = document.getElementById('status-panel');
        if (!panel) return;

        const relojUptime = document.getElementById('status-uptime');
        const arranque = parseFloat(panel.dataset.arranque || '0');

        // El uptime avanza en pantalla sin volver a pedir nada al servidor
        if (relojUptime && arranque) {
            setInterval(function () {
                const seg = Math.floor(Date.now() / 1000 - arranque);
                relojUptime.textContent = formatearUptime(seg);
            }, 1000);
        }

        // Refresco discreto del resto de métricas
        const url = panel.dataset.url;
        if (!url) return;

        setInterval(async function () {
            if (document.hidden) return;
            try {
                const respuesta = await fetch(url, { headers: { Accept: 'application/json' } });
                if (!respuesta.ok) return;
                const datos = await respuesta.json();
                const contador = document.getElementById('status-deploys');
                if (contador) contador.textContent = datos.deploys_visitantes;
            } catch (e) { /* sin conexión: el panel conserva el último valor */ }
        }, 60000);
    }

    function formatearUptime(segundos) {
        if (segundos < 0) segundos = 0;
        const d = Math.floor(segundos / 86400);
        const h = Math.floor((segundos % 86400) / 3600);
        const m = Math.floor((segundos % 3600) / 60);
        const s = segundos % 60;
        if (d) return d + 'd ' + h + 'h ' + m + 'm';
        if (h) return h + 'h ' + m + 'm ' + s + 's';
        if (m) return m + 'm ' + s + 's';
        return s + 's';
    }

    /* --------------------------------------------------------------------
       3. Diagrama de arquitectura que se traza solo
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

        // Preparar cada trazo con su propia longitud
        trazos.forEach(function (trazo) {
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
                    setTimeout(function () { trazo.style.strokeDashoffset = '0'; }, 240 + i * 170);
                });

                observador.disconnect();
            });
        }, { threshold: 0.35 });

        observador.observe(svg);
    }

    /* --------------------------------------------------------------------
       4. Títulos que se descifran
       -------------------------------------------------------------------- */
    const ALFABETO = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&/*<>{}[]';

    function descifrar(elemento) {
        const original = elemento.dataset.textoOriginal || elemento.textContent;
        elemento.dataset.textoOriginal = original;

        let cuadro = 0;
        const total = original.length;

        const temporizador = setInterval(function () {
            const avance = cuadro / 3;
            let salida = '';

            for (let i = 0; i < total; i++) {
                const c = original[i];
                if (c === ' ' || i < avance) {
                    salida += c;
                } else {
                    salida += ALFABETO[Math.floor(Math.random() * ALFABETO.length)];
                }
            }

            elemento.textContent = salida;
            cuadro++;

            if (avance >= total) {
                clearInterval(temporizador);
                elemento.textContent = original;
            }
        }, 34);
    }

    function iniciarDescifrado() {
        const objetivos = document.querySelectorAll('[data-descifrar]');
        if (!objetivos.length || quieto || !('IntersectionObserver' in window)) return;

        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (!entrada.isIntersecting) return;
                descifrar(entrada.target);
                observador.unobserve(entrada.target);
            });
        }, { threshold: 0.8 });

        objetivos.forEach(function (o) { observador.observe(o); });
    }

    /* --------------------------------------------------------------------
       5. Inclinación 3D en tarjetas
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
       6. Barra de progreso de lectura
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
       7. Revelado del texto en el FAQ
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
        iniciarEstado();
        iniciarArquitectura();
        iniciarDescifrado();
        iniciarInclinacion();
        iniciarProgreso();
        iniciarRevelarTexto();
    });
})();
