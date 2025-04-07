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
from app import config


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
    
    # Busca todas as inscrições do usuário
    inscricoes = Inscricao.query.filter_by(usuario_id=current_user.id).all()
    eventos_inscritos = {inscricao.evento_id for inscricao in inscricoes}
    
    # Busca todos os eventos
    todos_eventos = Evento.query.all()
    
    # Busca certificados disponíveis
    certificados_disponiveis = {
        cert.evento_id for cert in Certificado.query.filter_by(usuario_id=current_user.id).all()
    }
    
    # Separa os eventos em ativos e encerrados
    eventos_ativos = []
    eventos_encerrados = []
    agora = datetime.now()
    
    for evento in todos_eventos:
        # Adiciona informação se o usuário está inscrito e tem certificado
        evento.inscrito = evento.id in eventos_inscritos
        evento.certificado_disponivel = evento.id in certificados_disponiveis
        
        if evento.data_hora > agora:
            eventos_ativos.append(evento)
        else:
            eventos_encerrados.append(evento)
    
    # Ordena os eventos por data
    eventos_ativos.sort(key=lambda x: x.data_hora)
    eventos_encerrados.sort(key=lambda x: x.data_hora, reverse=True)
    
    # Conta certificados disponíveis
    certificados = Certificado.query.filter_by(usuario_id=current_user.id).count()
    
    return render_template('telespectador_dashboard.html',
                           eventos_ativos=eventos_ativos,
                           eventos_encerrados=eventos_encerrados,
                           total_eventos=len(inscricoes),
                           certificados=certificados)

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
@app.route('/evento/<int:evento_id>/inscrever', methods=['GET', 'POST'])
@login_required
def inscrever_evento(evento_id):
    if current_user.tipo != 'telespectador':
        flash('Apenas telespectadores podem se inscrever em eventos', 'error')
        return redirect(url_for('index'))

    try:
        evento = Evento.query.get_or_404(evento_id)
        
        # Verifica se já está inscrito
        inscricao_existente = Inscricao.query.filter_by(
            usuario_id=current_user.id,
            evento_id=evento_id
        ).first()
        
        if inscricao_existente:
            flash('Você já está inscrito neste evento', 'info')
            return redirect(url_for('telespectador_dashboard'))
        
        # Verifica se há vagas disponíveis usando uma query otimizada
        total_inscritos = db.session.query(db.func.count(Inscricao.id))\
            .filter_by(evento_id=evento_id).scalar()
            
        if total_inscritos >= evento.capacidade:
            flash(f'Evento já está com capacidade máxima ({evento.capacidade} vagas)', 'error')
            return redirect(url_for('telespectador_dashboard'))
        
        # Se for GET, apenas mostra a página de confirmação
        if request.method == 'GET':
            return render_template('confirmar_inscricao.html', evento=evento)
        
        # Se for POST, realiza a inscrição
        nova_inscricao = Inscricao(
            usuario_id=current_user.id,
            evento_id=evento_id,
            status='confirmado'
        )
        
        db.session.add(nova_inscricao)
        db.session.commit()
        
        vagas_restantes = evento.capacidade - (total_inscritos + 1)
        flash(f'Inscrição realizada com sucesso! Restam {vagas_restantes} vagas.', 'success')
        
        # Gera o ingresso após a inscrição
        return redirect(url_for('gerar_ingresso', inscricao_id=nova_inscricao.id))
        
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
@app.route('/evento/<int:evento_id>/cancelar-inscricao', methods=['GET', 'POST'])
@login_required
def cancelar_inscricao(evento_id):
    try:
        # Busca a inscrição
        inscricao = Inscricao.query.filter_by(
            usuario_id=current_user.id,
            evento_id=evento_id
        ).first()

        if not inscricao:
            flash('Inscrição não encontrada', 'error')
            return redirect(url_for('telespectador_dashboard'))

        # Busca o evento
        evento = Evento.query.get_or_404(evento_id)

        # Se for GET, mostra a página de confirmação
        if request.method == 'GET':
            return render_template('confirmar_cancelamento.html', evento=evento)

        # Se for POST, cancela a inscrição
        db.session.delete(inscricao)
        db.session.commit()

        flash('Inscrição cancelada com sucesso', 'success')
        return redirect(url_for('telespectador_dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar inscrição: {str(e)}', 'error')
        return redirect(url_for('telespectador_dashboard'))

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

    # Criar PDF em modo retrato
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Define as cores do tema
    cor_principal = (41, 128, 185)  # Azul
    cor_secundaria = (243, 156, 18)  # Dourado
    cor_texto = (44, 62, 80)  # Azul escuro
    cor_cinza = (189, 195, 199)  # Cinza claro para linhas
    
    # Adiciona uma borda decorativa na página
    pdf.set_draw_color(*cor_principal)
    pdf.set_line_width(1)
    pdf.rect(10, 10, 190, 277)
    
    # Adiciona elementos decorativos nos cantos
    pdf.set_fill_color(*cor_secundaria)
    tamanho_canto = 8
    pdf.rect(10, 10, tamanho_canto, tamanho_canto, 'F')  # Superior esquerdo
    pdf.rect(192, 10, tamanho_canto, tamanho_canto, 'F')  # Superior direito
    pdf.rect(10, 279, tamanho_canto, tamanho_canto, 'F')  # Inferior esquerdo
    pdf.rect(192, 279, tamanho_canto, tamanho_canto, 'F')  # Inferior direito
    
    # Título
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(*cor_principal)
    pdf.cell(0, 20, 'LISTA DE PRESENÇA', 0, 1, 'C')
    
    # Nome do evento
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(*cor_secundaria)
    pdf.cell(0, 10, evento.nome, 0, 1, 'C')
    pdf.ln(5)
    
    # Informações do evento em grid com estilo moderno
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(*cor_texto)
    
    # Box de informações do evento
    info_x = 20
    info_y = pdf.get_y()
    info_width = 170
    info_height = 35
    
    # Desenha um retângulo suave para as informações
    pdf.set_fill_color(245, 247, 250)  # Azul muito claro
    pdf.rect(info_x, info_y, info_width, info_height, 'F')
    
    # Informações do evento com ícones
    pdf.set_xy(info_x + 5, info_y + 6)
    pdf.cell(25, 8, 'Data:', 0)
    pdf.cell(40, 8, evento.data_hora.strftime('%d/%m/%Y'), 0, 1)
    pdf.set_xy(info_x + 5, info_y + 14)
    pdf.cell(35, 8, 'Horário:', 0)
    pdf.cell(40, 8, evento.data_hora.strftime('%H:%M'), 0, 1)
    pdf.set_xy(info_x + 5, info_y + 22)
    pdf.cell(25, 8, 'Local:', 0)
    pdf.cell(0, 8, evento.local, 0)
    pdf.ln(20)
    
    # Cabeçalho da tabela com design moderno
    pdf.set_fill_color(*cor_principal)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    
    # Larguras das colunas ajustadas para retrato
    col_nome = 75
    col_email = 75
    col_assinatura = 30
    
    # Cabeçalho com altura maior e centralizado
    header_height = 12
    pdf.cell(col_nome, header_height, 'Nome do Participante', 1, 0, 'C', True)
    pdf.cell(col_email, header_height, 'E-mail', 1, 0, 'C', True)
    pdf.cell(col_assinatura, header_height, 'Assinatura', 1, 1, 'C', True)
    
    # Lista de participantes com design moderno
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(*cor_texto)
    
    altura_linha = 15  # Altura aumentada para espaço de assinatura
    for i, inscricao in enumerate(inscricoes):
        # Linhas zebradas com cores suaves
        if i % 2 == 0:
            pdf.set_fill_color(245, 247, 250)  # Azul muito claro
        else:
            pdf.set_fill_color(255, 255, 255)  # Branco
            
        fill = True  # Define o preenchimento para linhas zebradas
        pdf.cell(col_nome, altura_linha, inscricao.participante.nome, 1, 0, 'L', fill)
        pdf.cell(col_email, altura_linha, inscricao.participante.email, 1, 0, 'L', fill)
        pdf.cell(col_assinatura, altura_linha, '', 1, 1, 'C', fill)  # Espaço para assinatura
    
    # Adicionar rodapé com informações
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128, 128, 128)  # Cinza
    pdf.cell(0, 5, f'Documento gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}', 0, 1, 'R')
    pdf.cell(0, 5, f'Total de participantes: {len(inscricoes)}', 0, 1, 'R')

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
            # Cria o certificado com orientação paisagem
            pdf = FPDF('L', 'mm', 'A4')
            pdf.add_page()
            
            # Define as cores do tema (tons de azul e dourado)
            cor_principal = (41, 128, 185)  # Azul
            cor_secundaria = (243, 156, 18)  # Dourado
            cor_texto = (44, 62, 80)  # Azul escuro
            
            # Adiciona uma borda decorativa
            pdf.set_draw_color(*cor_principal)
            pdf.set_line_width(2)
            pdf.rect(10, 10, 277, 190)
            
            # Adiciona elementos decorativos nos cantos
            pdf.set_fill_color(*cor_secundaria)
            pdf.rect(10, 10, 20, 20, 'F')
            pdf.rect(267, 10, 20, 20, 'F')
            pdf.rect(10, 180, 20, 20, 'F')
            pdf.rect(267, 180, 20, 20, 'F')
            
            # Título do certificado
            pdf.set_font('Arial', 'B', 40)
            pdf.set_text_color(*cor_principal)
            pdf.cell(0, 40, 'CERTIFICADO', 0, 1, 'C')
            
            # Texto principal
            pdf.set_font('Arial', '', 16)
            pdf.set_text_color(*cor_texto)
            pdf.cell(0, 10, 'Certificamos que', 0, 1, 'C')
            
            # Nome do participante
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 24)
            pdf.set_text_color(*cor_secundaria)
            pdf.cell(0, 15, current_user.nome, 0, 1, 'C')
            
            # Descrição do evento
            pdf.ln(5)
            pdf.set_font('Arial', '', 16)
            pdf.set_text_color(*cor_texto)
            pdf.cell(0, 10, 'participou do evento', 0, 1, 'C')
            
            # Nome do evento
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(*cor_principal)
            pdf.cell(0, 15, evento.nome, 0, 1, 'C')
            
            # Detalhes do evento
            pdf.ln(5)
            pdf.set_font('Arial', '', 14)
            pdf.set_text_color(*cor_texto)
            pdf.cell(0, 10, f'realizado em {evento.data_hora.strftime("%d/%m/%Y")}', 0, 1, 'C')
            pdf.cell(0, 10, f'no local {evento.local}', 0, 1, 'C')
            pdf.cell(0, 10, f'com carga horária total de {evento.carga_horaria} horas', 0, 1, 'C')
            
            # Assinatura
            pdf.ln(15)
            pdf.line(90, 160, 205, 160)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Organizador do Evento', 0, 1, 'C')
            
            # Código de verificação
            codigo = str(uuid.uuid4())
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(128, 128, 128)  # Cinza
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
    # Busca apenas eventos que ainda não aconteceram
    eventos = Evento.query.filter(Evento.data_hora > datetime.now()).order_by(Evento.data_hora).all()
    
    # Se o usuário está logado, verifica em quais eventos está inscrito
    eventos_inscritos = set()
    if current_user.is_authenticated:
        inscricoes = Inscricao.query.filter_by(usuario_id=current_user.id).all()
        eventos_inscritos = {inscricao.evento_id for inscricao in inscricoes}
    
    return render_template('todos_eventos.html', 
                           eventos=eventos,
                           eventos_inscritos=eventos_inscritos)

