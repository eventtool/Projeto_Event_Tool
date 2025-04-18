from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

# Inicialização do banco de dados
db = SQLAlchemy()

# Modelo de Usuário
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    celular = db.Column(db.String(20))
    tipo = db.Column(db.String(20), nullable=False)  # "palestrante" ou "telespectador"

    # Relacionamento com Perfil
    perfil = db.relationship('Perfil', back_populates='usuario', uselist=False, cascade="all, delete-orphan")
    eventos_criados = db.relationship('Evento', back_populates='criador', foreign_keys='Evento.criador_id')    
    inscricoes = db.relationship('Inscricao', back_populates='participante', cascade="all, delete")
    presencas = db.relationship('Presenca', back_populates='participante', cascade="all, delete")
    certificados = db.relationship('Certificado', back_populates='usuario', cascade="all, delete")
    organizador = db.relationship('Organizador', back_populates='usuario', uselist=False, cascade="all, delete")

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Modelo de Perfil
class Perfil(db.Model):
    __tablename__ = 'perfis'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    foto = db.Column(db.String(255), nullable=True)

    usuario = db.relationship('Usuario', back_populates='perfil')

    def __repr__(self):
        return f'<Perfil {self.id} - {self.usuario.nome}>'

# Modelo de Organizador
class Organizador(db.Model):
    __tablename__ = 'organizadores'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    nome_organizacao = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(20), unique=True, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)

    usuario = db.relationship('Usuario', back_populates='organizador')
    eventos = db.relationship('Evento', back_populates='organizador', cascade="all, delete")  # Changed from backref to back_populates

    def __repr__(self):
        return f'<Organizador {self.nome_organizacao}>'

# Modelo de Evento
class Evento(db.Model):
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_hora = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(100), nullable=False)
    capacidade = db.Column(db.Integer, nullable=False)  # Add if missing
    status = db.Column(db.String(20), default='aberto')  # Added status field
    carga_horaria = db.Column(db.Integer, nullable=False)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    organizador_id = db.Column(db.Integer, db.ForeignKey('organizadores.id'), nullable=False)
    
    # Relationships
    inscricoes = db.relationship('Inscricao', back_populates='evento', lazy=True)
    organizador = db.relationship('Organizador', back_populates='eventos')
    criador = db.relationship('Usuario', back_populates='eventos_criados', foreign_keys=[criador_id])
    presencas = db.relationship('Presenca', back_populates='evento', cascade="all, delete")
    certificados = db.relationship('Certificado', back_populates='evento', cascade="all, delete")
    
    @property
    def vagas_disponiveis(self):
        return self.capacidade - len(self.inscricoes)

    def __repr__(self):
        return f'<Evento {self.nome}>'

# Modelo de Inscrição
class Inscricao(db.Model):
    __tablename__ = 'inscricoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    data_inscricao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='pendente')

    participante = db.relationship('Usuario', back_populates='inscricoes')
    evento = db.relationship('Evento', back_populates='inscricoes')

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'evento_id', name='unique_inscricao'),
    )

    def __repr__(self):
        return f'<Inscricao Usuario {self.usuario_id} no Evento {self.evento_id}>'

# Modelo de Presença
class Presenca(db.Model):
    __tablename__ = 'presencas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    participante = db.relationship('Usuario', back_populates='presencas')
    evento = db.relationship('Evento', back_populates='presencas')

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'evento_id', name='unique_presenca'),
    )

    def __repr__(self):
        return f'<Presenca Usuario {self.usuario_id} no Evento {self.evento_id}>'

# Modelo de Certificado
class Certificado(db.Model):
    __tablename__ = 'certificados'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    data_emissao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship('Usuario', back_populates='certificados')
    evento = db.relationship('Evento', back_populates='certificados')

    def __repr__(self):
        return f'<Certificado {self.codigo}>'
