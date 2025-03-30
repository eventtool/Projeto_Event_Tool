from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from models import Usuario, Evento, Certificado, Presenca
import config
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_required, login_user, current_user
from models import Usuario

app = Flask(__name__)

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

# Testando a conexão com o banco
config.DatabaseConfig.test_db_connection()


db = SQLAlchemy(app)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    celular = db.Column(db.String(20))
    tipo = db.Column(db.String(20), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Buscar usuário no banco de dados
            usuario = Usuario.query.filter_by(email=data['email']).first()
            
            # Verificar credenciais
            if not usuario or not check_password_hash(usuario.senha, data['password']):
                return jsonify({
                    'success': False,
                    'message': 'Email ou senha incorretos'
                }), 401
            
            # Fazer login do usuário
            login_user(usuario, remember=data.get('remember', False))
            
            # Determinar para onde redirecionar com base no tipo de usuário
            if usuario.tipo == 'palestrante':
                redirect_url = url_for('palestrante')
            else:
                redirect_url = url_for('telespectador')
            
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': redirect_url
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Erro no servidor: ' + str(e)
            }), 500
    
    return render_template('login.html')

@app.route('/palestrante')
@login_required
def palestrante_dashboard():
    if current_user.tipo != 'palestrante':
        return redirect(url_for('login'))
    return render_template('palestrante.html')

@app.route('/telespectador')
@login_required
def telespectador_dashboard():
    if current_user.tipo != 'telespectador':
        return redirect(url_for('login'))
    return render_template('telespectador.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            data = request.get_json()
            usuario_existente = Usuario.query.filter_by(email=data['email']).first()
            if usuario_existente:
                return jsonify({
                    'success': False,
                    'message': 'Este email já está cadastrado.'
                }), 400

            novo_usuario = Usuario(
                nome=data['nome'],
                email=data['email'],
                senha=(data['senha']),
                celular=data['celular'],
                tipo=data['tipo_conta']
            )
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Cadastro realizado com sucesso!',
                'redirect': url_for('login')
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Erro no servidor: ' + str(e)
            }), 500
    
    return render_template('cadastro.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)