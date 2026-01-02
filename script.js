// Prevent browser from scrolling to hash on page load
if (window.location.hash) {
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 1);
}

document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    function activatePage(pageId, updateHash = true) {
        // Remove active class from all links and pages
        navLinks.forEach(l => l.classList.remove('active'));
        pages.forEach(p => p.classList.remove('active'));

        // Add active class to the correct link and page
        const targetLink = document.querySelector(`[data-page="${pageId}"]`);
        const targetPage = document.getElementById(pageId);

        if (targetLink && targetPage) {
            targetLink.classList.add('active');
            targetPage.classList.add('active');
        }

        // Update URL hash without scrolling
        if (updateHash) {
            history.replaceState(null, null, '#' + pageId);
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Show corresponding page
            const pageId = this.getAttribute('data-page');
            activatePage(pageId);
        });
    });

    // Handle hash navigation on page load
    function handleHashChange() {
        const hash = window.location.hash.slice(1); // Remove the #
        if (hash) {
            activatePage(hash, false);
        }
    }

    // Listen for hash changes (back/forward buttons)
    window.addEventListener('hashchange', handleHashChange);

    // Check hash on page load
    handleHashChange();

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
