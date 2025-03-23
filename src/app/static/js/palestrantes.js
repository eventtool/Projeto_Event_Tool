document.addEventListener('DOMContentLoaded', function() {
    // Menu Toggle para dispositivos móveis
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Inicialização do Flatpickr para campos de data e hora
    if (typeof flatpickr !== 'undefined') {
        // Configuração para o campo de data
        flatpickr("#evento-data", {
            dateFormat: "d/m/Y",
            minDate: "today",
            locale: {
                firstDayOfWeek: 1,
                weekdays: {
                    shorthand: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
                    longhand: ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
                },
                months: {
                    shorthand: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                    longhand: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                }
            }
        });
        
        // Configuração para o campo de hora
        flatpickr("#evento-hora", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true
        });
    }
    
    // Manipulação do Modal de Criação de Evento
    const modal = document.getElementById('criar-evento-modal');
    const openModalBtns = [
        document.getElementById('criar-evento-btn'),
        document.getElementById('criar-evento-header-btn')
    ];
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
    
    // Adiciona eventos aos botões
    openModalBtns.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', openModal);
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
    
    // Manipulação do upload de imagem
    const fileInput = document.getElementById('evento-imagem');
    const fileLabel = document.querySelector('.file-name');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Nenhum arquivo selecionado';
            }
        });
    }
    
    // Manipulação do formulário de criação de evento
    const criarEventoForm = document.getElementById('criar-evento-form');
    
    if (criarEventoForm) {
        criarEventoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Coleta os dados do formulário
            const nome = document.getElementById('evento-nome').value;
            const data = document.getElementById('evento-data').value;
            const hora = document.getElementById('evento-hora').value;
            const local = document.getElementById('evento-local').value;
            const vagas = document.getElementById('evento-vagas').value;
            const categoria = document.getElementById('evento-categoria').value;
            const descricao = document.getElementById('evento-descricao').value;
            
            // Validação básica
            if (!nome || !data || !hora || !local || !vagas || !categoria || !descricao) {
                alert('Por favor, preencha todos os campos obrigatórios.');
                return;
            }
            
            // Simulação de criação de evento bem-sucedida
            console.log('Evento criado:', {
                nome,
                data,
                hora,
                local,
                vagas,
                categoria,
                descricao
            });
            
            // Exibe mensagem de sucesso
            alert('Evento criado com sucesso!');
            
            // Fecha o modal
            closeModal();
            
            // Em uma aplicação real, aqui você faria uma requisição para o backend
            // e atualizaria a interface com o novo evento
        });
    }
    
    // Manipulação dos botões de ação da tabela
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.classList.contains('edit-btn') ? 'editar' :
                          this.classList.contains('view-btn') ? 'visualizar' :
                          this.classList.contains('delete-btn') ? 'excluir' : '';
            
            const eventName = this.closest('tr').querySelector('td:first-child').textContent;
            
            if (action === 'editar') {
                alert(`Editar evento: ${eventName}`);
                // Em uma aplicação real, abriria o modal de edição com os dados preenchidos
            } else if (action === 'visualizar') {
                alert(`Visualizar evento: ${eventName}`);
                // Em uma aplicação real, abriria o modal de detalhes do evento
            } else if (action === 'excluir') {
                if (confirm(`Tem certeza que deseja excluir o evento: ${eventName}?`)) {
                    alert(`Evento excluído: ${eventName}`);
                    // Em uma aplicação real, removeria o evento do backend e da interface
                }
            }
        });
    });
    // Adicione isso ao final do arquivo palestrante-dashboard.js
// Links para as novas páginas
const explorarEventosLink = document.querySelector('a[href="explorar-eventos.html"]');
const certificadosLink = document.querySelector('a[href="certificados.html"]');
const perfilLink = document.querySelector('a[href="perfil.html"]');

if (explorarEventosLink) {
    explorarEventosLink.addEventListener('click', function(e) {
        // Se quiser adicionar alguma lógica antes de navegar
        console.log('Navegando para Explorar Eventos');
    });
}

if (certificadosLink) {
    certificadosLink.addEventListener('click', function(e) {
        // Se quiser adicionar alguma lógica antes de navegar
        console.log('Navegando para Certificados');
    });
}

if (perfilLink) {
    perfilLink.addEventListener('click', function(e) {
        // Se quiser adicionar alguma lógica antes de navegar
        console.log('Navegando para Perfil');
    });
}
});