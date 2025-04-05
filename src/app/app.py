import os
from datetime import datetime, timedelta
from flask import (
    Flask, request, jsonify, render_template, redirect, url_for, flash, session,
    send_file
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_required, login_user, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from fpdf import FPDF
import config
from models import db, Usuario, Evento, Presenca, Inscricao, Certificado
from flask_migrate import Migrate
from urllib.parse import quote as url_quote
import uuid
import tempfile
from io import BytesIO


# Inicializa o Flask
app = Flask(__name__, static_folder='static')
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

# Inicializa o banco de dados e o Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)
config.DatabaseConfig.test_db_connection()

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Página de Login
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

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# Dashboard do Palestrante
@app.route('/palestrante_dashboard', methods=['GET'])
@login_required
def palestrante_dashboard():
    if current_user.tipo != 'palestrante':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))

    eventos = Evento.query.filter_by(criador_id=current_user.id).all()
    return render_template('palestrante_dashboard.html', eventos=eventos)

# Dashboard do Telespectador
@app.route('/telespectador/dashboard')
@login_required
def telespectador_dashboard():
    if current_user.tipo != 'telespectador':
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))
    
    inscricoes = Inscricao.query.filter_by(usuario_id=current_user.id).all()
    return render_template('telespectador_dashboard.html', inscricoes=inscricoes)

# Cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            data = request.get_json()
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
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erro no servidor: {str(e)}'}), 500

    return render_template('cadastro.html')

# Criar evento
@app.route('/criar-evento', methods=['GET', 'POST'])
@login_required
def criar_evento():
    if current_user.tipo != 'palestrante':
        flash('Apenas palestrantes podem criar eventos', 'error')
        return redirect(url_for('index'))

    # Se o usuário não tiver um registro de organizador, crie-o automaticamente
    if not current_user.organizador:
        from models import Organizador  # Caso ainda não tenha sido importado
        novo_organizador = Organizador(
            usuario_id=current_user.id,
            nome_organizacao=current_user.nome  # Nome do organizador é o mesmo do palestrante
        )
        db.session.add(novo_organizador)
        db.session.commit()
        # Atualiza o current_user para carregar o relacionamento, se necessário
        db.session.refresh(current_user)

    if request.method == 'POST':
        try:
            data = request.get_json()

            novo_evento = Evento(
                nome=data['nome'],
                descricao=data['descricao'],
                data_hora=datetime.strptime(f"{data['data']} {data['hora']}", '%Y-%m-%d %H:%M'),
                local=data['local'],
                capacidade=int(data['capacidade']),
                carga_horaria=int(data['carga_horaria']),
                criador_id=current_user.id,
                organizador_id=current_user.organizador.id  # Agora garantido que existe
            )

            db.session.add(novo_evento)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Evento criado com sucesso!',
                'redirect': url_for('palestrante_dashboard')
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Erro ao criar evento: {str(e)}'
            }), 500

    return render_template('criar_evento.html')

# Encerrar evento e gerar certificados
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

        # Gerando o certificado em PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
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

@app.route('/perfil')
@login_required
def perfil_usuario():
    usuario = current_user
    return render_template('perfil_usuario.html', usuario=usuario)

