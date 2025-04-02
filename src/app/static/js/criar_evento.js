document.addEventListener('DOMContentLoaded', function() {
    // Variáveis para controlar a navegação
    const etapas = document.querySelectorAll('.form-etapa');
    const progressoEtapas = document.querySelectorAll('.progresso-etapa');
    const btnNext = document.querySelectorAll('.btn-next');
    const btnPrev = document.querySelectorAll('.btn-prev');
    let etapaAtual = 0;
    
    // Função para mostrar uma etapa específica
    function mostrarEtapa(n) {
        // Esconde todas as etapas
        etapas.forEach(etapa => {
            etapa.classList.remove('active');
        });
        
        // Atualiza o progresso
        progressoEtapas.forEach((etapa, index) => {
            if (index <= n) {
                etapa.classList.add('active');
            } else {
                etapa.classList.remove('active');
            }
        });
        
        // Mostra a etapa atual
        etapas[n].classList.add('active');
        etapaAtual = n;

        if (etapaAtual === 4) {
            atualizarResumo();
        }

        // Atualiza os botões de navegação
        if (etapaAtual === 0) {
            document.querySelector('.btn-prev').setAttribute('disabled', true);
        } else {
            document.querySelector('.btn-prev').removeAttribute('disabled');
        }

    }
    
    // Adiciona eventos aos botões de próximo
    btnNext.forEach(btn => {
        btn.addEventListener('click', function() {
            if (validarEtapaAtual()) {
                // Se estiver indo para a última etapa
                if (etapaAtual === 3) {
                    try {
                        atualizarResumo();
                    } catch (error) {
                        console.error("Erro ao atualizar resumo:", error);
                    }
                }
                mostrarEtapa(etapaAtual + 1);
                window.scrollTo(0, 0);
            }
        });
    });
    
    // Adiciona eventos aos botões de anterior
    btnPrev.forEach(btn => {
        btn.addEventListener('click', function() {
            mostrarEtapa(etapaAtual - 1);
            window.scrollTo(0, 0);
        });
    });

    document.getElementById('nome-evento').addEventListener('change', function() {
        if (etapaAtual === 4) { // Se estiver na etapa de revisão
            atualizarResumo();
        }
    });

    document.getElementById('data-inicio').addEventListener('change', function() {
        if (etapaAtual === 4) atualizarResumo();
    });

    document.getElementById('hora-inicio').addEventListener('change', function() {
        if (etapaAtual === 4) atualizarResumo();
    });

    document.getElementById('tipo-evento').addEventListener('change', function() {
        // Código existente para mostrar/esconder campos
        
        // Adicione esta linha no final do evento
        if (etapaAtual === 4) atualizarResumo();
    });
    
    
    // Adiciona eventos aos links de edição na revisão
    document.querySelectorAll('.edit-section').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const step = parseInt(this.getAttribute('data-step')) - 1;
            mostrarEtapa(step);
        });
    });
    
    // Função para validar a etapa atual
    function validarEtapaAtual() {
        // Implementar validação específica para cada etapa
        // Por enquanto, retorna true para todas as etapas
        return true;
    }
        // Implementar preview de imagem
        const imageInput = document.getElementById('imagem-evento');
        const imagePreview = document.getElementById('image-preview');
        
        if (imageInput && imagePreview) {
            imageInput.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imagePreview.querySelector('img').src = e.target.result;
                        imagePreview.classList.add('has-image');
                    }
                    reader.readAsDataURL(file);
                }
            });
        }

            // Adicionar palestrantes
    const addPalestranteBtn = document.getElementById('add-palestrante-btn');
    const palestrantesContainer = document.getElementById('palestrantes-container');
    let palestranteCount = document.querySelectorAll('.palestrante-item').length;
    
    const botoesRemover = document.querySelectorAll('.remove-palestrante');
    if (botoesRemover.length > 0) {
        botoesRemover.forEach(btn => {
            btn.addEventListener('click', function() {
                const palestranteItem = this.closest('.palestrante-item');
                palestrantesContainer.removeChild(palestranteItem);
                if (etapaAtual === 4) atualizarResumo();
            });
        });
    }

    if (addPalestranteBtn && palestrantesContainer) {
        addPalestranteBtn.addEventListener('click', function() {
            palestranteCount++;
            const novoPalestrante = document.createElement('div');
            novoPalestrante.className = 'palestrante-item';
            novoPalestrante.innerHTML = `
                <div class="palestrante-avatar">
                    <img src="/static/img/placeholder.svg?height=60&width=60" alt="Avatar do Palestrante">
                </div>
                <div class="palestrante-info">
                    <input type="text" name="palestrante-nome-${palestranteCount}" placeholder="Nome do palestrante" required>
                    <input type="text" name="palestrante-cargo-${palestranteCount}" placeholder="Cargo ou especialidade">
                </div>
                <div class="palestrante-actions">
                    <button type="button" class="edit-palestrante"><i class="fas fa-edit"></i></button>
                    <button type="button" class="remove-palestrante remove"><i class="fas fa-trash"></i></button>
                </div>
            `;
            palestrantesContainer.appendChild(novoPalestrante);

            if (etapaAtual === 4) atualizarResumo();

            // Adicionar evento para remover palestrante
            novoPalestrante.querySelector('.remove-palestrante').addEventListener('click', function() {
                palestrantesContainer.removeChild(novoPalestrante);

                if (etapaAtual === 4) atualizarResumo();
            });
            
        });
        
    }

        // Adicionar ingressos
        const addIngressoBtn = document.getElementById('add-ingresso-btn');
        const ingressosContainer = document.getElementById('ingressos-container');
        let ingressoCount = 1;
        
        if (addIngressoBtn && ingressosContainer) {
            addIngressoBtn.addEventListener('click', function() {
                ingressoCount++;
                const novoIngresso = document.createElement('div');
                novoIngresso.className = 'ingresso-item';
                novoIngresso.innerHTML = `
                    <div class="ingresso-header">
                        <h3>Novo Ingresso</h3>
                        <button type="button" class="remove-ingresso"><i class="fas fa-times"></i></button>
                    </div>
                    
                    <div class="form-group">
                        <label for="nome-ingresso-${ingressoCount}" class="required">Nome do Ingresso</label>
                        <input type="text" id="nome-ingresso-${ingressoCount}" name="nome-ingresso-${ingressoCount}" placeholder="Ex: VIP, Estudante, etc." required>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="preco-ingresso-${ingressoCount}" class="required">Preço (R$)</label>
                            <input type="number" id="preco-ingresso-${ingressoCount}" name="preco-ingresso-${ingressoCount}" min="0" step="0.01" value="0.00" required>
                            <p class="form-help">Digite 0 para ingressos gratuitos.</p>
                        </div>
                        <div class="form-group">
                            <label for="quantidade-ingresso-${ingressoCount}" class="required">Quantidade Disponível</label>
                            <input type="number" id="quantidade-ingresso-${ingressoCount}" name="quantidade-ingresso-${ingressoCount}" min="1" value="100" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="descricao-ingresso-${ingressoCount}">Descrição</label>
                        <textarea id="descricao-ingresso-${ingressoCount}" name="descricao-ingresso-${ingressoCount}" placeholder="Descreva o que está incluso neste ingresso..."></textarea>
                    </div>
                `;
                ingressosContainer.appendChild(novoIngresso);

                if (etapaAtual === 4) atualizarResumo();
                
                // Adicionar evento para remover ingresso
                novoIngresso.querySelector('.remove-ingresso').addEventListener('click', function() {
                    ingressosContainer.removeChild(novoIngresso);

                    if (etapaAtual === 4) atualizarResumo();
                });
            });
            
            // Adicionar evento para remover ingresso existente
            document.querySelectorAll('.remove-ingresso').forEach(btn => {
                btn.addEventListener('click', function() {
                    const ingressoItem = this.closest('.ingresso-item');
                    ingressosContainer.removeChild(ingressoItem);

                    if (etapaAtual === 4) atualizarResumo();
                });
            });

            document.querySelector('input[name="emitir-certificados"]').addEventListener('change', function() {
                if (etapaAtual === 4) atualizarResumo();
            });
            
            document.querySelector('input[name="lista-espera"]').addEventListener('change', function() {
                if (etapaAtual === 4) atualizarResumo();
            });
            
            document.querySelector('input[name="evento-privado"]').addEventListener('change', function() {
                if (etapaAtual === 4) atualizarResumo();
            });
        }

        const tipoEventoSelect = document.getElementById('tipo-evento');
        const localPresencial = document.getElementById('local-presencial');
        const localOnline = document.getElementById('local-online');
        
        if (tipoEventoSelect && localPresencial && localOnline) {
            tipoEventoSelect.addEventListener('change', function() {
                const tipoEvento = this.value;
                
                if (tipoEvento === 'presencial') {
                    localPresencial.style.display = 'block';
                    localOnline.style.display = 'none';
                } else if (tipoEvento === 'online') {
                    localPresencial.style.display = 'none';
                    localOnline.style.display = 'block';
                } else if (tipoEvento === 'hibrido') {
                    localPresencial.style.display = 'block';
                    localOnline.style.display = 'block';
                } else {
                    localPresencial.style.display = 'none';
                    localOnline.style.display = 'none';
                }
            });
        }

            // Função para validar a etapa atual
    function validarEtapaAtual() {
        const etapa = etapas[etapaAtual];
        const campos = etapa.querySelectorAll('input[required], select[required], textarea[required]');
        let valido = true;
        
        campos.forEach(campo => {
            if (!campo.value.trim()) {
                campo.classList.add('invalid');
                valido = false;
            } else {
                campo.classList.remove('invalid');
            }
        });
        
        if (!valido) {
            alert('Por favor, preencha todos os campos obrigatórios antes de continuar.');
        }
        
        return valido;
    }
    
    // Adicionar validação em tempo real
    document.querySelectorAll('input, select, textarea').forEach(campo => {
        campo.addEventListener('input', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('invalid');
            } else {
                this.classList.remove('invalid');
            }
        });
    });
    
    // Validar formulário antes de enviar
    document.querySelector('.criar-evento-form').addEventListener('submit', function(e) {
        const termosCheck = document.getElementById('termos');
        
        if (!termosCheck.checked) {
            e.preventDefault();
            alert('Você precisa concordar com os termos de uso para continuar.');
            return false;
        }
        
        // Validar todos os campos obrigatórios
        const camposObrigatorios = document.querySelectorAll('input[required], select[required], textarea[required]');
        let formValido = true;
        
        camposObrigatorios.forEach(campo => {
            if (!campo.value.trim()) {
                campo.classList.add('invalid');
                formValido = false;
            }
        });
        
        if (!formValido) {
            e.preventDefault();
            alert('Por favor, preencha todos os campos obrigatórios antes de enviar.');
            return false;
        }
    });

   
