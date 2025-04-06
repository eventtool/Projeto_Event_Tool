document.addEventListener('DOMContentLoaded', function() {
    carregarEventos();
});

function carregarEventos() {
    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const eventosGrid = document.querySelector('.eventos-grid');
                if (!eventosGrid) return;
                
                eventosGrid.innerHTML = ''; // Limpa o conteúdo atual
                
                data.eventos.forEach(evento => {
                    renderizarEvento(evento, eventosGrid);
                });
            } else {
                console.error('Erro ao carregar eventos:', data.message);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar eventos:', error);
        });
}

function renderizarEvento(evento, container) {
    const card = document.createElement('div');
    card.className = 'evento-card';
    card.innerHTML = `
        <div class="evento-header">
            <h3>${evento.nome}</h3>
            <span>${new Date(evento.data_hora).toLocaleDateString('pt-BR')}</span>
        </div>
        <div class="evento-content">
            <p>${evento.descricao || 'Sem descrição'}</p>
            <div class="evento-info">
                <span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>
                <span><i class="fas fa-users"></i> ${evento.inscricoes_count}/${evento.capacidade}</span>
            </div>
            <button 
                ${evento.inscrito ? 'disabled' : `onclick="inscreverEvento(${evento.id})"`}
                class="btn ${evento.inscrito ? 'btn-secondary' : 'btn-primary'}">
                ${evento.inscrito ? 'Inscrito' : 'Inscrever-se'}
            </button>
        </div>
    `;
    container.appendChild(card);
}

function getBotaoEvento(evento) {
    if (evento.status === 'finalizado') {
        return `<button onclick="gerarCertificado(${evento.id})" class="btn btn-primary">
                    <i class="fas fa-certificate"></i> Gerar Certificado
                </button>`;
    }
    
    if (evento.inscrito) {
        return `<button class="btn btn-secondary" disabled>
                    <i class="fas fa-check"></i> Inscrito
                </button>`;
    }
    
    if (evento.inscricoes_count >= evento.capacidade) {
        return `<button class="btn btn-secondary" disabled>
                    <i class="fas fa-times"></i> Lotado
                </button>`;
    }
    
    return `<button onclick="inscreverEvento(${evento.id})" class="btn btn-primary">
                <i class="fas fa-ticket-alt"></i> Inscrever-se
            </button>`;
}

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
            
            // Baixar o ingresso automaticamente
            if (data.ingresso_url) {
                window.location.href = data.ingresso_url;
            }
            
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
// Função para renderizar eventos na página
function renderizarEvento(evento, container) {
    const card = document.createElement('div');
    card.className = 'evento-card';
    card.innerHTML = `
        <div class="evento-header">
            <h3>${evento.nome}</h3>
            <span>${new Date(evento.data_hora).toLocaleDateString('pt-BR')}</span>
        </div>
        <div class="evento-content">
            <p>${evento.descricao || 'Sem descrição'}</p>
            <div class="evento-info">
                <span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>
                <span><i class="fas fa-users"></i> ${evento.inscricoes_count}/${evento.capacidade}</span>
            </div>
            ${evento.status === 'finalizado' 
                ? `<button onclick="gerarCertificado(${evento.id})" class="btn btn-primary">
                    <i class="fas fa-certificate"></i> Gerar Certificado
                   </button>`
                : evento.inscrito 
                    ? `<button class="btn btn-secondary" disabled>
                        <i class="fas fa-check"></i> Inscrito
                       </button>`
                    : `<button onclick="inscreverEvento(${evento.id})" class="btn btn-primary" 
                        ${evento.inscricoes_count >= evento.capacidade ? 'disabled' : ''}>
                        <i class="fas fa-ticket-alt"></i> 
                        ${evento.inscricoes_count >= evento.capacidade ? 'Lotado' : 'Inscrever-se'}
                       </button>`
            }
        </div>
    `;
    container.appendChild(card);
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
            
            // Baixar o ingresso automaticamente
            if (data.ingresso_url) {
                window.location.href = data.ingresso_url;
            }
            
            // Recarregar os eventos para atualizar o status
            carregarProximosEventos();
            carregarEventosEncerrados();
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
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json().then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert(data.message);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao cancelar inscrição');
        });
    }
}

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

