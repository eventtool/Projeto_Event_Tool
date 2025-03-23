document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const authButtons = document.querySelector('.auth-buttons');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            authButtons.classList.toggle('active');
        });
    }
    
  
    const filterButtons = document.querySelectorAll('.filter-btn');
    const eventCards = document.querySelectorAll('.evento-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // Filtra os cards de eventos
            eventCards.forEach(card => {
                if (filter === 'todos') {
                    card.style.display = 'block';
                } else if (card.getAttribute('data-category') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // Animação de números na seção "Quem Somos"
    const statNumbers = document.querySelectorAll('.stat-number');
    
    // Função para animar contagem de números
    function animateNumbers() {
        statNumbers.forEach(number => {
            const target = parseInt(number.textContent);
            const duration = 2000; // 2 segundos
            const step = target / (duration / 20); // 20ms por passo
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    clearInterval(timer);
                    number.textContent = target + '+';
                } else {
                    number.textContent = Math.floor(current) + '+';
                }
            }, 20);
        });
    }
    
    // Verifica se o elemento está visível na tela
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Verifica se a seção de estatísticas está visível e inicia a animação
    function checkStats() {
        const statsSection = document.querySelector('.stats');
        if (statsSection && isElementInViewport(statsSection)) {
            animateNumbers();
            window.removeEventListener('scroll', checkStats);
        }
    }
    
    // Adiciona evento de scroll para verificar quando a seção de estatísticas fica visível
    window.addEventListener('scroll', checkStats);
    
    // Verifica uma vez quando a página carrega
    checkStats();
    
    // Smooth scroll para links de navegação
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, 
                    behavior: 'smooth'
                });
            
                if (navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    authButtons.classList.remove('active');
                }
            }
        });
    });
    eventCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.querySelector('.evento-image img').style.transform = 'scale(1.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.querySelector('.evento-image img').style.transform = 'scale(1)';
        });
    });
});