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
        
        if (n === 4) {
            try {
                atualizarResumo();
            } catch (error) {
                console.error("Erro ao atualizar resumo:", error);
            }
        }
        // Mostra a etapa atual
        etapas[n].classList.add('active');
        etapaAtual = n;
        
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
    let palestranteCount = 1;
    
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
        
        // Adicionar evento para remover palestrante existente
        document.querySelectorAll('.remove-palestrante').forEach(btn => {
            btn.addEventListener('click', function() {
                const palestranteItem = this.closest('.palestrante-item');
                palestrantesContainer.removeChild(palestranteItem);

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
            const nomeEvento = document.getElementById('nome-evento').value;
            const descricaoEvento = document.getElementById('descricao-evento').value;
            
            // Atualizar nome do evento
            const nomeEventoElement = document.querySelector('.resumo-evento:nth-of-type(1) .resumo-item:nth-of-type(1) p');
            if (nomeEvento && nomeEventoElement) {
                nomeEventoElement.textContent = nomeEvento;
                console.log("Nome do evento atualizado:", nomeEvento);
            }
            
            // Atualizar imagem de capa
            const imagemPreview = document.querySelector('#image-preview img').src;
            const imagemResumo = document.querySelector('.resumo-image img');
            if (imagemPreview && !imagemPreview.includes('placeholder.svg') && imagemResumo) {
                imagemResumo.src = imagemPreview;
                console.log("Imagem atualizada");
            }
            
            // Palestrantes
            const palestrantesContainer = document.getElementById('palestrantes-container');
            const palestrantesItems = palestrantesContainer.querySelectorAll('.palestrante-item');
            const palestrantesResumo = document.querySelector('.resumo-evento:nth-of-type(2) .resumo-item ul');
            
            if (palestrantesResumo) {
                // Limpar lista atual
                palestrantesResumo.innerHTML = '';
                console.log("Atualizando palestrantes...", palestrantesItems.length);
                
                // Adicionar cada palestrante à lista de resumo
                palestrantesItems.forEach((item, index) => {
                    let nome = '';
                    let cargo = '';
                    
                    // Tentar obter nome e cargo de diferentes maneiras
                    const nomeElement = item.querySelector('h4');
                    const cargoElement = item.querySelector('p');
                    const nomeInput = item.querySelector('input[name^="palestrante-nome"]');
                    const cargoInput = item.querySelector('input[name^="palestrante-cargo"]');
                    
                    if (nomeElement) nome = nomeElement.textContent;
                    else if (nomeInput) nome = nomeInput.value;
                    
                    if (cargoElement) cargo = cargoElement.textContent;
                    else if (cargoInput) cargo = cargoInput.value;
                    
                    if (nome) {
                        const li = document.createElement('li');
                        li.innerHTML = `<i class="fas fa-user"></i> ${nome}${cargo ? ' - ' + cargo : ''}`;
                        palestrantesResumo.appendChild(li);
                        console.log("Palestrante adicionado:", nome);
                    }
                });
            }
            
            // Local e Data
            const dataInicio = document.getElementById('data-inicio').value;
            const horaInicio = document.getElementById('hora-inicio').value;
            const horaFim = document.getElementById('hora-fim').value;
            const tipoEvento = document.getElementById('tipo-evento').value;
            
            // Atualizar data e hora
            const dataHoraElement = document.querySelector('.resumo-evento:nth-of-type(3) .resumo-item:nth-of-type(1) p');
            if (dataInicio && horaInicio && horaFim && dataHoraElement) {
                try {
                    const dataFormatada = new Date(dataInicio).toLocaleDateString('pt-BR');
                    dataHoraElement.textContent = `${dataFormatada} - ${horaInicio} às ${horaFim}`;
                    console.log("Data e hora atualizadas");
                } catch (e) {
                    console.error("Erro ao formatar data:", e);
                }
            }
            
            // Atualizar tipo de evento
            const tipoEventoElement = document.querySelector('.resumo-evento:nth-of-type(3) .resumo-item:nth-of-type(2) p');
            if (tipoEvento && tipoEventoElement) {
                let tipoTexto = '';
                switch(tipoEvento) {
                    case 'presencial': tipoTexto = 'Presencial'; break;
                    case 'online': tipoTexto = 'Online'; break;
                    case 'hibrido': tipoTexto = 'Híbrido'; break;
                    default: tipoTexto = tipoEvento;
                }
                tipoEventoElement.textContent = tipoTexto;
                console.log("Tipo de evento atualizado:", tipoTexto);
            }
            
            // Atualizar local
            const localElement = document.querySelector('.resumo-evento:nth-of-type(3) .resumo-item:nth-of-type(3)');
            if (localElement) {
                const paragrafos = localElement.querySelectorAll('p');
                
                if (tipoEvento === 'presencial' || tipoEvento === 'hibrido') {
                    const nomeLocal = document.getElementById('nome-local').value;
                    const endereco = document.getElementById('endereco').value;
                    const cidade = document.getElementById('cidade').value;
                    const estado = document.getElementById('estado').value;
                    
                    if (paragrafos.length >= 1 && nomeLocal) 
                        paragrafos[0].textContent = nomeLocal;
                    
                    if (paragrafos.length >= 2 && endereco) 
                        paragrafos[1].textContent = `${endereco}${cidade && estado ? ` - ${cidade}, ${estado}` : ''}`;
                    
                    console.log("Local presencial atualizado");
                } else if (tipoEvento === 'online') {
                    const plataforma = document.getElementById('plataforma').value;
                    const linkEvento = document.getElementById('link-evento').value;
                    
                    if (paragrafos.length >= 1) 
                        paragrafos[0].textContent = plataforma || 'Plataforma Online';
                    
                    if (paragrafos.length >= 2 && linkEvento) 
                        paragrafos[1].textContent = linkEvento;
                    
                    console.log("Local online atualizado");
                }
            }
            
            // Atualizar capacidade
            const capacidade = document.getElementById('capacidade').value;
            const capacidadeElement = document.querySelector('.resumo-evento:nth-of-type(3) .resumo-item:nth-of-type(4) p');
            if (capacidade && capacidadeElement) {
                capacidadeElement.textContent = `${capacidade} vagas`;
                console.log("Capacidade atualizada:", capacidade);
            }
            
            // Ingressos
            const ingressosContainer = document.getElementById('ingressos-container');
            const ingressosItems = ingressosContainer.querySelectorAll('.ingresso-item');
            const ingressosResumo = document.querySelector('.resumo-evento:nth-of-type(4) .resumo-item:nth-of-type(1) ul');
            
            if (ingressosResumo) {
                // Limpar lista atual
                ingressosResumo.innerHTML = '';
                console.log("Atualizando ingressos...", ingressosItems.length);
                
                // Adicionar cada ingresso à lista de resumo
                ingressosItems.forEach((item, index) => {
                    const nomeInput = item.querySelector('input[id^="nome-ingresso"]');
                    const precoInput = item.querySelector('input[id^="preco-ingresso"]');
                    const quantidadeInput = item.querySelector('input[id^="quantidade-ingresso"]');
                    
                    if (nomeInput && precoInput && quantidadeInput) {
                        const nome = nomeInput.value;
                        const preco = precoInput.value;
                        const quantidade = quantidadeInput.value;
                        
                        if (nome) {
                            const li = document.createElement('li');
                            li.innerHTML = `<i class="fas fa-ticket-alt"></i> ${nome} - R$ ${parseFloat(preco).toFixed(2)} ${parseFloat(preco) === 0 ? '(Gratuito)' : ''} - ${quantidade} unidades`;
                            ingressosResumo.appendChild(li);
                            console.log("Ingresso adicionado:", nome);
                        }
                    }
                });
            }
            
            // Configurações adicionais
            const emitirCertificadosInput = document.querySelector('input[name="emitir-certificados"]');
            const listaEsperaInput = document.querySelector('input[name="lista-espera"]');
            const eventoPrivadoInput = document.querySelector('input[name="evento-privado"]');
            const configuracoesResumo = document.querySelector('.resumo-evento:nth-of-type(4) .resumo-item:nth-of-type(2) ul');
            
            if (configuracoesResumo && emitirCertificadosInput && listaEsperaInput && eventoPrivadoInput) {
                const emitirCertificados = emitirCertificadosInput.checked;
                const listaEspera = listaEsperaInput.checked;
                const eventoPrivado = eventoPrivadoInput.checked;
                
                // Limpar lista atual
                configuracoesResumo.innerHTML = '';
                
                // Adicionar configurações
                configuracoesResumo.innerHTML += `<li><i class="fas ${emitirCertificados ? 'fa-check' : 'fa-times'}"></i> Emitir certificados</li>`;
                configuracoesResumo.innerHTML += `<li><i class="fas ${listaEspera ? 'fa-check' : 'fa-times'}"></i> Lista de espera</li>`;
                configuracoesResumo.innerHTML += `<li><i class="fas ${eventoPrivado ? 'fa-check' : 'fa-times'}"></i> Evento privado</li>`;
                
                console.log("Configurações atualizadas");
            }
            
            console.log("Resumo atualizado com sucesso!");
        } catch (error) {
            console.error("Erro ao atualizar resumo:", error);
        }
    }
    
});
