// Funcionalidad del Portafolio
document.addEventListener('DOMContentLoaded', function() {
    
    // Obtener elementos del DOM
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('#navbarSupportedContent');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Funcionalidad del botón hamburguesa
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            // Bootstrap maneja la clase 'show' automáticamente
            // Cambiar el icono del botón hamburguesa (opcional)
            const isExpanded = navbarToggler.getAttribute('aria-expanded') === 'true';
            
            // Agregar clase para animación personalizada
            if (isExpanded) {
                navbarToggler.classList.add('collapsed');
            } else {
                navbarToggler.classList.remove('collapsed');
            }
        });
    }
    
    // Cerrar menú al hacer click en un enlace (móvil)
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Solo cerrar en dispositivos móviles
            if (window.innerWidth < 992) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    hide: true
                });
            }
        });
    });
    
    // Scroll suave para enlaces de navegación
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Solo para enlaces internos
            if (href.startsWith('#')) {
                e.preventDefault();
                
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    // Calcular offset para navbar fijo
                    const navbarHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Resaltar enlace activo en navbar según scroll
    function updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        
        let current = '';
        
        sections.forEach(function(section) {
            const sectionTop = section.getBoundingClientRect().top;
            const sectionHeight = section.offsetHeight;
            
            if (sectionTop <= navbarHeight + 100 && sectionTop + sectionHeight > navbarHeight + 100) {
                current = section.getAttribute('id');
            }
        });
        
        // Remover clase activa de todos los enlaces
        navLinks.forEach(function(link) {
            link.classList.remove('active');
        });
        
        // Agregar clase activa al enlace correspondiente
        if (current) {
            const activeLink = document.querySelector(`.nav-link[href="#${current}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
    }
    
    // Escuchar evento scroll para navegación activa
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        // Throttle scroll events para mejor rendimiento
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(updateActiveNavLink, 10);
    });
    
    // Inicializar navegación activa
    updateActiveNavLink();
    
    // Animaciones de entrada para tarjetas
    function animateCardsOnScroll() {
        const cards = document.querySelectorAll('.card-custom');
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        cards.forEach(function(card) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }
    
    // Inicializar animaciones
    animateCardsOnScroll();
    
    // Mejorar experiencia con tooltips (opcional)
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Inicializar tooltips si existen
    initializeTooltips();
    
    // Manejo de resize de ventana
    window.addEventListener('resize', function() {
        // Cerrar menú si se cambia a desktop
        if (window.innerWidth >= 992 && navbarCollapse.classList.contains('show')) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                hide: true
            });
        }
    });
    
    // Loading state para imágenes
    function handleImageLoading() {
        const images = document.querySelectorAll('img');
        
        images.forEach(function(img) {
            if (img.complete) {
                img.style.opacity = '1';
            } else {
                img.addEventListener('load', function() {
                    this.style.opacity = '1';
                });
                
                img.addEventListener('error', function() {
                    // Fallback para imágenes que no cargan
                    this.style.opacity = '0.5';
                    console.warn('Error loading image:', this.src);
                });
            }
        });
    }
    
    // Inicializar carga de imágenes
    handleImageLoading();
    
    // Función para smooth scroll al inicio
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    // Botón back to top
    function createBackToTopButton() {
        const backToTopBtn = document.createElement('button');
        backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        backToTopBtn.className = 'btn btn-primary position-fixed rounded-circle d-flex align-items-center justify-content-center';
        backToTopBtn.style.cssText = `
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        `;
        
        backToTopBtn.addEventListener('click', scrollToTop);
        
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.opacity = '1';
                backToTopBtn.style.visibility = 'visible';
            } else {
                backToTopBtn.style.opacity = '0';
                backToTopBtn.style.visibility = 'hidden';
            }
        });
        
        document.body.appendChild(backToTopBtn);
    }
    
    // Crear botón back to top
    createBackToTopButton();

    // Banner click tracking para GTM
    document.querySelectorAll('.data-banner').forEach(el => {
        el.addEventListener('click', () => {
            const name = el.getAttribute('data-banner-name') || 'unknown';
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ event: 'banner_click', banner_name: name });
            console.log('GTM Event sent:', { event: 'banner_click', banner_name: name });
        });
    });

    // Eventos personalizados para tracking de secciones
    const sections = document.querySelectorAll('section[id]');
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push({ 
                    event: 'section_view', 
                    section_name: sectionId,
                    timestamp: new Date().toISOString()
                });
            }
        });
    }, { threshold: 0.5 });

    sections.forEach(section => {
        sectionObserver.observe(section);
    });
});

// Función para validar formularios (si se añaden en el futuro)
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Función para copiar email al clipboard
function copyEmailToClipboard(email) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(email).then(function() {
            // Mostrar feedback visual
            showToast('Email copiado al portapapeles', 'success');
        }).catch(function(err) {
            console.error('Error al copiar email: ', err);
        });
    }
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'info') {
    // Crear elemento toast
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Mostrar toast
    setTimeout(function() {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Ocultar toast después de 3 segundos
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Portfolio-specific enhancements
function enhancePortfolioLinks() {
    const portfolioLinks = document.querySelectorAll('.portfolio-link');
    
    portfolioLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const linkText = this.textContent;
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'portfolio_link_click',
                link_text: linkText,
                timestamp: new Date().toISOString()
            });
        });
    });
}

// Llamar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', enhancePortfolioLinks);
