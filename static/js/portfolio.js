/* =========================================================================
   PORTAFOLIO — COMPORTAMIENTO BASE
   Navegación, accesibilidad y analítica (GTM/GA4).
   Las animaciones y el scroll suave viven en motion.js; el minijuego en
   pipeline.js. Aquí no se duplica nada de eso.
   ========================================================================= */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    const navbarCollapse = document.querySelector('#navbarSupportedContent');
    const navLinks = document.querySelectorAll('.nav-link');

    /* --------------------------------------------------------------------
       Navegación móvil
       -------------------------------------------------------------------- */
    navLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) bsCollapse.hide();
            }
        });
    });

    window.addEventListener('resize', function () {
        if (window.innerWidth >= 992 && navbarCollapse && navbarCollapse.classList.contains('show')) {
            const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
            if (bsCollapse) bsCollapse.hide();
        }
    });

    /* --------------------------------------------------------------------
       Enlace activo según la sección visible
       -------------------------------------------------------------------- */
    function actualizarEnlaceActivo() {
        const secciones = document.querySelectorAll('section[id]');
        const navbar = document.querySelector('.navbar');
        const alturaNavbar = navbar ? navbar.offsetHeight : 0;
        let actual = '';

        secciones.forEach(function (seccion) {
            const tope = seccion.offsetTop - alturaNavbar - 80;
            if (window.pageYOffset >= tope) {
                actual = seccion.getAttribute('id');
            }
        });

        navLinks.forEach(function (link) { link.classList.remove('active'); });

        if (actual) {
            const activo = document.querySelector('.nav-link[href="#' + actual + '"]');
            if (activo) activo.classList.add('active');
        }
    }

    let temporizador;
    window.addEventListener('scroll', function () {
        if (temporizador) clearTimeout(temporizador);
        temporizador = setTimeout(actualizarEnlaceActivo, 60);
    }, { passive: true });

    actualizarEnlaceActivo();

    /* --------------------------------------------------------------------
       Analítica: clics en banners de desarrolladores
       -------------------------------------------------------------------- */
    document.querySelectorAll('.data-banner').forEach(function (el) {
        el.addEventListener('click', function () {
            const nombre = el.getAttribute('data-banner-name') || 'unknown';
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ event: 'banner_click', banner_name: nombre });
        });
    });

    /* --------------------------------------------------------------------
       Analítica: visualización de secciones (una vez por sección)
       -------------------------------------------------------------------- */
    const secciones = document.querySelectorAll('section[id]');
    if ('IntersectionObserver' in window && secciones.length) {
        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (entrada.isIntersecting) {
                    window.dataLayer = window.dataLayer || [];
                    window.dataLayer.push({
                        event: 'section_view',
                        section_name: entrada.target.id,
                        timestamp: new Date().toISOString()
                    });
                    observador.unobserve(entrada.target);
                }
            });
        }, { threshold: 0.5 });

        secciones.forEach(function (seccion) { observador.observe(seccion); });
    }

    /* --------------------------------------------------------------------
       Analítica: enlaces del portafolio
       -------------------------------------------------------------------- */
    document.querySelectorAll('.portfolio-link').forEach(function (link) {
        link.addEventListener('click', function () {
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'portfolio_link_click',
                link_text: this.textContent.trim(),
                timestamp: new Date().toISOString()
            });
        });
    });
});

/* =========================================================================
   UTILIDADES GLOBALES
   Usadas por otras plantillas (p. ej. openapp/open_detail.html).
   ========================================================================= */

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let esValido = true;

    inputs.forEach(function (input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            esValido = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return esValido;
}

function copyEmailToClipboard(email) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(email).then(function () {
            showToast('Email copiado al portapapeles', 'success');
        }).catch(function () {
            showToast('No se pudo copiar el email', 'danger');
        });
    }
}

function showToast(message, type) {
    const tipo = type === 'error' ? 'danger' : (type || 'info');
    const toast = document.createElement('div');
    toast.className = 'alert alert-' + tipo + ' position-fixed shadow-sm';
    toast.setAttribute('role', 'status');
    toast.style.cssText = [
        'top: 5rem',
        'right: 1.25rem',
        'z-index: 9999',
        'opacity: 0',
        'border-radius: 0.75rem',
        'transform: translateX(100%)',
        'transition: all 0.35s cubic-bezier(0.33, 1, 0.68, 1)'
    ].join(';');
    toast.textContent = message;

    document.body.appendChild(toast);

    requestAnimationFrame(function () {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });

    setTimeout(function () {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 350);
    }, 3000);
}
