document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const form = document.querySelector('.criar-evento-form');
    const etapas = document.querySelectorAll('.form-etapa');
    const progressoEtapas = document.querySelectorAll('.progresso-etapa');
    const btnNext = document.querySelectorAll('.btn-next');
    const btnPrev = document.querySelectorAll('.btn-prev');
    const btnSubmit = document.querySelector('.btn-submit');
    const editSections = document.querySelectorAll('.edit-section');
    
    // Elementos específicos
    const imagePreview = document.getElementById('image-preview');
    const imageInput = document.getElementById('imagem-evento');
    const tipoEventoSelect = document.getElementById('tipo-evento');
    const localPresencial = document.getElementById('local-presencial');
    const localOnline = document.getElementById('local-online');
    const addPalestranteBtn = document.getElementById('add-palestrante-btn');
    const palestrantesContainer = document.getElementById('palestrantes-container');
    const addIngressoBtn = document.getElementById('add-ingresso-btn');
    const ingressosContainer = document.getElementById('ingressos-container');
    const addTagInput = document.getElementById('add-tag-input');
    const addTagBtn = document.getElementById('add-tag-btn');
    const tagsContainer = document.getElementById('tags-container');
    
    // Variáveis de estado
    let etapaAtual = 0;
    let palestranteCount = 1;
    let ingressoCount = 1;
    
    // Inicialização
    atualizarProgressoEtapas();
    
    // ===== NAVEGAÇÃO ENTRE ETAPAS =====
    
    // Avançar para a próxima etapa
    btnNext.forEach(btn => {
        btn.addEventListener('click', () => {
            if (validarEtapaAtual()) {
                etapas[etapaAtual].classList.remove('active');
                etapaAtual++;
                etapas[etapaAtual].classList.add('active');
                atualizarProgressoEtapas();
                window.scrollTo(0, 0);
            }
        });
    });
    
    // Voltar para a etapa anterior
    btnPrev.forEach(btn => {
        btn.addEventListener('click', () => {
            etapas[etapaAtual].classList.remove('active');
            etapaAtual--;
            etapas[etapaAtual].classList.add('active');
            atualizarProgressoEtapas();
            window.scrollTo(0, 0);
        });
    });
    
    // Editar seção específica na revisão
    editSections.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetStep = parseInt(btn.getAttribute('data-step')) - 1;
            etapas[etapaAtual].classList.remove('active');
            etapaAtual = targetStep;
            etapas[etapaAtual].classList.add('active');
            atualizarProgressoEtapas();
            window.scrollTo(0, 0);
        });
    });
    
    // Atualizar indicadores de progresso
    function atualizarProgressoEtapas() {
        progressoEtapas.forEach((etapa, index) => {
            if (index < etapaAtual) {
                etapa.classList.remove('active');
                etapa.classList.add('completed');
            } else if (index === etapaAtual) {
                etapa.classList.add('active');
                etapa.classList.remove('completed');
            } else {
                etapa.classList.remove('active');
                etapa.classList.remove('completed');
            }
        });
    }
    
    // ===== VALIDAÇÃO DE FORMULÁRIO =====
    
    // Validar campos da etapa atual
    function validarEtapaAtual() {
        const camposObrigatorios = etapas[etapaAtual].querySelectorAll('[required]');
        let valido = true;
        
        camposObrigatorios.forEach(campo => {
            if (!campo.value.trim()) {
                destacarCampoInvalido(campo);
                valido = false;
            } else {
                removerDestaqueCampo(campo);
            }
        });
        
        // Validações específicas por etapa
        if (etapaAtual === 0) {
            // Validar nome do evento (mínimo 5 caracteres)
            const nomeEvento = document.getElementById('nome-evento');
            if (nomeEvento.value.trim().length < 5) {
                destacarCampoInvalido(nomeEvento);
                mostrarMensagemErro(nomeEvento, 'O nome do evento deve ter pelo menos 5 caracteres');
                valido = false;
            }
            
            // Validar descrição (mínimo 20 caracteres)
            const descricaoEvento = document.getElementById('descricao-evento');
            if (descricaoEvento.value.trim().length < 20) {
                destacarCampoInvalido(descricaoEvento);
                mostrarMensagemErro(descricaoEvento, 'A descrição deve ter pelo menos 20 caracteres');
                valido = false;
            }
        } else if (etapaAtual === 2) {
            // Validar data e hora
            const dataInicio = document.getElementById('data-inicio');
            const horaInicio = document.getElementById('hora-inicio');
            const dataFim = document.getElementById('data-fim');
            const horaFim = document.getElementById('hora-fim');
            
            const dataInicioObj = new Date(`${dataInicio.value}T${horaInicio.value}`);
            const dataAtual = new Date();
            
            // Verificar se a data é futura
            if (dataInicioObj <= dataAtual) {
                destacarCampoInvalido(dataInicio);
                mostrarMensagemErro(dataInicio, 'A data do evento deve ser futura');
                valido = false;
            }
            
            // Se data de término está preenchida, verificar se é posterior à data de início
            if (dataFim.value) {
                const dataFimObj = new Date(`${dataFim.value}T${horaFim.value}`);
                if (dataFimObj <= dataInicioObj) {
                    destacarCampoInvalido(dataFim);
                    mostrarMensagemErro(dataFim, 'A data de término deve ser posterior à data de início');
                    valido = false;
                }
            }
            
            // Validar campos específicos do tipo de evento
            if (tipoEventoSelect.value === 'presencial') {
                const endereco = document.getElementById('endereco');
                const cidade = document.getElementById('cidade');
                const estado = document.getElementById('estado');
                
                if (!endereco.value.trim() || !cidade.value.trim() || !estado.value) {
                    if (!endereco.value.trim()) destacarCampoInvalido(endereco);
                    if (!cidade.value.trim()) destacarCampoInvalido(cidade);
                    if (!estado.value) destacarCampoInvalido(estado);
                    valido = false;
                }
            } else if (tipoEventoSelect.value === 'online') {
                const plataforma = document.getElementById('plataforma');
                const linkEvento = document.getElementById('link-evento');
                
                if (!plataforma.value || !linkEvento.value.trim()) {
                    if (!plataforma.value) destacarCampoInvalido(plataforma);
                    if (!linkEvento.value.trim()) destacarCampoInvalido(linkEvento);
                    valido = false;
                }
                
                // Validar formato do link
                if (linkEvento.value.trim() && !isValidUrl(linkEvento.value.trim())) {
                    destacarCampoInvalido(linkEvento);
                    mostrarMensagemErro(linkEvento, 'Insira um URL válido');
                    valido = false;
                }
            }
        }
        
        return valido;
    }
    
    // Destacar campo inválido
    function destacarCampoInvalido(campo) {
        campo.classList.add('invalid');
        campo.addEventListener('input', function removerInvalido() {
            campo.classList.remove('invalid');
            const mensagemErro = campo.parentElement.querySelector('.error-message');
            if (mensagemErro) mensagemErro.remove();
            campo.removeEventListener('input', removerInvalido);
        });
    }
    
    // Remover destaque de campo
    function removerDestaqueCampo(campo) {
        campo.classList.remove('invalid');
        const mensagemErro = campo.parentElement.querySelector('.error-message');
        if (mensagemErro) mensagemErro.remove();
    }
    
    // Mostrar mensagem de erro
    function mostrarMensagemErro(campo, mensagem) {
        const mensagemErro = campo.parentElement.querySelector('.error-message');
        if (!mensagemErro) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = mensagem;
            campo.parentElement.appendChild(errorDiv);
        }
    }
    
    // Validar URL
    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    // ===== UPLOAD E PREVIEW DE IMAGEM =====
    
    // Preview de imagem
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = imagePreview.querySelector('img');
                    img.src = e.target.result;
                    imagePreview.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // ===== TIPO DE EVENTO (PRESENCIAL/ONLINE) =====
    
    // Alternar entre campos de evento presencial e online
    if (tipoEventoSelect) {
        tipoEventoSelect.addEventListener('change', function() {
            if (this.value === 'presencial') {
                localPresencial.style.display = 'block';
                localOnline.style.display = 'none';
            } else if (this.value === 'online') {
                localPresencial.style.display = 'none';
                localOnline.style.display = 'block';
            } else if (this.value === 'hibrido') {
                localPresencial.style.display = 'block';
                localOnline.style.display = 'block';
            } else {
                localPresencial.style.display = 'none';
                localOnline.style.display = 'none';
            }
        });
    }
    
    // ===== GERENCIAMENTO DE PALESTRANTES =====
    
    // Adicionar novo palestrante
    if (addPalestranteBtn) {
        addPalestranteBtn.addEventListener('click', function() {
            palestranteCount++;
            
            const novoPalestrante = document.createElement('div');
            novoPalestrante.className = 'palestrante-item';
            novoPalestrante.innerHTML = `
                <div class="palestrante-avatar">
                    <img src="placeholder.svg?height=60&width=60" alt="Avatar do Palestrante">
                </div>
                <div class="palestrante-info">
                    <h4>Novo Palestrante</h4>
                    <p>Clique em editar para adicionar informações</p>
                </div>
                <div class="palestrante-actions">
                    <button type="button" class="edit-palestrante"><i class="fas fa-edit"></i></button>
                    <button type="button" class="remove-palestrante remove"><i class="fas fa-trash"></i></button>
                </div>
            `;
            
            palestrantesContainer.appendChild(novoPalestrante);
            
            // Adicionar evento para remover palestrante
            const btnRemover = novoPalestrante.querySelector('.remove-palestrante');
            btnRemover.addEventListener('click', function() {
                novoPalestrante.remove();
            });
            
            // Adicionar evento para editar palestrante
            const btnEditar = novoPalestrante.querySelector('.edit-palestrante');
            btnEditar.addEventListener('click', function() {
                abrirModalPalestrante(novoPalestrante);
            });
        });
        
        // Adicionar eventos aos botões existentes
        const botoesRemoverPalestrante = document.querySelectorAll('.remove-palestrante');
        botoesRemoverPalestrante.forEach(btn => {
            btn.addEventListener('click', function() {
                this.closest('.palestrante-item').remove();
            });
        });
        
        const botoesEditarPalestrante = document.querySelectorAll('.edit-palestrante');
        botoesEditarPalestrante.forEach(btn => {
            btn.addEventListener('click', function() {
                abrirModalPalestrante(this.closest('.palestrante-item'));
            });
        });
    }
    
    // Abrir modal para editar palestrante
    function abrirModalPalestrante(palestranteItem) {
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'modal active';
        
        const nomePalestrante = palestranteItem.querySelector('h4').textContent;
        const bioPalestrante = palestranteItem.querySelector('p').textContent;
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Editar Palestrante</h2>
                    <button type="button" class="close-modal"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label for="nome-palestrante">Nome do Palestrante</label>
                        <input type="text" id="nome-palestrante" value="${nomePalestrante === 'Novo Palestrante' ? '' : nomePalestrante}" placeholder="Nome completo do palestrante">
                    </div>
                    <div class="form-group">
                        <label for="cargo-palestrante">Cargo/Especialidade</label>
                        <input type="text" id="cargo-palestrante" value="${bioPalestrante === 'Clique em editar para adicionar informações' ? '' : bioPalestrante}" placeholder="Ex: Especialista em UX Design">
                    </div>
                    <div class="form-group">
                        <label for="bio-palestrante">Biografia</label>
                        <textarea id="bio-palestrante" rows="4" placeholder="Breve biografia do palestrante..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="foto-palestrante">Foto</label>
                        <div class="file-upload">
                            <input type="file" id="foto-palestrante" accept="image/*">
                            <label for="foto-palestrante" class="file-upload-label">
                                <i class="fas fa-cloud-upload-alt"></i>
                                <span>Escolher arquivo</span>
                            </label>
                            <div class="file-name">Nenhum arquivo selecionado</div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline btn-cancel">Cancelar</button>
                    <button type="button" class="btn btn-primary btn-save">Salvar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Fechar modal
        const closeBtn = modal.querySelector('.close-modal');
        const cancelBtn = modal.querySelector('.btn-cancel');
        const saveBtn = modal.querySelector('.btn-save');
        
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        cancelBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        // Salvar alterações
        saveBtn.addEventListener('click', () => {
            const nome = modal.querySelector('#nome-palestrante').value;
            const cargo = modal.querySelector('#cargo-palestrante').value;
            
            if (nome.trim()) {
                palestranteItem.querySelector('h4').textContent = nome;
                palestranteItem.querySelector('p').textContent = cargo || 'Sem informações adicionais';
                modal.remove();
            } else {
                alert('O nome do palestrante é obrigatório');
            }
        });
        
        // Preview de imagem
        const fotoInput = modal.querySelector('#foto-palestrante');
        const fileName = modal.querySelector('.file-name');
        
        fotoInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileName.textContent = this.files[0].name;
                
                // Atualizar avatar do palestrante
                const file = this.files[0];
                const reader = new FileReader();
                reader.onload = function(e) {
                    palestranteItem.querySelector('.palestrante-avatar img').src = e.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                fileName.textContent = 'Nenhum arquivo selecionado';
            }
        });
    }
    
    // ===== GERENCIAMENTO DE INGRESSOS =====
    
    // Adicionar novo ingresso
    if (addIngressoBtn) {
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
            
            // Adicionar evento para remover ingresso
            const btnRemover = novoIngresso.querySelector('.remove-ingresso');
            btnRemover.addEventListener('click', function() {
                novoIngresso.remove();
            });
        });
        
        // Adicionar eventos aos botões existentes
        const botoesRemoverIngresso = document.querySelectorAll('.remove-ingresso');
        botoesRemoverIngresso.forEach(btn => {
            btn.addEventListener('click', function() {
                // Não remover se for o único ingresso
                if (ingressosContainer.querySelectorAll('.ingresso-item').length > 1) {
                    this.closest('.ingresso-item').remove();
                } else {
                    alert('É necessário ter pelo menos um tipo de ingresso');
                }
            });
        });
    }
    
    // ===== GERENCIAMENTO DE TAGS =====
    
    // Adicionar nova tag
    if (addTagBtn && addTagInput && tagsContainer) {
        addTagBtn.addEventListener('click', function() {
            adicionarTag();
        });
        
        addTagInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                adicionarTag();
            }
        });
        
        // Adicionar eventos aos botões de remover tag existentes
        const botoesRemoverTag = document.querySelectorAll('.remove-tag');
        botoesRemoverTag.forEach(btn => {
            btn.addEventListener('click', function() {
                this.closest('.tag').remove();
            });
        });
    }
    
    function adicionarTag() {
        const tagText = addTagInput.value.trim();
        
        if (tagText) {
            // Verificar se a tag já existe
            const tagsExistentes = Array.from(tagsContainer.querySelectorAll('.tag')).map(tag => 
                tag.textContent.trim().replace('×', '').trim()
            );
            
            if (!tagsExistentes.includes(tagText)) {
                const novaTag = document.createElement('div');
                novaTag.className = 'tag';
                novaTag.innerHTML = `
                    ${tagText}
                    <button type="button" class="remove-tag"><i class="fas fa-times"></i></button>
                `;
                
                tagsContainer.appendChild(novaTag);
                
                // Adicionar evento para remover tag
                const btnRemover = novaTag.querySelector('.remove-tag');
                btnRemover.addEventListener('click', function() {
                    novaTag.remove();
                });
                
                // Limpar input
                addTagInput.value = '';
            } else {
                alert('Esta tag já foi adicionada');
            }
        }
    }
    
    // ===== SUBMISSÃO DO FORMULÁRIO =====
    
    // Submeter formulário
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar última etapa
            if (validarEtapaAtual()) {
                // Verificar se os termos foram aceitos
                const termosCheck = document.getElementById('termos');
                if (!termosCheck.checked) {
                    alert('Você precisa aceitar os termos para continuar');
                    return;
                }
                
                // Aqui você pode implementar o envio do formulário para o servidor
                // Por enquanto, vamos apenas mostrar uma mensagem de sucesso
                alert('Evento criado com sucesso!');
                
                // Redirecionar para a página de eventos
                // window.location.href = 'eventos.html';
            }
        });
    }
    
    // ===== FUNCIONALIDADES ADICIONAIS =====
    
    // Toggle de senha
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Máscaras de input
    const cepInput = document.getElementById('cep');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 5) {
                value = value.substring(0, 5) + '-' + value.substring(5, 8);
            }
            e.target.value = value;
        });
    }
    
    const telefoneInput = document.getElementById('telefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = '(' + value;
                if (value.length > 3) {
                    value = value.substring(0, 3) + ') ' + value.substring(3);
                }
                if (value.length > 10) {
                    value = value.substring(0, 10) + '-' + value.substring(10, 15);
                }
            }
            e.target.value = value;
        });
    }
});