function atualizarResumo() {
    console.log("Atualizando resumo...");
    
    try {
        // Informações Básicas
        const nomeEvento = document.getElementById('nome-evento').value || 'Não informado';
        const descricaoEvento = document.getElementById('descricao-evento').value || 'Não informada';
        const categoriaEvento = document.getElementById('categoria-evento')?.value || 'Não informada';
        
        // Atualizar nome e descrição do evento
        document.querySelector('.resumo-nome-evento').textContent = nomeEvento;
        document.querySelector('.resumo-descricao-evento').textContent = descricaoEvento;
        document.querySelector('.resumo-categoria-evento').textContent = categoriaEvento;
        
        // Atualizar imagem de capa
        const imagemPreview = document.querySelector('#image-preview img')?.src;
        const imagemResumo = document.querySelector('.resumo-image img');
        if (imagemPreview && !imagemPreview.includes('placeholder.svg') && imagemResumo) {
            imagemResumo.src = imagemPreview;
        }
        
        // Atualizar as demais seções usando as funções auxiliares
        atualizarPalestrantes();
        atualizarLocalData();
        atualizarIngressos();
        atualizarConfiguracoes();

        console.log("Resumo atualizado com sucesso!");
    } catch (error) {
        console.error("Erro ao atualizar resumo:", error);
    }
}


    function atualizarPalestrantes() {
        const palestrantesContainer = document.getElementById('palestrantes-container');
        const palestrantesItems = palestrantesContainer.querySelectorAll('.palestrante-item');
        const palestrantesResumo = document.querySelector('.resumo-palestrantes');
        
        if (palestrantesResumo) {
            // Limpar lista atual
            palestrantesResumo.innerHTML = '';
            
            if (palestrantesItems.length === 0) {
                palestrantesResumo.innerHTML = '<li>Nenhum palestrante adicionado</li>';
                return;
            }
            
            // Adicionar cada palestrante à lista de resumo
            palestrantesItems.forEach((item) => {
                const nomeInput = item.querySelector('input[name^="palestrante-nome"]');
                const cargoInput = item.querySelector('input[name^="palestrante-cargo"]');
                
                if (nomeInput) {
                    const nome = nomeInput.value || 'Sem nome';
                    const cargo = cargoInput?.value || '';
                    
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-user"></i> ${nome}${cargo ? ' - ' + cargo : ''}`;
                    palestrantesResumo.appendChild(li);
                }
            });
        }
    }
    
    function atualizarLocalData() {
        const dataInicio = document.getElementById('data-inicio').value || 'Não informada';
        const dataFim = document.getElementById('data-fim').value || dataInicio;
        const horaInicio = document.getElementById('hora-inicio').value || 'Não informada';
        const horaFim = document.getElementById('hora-fim').value || 'Não informada';
        const tipoEvento = document.getElementById('tipo-evento').value;
        
        // Atualizar data e hora
        const dataHoraElement = document.querySelector('.resumo-item:nth-child(1) p');
        if (dataHoraElement) {
            try {
                // Função para formatar a data no padrão brasileiro
                function formatarDataBR(dataStr) {
                    if (dataStr === 'Não informada') return dataStr;
                    
                    // Converter string de data para objeto Date
                    const data = new Date(dataStr);
                    
                    // Formatar para DD/MM/AAAA
                    const dia = data.getDate().toString().padStart(2, '0');
                    const mes = (data.getMonth() + 1).toString().padStart(2, '0');
                    const ano = data.getFullYear();
                    
                    return `${dia}/${mes}/${ano}`;
                }
                
                const dataInicioFormatada = formatarDataBR(dataInicio);
                const dataFimFormatada = formatarDataBR(dataFim);
                    
                // Se as datas são iguais, mostrar apenas uma data
                if (dataInicio === dataFim || !dataFim) {
                    dataHoraElement.textContent = `${dataInicioFormatada} - ${horaInicio} às ${horaFim}`;
                } else {
                    dataHoraElement.textContent = `De ${dataInicioFormatada} às ${horaInicio} até ${dataFimFormatada} às ${horaFim}`;
                }
            } catch (e) {
                console.error("Erro ao formatar data:", e);
                dataHoraElement.textContent = `${dataInicio} - ${horaInicio} às ${horaFim}`;
            }
        }
        
        let tipoEventoElement = null;
        document.querySelectorAll('.resumo-item h4').forEach(h4 => {
            if (h4.textContent.includes('Tipo')) {
                tipoEventoElement = h4.closest('.resumo-item').querySelector('p');
            }
        });
      
        if (tipoEventoElement) {
            let tipoTexto = 'Não informado';
            switch(tipoEvento) {
                case 'presencial': tipoTexto = 'Presencial'; break;
                case 'online': tipoTexto = 'Online'; break;
                case 'hibrido': tipoTexto = 'Híbrido'; break;
                default: tipoTexto = tipoEvento || 'Não informado';
            }
            tipoEventoElement.textContent = tipoTexto;
        }
        
        // Atualizar local
        atualizarLocal(tipoEvento);
        
        // Atualizar capacidade
        const capacidadeInput = document.getElementById('capacidade');
        let capacidadeElement = null;
    
        document.querySelectorAll('.resumo-item h4').forEach(h4 => {
            if (h4.textContent.includes('Capacidade')) {
                capacidadeElement = h4.closest('.resumo-item').querySelector('p');
            }
        });
          
        let capacidade = 'Não informada';
        if (capacidadeInput && capacidadeInput.value) {
            capacidade = capacidadeInput.value;
            console.log("Valor da capacidade:", capacidade);
        }
        
        if (capacidadeElement) {
            capacidadeElement.textContent = `${capacidade} vagas`;
        }
    }
    function atualizarLocal(tipoEvento) {
        let localElement = null;
        document.querySelectorAll('.resumo-item h4').forEach(h4 => {
            if (h4.textContent.includes('Local')) {
                localElement = h4.closest('.resumo-item');
            }
        });

        if (!localElement) return;
        
        // Manter o título
        const titulo = localElement.querySelector('h4');
        localElement.innerHTML = '';
        localElement.appendChild(titulo);
        
        if (tipoEvento === 'presencial' || tipoEvento === 'hibrido') {
            const nomeLocal = document.getElementById('nome-local').value || 'Não informado';
            const endereco = document.getElementById('endereco').value || 'Não informado';
            const cidade = document.getElementById('cidade').value || '';
            const estado = document.getElementById('estado').value || '';
            
            const p1 = document.createElement('p');
            p1.textContent = nomeLocal;
            localElement.appendChild(p1);
            
            const p2 = document.createElement('p');
            p2.textContent = `${endereco}${cidade && estado ? ` - ${cidade}, ${estado}` : ''}`;
            localElement.appendChild(p2);
        }
        
        if (tipoEvento === 'online' || tipoEvento === 'hibrido') {
            const plataforma = document.getElementById('plataforma')?.value || 'Plataforma Online';
            const linkEvento = document.getElementById('link-evento')?.value || 'Link não informado';
            
            const p1 = document.createElement('p');
            p1.textContent = plataforma;
            localElement.appendChild(p1);
            
            const p2 = document.createElement('p');
            p2.textContent = linkEvento;
            localElement.appendChild(p2);
        }
    }
    
    function atualizarIngressos() {
        const ingressosContainer = document.getElementById('ingressos-container');
        const ingressosItems = ingressosContainer.querySelectorAll('.ingresso-item');

        let ingressosResumo;
        document.querySelectorAll('.resumo-item h4').forEach(h4 => {
            if (h4.textContent.includes('Ingressos')) {
                ingressosResumo = h4.closest('.resumo-item').querySelector('ul');
            }
        });
      
        if (!ingressosResumo) return;
        
        // Limpar lista atual
        ingressosResumo.innerHTML = '';
        
        if (ingressosItems.length === 0) {
            ingressosResumo.innerHTML = '<li>Nenhum ingresso adicionado</li>';
            return;
        }
        
        // Adicionar cada ingresso à lista de resumo
        ingressosItems.forEach((item) => {
            const nomeInput = item.querySelector('input[id^="nome-ingresso"]');
            const precoInput = item.querySelector('input[id^="preco-ingresso"]');
            const quantidadeInput = item.querySelector('input[id^="quantidade-ingresso"]');
            
            if (nomeInput) {
                const nome = nomeInput.value || 'Sem nome';
                const preco = precoInput?.value || '0.00';
                const quantidade = quantidadeInput?.value || '0';
                
                const li = document.createElement('li');
                li.innerHTML = `<i class="fas fa-ticket-alt"></i> ${nome} - R$ ${parseFloat(preco).toFixed(2)} ${parseFloat(preco) === 0 ? '(Gratuito)' : ''} - ${quantidade} unidades`;
                ingressosResumo.appendChild(li);
            }
        });
    }
    
    function atualizarConfiguracoes() {
        const emitirCertificadosInput = document.querySelector('input[name="emitir-certificados"]');
        const listaEsperaInput = document.querySelector('input[name="lista-espera"]');
        const eventoPrivadoInput = document.querySelector('input[name="evento-privado"]');

        let configuracoesResumo;
        document.querySelectorAll('.resumo-item h4').forEach(h4 => {
            if (h4.textContent.includes('Configurações')) {
                configuracoesResumo = h4.closest('.resumo-item').querySelector('ul');
            }
        });
        
        if (!configuracoesResumo || !emitirCertificadosInput || !listaEsperaInput || !eventoPrivadoInput) return;
        
        const emitirCertificados = emitirCertificadosInput.checked;
        const listaEspera = listaEsperaInput.checked;
        const eventoPrivado = eventoPrivadoInput.checked;
        
        // Limpar lista atual
        configuracoesResumo.innerHTML = '';
        
        // Adicionar configurações
        configuracoesResumo.innerHTML += `<li><i class="fas ${emitirCertificados ? 'fa-check' : 'fa-times'}"></i> Emitir certificados</li>`;
        configuracoesResumo.innerHTML += `<li><i class="fas ${listaEspera ? 'fa-check' : 'fa-times'}"></i> Lista de espera</li>`;
        configuracoesResumo.innerHTML += `<li><i class="fas ${eventoPrivado ? 'fa-check' : 'fa-times'}"></i> Evento privado</li>`;
    }

    document.querySelectorAll('input, select, textarea').forEach(campo => {
        campo.addEventListener('change', function() {
            if (etapaAtual === 4) { // Se estiver na etapa de revisão
                atualizarResumo();
            }
        });
    });

    // Adicionar no final do DOMContentLoaded
// Adicionar listeners para data de término e outros campos importantes
document.getElementById('data-fim')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('hora-fim')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('nome-local')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('endereco')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('cidade')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('estado')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('plataforma')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('link-evento')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

document.getElementById('capacidade')?.addEventListener('change', function() {
    if (etapaAtual === 4) atualizarResumo();
});

const capacidadeInput = document.getElementById('capacidade');
if (capacidadeInput) {
    capacidadeInput.addEventListener('input', function() {
        console.log("Capacidade alterada para:", this.value);
        if (etapaAtual === 4) {
            atualizarResumo();
        }
    });
    
    // Adicionar também o evento change para garantir
    capacidadeInput.addEventListener('change', function() {
        console.log("Capacidade alterada (change) para:", this.value);
        if (etapaAtual === 4) {
            atualizarResumo();
        }
    });
}


});