# Rota para inscrição em eventos
@app.route('/evento/<int:evento_id>/inscrever', methods=['POST'])
@login_required
def inscrever_evento(evento_id):
    if current_user.tipo != 'telespectador':
        return jsonify({
            'success': False,
            'message': 'Apenas telespectadores podem se inscrever em eventos'
        }), 403

    try:
        evento = Evento.query.get_or_404(evento_id)
        
        # Verifica se já está inscrito
        inscricao_existente = Inscricao.query.filter_by(
            usuario_id=current_user.id,
            evento_id=evento_id
        ).first()
        
        if inscricao_existente:
            return jsonify({
                'success': False,
                'message': 'Você já está inscrito neste evento'
            }), 400
        
        # Verifica se há vagas disponíveis usando uma query otimizada
        total_inscritos = db.session.query(db.func.count(Inscricao.id))\
            .filter_by(evento_id=evento_id).scalar()
            
        if total_inscritos >= evento.capacidade:
            return jsonify({
                'success': False,
                'message': f'Evento já está com capacidade máxima ({evento.capacidade} vagas)'
            }), 400
        
        nova_inscricao = Inscricao(
            usuario_id=current_user.id,
            evento_id=evento_id,
            status='confirmado'
        )
        
        db.session.add(nova_inscricao)
        db.session.commit()
        
        vagas_restantes = evento.capacidade - (total_inscritos + 1)
        
        return jsonify({
            'success': True,
            'message': f'Inscrição realizada com sucesso! Restam {vagas_restantes} vagas.',
            'vagas_restantes': vagas_restantes
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao realizar inscrição: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao realizar inscrição: {str(e)}'
        }), 500

# API para listar eventos
@app.route('/api/eventos')
def get_eventos():
    try:
        eventos = Evento.query.all()
        eventos_data = []
        
        for evento in eventos:
            # Check if user is authenticated before checking inscription
            inscrito = False
            if current_user.is_authenticated:
                inscrito = Inscricao.query.filter_by(
                    usuario_id=current_user.id,
                    evento_id=evento.id
                ).first() is not None
            
            # Format date properly
            data_hora = evento.data_hora.isoformat() if evento.data_hora else None
            
            eventos_data.append({
                'id': evento.id,
                'nome': evento.nome,
                'descricao': evento.descricao,
                'data_hora': data_hora,
                'local': evento.local,
                'capacidade': evento.capacidade,
                'inscricoes_count': len(evento.inscricoes) if evento.inscricoes else 0,
                'status': evento.status if hasattr(evento, 'status') else 'ativo',
                'inscrito': inscrito
            })
            
        return jsonify({
            'success': True,
            'eventos': eventos_data
        })
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error in get_eventos: {str(e)}")
        return jsonify({
            'success': False,
            'message': "Erro ao carregar eventos: " + str(e)
        }), 500

# Rota para cancelar inscrição em evento
@app.route('/evento/<int:evento_id>/cancelar-inscricao', methods=['POST'])
@login_required
def cancelar_inscricao(evento_id):
    try:
        inscricao = Inscricao.query.filter_by(
            usuario_id=current_user.id,
            evento_id=evento_id
        ).first()

        if not inscricao:
            return jsonify({
                'success': False,
                'message': 'Inscrição não encontrada'
            }), 404

        db.session.delete(inscricao)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Inscrição cancelada com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao cancelar inscrição: {str(e)}'
        }), 500

# Rodar o aplicativo Flask
# Gerar lista de presença em PDF
@app.route('/evento/<int:evento_id>/lista-presenca', methods=['GET'])
@login_required
def gerar_lista_presenca(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    
    # Verificar se o usuário é o organizador do evento
    if evento.organizador.usuario_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'Apenas o organizador pode gerar a lista de presença'
        }), 403

    # Buscar todas as inscrições do evento
    inscricoes = Inscricao.query.filter_by(evento_id=evento_id).all()

    # Criar PDF
    pdf = FPDF('L', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Título
    pdf.cell(0, 10, f'Lista de Presença - {evento.nome}', 0, 1, 'C')
    pdf.ln(10)
    
    # Informações do evento
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Data: {evento.data_hora.strftime("%d/%m/%Y")}', 0, 1)
    pdf.cell(0, 10, f'Horário: {evento.data_hora.strftime("%H:%M")}', 0, 1)
    pdf.cell(0, 10, f'Local: {evento.local}', 0, 1)
    pdf.ln(10)
    
    # Cabeçalho da tabela
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Nome', 1)
    pdf.cell(70, 10, 'Email', 1)
    pdf.cell(40, 10, 'Assinatura', 1)
    pdf.ln()
    
    # Lista de participantes
    pdf.set_font('Arial', '', 12)
    for inscricao in inscricoes:
        pdf.cell(80, 10, inscricao.participante.nome, 1)
        pdf.cell(70, 10, inscricao.participante.email, 1)
        pdf.cell(40, 10, '', 1)  # Espaço para assinatura
        pdf.ln()

    # Salvar PDF temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        pdf.output(temp_file.name)
        return send_file(
            temp_file.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'lista_presenca_{evento.nome}.pdf'
        )

# Marcar evento como finalizado
@app.route('/evento/<int:evento_id>/finalizar', methods=['POST'])
@login_required
def finalizar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    
    # Verificar se o usuário é o organizador do evento
    if evento.organizador.usuario_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'Apenas o organizador pode finalizar o evento'
        }), 403

    try:
        # Marcar evento como finalizado
        evento.status = 'finalizado'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento finalizado com sucesso!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao finalizar evento: {str(e)}'
        }), 500

