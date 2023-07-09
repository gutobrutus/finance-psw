from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from .models import Conta, Categoria
from extrato.models import Valores
from .utils import calcula_total, calcula_equilibrio_financeiro
from datetime import datetime

def home(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')
    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')

    saldo_mensal = total_entradas - total_saidas
    despesa_mensal = total_saidas
    total_entradas_global = Valores.objects.filter(tipo='E')
    total_saidas_global = Valores.objects.filter(tipo='S')
    total_livre = calcula_total(total_entradas_global, 'valor') - calcula_total(total_saidas_global, 'valor') 

    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    context =  {
        'contas': contas, 
        'total_contas': total_contas,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo_mensal': saldo_mensal,
        'despesa_mensal': despesa_mensal,
        'total_livre': total_livre,
        'percentual_gastos_essenciais': int(percentual_gastos_essenciais),
        'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais)
    }

    return render(request, 'home.html', context)

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = calcula_total(contas, 'valor')
    return render(request, 'gerenciar.html', {'contas': contas, 'total_contas': total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.WARNING, 'Preencha todos os campos.')
        return redirect('/perfil/gerenciar/')

    conta = Conta(
        apelido = apelido,
        banco = banco,
        tipo = tipo,
        valor = valor,
        icone = icone
    )

    conta.save()

    messages.add_message(request, constants.SUCCESS, f'Cadastro da conta {apelido} realizado com sucesso')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    apelido_message = conta.apelido
    conta.delete()
    
    messages.add_message(request, constants.SUCCESS, f'Conta {apelido_message} excluída com sucesso')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()
    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}

    categorias = Categoria.objects.all()
    
    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total += v.valor
    
        dados[categoria.categoria] = total
    
    context = {
        'labels': list(dados.keys()),
        'values': list(dados.values()),
    }

    return render(request, 'dashboard.html', context)