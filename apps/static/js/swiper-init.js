/**
 * Inicializa galerías de Swiper en toda la aplicación
 */
document.addEventListener('DOMContentLoaded', function() {
    // Comprueba si hay galerías de Swiper en la página
    if (document.querySelector('.thumbs-swiper') && document.querySelector('.main-swiper')) {
        // Inicializar Swiper de miniaturas
        const thumbsSwiper = new Swiper('.thumbs-swiper', {
            spaceBetween: 10,
            slidesPerView: 'auto',
            freeMode: true,
            watchSlidesProgress: true,
            centerInsufficientSlides: true,
            navigation: {
                nextEl: '.thumbs-button-next',
                prevEl: '.thumbs-button-prev',
            },
        });
        
        // Inicializar Swiper principal
        const mainSwiper = new Swiper('.main-swiper', {
            spaceBetween: 10,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
                dynamicBullets: true,
            },
            keyboard: {
                enabled: true,
            },
            thumbs: {
                swiper: thumbsSwiper,
            },
            zoom: {
                maxRatio: 2,
                toggle: true,
            },
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
                pauseOnMouseEnter: true
            },
            // Detener autoplay cuando haya interacción del usuario
            on: {
                click: function() {
                    this.autoplay.stop();
                }
            }
        });
    }
    
    // Para galerías simples sin miniaturas
    const singleSwipers = document.querySelectorAll('.single-swiper');
    if (singleSwipers.length > 0) {
        singleSwipers.forEach((swiperElement, index) => {
            new Swiper(swiperElement, {
                spaceBetween: 30,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                autoplay: {
                    delay: 5000,
                    disableOnInteraction: false,
                },
            });
        });
    }
}); 