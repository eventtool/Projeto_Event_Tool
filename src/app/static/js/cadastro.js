document.addEventListener('DOMContentLoaded', function() {
    //o famoso navburguer
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const authButtons = document.querySelector('.auth-buttons');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            authButtons.classList.toggle('active');
        });
    }
    
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.querySelector('#senha');
    
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
    
    // Verificador de força da senha
    const strengthMeter = document.querySelector('.strength-meter-fill');
    const strengthText = document.querySelector('.strength-text span');
    
    if (passwordInput && strengthMeter && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = checkPasswordStrength(password);
            
            // Atualiza o medidor de força
            strengthMeter.setAttribute('data-strength', strength.score);
            strengthText.textContent = strength.text;
        });
    }
    
    // Função para verificar a força da senha
    function checkPasswordStrength(password) {
        // Critérios de força
        const hasLowerCase = /[a-z]/.test(password);
        const hasUpperCase = /[A-Z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecialChar = /[^A-Za-z0-9]/.test(password);
        const isLongEnough = password.length >= 8;
        
        // Calcula a pontuação (0-4)
        let score = 0;
        if (hasLowerCase) score++;
        if (hasUpperCase) score++;
        if (hasNumber) score++;
        if (hasSpecialChar) score++;
        if (isLongEnough) score++;
        
        score = Math.min(score, 4);
        
        let text = '';
        switch (score) {
            case 0:
                text = 'Muito fraca';
                break;
            case 1:
                text = 'Fraca';
                break;
            case 2:
                text = 'Média';
                break;
            case 3:
                text = 'Forte';
                break;
            case 4:
                text = 'Muito forte';
                break;
        }
        
        return { score, text };
    }
    

    const celularInput = document.querySelector('#celular');
    if (celularInput) {
        celularInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 0) {
                //formato(XX) XXXXX-XXXX
                value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
                value = value.replace(/(\d)(\d{4})$/, '$1-$2');
            }
            
            e.target.value = value;
        });
    }
    
   
    const cadastroForm = document.querySelector('#cadastro-form');
    
    if (cadastroForm) {
        cadastroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const nome = document.querySelector('#nome').value;
            const email = document.querySelector('#email').value;
            const senha = document.querySelector('#senha').value;
            const celular = document.querySelector('#celular').value;
            const tipoConta = document.querySelector('input[name="tipo-conta"]:checked').value;
            const aceitouTermos = document.querySelector('#termos').checked;
            
            if (!nome || !email || !senha || !celular || !aceitouTermos) {
                alert('Por favor, preencha todos os campos obrigatórios.');
                return;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Por favor, insira um email válido.');
                return;
            }
            
            const senhaForte = checkPasswordStrength(senha);
            if (senhaForte.score < 2) {
                alert('Por favor, escolha uma senha mais forte.');
                return;
            }
            console.log('Cadastro:', {
                nome,
                email,
                senha,
                celular,
                tipoConta
            });
            
            
            alert('Cadastro realizado com sucesso! Você será redirecionado para a página inicial.');
            
            //volta para a tela inicial
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        });
    }
    
    const googleBtn = document.querySelector('.btn-google');
    
    if (googleBtn) {
        googleBtn.addEventListener('click', function() {
            
            alert('Redirecionando para autenticação do Google...');
        });
    }
});