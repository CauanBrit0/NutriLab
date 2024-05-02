from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.models import User
from .utils import password_is_valid, email_html
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256

def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        

        return render(request, 'cadastro.html')

    if request.method =="POST":
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        
        
        if len(usuario.strip()) == 0 or len(email.strip()) == 0 or len(senha.strip()) == 0:
            messages.add_message(request,constants.ERROR,'Preencha os campos em branco.')
            return redirect('/auth/cadastro')
        
        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro/')

        if User.objects.filter(username = usuario):
            messages.add_message(request,constants.ERROR,'Usuário já existente.')
            return redirect('/auth/cadastro')

        
        usuarios = User.objects.create_user(username =  usuario, password = senha,  email= email , is_active = False)
        usuarios.save()

        token = sha256(f"{usuario}{email}".encode()).hexdigest()
        ativacao = Ativacao(token = token, user=usuarios)
        ativacao.save()


        path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
        email_html(path_template, 'Cadastro confirmado', [email,], username=usuario, link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")
        messages.add_message(request,constants.SUCCESS,'Cadastro realizado com Sucesso!')
        return redirect('/auth/cadastro/')


        
           

def login(request):
    if request.method =="GET":
        if request.user.is_authenticated:
            return redirect('/pacientes')
        return render(request,'login.html')
    
    if request.method =="POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        usuarios = auth.authenticate(username = usuario, password = senha)

        if usuarios:
            auth.login(request, usuarios)
            return redirect('/auth/login/')
        
        else:
            messages.add_message(request,constants.ERROR,'Usuario não cadastrado')
            return redirect('/auth/login/')
        

def sair(request):
    auth.logout(request)
    return redirect('/auth/login')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Essa token já foi usado')
        return redirect('/auth/login')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/login')