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

    // Water droplet effect
    let lastX = 0;
    let lastY = 0;
    let lastTime = Date.now();

    document.addEventListener('mousemove', function(e) {
        const currentTime = Date.now();
        const timeDiff = currentTime - lastTime;

        if (timeDiff === 0) return;

        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const velocity = distance / timeDiff;

        // Create more droplets based on velocity
        const numDroplets = Math.min(Math.floor(velocity * 2), 5);

        for (let i = 0; i < numDroplets; i++) {
            createDroplet(e.clientX + (Math.random() - 0.5) * 20, e.clientY + (Math.random() - 0.5) * 20);
        }

        lastX = e.clientX;
        lastY = e.clientY;
        lastTime = currentTime;
    });

    function createDroplet(x, y) {
        const droplet = document.createElement('div');
        droplet.className = 'water-droplet';
        droplet.style.left = x + 'px';
        droplet.style.top = y + 'px';

        document.body.appendChild(droplet);

        // Remove droplet after animation
        setTimeout(() => {
            droplet.remove();
        }, 800);
    }
});
