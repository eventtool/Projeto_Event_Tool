document.addEventListener('DOMContentLoaded', function() {
    
    const formLogin = document.querySelector('.login-form');
    const inputSenha = document.getElementById('password');
    const togglePassword = document.querySelector('.toggle-password');
    const forgotPasswordLink = document.querySelector('.forgot-password');

    
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = inputSenha.getAttribute('type') === 'password' ? 'text' : 'password';
            inputSenha.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Funcionalidade de recuperação de senha será implementada em breve!');
        });
    }

    // Envio do formulário
    if (formLogin) {
        formLogin.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                remember: document.getElementById('remember').checked
            };

            try {
                // Mostrar feedback visual (opcional)
                const submitButton = formLogin.querySelector('button[type="submit"]');
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Entrando...';
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    // Login bem-sucedido
                    window.location.href = data.redirect || '/dashboard';
                } else {

                    alert(data.message || 'Credenciais inválidas. Por favor, tente novamente.');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Ocorreu um erro ao processar seu login. Por favor, tente novamente.');
            } finally {
                const submitButton = formLogin.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Entrar';
                }
            }
        });
    }

});