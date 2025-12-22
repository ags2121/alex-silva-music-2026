document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove active class from all links and pages
            navLinks.forEach(l => l.classList.remove('active'));
            pages.forEach(p => p.classList.remove('active'));

            // Add active class to clicked link
            this.classList.add('active');

            // Show corresponding page
            const pageId = this.getAttribute('data-page');
            document.getElementById(pageId).classList.add('active');
        });
    });

    // Letter trail effect
    const text = "AlexSilvaMusic";
    let letterIndex = 0;
    let lastX = 0;
    let lastY = 0;
    const minDistance = 30; // Minimum distance in pixels before creating a new letter

    document.addEventListener('mousemove', function(e) {
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance >= minDistance) {
            createLetter(e.clientX, e.clientY);
            lastX = e.clientX;
            lastY = e.clientY;
        }
    });

    function createLetter(x, y) {
        const letter = document.createElement('div');
        letter.className = 'trail-letter';
        letter.textContent = text[letterIndex];
        letter.style.left = x + 'px';
        letter.style.top = y + 'px';

        document.body.appendChild(letter);

        // Cycle through letters
        letterIndex = (letterIndex + 1) % text.length;

        // Remove letter after animation
        setTimeout(() => {
            letter.remove();
        }, 600);
    }
});
