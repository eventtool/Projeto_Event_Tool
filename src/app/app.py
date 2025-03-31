import os
from datetime import datetime, timedelta
from flask import (
    Flask, request, jsonify, render_template, redirect, url_for, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_required, login_user, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from fpdf import FPDF
import config
from models import db, Usuario, Evento, Presenca, Certificado  # Importação corrigida

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
config.DatabaseConfig.test_db_connection()

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            usuario = Usuario.query.filter_by(email=data['email']).first()

            if not usuario or not check_password_hash(usuario.senha, data['password']):
                return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401

            remember = data.get('remember', False)
            login_user(usuario, remember=remember)

            session.permanent = remember
            app.permanent_session_lifetime = timedelta(days=30) if remember else timedelta(hours=2)

            redirect_url = url_for('palestrante_dashboard') if usuario.tipo == 'palestrante' else url_for('telespectador_dashboard')
            return jsonify({'success': True, 'message': 'Login realizado com sucesso!', 'redirect': redirect_url})

        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro no servidor: {str(e)}'}), 500

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/palestrante/dashboard')
@login_required
def palestrante_dashboard():
    if current_user.tipo != 'palestrante':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))
    return render_template('palestrante_dashboard.html')

@app.route('/telespectador/dashboard')
@login_required
def telespectador_dashboard():
    if current_user.tipo != 'telespectador':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))
    return render_template('telespectador_dashboard.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print("Dados recebidos no cadastro:", data)

            if Usuario.query.filter_by(email=data.get('email')).first():
                return jsonify({'success': False, 'message': 'Este email já está cadastrado.'}), 400

            novo_usuario = Usuario(
                nome=data.get('nome'),
                email=data.get('email'),
                senha=generate_password_hash(data.get('senha')),
                celular=data.get('celular', ''),
                tipo=data.get('tipo_conta')
            )

            db.session.add(novo_usuario)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!', 'redirect': url_for('login')})
        
        except Exception as e:
            print("Erro durante o cadastro:", str(e))
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro no servidor: {str(e)}'}), 500

    return render_template('cadastro.html')

@app.route('/criar-evento', methods=['GET', 'POST'])
@login_required
def criar_evento():
    if current_user.tipo != 'palestrante':
        flash('Apenas palestrantes podem criar eventos', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            evento = Evento(
                nome=request.form.get('nome'),
                data=datetime.strptime(request.form.get('data'), '%Y-%m-%d').date(),
                hora=datetime.strptime(request.form.get('hora'), '%H:%M').time(),
                vagas=int(request.form.get('vagas')),
                palestrante_id=current_user.id
            )
            db.session.add(evento)
            db.session.commit()
            flash('Evento criado com sucesso!', 'success')
            return redirect(url_for('palestrante_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar evento: {str(e)}', 'error')
    
    return render_template('criar_evento.html')

@app.route('/palestrante/encerrar_evento/<int:evento_id>', methods=['POST'])
@login_required
def encerrar_evento(evento_id):
    if current_user.tipo != 'palestrante':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('palestrante_dashboard'))
    
    evento = Evento.query.get(evento_id)
    if not evento or evento.organizador_id != current_user.id:
        flash('Evento não encontrado ou acesso negado', 'error')
        return redirect(url_for('palestrante_dashboard'))
    
    certificado_folder = os.path.join('static', 'certificados', f'evento_{evento.id}')
    os.makedirs(certificado_folder, exist_ok=True)

    presencas = Presenca.query.filter_by(evento_id=evento.id).all()
    for presenca in presencas:
        usuario = Usuario.query.get(presenca.usuario_id)
        if not usuario:
            continue

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Certificado de Participação", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Certificamos que {usuario.nome} participou do evento {evento.nome}.", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
        pdf.output(os.path.join(certificado_folder, f"certificado_{usuario.id}.pdf"))
    
    flash("Certificados gerados com sucesso!", "success")
    return redirect(url_for('palestrante_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)