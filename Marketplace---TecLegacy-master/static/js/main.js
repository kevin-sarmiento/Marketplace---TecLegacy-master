document.addEventListener('DOMContentLoaded', function() {
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicialización de elementos con efecto de animación al scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');

    if (animatedElements.length > 0) {
        function checkScroll() {
            animatedElements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;

                if (elementPosition < windowHeight - 50) {
                    element.classList.add('visible');
                }
            });
        }

        // Comprobar posición inicial
        checkScroll();

        // Comprobar al hacer scroll
        window.addEventListener('scroll', checkScroll);
    }

    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
});