# Gerar ingresso
@app.route('/inscricao/<int:inscricao_id>/ingresso', methods=['GET'])
@login_required
def gerar_ingresso(inscricao_id):
    try:
        # Busca a inscrição
        inscricao = Inscricao.query.get_or_404(inscricao_id)
        
        # Verifica se o usuário é o dono da inscrição
        if inscricao.usuario_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Você não tem permissão para acessar este ingresso'
            }), 403

        # Busca o evento
        evento = inscricao.evento
        
        # Cria o PDF do ingresso em tamanho A4 (retrato)
        pdf = FPDF('P', 'cm', 'A4')  # P para orientação retrato
        pdf.add_page()
        
        # Define as cores do tema
        cor_principal = (41, 128, 185)  # Azul
        cor_secundaria = (243, 156, 18)  # Dourado
        cor_texto = (44, 62, 80)  # Azul escuro
        cor_fundo = (247, 247, 247)  # Cinza claro
        
        # Define as dimensões do ingresso (14 x 5 cm)
        pagina_largura = 21.0  # A4 largura
        pagina_altura = 29.7   # A4 altura
        ingresso_largura = 14.0  # Largura do ingresso
        ingresso_altura = 5.0   # Altura do ingresso
        
        # Define as margens
        margem_y = 2.0  # 2 cm do topo
        margem_x = (pagina_largura - ingresso_largura) / 2  # Centralizado horizontalmente
        
        # Adiciona fundo do ingresso
        pdf.set_fill_color(*cor_fundo)
        pdf.rect(margem_x, margem_y, ingresso_largura, ingresso_altura, 'F')
        
        # Adiciona uma borda decorativa
        pdf.set_draw_color(*cor_principal)
        pdf.set_line_width(0.05)  # 0.5mm
        pdf.rect(margem_x + 0.3, margem_y + 0.3, ingresso_largura - 0.6, ingresso_altura - 0.6)
        pdf.set_line_width(0.1)  # 1mm
        pdf.rect(margem_x, margem_y, ingresso_largura, ingresso_altura)
        
        # Divide o ingresso em duas seções
        secao_esquerda = 5  # 5 cm para a seção esquerda
        
        # Linha divisora vertical
        pdf.set_draw_color(*cor_secundaria)
        pdf.line(margem_x + secao_esquerda, margem_y + 0.5, margem_x + secao_esquerda, margem_y + ingresso_altura - 0.5)
        
        # Título do ingresso (seção esquerda)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*cor_principal)
        pdf.set_xy(margem_x, margem_y + 0.8)
        pdf.cell(secao_esquerda, 1, 'INGRESSO', 0, 1, 'C')
        
        # Nome do evento (seção esquerda)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*cor_secundaria)
        pdf.set_xy(margem_x, margem_y + 1.8)
        pdf.multi_cell(secao_esquerda, 0.8, evento.nome, 0, 'C')
        
        # Informações do evento (seção direita)
        info_x = margem_x + secao_esquerda + 0.5
        info_y = margem_y + 0.6
        espaco_linha = 1.2  # Aumentado para dar mais espaço entre os campos
        
        # Títulos e valores
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(*cor_texto)
        
        # Participante
        pdf.set_xy(info_x, info_y)
        pdf.cell(3, 0.4, 'Participante:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(info_x + 3, info_y)
        # Guarda a posição Y antes do multi_cell
        y_antes = pdf.get_y()
        # Usa multi_cell para nomes longos
        pdf.multi_cell(5.5, 0.4, current_user.nome, 0, 'L')
        # Pega a posição Y após o multi_cell
        y_depois = pdf.get_y()
        # Calcula o espaço usado pelo nome
        espaco_usado = y_depois - y_antes
        
        # Data - começa depois do nome com espaçamento fixo
        pdf.set_font('Arial', 'B', 10)
        pdf.set_xy(info_x, y_depois + 0.2)  # 2mm de espaço após o nome
        pdf.cell(3, 0.4, 'Data:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(info_x + 3, y_depois + 0.2)
        pdf.cell(5.5, 0.4, evento.data_hora.strftime('%d/%m/%Y'), 0, 1)
        
        # Local - começa depois da data
        pdf.set_font('Arial', 'B', 10)
        pdf.set_xy(info_x, y_depois + 0.2 + espaco_linha)
        pdf.cell(3, 0.4, 'Local:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(info_x + 3, y_depois + 0.2 + espaco_linha)
        # Guarda a posição Y antes do local
        y_antes = pdf.get_y()
        # Usa multi_cell para locais longos
        pdf.multi_cell(5.5, 0.4, evento.local, 0, 'L')
        # Pega a nova posição Y
        y_depois = pdf.get_y()
        
        # Horário - começa depois do local
        pdf.set_font('Arial', 'B', 10)
        pdf.set_xy(info_x, y_depois + 0.2)
        pdf.cell(3, 0.4, 'Horário:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(info_x + 3, y_depois + 0.2)
        pdf.cell(5.5, 0.4, evento.data_hora.strftime('%H:%M'), 0, 1)
        
        # Código de verificação
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(info_x, margem_y + ingresso_altura - 0.8)
        pdf.cell(0, 0.6, f'Código de verificação: {inscricao.id}', 0, 0, 'L')

        # Salva o PDF temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            pdf.output(temp_file.name)
            return send_file(
                temp_file.name,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'ingresso_{evento.nome}.pdf'
            )

    except Exception as e:
        app.logger.error(f"Erro ao gerar ingresso: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao gerar ingresso'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
