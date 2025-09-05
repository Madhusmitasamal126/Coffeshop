let slideIndex = 0;
const slides = document.querySelectorAll('.slide');

function showSlides() {
    if(slides.length === 0) return;
    slides.forEach(s => s.style.display = "none");
    slideIndex++;
    if(slideIndex > slides.length) slideIndex = 1;
    slides[slideIndex - 1].style.display = "block";
    setTimeout(showSlides, 3000);
}

document.addEventListener('DOMContentLoaded', showSlides);
