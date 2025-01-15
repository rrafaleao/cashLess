from flask import Blueprint, render_template, flash, redirect, url_for, session, request, send_from_directory
from models import *
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    usuarios = Usuario.listar_usuarios()
    objetivos = Objetivo.query.filter_by(id_usuario=session['user_id']).all()
    transacoes = Transacao.query.filter_by(id_usuario=session['user_id']) .order_by(Transacao.data.desc()) .limit(2) .all()
    return render_template('/main/index.html', usuarios=usuarios, objetivos=objetivos, transacoes=transacoes)

@main.route('/transactions', methods=['POST', 'GET'])
def transactions():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Você precisa estar logado para adicionar uma transação.', 'error')
            return redirect(url_for('auth.login'))

        id_usuario = session['user_id']
        descricao = request.form['descricao']
        valor = request.form['valor']
        categoria = request.form['categoria']
        forma_pagamento = request.form['forma_pagamento']
        data = request.form['data']
        tipo_transacao = request.form['tipo_transacao']  # Novo campo capturado

        Transacao.create_transacao(
            descricao=descricao,
            valor=valor,
            categoria=categoria,
            forma_pagamento=forma_pagamento,
            data=data,
            id_usuario=id_usuario,
            tipo_transacao=tipo_transacao
        )
        return redirect(url_for('main.transactions'))
    return render_template('/main/transactions.html')

@main.route('/extract', methods=['GET'])
def extract():
    transacoes = Transacao.query.filter_by(
        id_usuario=session['user_id']
    ).order_by(
        Transacao.data.desc()
    ).all()

    # Calcula totais
    total_entradas = sum(t.valor for t in transacoes if t.tipo_transacao == 'entrada')
    total_saidas = sum(t.valor for t in transacoes if t.tipo_transacao == 'saida')
    saldo = total_entradas - total_saidas

    # Formata os valores para exibição
    total_entradas = "{:.2f}".format(total_entradas)
    total_saidas = "{:.2f}".format(total_saidas)
    saldo = "{:.2f}".format(saldo)

    # Organiza as transações por data
    for transacao in transacoes:
        # Converte a string da data para objeto datetime
        data_obj = datetime.strptime(transacao.data, '%Y-%m-%d')
        # Reformata para exibição
        transacao.data = data_obj.strftime('%d/%m/%Y')

    return render_template('/main/extract.html',transacoes=transacoes,total_entradas=total_entradas,total_saidas=total_saidas,saldo=saldo)


@main.route('/goals')
def goals():
    objetivos = Objetivo.query.filter_by(id_usuario=session['user_id']).all()
    return render_template('/main/goals.html', objetivos=objetivos)

@main.route('/goals/create', methods=['POST'])
def create():
    try:
        nome = request.form.get('nome')
        valor_total = float(request.form.get('valor_total'))
        valor_inicial = float(request.form.get('valor_inicial', 0))
        data_limite = datetime.strptime(request.form.get('data_limite'), '%Y-%m-%d')
        
        novo_objetivo = Objetivo(
            nome=nome,
            valor_total=valor_total,
            valor_recebido=valor_inicial,
            data_limite=data_limite,
            id_usuario=session['user_id']
        )
        
        db.session.add(novo_objetivo)
        db.session.commit()
        
        return redirect(url_for('main.goals'))
    except Exception as e:
        return redirect(url_for('main.goals'))

@main.route('/goals/<int:id>/add', methods=['POST'])
def add_value(id):  # Inclua o parâmetro id aqui
    try:
        objetivo = Objetivo.query.get_or_404(id)
        
        # Verifica se o objetivo pertence ao usuário atual
        if objetivo.id_usuario != session['user_id']:
            flash('Operação não permitida.', 'error')
            return redirect(url_for('main.goals'))
            
        valor_adicional = float(request.form.get('valor'))
        objetivo.valor_recebido += valor_adicional
        
        db.session.commit()
        flash('Valor adicionado com sucesso!', 'success')
        return redirect(url_for('main.goals'))
    except Exception as e:
        flash('Erro ao adicionar valor. Por favor, tente novamente.', 'error')
        return redirect(url_for('main.goals'))
    
@main.route('/goals/delete/<int:goal_id>', methods=['GET', 'POST'])
def delete_goal(goal_id):
    objetivo = Objetivo.query.get(goal_id)
    if objetivo:
        db.session.delete(objetivo)
        db.session.commit()

    return redirect(url_for('main.goals'))

@main.route('/goals/edit/<int:goal_id>', methods=['POST'])
def edit_goal(goal_id):
    objetivo = Objetivo.query.get(goal_id)
    
    if objetivo:
        objetivo.nome = request.form['nome']
        objetivo.valor_total = float(request.form['valor_total'])
        objetivo.data_limite = datetime.strptime(request.form['data_limite'], '%Y-%m-%d')
        
        db.session.commit()

    return redirect(url_for('main.goals'))