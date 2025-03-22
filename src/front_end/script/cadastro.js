document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cadastroForm');
    const toggleSenha = document.getElementById('toggleSenha');
    const senhaInput = document.getElementById('senha');
    const celularInput = document.getElementById('celular');

    // Máscara para o campo de celular
    celularInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 11) value = value.slice(0, 11);
        
        if (value.length > 2) {
            value = '(' + value.substring(0, 2) + ')' + (value.length > 2 ? ' ' + value.substring(2) : '');
        }
        if (value.length > 9) {
            value = value.substring(0, 9) + '-' + value.substring(9);
        }
        
        e.target.value = value;
    });

    // Toggle para mostrar/esconder senha
    toggleSenha.addEventListener('click', function() {
        if (senhaInput.type === 'password') {
            senhaInput.type = 'text';
            toggleSenha.textContent = '🔒';
        } else {
            senhaInput.type = 'password';
            toggleSenha.textContent = '👁️';
        }
    });

    // Validação do formulário
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        let isValid = true;

        // Validar nome
        const nome = document.getElementById('nome').value.trim();
        if (nome === '' || nome.split(' ').length < 2) {
            document.getElementById('nomeError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('nomeError').style.display = 'none';
        }

        // Validar email
        const email = document.getElementById('email').value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            document.getElementById('emailError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('emailError').style.display = 'none';
        }

        // Validar senha
        const senha = document.getElementById('senha').value;
        if (senha.length < 6) {
            document.getElementById('senhaError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('senhaError').style.display = 'none';
        }

        // Validar celular
        const celular = document.getElementById('celular').value.replace(/\D/g, '');
        if (celular.length < 10) {
            document.getElementById('celularError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('celularError').style.display = 'none';
        }

        // Validar tipo (palestrante ou telespectador)
        const tipoSelecionado = document.querySelector('input[name="tipo"]:checked');
        if (!tipoSelecionado) {
            document.getElementById('tipoError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('tipoError').style.display = 'none';
        }

        // Se tudo estiver válido, enviar o formulário
        if (isValid) {
            const formData = {
                nome: nome,
                email: email,
                senha: senha,
                celular: celular,
                tipo: tipoSelecionado.value
            };
            
            console.log('Dados do formulário:', formData);
            alert('Cadastro realizado com sucesso!');
            form.reset();
        }
    });
});