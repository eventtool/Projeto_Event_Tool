document.addEventListener('DOMContentLoaded', function() {
    // Menu Toggle para dispositivos móveis
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Manipulação do Modal de Detalhes do Evento
    const modal = document.getElementById('evento-detalhes-modal');
    const viewButtons = document.querySelectorAll('.view-btn');
    const closeModalBtn = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.cancel-btn');
    
    // Função para abrir o modal
    function openModal() {
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Impede o scroll da página
        }
    }
    
    // Função para fechar o modal
    function closeModal() {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restaura o scroll da página
        }
    }
    
    // Adiciona eventos aos botões de visualização
    viewButtons.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                const eventName = this.closest('tr').querySelector('td:first-child').textContent;
                // Em uma aplicação real, aqui você buscaria os detalhes do evento no backend
                // e preencheria o modal com esses dados
                openModal();
            });
        }
    });
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }
    
    // Fecha o modal ao clicar fora dele
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    // Manipulação dos botões de inscrição
    const inscricaoBtns = document.querySelectorAll('.btn-primary');
    
    inscricaoBtns.forEach(btn => {
        if (btn && btn.textContent.trim() === 'Inscrever-se') {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const eventoCard = this.closest('.evento-card');
                const eventoNome = eventoCard.querySelector('h3').textContent;
                
                if (confirm(`Confirmar inscrição no evento: ${eventoNome}?`)) {
                    alert(`Inscrição realizada com sucesso no evento: ${eventoNome}`);
                    // Em uma aplicação real, você enviaria a inscrição para o backend
                    // e atualizaria a interface
                    
                    // Simulação de atualização da interface
                    this.textContent = 'Inscrito';
                    this.classList.add('btn-success');
                    this.classList.remove('btn-primary');
                    this.disabled = true;
                }
            });
        }
    });
    
    // Manipulação dos botões de cancelamento de inscrição
    const cancelButtons = document.querySelectorAll('.cancel-btn');
    
    cancelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const eventName = this.closest('tr').querySelector('td:first-child').textContent;
            
            if (confirm(`Tem certeza que deseja cancelar sua inscrição no evento: ${eventName}?`)) {
                alert(`Inscrição cancelada: ${eventName}`);
                // Em uma aplicação real, você enviaria o cancelamento para o backend
                // e atualizaria a interface (removendo a linha da tabela, por exemplo)
            }
        });
    });
    
    // Funcionalidade de busca
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', function() {
            const searchTerm = searchInput.value.trim().toLowerCase();
            
            if (searchTerm) {
                alert(`Buscando por: ${searchTerm}`);
                // Em uma aplicação real, você enviaria a busca para o backend
                // e atualizaria a interface com os resultados
            }
        });
        
        // Permite buscar ao pressionar Enter
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchBtn.click();
            }
        });
    }
    
    // Explorar eventos (botão da sidebar)
    const explorarEventosBtn = document.getElementById('explorar-eventos-btn');
    
    if (explorarEventosBtn) {
        explorarEventosBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Em uma aplicação real, redirecionaria para a página de exploração de eventos
            alert('Redirecionando para a página de exploração de eventos...');
        });
    }
});