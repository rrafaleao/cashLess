from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    @classmethod
    def create_user(cls, nome, email, senha):
        novo_usuario = cls(nome=nome, email=email)
        novo_usuario.set_senha(senha)  # Gerar o hash da senha
        db.session.add(novo_usuario)
        db.session.commit()
        return novo_usuario

    
    @classmethod
    def listar_usuarios(cls):
        return cls.query.all()
    
    def set_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha, senha)

class Transacao(db.Model):
    __tablename__ = 'transacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    forma_pagamento = db.Column(db.String(100), nullable=False)
    data = db.Column(db.DateTime, default=func.utcnow)

class Objetivo(db.Model):
    __tablename__ = 'objetivos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    valor_recebido = db.Column(db.Float, nullable=False)
    data_limite = db.Column(db.DateTime, default=func.utcnow)  