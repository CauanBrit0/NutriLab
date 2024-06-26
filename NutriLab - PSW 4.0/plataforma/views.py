from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Pacientes, DadosPaciente, Refeicao, Opcao
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/auth/login/')
def pacientes(request):
    if request.method =="GET":
        pacientes = Pacientes.objects.filter(nutri = request.user)
        return render(request, 'pacientes.html',{'pacientes':pacientes})
    
    if request.method =="POST":
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        if len(nome.strip()) == 0  or len(idade.strip()) == 0  or len(email.strip()) == 0 or len(telefone.strip()) == 0 or len(sexo.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha os campos em branco.')
            return redirect('/pacientes')
        
        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')
        
        pacientes = Pacientes.objects.filter(email=email)
        if pacientes.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')
        
        try:
            paciente = Pacientes(nome = nome, sexo = sexo, idade = idade, email = email, telefone = telefone, nutri = request.user)
            paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso.')
            return redirect('/pacientes')

        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema.')
            return redirect('/pacientes')
        


@login_required(login_url='/auth/login/')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri = request.user)
        return render(request, 'dados_paciente_listar.html',{'pacientes':pacientes})
    
@login_required(login_url='/auth/login/')
def dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    dados_paciente = DadosPaciente.objects.filter(paciente = paciente)

    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')
        
    if request.method == "GET":
        return render(request,'dados_paciente.html', {'paciente':paciente,'dados_paciente': dados_paciente})
    
    elif request.method == "POST":
        peso = request.POST.get('peso')
        altura = request.POST.get('altura')
        gordura = request.POST.get('gordura')
        musculo = request.POST.get('musculo')
        hdl = request.POST.get('hdl')
        ldl = request.POST.get('ldl')
        ctotal = request.POST.get('ctotal')
        triglicerídios = request.POST.get('triglicerídios')

        if len(peso.strip()) == 0 or len(altura.strip()) == 0 or len(gordura.strip()) == 0 or len(musculo.strip()) == 0 or len(hdl.strip()) == 0 or len(ldl.strip()) == 0 or len(ctotal.strip()) == 0 or len(triglicerídios.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha os campos em branco')
            return redirect(f'/dados_paciente/{id}')
        
        if not peso.isnumeric() or not altura.isnumeric() or not gordura.isnumeric() or not musculo.isnumeric() or not hdl.isnumeric() or not ldl.isnumeric() or not ctotal.isnumeric() or not triglicerídios.isnumeric():
            messages.add_message(request, constants.ERROR, 'Preencha os campos com números.')
            return redirect(f'/dados_paciente/{id}')

        try:
            paciente_s = DadosPaciente(peso = peso, 
                                   data = datetime.now(),
                                     altura = altura, 
                                     percentual_gordura = gordura, 
                                     percentual_musculo = musculo, 
                                     colesterol_hdl= hdl, 
                                     colesterol_ldl = ldl, 
                                     colesterol_total = ctotal, 
                                     trigliceridios = triglicerídios,
                                     paciente = paciente)
            paciente_s.save()
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrados com Sucesso!')
            return redirect(f'/dados_paciente/{id}')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema.')
            return redirect(f'/dados_paciente/{id}')

@login_required(login_url='/auth/login/')
@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data")
    
    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {'peso': pesos,
            'labels': labels}
    return JsonResponse(data)


def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri = request.user)
        return render(request,'plano_alimentar_listar.html',{'pacientes':pacientes})
    


def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id = id)
    refeicoes = Refeicao.objects.filter(paciente = paciente).order_by('horario')
    opcoes = Opcao.objects.all()
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect(f'/plano_alimentar/')
    
    if request.method == "GET":
        return render(request,'plano_alimentar.html',{'paciente':paciente,'refeicoes':refeicoes,'opcoes':opcoes})
    
    

def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')

    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('gorduras')
        if not proteinas or not gorduras or not carboidratos:
            messages.add_message(request, constants.ERROR, 'Preencha os campos em branco.')
            return redirect(f'/plano_alimentar/{id_paciente}')
        
        r1 = Refeicao(paciente=paciente,
                      titulo=titulo,
                      horario=horario,
                      carboidratos=carboidratos,
                      proteinas=proteinas,
                      gorduras=gorduras)

        r1.save()

        messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')


def opcao(request, id_paciente):    
    if request.method =="POST":
        id_refeicao = request.POST.get('refeicao')
        descricao = request.POST.get('descricao')
        imagem = request.FILES.get('imagem')
        opc = Opcao(refeicao_id = id_refeicao, descricao = descricao, imagem = imagem)
        opc.save()
        messages.add_message(request, constants.SUCCESS, 'Opção cadastrada.')
        return redirect(f'/plano_alimentar/{id_paciente}/')