# Gerar certificado
@app.route('/evento/<int:evento_id>/certificado', methods=['GET'])
@login_required
def gerar_certificado(evento_id):
    try:
        # Busca o evento
        evento = Evento.query.get_or_404(evento_id)
        
        # Verifica se o evento foi finalizado
        if evento.status != 'finalizado':
            return jsonify({
                'success': False,
                'message': 'O evento ainda não foi finalizado'
            }), 400

        # Verifica se o usuário está inscrito
        inscricao = Inscricao.query.filter_by(
            usuario_id=current_user.id,
            evento_id=evento_id
        ).first()
        
        if not inscricao:
            return jsonify({
                'success': False,
                'message': 'Você não está inscrito neste evento'
            }), 400

        # Cria um arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Cria o certificado
            pdf = FPDF('L', 'mm', 'A4')
            pdf.add_page()
            
            # Configurações de fonte e cores
            pdf.set_font('Arial', 'B', 30)
            pdf.set_text_color(0, 0, 128)  # Azul escuro
            pdf.cell(0, 30, 'CERTIFICADO', 0, 1, 'C')
            
            pdf.set_font('Arial', '', 16)
            pdf.set_text_color(0, 0, 0)  # Preto
            
            texto = f"""
            Certificamos que

            {current_user.nome}

            participou do evento

            {evento.nome}

            realizado em {evento.data_hora.strftime('%d/%m/%Y')},
            no local {evento.local}, com carga horária total de {evento.carga_horaria} horas.
            """
            
            for linha in texto.split('\n'):
                if linha.strip() == current_user.nome:
                    pdf.set_font('Arial', 'B', 20)
                    pdf.cell(0, 10, linha.strip(), 0, 1, 'C')
                    pdf.set_font('Arial', '', 16)
                else:
                    pdf.cell(0, 10, linha.strip(), 0, 1, 'C')

            # Adiciona assinatura e código de verificação
            pdf.ln(20)
            pdf.line(80, 180, 215, 180)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Organizador do Evento', 0, 1, 'C')
            
            # Código de verificação
            codigo = str(uuid.uuid4())
            pdf.set_font('Arial', '', 8)
            pdf.cell(0, 10, f'Código de verificação: {codigo}', 0, 1, 'C')

            # Salva o PDF no arquivo temporário
            pdf.output(temp_file.name)

            # Retorna o arquivo
            return send_file(
                temp_file.name,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'certificado_{evento.nome}.pdf'
            )

    except Exception as e:
        app.logger.error(f"Erro ao gerar certificado: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao gerar certificado'
        }), 500

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.tipo == 'palestrante':
        return redirect(url_for('palestrante_dashboard'))
    elif current_user.tipo == 'telespectador':
        return redirect(url_for('telespectador_dashboard'))
    else:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('index'))

@app.route('/eventos', methods=['GET'])
def todos_eventos():
    eventos = Evento.query.all()  # Busca todos os eventos no banco de dados
    return render_template('todos_eventos.html', eventos=eventos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
