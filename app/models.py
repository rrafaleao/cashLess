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
    saldo = db.Column(db.Float, default=0.0)
    total_ganho = db.Column(db.Float, default=0.0)
    total_gasto = db.Column(db.Float, default=0.0)

    def atualizar_saldo(self):
        """Recalcula o saldo total do usuário com base nas transações existentes."""
        ganhos = sum(transacao.valor for transacao in self.transacoes if transacao.tipo_transacao == 'ganho')
        gastos = sum(transacao.valor for transacao in self.transacoes if transacao.tipo_transacao == 'gasto')
        self.total_ganho = ganhos
        self.total_gasto = gastos
        self.saldo = ganhos - gastos
        db.session.commit()

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
    data = db.Column(db.String(100), nullable=False)
    tipo_transacao = db.Column(db.String(10), nullable=False)  # Novo campo para gasto/ganho
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship('Usuario', backref='transacoes')

    @classmethod
    def create_transacao(cls, descricao, valor, categoria, forma_pagamento, data, id_usuario, tipo_transacao):
        nova_transacao = cls(
            descricao=descricao,
            valor=valor,
            categoria=categoria,
            forma_pagamento=forma_pagamento,
            data=data,
            id_usuario=id_usuario,
            tipo_transacao=tipo_transacao  # Armazenar o tipo de transação
        )
        db.session.add(nova_transacao)
        db.session.commit()

        # Atualizar o saldo, total_ganho e total_gasto do usuário
        usuario = Usuario.query.get(id_usuario)
        if usuario:
            usuario.atualizar_saldo()
        return nova_transacao

    @classmethod
    def listar_transacao(cls):
        return cls.query.all()

class Objetivo(db.Model):
    __tablename__ = 'objetivos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    valor_recebido = db.Column(db.Float, nullable=False)
    data_limite = db.Column(db.DateTime, default=func.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship('Usuario', backref='objetivos')