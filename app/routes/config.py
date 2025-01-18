from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from models import db, Usuario, Transacao, Objetivo
from werkzeug.security import generate_password_hash

config = Blueprint('settings', __name__)

@config.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(session['user_id'])

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('config/settings.html', usuario=usuario)

@config.route('/settings/edit', methods=['POST', 'GET'])
def edit_user():
    """Altera as informações da conta do usuário."""
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')

        try:
            # Atualizar nome e email
            if nome:
                usuario.nome = nome
            if email:
                usuario.email = email

            # Verificar e atualizar senha
            if senha_atual and nova_senha:
                if usuario.check_senha(senha_atual):  # Usar o método definido no modelo
                    usuario.set_senha(nova_senha)
                else:
                    flash('Senha atual está incorreta.', 'danger')
                    return render_template('config/edit_user.html', usuario=usuario)

            # Commit das mudanças no banco de dados
            db.session.commit()
            flash('Informações alteradas com sucesso!', 'success')
        except Exception as e:
            flash('Ocorreu um erro ao atualizar as informações: {}'.format(str(e)), 'danger')
            return render_template('config/edit_user.html', usuario=usuario)

    return render_template('config/edit_user.html', usuario=usuario)


@config.route('/settings/delete/transactions', methods=['POST', 'GET'])
def apagar_transacoes():
    """Apaga todas as transações do usuário."""
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    Transacao.query.filter_by(id_usuario=usuario.id).delete()
    usuario.atualizar_saldo()
    db.session.commit()

    flash('Todas as transações foram apagadas com sucesso.', 'success')
    return redirect(url_for('settings.settings'))

@config.route('/settings/delete/account', methods=['POST', 'GET'])
def apagar_conta():
    """Apaga a conta do usuário e todas as suas transações."""
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    # Apagar transações associadas ao usuário
    Transacao.query.filter_by(id_usuario=usuario.id).delete()

    Objetivo.query.filter_by(id_usuario=usuario.id).delete()
    # Apagar o usuário
    db.session.delete(usuario)
    db.session.commit()

    session.pop('user_id', None)  # Remover usuário da sessão

    flash('Sua conta foi apagada com sucesso.', 'success')
    return redirect(url_for('auth.login'))
