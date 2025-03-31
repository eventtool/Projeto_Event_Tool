import os
from datetime import datetime
from flask import (
    Flask, 
    request, 
    jsonify, 
    render_template, 
    redirect, 
    url_for, 
    flash, 
    session
 
)
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, 
    login_required, 
    login_user, 
    current_user,
    UserMixin
)
from werkzeug.security import check_password_hash

from dotenv import load_dotenv
import config
from models import Usuario

app = Flask(__name__)
app.secret_key = 'fe9gfef4efefg'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:MdggWwLuExAMuAIxWoPeVbbCPQgXtQxw@interchange.proxy.rlwy.net:12530/railway'
#usando PyMySQL
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MdggWwLuExAMuAIxWoPeVbbCPQgXtQxw@interchange.proxy.rlwy.net:12530/railway'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

# Testando a conexão com o banco
config.DatabaseConfig.test_db_connection()


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    celular = db.Column(db.String(20))
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
   

    # Métodos obrigatórios para Flask-Login
    @property
    def is_active(self):
        """Todos os usuários estão ativos por padrão"""
        return True

    @property
    def is_authenticated(self):
        """Retorna True se o usuário estiver autenticado"""
        return True

    @property
    def is_anonymous(self):
        """Retorna False para usuários regulares"""
        return False

    def get_id(self):
        """Retorna o ID do usuário como string"""
        return str(self.id)


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
            
            usuario = Usuario.query.filter_by(email=data['email']).first()
            
            if not usuario or usuario.senha != data['password']:
                return jsonify({
                    'success': False,
                    'message': 'Email ou senha incorretos'
                }), 401
            
            # Configuração da sessão persistente
            remember = data.get('remember', False)
            login_user(usuario, remember=remember)
            
            # Configuração da duração da sessão
            if remember:
                # Sessão persistente (30 dias)
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                # Sessão temporária (fecha ao sair do navegador)
                session.permanent = False
            
            # Determinar redirecionamento
            if usuario.tipo == 'palestrante':
                redirect_url = url_for('palestrante_dashboard')
            else:
                redirect_url = url_for('telespectador_dashboard')
            
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

@app.route('/palestrante/dashboard')
@login_required
def palestrante_dashboard():
    if current_user.tipo != 'palestrante':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('login'))
    return render_template('palestrante_dashboard.html')

@app.route('/telespectador/dashboard')
@login_required
def telespectador_dashboard():
    if current_user.tipo != 'telespectador':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('login'))
    return render_template('telespectador_dashboard.html')

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

@app.route('/criar-evento', methods=['GET', 'POST'])
@login_required
def criar_evento():
    if current_user.tipo != 'palestrante':
        flash('Apenas palestrantes podem criar eventos', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        
        try:
            
            flash('Evento criado com sucesso!', 'success')
            return redirect(url_for('palestrante_dashboard'))
        except Exception as e:
            flash(f'Erro ao criar evento: {str(e)}', 'error')
    
    return render_template('criar_evento.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)