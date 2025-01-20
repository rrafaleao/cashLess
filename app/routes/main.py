from flask import Blueprint, render_template, flash, redirect, url_for, session, request, send_from_directory
from models import *
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect('login')
    # Busca somente as 2 últimas transações
    transacoes = Transacao.query.filter_by(id_usuario=session['user_id']).order_by(Transacao.id.desc()).limit(2).all()
    total_ganhos = db.session.query(func.sum(Transacao.valor)).filter_by(id_usuario=session['user_id'], tipo_transacao='ganho').scalar() or 0.0
    total_gastos = db.session.query(func.sum(Transacao.valor)).filter_by(id_usuario=session['user_id'], tipo_transacao='gasto').scalar() or 0.0
    saldo = total_ganhos - total_gastos
    max_valor = max(total_ganhos, total_gastos, 1)
    grafico_ganhos = (total_ganhos / max_valor) * 100
    grafico_gastos = (total_gastos / max_valor) * 100
    objetivos = Objetivo.query.filter_by(id_usuario=session['user_id']).order_by(Objetivo.data_limite).limit(1).all()

    return render_template('/main/index.html',
                           transacoes=transacoes,
                           total_ganhos=f"{total_ganhos:,.2f}",
                           total_gastos=f"{total_gastos:,.2f}",
                           saldo="{:.2f}".format(saldo),
                           grafico_ganhos=grafico_ganhos,
                           grafico_gastos=grafico_gastos,
                           objetivos=objetivos)


@main.route('/transactions', methods=['POST', 'GET'])
def transactions():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Você precisa estar logado para adicionar uma transação.', 'error')
            return redirect(url_for('auth.login'))

        id_usuario = session['user_id']
        descricao = request.form['descricao']
        valor = float(request.form['valor'])
        categoria = request.form['categoria']
        forma_pagamento = request.form['forma_pagamento']
        data = request.form['data']
        tipo_transacao = request.form['tipo_transacao']
        
        # Verificar se é parcelado
        has_parcelas = 'has_parcelas' in request.form
        
        if has_parcelas and 'num_parcelas' in request.form:
            num_parcelas = int(request.form['num_parcelas'])
            if num_parcelas > 1:
                # Criar transação parcelada
                Transacao.criar_transacao_parcelada(
                    descricao=descricao,
                    valor_total=valor,
                    categoria=categoria,
                    forma_pagamento=forma_pagamento,
                    data_inicial=data,
                    id_usuario=id_usuario,
                    tipo_transacao=tipo_transacao,
                    num_parcelas=num_parcelas
                )
                flash('Transação parcelada criada com sucesso!', 'success')
                return redirect(url_for('main.transactions'))
        
        # Se não for parcelado ou se houver algum erro, criar transação normal
        Transacao.create_transacao(
            descricao=descricao,
            valor=valor,
            categoria=categoria,
            forma_pagamento=forma_pagamento,
            data=data,
            id_usuario=id_usuario,
            tipo_transacao=tipo_transacao
        )
        flash('Transação criada com sucesso!', 'success')
        return redirect(url_for('main.transactions'))
        
    return render_template('/main/add_transactions.html')

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
        
        # Busca o usuário atual
        usuario = Usuario.query.get(session['user_id'])
        
        # Verifica se tem saldo suficiente para o valor inicial
        if valor_inicial > 0:
            if usuario.saldo < valor_inicial:
                flash('Saldo insuficiente para o valor inicial! Seu saldo atual é R$ {:.2f}'.format(usuario.saldo), 'error')
                return redirect(url_for('main.goals'))
            
            # Cria uma transação para o valor inicial
            nova_transacao = Transacao(
                descricao=f"Valor inicial para objetivo: {nome}",
                valor=valor_inicial,
                categoria="Objetivos",
                forma_pagamento="Outro",
                data=datetime.now().strftime('%Y-%m-%d'),
                tipo_transacao="gasto",
                id_usuario=session['user_id']
            )
            db.session.add(nova_transacao)
        
        novo_objetivo = Objetivo(
            nome=nome,
            valor_total=valor_total,
            valor_recebido=valor_inicial,
            data_limite=data_limite,
            id_usuario=session['user_id']
        )
        
        db.session.add(novo_objetivo)
        
        # Atualiza o saldo do usuário se houver valor inicial
        if valor_inicial > 0:
            usuario.atualizar_saldo()
            
        db.session.commit()
        flash('Objetivo criado com sucesso!', 'success')
        return redirect(url_for('main.goals'))
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao criar objetivo. Por favor, tente novamente.', 'error')
        return redirect(url_for('main.goals'))

@main.route('/goals/<int:id>/add', methods=['POST'])
def add_value(id):
    try:
        objetivo = Objetivo.query.get_or_404(id)
        
        # Verifica se o objetivo pertence ao usuário atual
        if objetivo.id_usuario != session['user_id']:
            flash('Operação não permitida.', 'error')
            return redirect(url_for('main.goals'))
            
        valor_adicional = float(request.form.get('valor'))
        
        # Busca o usuário atual
        usuario = Usuario.query.get(session['user_id'])
        
        # Verifica se o usuário tem saldo suficiente
        if usuario.saldo < valor_adicional:
            flash('Saldo insuficiente! Seu saldo atual é R$ {:.2f}'.format(usuario.saldo), 'error')
            return redirect(url_for('main.goals'))
        
        # Adiciona o valor ao objetivo
        objetivo.valor_recebido += valor_adicional
        
        # Cria uma nova transação
        nova_transacao = Transacao(
            descricao=f"Valor adicionado ao objetivo: {objetivo.nome}",
            valor=valor_adicional,
            categoria="Objetivos",
            forma_pagamento="Outro",
            data=datetime.now().strftime('%Y-%m-%d'),
            tipo_transacao="gasto",
            id_usuario=session['user_id']
        )
        
        # Adiciona a transação ao banco de dados
        db.session.add(nova_transacao)
        
        # Atualiza o saldo do usuário
        usuario.atualizar_saldo()
        
        db.session.commit()
        flash('Valor adicionado com sucesso!', 'success')
        return redirect(url_for('main.goals'))
        
    except Exception as e:
        db.session.rollback()
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


@main.route('/financial-control')
def controller():
    usuario_atual = Usuario.query.get(session['user_id'])
    
    if not usuario_atual:
        return redirect(url_for('login'))
    
    # Obter todas as transações do usuário
    transacoes = Transacao.query.filter_by(id_usuario=usuario_atual.id).all()
    
    # Calcular totais
    total_ganho = sum(t.valor for t in transacoes if t.tipo_transacao == 'ganho')
    total_gasto = sum(t.valor for t in transacoes if t.tipo_transacao == 'gasto')
    saldo = total_ganho - total_gasto
    
    # Converter transações para dicionário para uso no JavaScript
    transacoes_dict = [{
        'valor': float(t.valor),
        'categoria': t.categoria,
        'tipo_transacao': t.tipo_transacao
    } for t in transacoes]
    
    return render_template('/main/controller.html',
                         transacoes=transacoes_dict,
                         total_ganho="{:.2f}".format(total_ganho),
                         total_gasto="{:.2f}".format(total_gasto),
                         saldo="{:.2f}".format(saldo))
