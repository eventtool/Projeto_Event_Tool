from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False)  # 'telespectador' ou 'palestrante'
    data_nascimento = db.Column(db.Date)
    biografia = db.Column(db.Text)
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    site = db.Column(db.String(200))

    # Relacionamentos
    eventos_criados = db.relationship('Evento', backref='palestrante', lazy=True)
    certificados = db.relationship('Certificado', backref='usuario', lazy=True)
    presencas = db.relationship('Presenca', backref='usuario', lazy=True)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    vagas = db.Column(db.Integer, nullable=False)
    palestrante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    # Relacionamentos
    presencas = db.relationship('Presenca', backref='evento', lazy=True)
    certificados = db.relationship('Certificado', backref='evento', lazy=True)

class Certificado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_telespectador = db.Column(db.String(100), nullable=False)
    horas = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, nullable=False)  # Data de emissão do certificado
    hora = db.Column(db.Time, nullable=False)  # Hora de emissão do certificado
    data_evento = db.Column(db.Date, nullable=False)  # Data do evento
    hora_evento = db.Column(db.Time, nullable=False)  # Hora do evento
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Presenca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)