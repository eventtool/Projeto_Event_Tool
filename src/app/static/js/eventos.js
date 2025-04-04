// Função para carregar eventos
function carregarEventos() {
    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderizarEventos(data.eventos);
            } else {
                console.error('Erro ao carregar eventos:', data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
        });
}

// Função para renderizar eventos na página
function renderizarEventos(eventos) {
    const eventosGrid = document.querySelector('.eventos-grid');
    if (!eventosGrid) return;

    eventosGrid.innerHTML = '';

    eventos.forEach(evento => {
        const eventoCard = document.createElement('div');
        eventoCard.className = 'evento-card';
        
        const dataEvento = new Date(evento.data_hora);
        const dataFormatada = dataEvento.toLocaleDateString('pt-BR') + ' ' + 
                            dataEvento.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

        eventoCard.innerHTML = `
            <div class="evento-header">
                <h3>${evento.nome}</h3>
                <span class="evento-data">${dataFormatada}</span>
            </div>
            <div class="evento-content">
                <p>${evento.descricao.substring(0, 150)}...</p>
                <div class="evento-info">
                    <span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>
                    <span><i class="fas fa-users"></i> ${evento.inscricoes_count}/${evento.capacidade} vagas</span>
                </div>
            </div>
            <div class="evento-footer">
                ${evento.inscrito ? 
                    `<button class="btn-inscrito" disabled>
                        <i class="fas fa-check"></i> Inscrito
                    </button>` :
                    `<button class="btn-inscrever" onclick="inscreverEvento(${evento.id})">
                        <i class="fas fa-ticket-alt"></i> Inscrever-se
                    </button>`
                }
            </div>
        `;
        
        eventosGrid.appendChild(eventoCard);
    });
}

// Função para inscrever em um evento
function inscreverEvento(eventoId) {
    fetch(`/evento/${eventoId}/inscrever`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            carregarEventos(); // Recarrega os eventos para atualizar o status
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao realizar inscrição');
    });
}

// Função para filtrar eventos
function filtrarEventos(termo) {
    const cards = document.querySelectorAll('.evento-card');
    
    cards.forEach(card => {
        const titulo = card.querySelector('h3').textContent.toLowerCase();
        const descricao = card.querySelector('.evento-content p').textContent.toLowerCase();
        const termoBusca = termo.toLowerCase();
        
        if (titulo.includes(termoBusca) || descricao.includes(termoBusca)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

// Função para cancelar inscrição
function cancelarInscricao(eventoId) {
    if (confirm('Tem certeza que deseja cancelar sua inscrição neste evento?')) {
        fetch(`/evento/${eventoId}/cancelar-inscricao`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao cancelar inscrição');
        });
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarEventos();
    
    // Configurar busca
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filtrarEventos(e.target.value);
        });
    }
});

// Função para encerrar evento
function encerrarEvento(eventoId) {
    if (confirm('Tem certeza que deseja encerrar este evento? Isso irá gerar certificados para os participantes.')) {
        fetch(`/evento/${eventoId}/finalizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao encerrar evento');
        });
    }
}

// Função para mostrar/esconder abas
function mostrarAba(abaId) {
    // Esconde todas as abas
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove a classe active de todos os botões
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Mostra a aba selecionada
    document.getElementById(abaId).classList.add('active');
    
    // Ativa o botão da aba selecionada
    document.querySelector(`[onclick="mostrarAba('${abaId}')"]`).classList.add('active');
}
