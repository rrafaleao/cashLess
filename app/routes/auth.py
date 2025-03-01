from flask import Blueprint, render_template, flash, redirect, url_for, session, request, send_from_directory
from models import *
import logging 

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        nome = request.form['username']
        email = request.form['email']
        senha = request.form['password']

        # Verificar se o usuário já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return redirect(url_for('auth.register'))

        # Criar o novo usuário (a função create_user já faz o hash da senha)
        Usuario.create_user(nome=nome, email=email, senha=senha)

        return redirect(url_for('auth.login'))

    return render_template('/auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            senha = request.form.get('password')  
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and usuario.check_senha(senha):
                session['user_id'] = usuario.id
                return redirect(url_for('main.index'))  # Redireciona para a rota principal
            else:
                return redirect(url_for('auth.login'))
        
        except Exception as e:
            return redirect(url_for('auth.login'))
     
    return render_template('/auth/login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))