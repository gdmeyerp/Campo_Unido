// Inicializar Swiper con efecto Parallax
var swiper = new Swiper('.hero-parallax-slider', {
    parallax: true,
    speed: 600,
    loop: true,
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
});