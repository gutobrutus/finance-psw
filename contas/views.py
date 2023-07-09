from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import constants
from perfil.models import Categoria
from .models import ContaPagar, ContaPaga

# Create your views here.
def definir_contas(request):
    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias
    }
    if request.method == "GET":
        return render(request, 'definir_contas.html', context)
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo = titulo,
            categoria_id = categoria,
            descricao = descricao,
            valor = valor,
            dia_pagamento = dia_pagamento
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!')

        return redirect('/contas/definir_contas/')
    
def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day

    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(
        data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(
        dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    contas_proximas_do_vencimento = contas.filter(
        dia_pagamento__lte=DIA_ATUAL + 5).filter(
        dia_pagamento__gt=DIA_ATUAL).exclude(
        id__in=contas_pagas)
    
    contas_restantes = contas.exclude(
        id__in=contas_vencidas).exclude(
        id__in=contas_proximas_do_vencimento).exclude(
        id__in=contas_pagas)

    context = {
        'contas_vencidas': contas_vencidas,
        'contas_proximas_do_vencimento': contas_proximas_do_vencimento,
        'contas_restantes': contas_restantes
    }

    return render(request, 'ver_contas.html', context)