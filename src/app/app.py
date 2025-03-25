from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from models import Usuario, Evento, Certificado, Presenca
import config
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

# Testando a conexão com o banco
config.DatabaseConfig.test_db_connection()


db = SQLAlchemy(app)


# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para cadastro de usuários
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        celular = request.form['celular']
        tipo_usuario = request.form['tipo_usuario']

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,  # Em um cenário real, criptografe a senha!
            celular=celular,
            tipo_usuario=tipo_usuario
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['tipo_usuario'] = usuario.tipo_usuario
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('perfil'))
        else:
            flash('Credenciais inválidas', 'error')

    return render_template('login.html')

# Rota para perfil do usuário
@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        flash('Faça login para acessar esta página', 'error')
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('perfil.html', usuario=usuario)

# Rota para criar eventos (apenas palestrantes)
@app.route('/criar_evento', methods=['GET', 'POST'])
def criar_evento():
    if 'usuario_id' not in session or session['tipo_usuario'] != 'palestrante':
        flash('Apenas palestrantes podem criar eventos', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
        hora = datetime.strptime(request.form['hora'], '%H:%M').time()
        vagas = int(request.form['vagas'])

        novo_evento = Evento(
            nome=nome,
            data=data,
            hora=hora,
            vagas=vagas,
            palestrante_id=session['usuario_id']
        )
        db.session.add(novo_evento)
        db.session.commit()
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('eventos'))

    return render_template('criar_evento.html')

# Rota para listar eventos
@app.route('/eventos')
def eventos():
    eventos = Evento.query.all()
    return render_template('eventos.html', eventos=eventos)

# Rota para gerar certificados
@app.route('/gerar_certificado', methods=['POST'])
def gerar_certificado():
    if 'usuario_id' not in session:
        flash('Faça login para gerar certificados', 'error')
        return redirect(url_for('login'))

    nome_telespectador = request.form['nome_telespectador']
    horas = int(request.form['horas'])
    evento_id = int(request.form['evento_id'])

    # Recupera o evento do banco de dados
    evento = Evento.query.get(evento_id)
    if not evento:
        flash('Evento não encontrado', 'error')
        return redirect(url_for('eventos'))

    # Verifica se o evento já terminou
    data_hora_atual = datetime.now()
    data_hora_evento = datetime.combine(evento.data, evento.hora)

    if data_hora_atual < data_hora_evento:
        flash('O certificado só pode ser gerado após o término do evento', 'error')
        return redirect(url_for('eventos'))

    # Gera o certificado
    novo_certificado = Certificado(
        nome_telespectador=nome_telespectador,
        horas=horas,
        data=data_hora_atual.date(),  # Data de emissão do certificado
        hora=data_hora_atual.time(),  # Hora de emissão do certificado
        data_evento=evento.data,  # Data do evento
        hora_evento=evento.hora,  # Hora do evento
        evento_id=evento_id,
        usuario_id=session['usuario_id']
    )
    db.session.add(novo_certificado)
    db.session.commit()
    flash('Certificado gerado com sucesso!', 'success')
    return redirect(url_for('certificados'))

# Rota para listar certificados do usuário
@app.route('/certificados')
def certificados():
    if 'usuario_id' not in session:
        flash('Faça login para ver seus certificados', 'error')
        return redirect(url_for('login'))

    certificados = Certificado.query.filter_by(usuario_id=session['usuario_id']).all()
    return render_template('certificados.html', certificados=certificados)

# Rota para lista de presença
@app.route('/lista_presenca/<int:evento_id>')
def lista_presenca(evento_id):
    if 'usuario_id' not in session:
        flash('Faça login para ver a lista de presença', 'error')
        return redirect(url_for('login'))

    evento = Evento.query.get(evento_id)
    presencas = Presenca.query.filter_by(evento_id=evento_id).all()
    return render_template('lista_presenca.html', evento=evento, presencas=presencas)

# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)