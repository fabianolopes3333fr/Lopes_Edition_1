from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from decimal import Decimal
import json

from .models import Produto, Fornecedor, ItemOrcamento
from .forms import ProdutoForm, FornecedorForm

def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin_user)
def lista_produtos(request):
    """Lista todos os produtos com filtros e paginação"""
    query = request.GET.get('q', '')
    atividade_filter = request.GET.get('atividade', '')
    unidade_filter = request.GET.get('unidade', '')
    fornecedor_filter = request.GET.get('fornecedor', '')

    produtos = Produto.objects.filter(ativo=True)

    # Aplicar filtros
    if query:
        produtos = produtos.filter(
            Q(referencia__icontains=query) |
            Q(descricao__icontains=query)
        )

    if atividade_filter:
        produtos = produtos.filter(atividade=atividade_filter)

    if unidade_filter:
        produtos = produtos.filter(unidade=unidade_filter)

    if fornecedor_filter:
        produtos = produtos.filter(fornecedor_id=fornecedor_filter)

    # Paginação
    paginator = Paginator(produtos, 20)
    page = request.GET.get('page')
    produtos_paginados = paginator.get_page(page)

    # Dados para os filtros
    fornecedores = Fornecedor.objects.filter(ativo=True)

    context = {
        'produtos': produtos_paginados,
        'query': query,
        'atividade_filter': atividade_filter,
        'unidade_filter': unidade_filter,
        'fornecedor_filter': fornecedor_filter,
        'fornecedores': fornecedores,
        'atividades': Produto._meta.get_field('atividade').choices,
        'unidades': Produto._meta.get_field('unidade').choices,
    }

    return render(request, 'orcamentos/produtos/lista.html', context)

@login_required
@user_passes_test(is_admin_user)
def criar_produto(request):
    """Criar novo produto"""
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f'Produto {produto.referencia} criado com sucesso!')
            return redirect('orcamentos:lista_produtos')
        else:
            messages.error(request, 'Erro ao criar produto. Verifique os dados.')
    else:
        form = ProdutoForm()

    context = {
        'form': form,
        'title': 'Criar Produto',
        'action': 'criar'
    }

    return render(request, 'orcamentos/produtos/form.html', context)

@login_required
@user_passes_test(is_admin_user)
def editar_produto(request, produto_id):
    """Editar produto existente"""
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f'Produto {produto.referencia} atualizado com sucesso!')
            return redirect('orcamentos:lista_produtos')
        else:
            messages.error(request, 'Erro ao atualizar produto. Verifique os dados.')
    else:
        form = ProdutoForm(instance=produto)

    context = {
        'form': form,
        'produto': produto,
        'title': f'Editar Produto - {produto.referencia}',
        'action': 'editar'
    }

    return render(request, 'orcamentos/produtos/form.html', context)

@login_required
@user_passes_test(is_admin_user)
def excluir_produto(request, produto_id):
    """Excluir produto (soft delete)"""
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        produto.ativo = False
        produto.save()
        messages.success(request, f'Produto {produto.referencia} excluído com sucesso!')
        return redirect('orcamentos:lista_produtos')

    context = {
        'produto': produto,
        'title': f'Excluir Produto - {produto.referencia}'
    }

    return render(request, 'orcamentos/produtos/confirmar_exclusao.html', context)

@login_required
@user_passes_test(is_admin_user)
def buscar_produtos_ajax(request):
    """Busca produtos via AJAX para uso nos orçamentos"""
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'produtos': []})

    produtos = Produto.objects.filter(
        ativo=True
    ).filter(
        Q(referencia__icontains=query) |
        Q(descricao__icontains=query)
    )[:10]

    produtos_data = []
    for produto in produtos:
        produtos_data.append({
            'id': produto.id,
            'referencia': produto.referencia,
            'descricao': produto.descricao,
            'unidade': produto.unidade,
            'atividade': produto.atividade,
            'preco_venda_ht': str(produto.preco_venda_ht),
            'preco_venda_ttc': str(produto.preco_venda_ttc),
            'taxa_tva': produto.taxa_tva,
            'preco_compra': str(produto.preco_compra),
        })

    return JsonResponse({'produtos': produtos_data})

@login_required
@user_passes_test(is_admin_user)
def detalhes_produto_ajax(request, produto_id):
    """Retorna detalhes do produto via AJAX"""
    try:
        produto = Produto.objects.get(id=produto_id, ativo=True)
        data = {
            'id': produto.id,
            'referencia': produto.referencia,
            'descricao': produto.descricao,
            'unidade': produto.unidade,
            'unidade_display': produto.get_unidade_display(),
            'atividade': produto.atividade,
            'atividade_display': produto.get_atividade_display(),
            'preco_venda_ht': str(produto.preco_venda_ht),
            'preco_venda_ttc': str(produto.preco_venda_ttc),
            'taxa_tva': produto.taxa_tva,
            'preco_compra': str(produto.preco_compra),
            'fornecedor': produto.fornecedor.nome if produto.fornecedor else '',
        }
        return JsonResponse({'success': True, 'produto': data})
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'})

# Views para fornecedores
@login_required
@user_passes_test(is_admin_user)
def lista_fornecedores(request):
    """Lista todos os fornecedores"""
    query = request.GET.get('q', '')

    fornecedores = Fornecedor.objects.filter(ativo=True)

    if query:
        fornecedores = fornecedores.filter(
            Q(nome__icontains=query) |
            Q(email__icontains=query)
        )

    # Paginação
    paginator = Paginator(fornecedores, 20)
    page = request.GET.get('page')
    fornecedores_paginados = paginator.get_page(page)

    context = {
        'fornecedores': fornecedores_paginados,
        'query': query,
    }

    return render(request, 'orcamentos/fornecedores/lista.html', context)

@login_required
@user_passes_test(is_admin_user)
def criar_fornecedor(request):
    """Criar novo fornecedor"""
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            fornecedor = form.save()
            messages.success(request, f'Fornecedor {fornecedor.nome} criado com sucesso!')
            return redirect('orcamentos:lista_fornecedores')
        else:
            messages.error(request, 'Erro ao criar fornecedor. Verifique os dados.')
    else:
        form = FornecedorForm()

    context = {
        'form': form,
        'title': 'Criar Fornecedor',
        'action': 'criar'
    }

    return render(request, 'orcamentos/fornecedores/form.html', context)

@login_required
@user_passes_test(is_admin_user)
def editar_fornecedor(request, fornecedor_id):
    """Editar fornecedor existente"""
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            fornecedor = form.save()
            messages.success(request, f'Fornecedor {fornecedor.nome} atualizado com sucesso!')
            return redirect('orcamentos:lista_fornecedores')
        else:
            messages.error(request, 'Erro ao atualizar fornecedor. Verifique os dados.')
    else:
        form = FornecedorForm(instance=fornecedor)

    context = {
        'form': form,
        'fornecedor': fornecedor,
        'title': f'Editar Fornecedor - {fornecedor.nome}',
        'action': 'editar'
    }

    return render(request, 'orcamentos/fornecedores/form.html', context)
