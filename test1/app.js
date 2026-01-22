// Scroll Reveal
const revealElements = document.querySelectorAll('.reveal');

const scrollReveal = () => {
    revealElements.forEach(el => {
        const elementTop = el.getBoundingClientRect().top;
        if (elementTop < window.innerHeight - 150) {
            el.classList.add('active');
        }
    });
};

window.addEventListener('scroll', scrollReveal);
window.addEventListener('load', scrollReveal);

// Animation Logic
const analyzeBtn = document.getElementById('analyzeBtn');
const loader = document.getElementById('loader');
const btnText = document.getElementById('btnText');
const scanner = document.getElementById('visualScanner');
const bars = [
    document.getElementById('bar1'),
    document.getElementById('bar2'),
    document.getElementById('bar3')
];

if (analyzeBtn) {
    analyzeBtn.addEventListener('click', () => {
        btnText.textContent = 'Processing...';
        loader.classList.remove('hidden');
        if (scanner) scanner.classList.remove('hidden');

        setTimeout(() => {
            bars.forEach((bar, index) => {
                if (bar) {
                    setTimeout(() => {
                        bar.style.width = '100%';
                        bar.classList.remove('bg-slate-800');
                        bar.classList.add('bg-cyan-500');
                    }, index * 200);
                }
            });
        }, 500);

        setTimeout(() => {
            btnText.textContent = 'Optimized!';
            loader.classList.add('hidden');
            if (scanner) scanner.classList.add('hidden');
        }, 3500);
    });
}