// Função para carregar eventos encerrados
function carregarEventosEncerrados() {
    console.log('Carregando eventos encerrados...');
    const encerradosContainer = document.getElementById('encerrados');
    if (!encerradosContainer) {
        console.error('Container de eventos encerrados não encontrado');
        return;
    }

    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => {
            console.log('Dados recebidos:', data);
            if (data.success) {
                encerradosContainer.innerHTML = '';
                const eventosEncerrados = data.eventos.filter(evento => evento.status === 'finalizado');
                
                if (eventosEncerrados.length === 0) {
                    encerradosContainer.innerHTML = '<p>Nenhum evento encerrado.</p>';
                    return;
                }

                eventosEncerrados.forEach(evento => {
                    const card = document.createElement('div');
                    card.className = 'evento-card';
                    card.innerHTML = `
                        <div class="evento-header">
                            <h3>${evento.nome}</h3>
                            <span>${new Date(evento.data_hora).toLocaleDateString('pt-BR')}</span>
                        </div>
                        <div class="evento-content">
                            <p>${evento.descricao || 'Sem descrição'}</p>
                            <div class="evento-info">
                                <span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>
                                <span><i class="fas fa-users"></i> ${evento.inscricoes_count}/${evento.capacidade}</span>
                            </div>
                            <button onclick="gerarCertificado(${evento.id})" class="btn btn-primary">
                                <i class="fas fa-certificate"></i> Gerar Certificado
                            </button>
                        </div>
                    `;
                    encerradosContainer.appendChild(card);
                });
            }
        })
        .catch(error => console.error('Erro:', error));
}

// Função para carregar próximos eventos
function carregarProximosEventos() {
    console.log('Carregando próximos eventos...');
    const proximosContainer = document.getElementById('proximos');
    if (!proximosContainer) {
        console.error('Container de próximos eventos não encontrado');
        return;
    }

    fetch('/api/eventos')
        .then(response => response.json())
        .then(data => {
            console.log('Dados recebidos:', data);
            if (data.success) {
                proximosContainer.innerHTML = '';
                // Filtra apenas eventos ativos (não finalizados)
                const proximosEventos = data.eventos.filter(evento => evento.status === 'ativo');
                
                if (proximosEventos.length === 0) {
                    proximosContainer.innerHTML = '<p>Nenhum evento disponível.</p>';
                    return;
                }

                proximosEventos.forEach(evento => {
                    const card = document.createElement('div');
                    card.className = 'evento-card';
                    card.innerHTML = `
                        <div class="evento-header">
                            <h3>${evento.nome}</h3>
                            <span>${new Date(evento.data_hora).toLocaleDateString('pt-BR')}</span>
                        </div>
                        <div class="evento-content">
                            <p>${evento.descricao || 'Sem descrição'}</p>
                            <div class="evento-info">
                                <span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>
                                <span><i class="fas fa-users"></i> ${evento.inscricoes_count}/${evento.capacidade}</span>
                            </div>
                            ${evento.inscrito 
                                ? `<button class="btn btn-secondary" disabled>
                                    <i class="fas fa-check"></i> Inscrito
                                   </button>`
                                : `<button onclick="inscreverEvento(${evento.id})" class="btn btn-primary">
                                    <i class="fas fa-ticket-alt"></i> Inscrever-se
                                   </button>`
                            }
                        </div>
                    `;
                    proximosContainer.appendChild(card);
                });
            }
        })
        .catch(error => console.error('Erro:', error));
}

// Função para alterar entre as abas
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

    // Carrega os eventos apropriados
    if (abaId === 'encerrados') {
        carregarEventosEncerrados();
    } else {
        carregarProximosEventos();
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    carregarEventosEncerrados();
    carregarProximosEventos();
});
