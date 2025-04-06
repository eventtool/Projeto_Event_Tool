// Função para carregar eventos na página inicial
function carregarEventosIndex() {
    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const eventosGrid = document.querySelector('#eventos-destaque .eventos-grid');
                eventosGrid.innerHTML = '';

                data.eventos.forEach(evento => {
                    const eventoCard = document.createElement('div');
                    eventoCard.classList.add('evento-card');

                    eventoCard.innerHTML = `
                        <div class="evento-header">
                            <img src="${evento.imagem}" alt="Capa do Evento" class="evento-capa">
                            <h3>${evento.nome}</h3>
                            <span class="evento-data">${new Date(evento.data_hora).toLocaleString()}</span>
                        </div>
                        <div class="evento-content">
                            <p>${evento.descricao.substring(0, 100)}...</p>
                            <div class="evento-info">
                                <span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>
                                <span><i class="fas fa-users"></i> ${evento.inscricoes_count || 0}/${evento.capacidade}</span>
                            </div>
                        </div>
                        <div class="evento-footer">
                            <a href="/evento/${evento.id}" class="btn-detalhes">Ver Detalhes</a>
                        </div>
                    `;

                    eventosGrid.appendChild(eventoCard);
                });
            } else {
                console.error('Erro ao carregar eventos:', data.message);
            }
        })
        .catch(error => console.error('Erro ao carregar eventos:', error));
}

// Carregar eventos ao carregar a página
document.addEventListener('DOMContentLoaded', carregarEventosIndex);