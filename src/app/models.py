from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  # Importação corrigida
from datetime import datetime, timezone

db = SQLAlchemy()

# Tabela de Usuário
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    celular = db.Column(db.String(20), nullable=True)
    tipo = db.Column(db.String(20), nullable=False)

    # Relacionamentos
    perfil = db.relationship('Perfil', back_populates='usuario', uselist=False)
    eventos_criados = db.relationship('Evento', back_populates='organizador')
    inscricoes = db.relationship('Inscricao', back_populates='participante')
    presencas = db.relationship('Presenca', back_populates='participante')
    certificados = db.relationship('Certificado', back_populates='usuario')

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Perfil(db.Model):
    __tablename__ = 'perfis'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)
    nome_completo = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date)
    biografia = db.Column(db.Text)
    telefone = db.Column(db.String(20))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    site = db.Column(db.String(200))
    avatar = db.Column(db.String(200))
    
    usuario = db.relationship('Usuario', back_populates='perfil')

    def __repr__(self):
        return f'<Perfil {self.nome_completo}>'

class Evento(db.Model):
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(255), nullable=False)
    capacidade = db.Column(db.Integer, nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    organizador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    organizador = db.relationship('Usuario', back_populates='eventos_criados')
    inscricoes = db.relationship('Inscricao', back_populates='evento', lazy=True)
    certificados = db.relationship('Certificado', back_populates='evento', lazy=True)
    presencas = db.relationship('Presenca', back_populates='evento', lazy=True)

    @property
    def vagas_disponiveis(self):
        return self.capacidade - len(self.inscricoes)

    def __repr__(self):
        return f'<Evento {self.nome}>'

class Inscricao(db.Model):
    __tablename__ = 'inscricoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    data_inscricao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='pendente')
    
    participante = db.relationship('Usuario', back_populates='inscricoes')
    evento = db.relationship('Evento', back_populates='inscricoes')
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'evento_id', name='unique_inscricao'),
    )

    def __repr__(self):
        return f'<Inscricao {self.usuario_id} no evento {self.evento_id}>'

class Presenca(db.Model):
    __tablename__ = 'presencas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    participante = db.relationship('Usuario', back_populates='presencas')
    evento = db.relationship('Evento', back_populates='presencas')
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'evento_id', name='unique_presenca'),
    )

    def __repr__(self):
        return f'<Presenca {self.usuario_id} no evento {self.evento_id}>'

class Certificado(db.Model):
    __tablename__ = 'certificados'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    data_emissao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    nome_evento = db.Column(db.String(100), nullable=False)
    data_evento = db.Column(db.Date, nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    nome_participante = db.Column(db.String(100), nullable=False)
    
    usuario = db.relationship('Usuario', back_populates='certificados')
    evento = db.relationship('Evento', back_populates='certificados')

    def __repr__(self):
        return f'<Certificado {self.codigo}>'