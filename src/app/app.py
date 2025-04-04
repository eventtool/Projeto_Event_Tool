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
@app.route('/palestrante/dashboard')
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


    return render_template('criar_evento.html')
    try:
        evento = Evento(
            nome=request.form.get('nome'),
            data=datetime.strptime(request.form.get('data'), '%Y-%m-%d').date(),
            horario=datetime.strptime(request.form.get('horario'), '%H:%M').time(),
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
        return redirect(url_for('criar_evento'))

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
        
        # Verifica se há vagas disponíveis
        total_inscritos = Inscricao.query.filter_by(evento_id=evento_id).count()
        if total_inscritos >= evento.capacidade:
            return jsonify({
                'success': False,
                'message': 'Evento já está com capacidade máxima'
            }), 400
        
        nova_inscricao = Inscricao(
            usuario_id=current_user.id,
            evento_id=evento_id,
            status='confirmado'
        )
        
        db.session.add(nova_inscricao)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Inscrição realizada com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao realizar inscrição: {str(e)}'
        }), 500

# API para listar eventos
@app.route('/api/eventos')
@login_required
def listar_eventos_api():
    try:
        eventos = Evento.query.all()
        eventos_data = []

        for evento in eventos:
            inscrito = False
            if current_user.tipo == 'telespectador':
                inscrito = any(i.usuario_id == current_user.id for i in evento.inscricoes)

            eventos_data.append({
                'id': evento.id,
                'nome': evento.nome,
                'descricao': evento.descricao,
                'data_hora': evento.data_hora.isoformat(),
                'local': evento.local,
                'capacidade': evento.capacidade,
                'inscricoes_count': len(evento.inscricoes),
                'inscrito': inscrito
            })

        return jsonify({
            'success': True,
            'eventos': eventos_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar eventos: {str(e)}'
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
    pdf = FPDF()
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
        # Registrar presença para todos os inscritos
        inscricoes = Inscricao.query.filter_by(evento_id=evento_id).all()
        for inscricao in inscricoes:
            # Verificar se já existe presença
            presenca = Presenca.query.filter_by(
                usuario_id=inscricao.usuario_id,
                evento_id=evento_id
            ).first()
            
            if not presenca:
                # Criar presença
                presenca = Presenca(
                    usuario_id=inscricao.usuario_id,
                    evento_id=evento_id
                )
                db.session.add(presenca)
        
        # Marcar evento como finalizado
        evento.status = 'finalizado'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento finalizado com sucesso e presenças registradas!'
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
    evento = Evento.query.get_or_404(evento_id)
    
    # Verificar se o evento está finalizado
    if evento.status != 'finalizado':
        return jsonify({
            'success': False,
            'message': 'O evento ainda não foi finalizado'
        }), 400

    # Verificar se o usuário está inscrito no evento
    inscricao = Inscricao.query.filter_by(
        usuario_id=current_user.id,
        evento_id=evento_id
    ).first()
    
    if not inscricao:
        return jsonify({
            'success': False,
            'message': 'Você não está inscrito neste evento'
        }), 400
    
    # Quando o evento é finalizado, automaticamente registra presença para todos os inscritos
    presenca = Presenca.query.filter_by(
        usuario_id=current_user.id,
        evento_id=evento_id
    ).first()
    
    if not presenca:
        # Criar presença automaticamente para eventos finalizados
        presenca = Presenca(
            usuario_id=current_user.id,
            evento_id=evento_id
        )
        db.session.add(presenca)
        db.session.commit()

    # Verificar se já existe um certificado
    certificado = Certificado.query.filter_by(
        usuario_id=current_user.id,
        evento_id=evento_id
    ).first()
    
    if not certificado:
        # Criar novo certificado
        certificado = Certificado(
            codigo=str(uuid.uuid4()),
            usuario_id=current_user.id,
            evento_id=evento_id
        )
        db.session.add(certificado)
        db.session.commit()

    # Gerar PDF do certificado
    pdf = FPDF('L', 'mm', 'A4')  # Landscape mode
    pdf.add_page()
    
    # Adicionar borda decorativa
    pdf.set_draw_color(0, 0, 128)  # Cor azul escuro para a borda
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    # Título
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(0, 0, 128)  # Azul escuro para o título
    pdf.cell(0, 40, 'CERTIFICADO', 0, 1, 'C')
    
    # Conteúdo
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(0, 0, 0)  # Voltar para texto preto
    
    # Texto principal
    texto_principal = f"""Certificamos que

{current_user.nome}

participou com êxito do evento

{evento.nome}

realizado em {evento.data_hora.strftime('%d de %B de %Y')},
no local {evento.local}, com carga horária total de {evento.carga_horaria} horas."""
    
    # Centralizar texto principal
    pdf.ln(10)
    for linha in texto_principal.split('\n'):
        if linha.strip() == current_user.nome:
            pdf.set_font('Arial', 'B', 20)  # Nome em negrito e maior
            pdf.cell(0, 10, linha, 0, 1, 'C')
            pdf.set_font('Arial', '', 16)  # Voltar ao estilo normal
        elif linha.strip() == evento.nome:
            pdf.set_font('Arial', 'B', 18)  # Nome do evento em negrito
            pdf.cell(0, 10, linha, 0, 1, 'C')
            pdf.set_font('Arial', '', 16)  # Voltar ao estilo normal
        else:
            pdf.cell(0, 10, linha, 0, 1, 'C')
    
    # Adicionar data de emissão
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    data_atual = datetime.now().strftime('%d de %B de %Y')
    pdf.cell(0, 10, f'Emitido em {data_atual}', 0, 1, 'C')
    
    # Adicionar assinatura do organizador
    pdf.ln(10)
    pdf.line(85, 160, 205, 160)  # Linha para assinatura
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, evento.organizador.nome_organizacao, 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Organizador do Evento', 0, 1, 'C')
    
    # Código de verificação
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(128, 128, 128)  # Cinza para o código
    pdf.cell(0, 10, f'Código de verificação: {certificado.codigo}', 0, 1, 'C')
    
    # Salvar PDF temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        pdf.output(temp_file.name)
        return send_file(
            temp_file.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'certificado_{evento.nome}.pdf'
        )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Apenas para inicialização; use migrações em produção.
    app.run(debug=True)
