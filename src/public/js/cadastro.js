document.addEventListener('DOMContentLoaded', function() {
    // Elementos do formulário
    const formCadastro = document.getElementById('cadastro-form');
    const inputSenha = document.getElementById('senha');
    const togglePassword = document.querySelector('.toggle-password');
    const strengthMeter = document.querySelector('.strength-meter-fill');
    const strengthText = document.querySelector('.strength-text span');
    const inputCelular = document.getElementById('celular');

    // Máscara para o campo de celular
    if (inputCelular) {
        inputCelular.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
            value = value.replace(/(\d)(\d{4})$/, '$1-$2');
            e.target.value = value;
        });
    }

    // Mostrar/ocultar senha
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = inputSenha.getAttribute('type') === 'password' ? 'text' : 'password';
            inputSenha.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Verificar força da senha
    if (inputSenha) {
        inputSenha.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            strengthMeter.setAttribute('data-strength', strength.level);
            strengthMeter.style.width = `${strength.score * 25}%`;
            strengthText.textContent = strength.level;
            strengthText.className = strength.level.toLowerCase();
        });
    }

    // Função para verificar força da senha
    function checkPasswordStrength(password) {
        let score = 0;
        
        // Verifica o comprimento
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        
        // Verifica caracteres diversos
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        // Define o nível com base no score
        const levels = ['Fraca', 'Média', 'Forte', 'Muito Forte'];
        const level = levels[Math.min(score, levels.length - 1)];
        
        return { score, level };
    }

    // Envio do formulário
    if (formCadastro) {
        formCadastro.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validação dos termos
            const termos = document.getElementById('termos');
            if (!termos.checked) {
                alert('Você deve aceitar os termos de uso e política de privacidade');
                return;
            }

            // Coletar dados do formulário
            const formData = {
                nome: document.getElementById('nome').value,
                email: document.getElementById('email').value,
                senha: document.getElementById('senha').value,
                celular: document.getElementById('celular').value,
                tipo_conta: document.querySelector('input[name="tipo-conta"]:checked').value
            };

            try {
                // Enviar dados para o backend
                const response = await fetch('/cadastro', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    // Cadastro bem-sucedido
                    window.location.href = data.redirect || '/login';
                } else {
                    // Mostrar mensagem de erro
                    alert(data.message || 'Erro no cadastro. Por favor, tente novamente.');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Ocorreu um erro ao processar seu cadastro. Por favor, tente novamente.');
            }
        });
    }
});