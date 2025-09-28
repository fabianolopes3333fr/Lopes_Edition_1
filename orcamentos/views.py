from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    AnexoProjeto, StatusOrcamento, StatusProjeto
)
from .forms import (
    ProjetoForm, SolicitacaoOrcamentoPublicoForm, SolicitacaoOrcamentoProjetoForm,
    OrcamentoForm, ItemOrcamentoFormSet, AnexoProjetoForm
)

# ============ VIEWS PÚBLICAS (SEM LOGIN) ============

def solicitar_orcamento_publico(request):
    """Página pública para solicitação de orçamento"""
    if request.method == 'POST':
        form = SolicitacaoOrcamentoPublicoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save()
            messages.success(
                request,
                f'Votre demande de devis #{solicitacao.numero} a été envoyée avec succès! '
                f'Nous vous contacterons sous 24h.'
            )
            return redirect('orcamentos:sucesso_solicitacao', numero=solicitacao.numero)
    else:
        form = SolicitacaoOrcamentoPublicoForm()

    context = {
        'form': form,
        'page_title': 'Demander un devis gratuit',
    }
    return render(request, 'orcamentos/solicitar_publico.html', context)

def sucesso_solicitacao(request, numero):
    """Página de sucesso após solicitação"""
    solicitacao = get_object_or_404(SolicitacaoOrcamento, numero=numero)
    context = {
        'solicitacao': solicitacao,
        'page_title': 'Demande envoyée avec succès'
    }
    return render(request, 'orcamentos/sucesso_solicitacao.html', context)

# ============ VIEWS PARA CLIENTES ============

@login_required
def cliente_projetos(request):
    """Lista de projetos do cliente"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    projetos = Projeto.objects.filter(cliente=request.user).order_by('-created_at')

    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        projetos = projetos.filter(status=status_filter)

    # Paginação
    paginator = Paginator(projetos, 10)
    page_number = request.GET.get('page')
    projetos_page = paginator.get_page(page_number)

    context = {
        'projetos': projetos_page,
        'status_choices': StatusProjeto.choices,
        'current_status': status_filter,
        'page_title': 'Mes Projets'
    }
    return render(request, 'orcamentos/cliente_projetos.html', context)

@login_required
def cliente_criar_projeto(request):
    """Criar novo projeto"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            projeto = form.save(commit=False)
            projeto.cliente = request.user
            projeto.save()
            messages.success(request, 'Projet créé avec succès!')
            return redirect('orcamentos:cliente_projeto_detail', uuid=projeto.uuid)
    else:
        form = ProjetoForm()

    context = {
        'form': form,
        'page_title': 'Nouveau Projet'
    }
    return render(request, 'orcamentos/cliente_criar_projeto.html', context)

@login_required
def cliente_projeto_detail(request, uuid):
    """Detalhes do projeto"""
    projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)

    # Anexos do projeto
    anexos = projeto.anexos.all()

    # Solicitações de orçamento deste projeto
    solicitacoes = projeto.solicitacoes_orcamento.all().order_by('-created_at')

    context = {
        'projeto': projeto,
        'anexos': anexos,
        'solicitacoes': solicitacoes,
        'page_title': projeto.titulo
    }
    return render(request, 'orcamentos/cliente_projeto_detail.html', context)

@login_required
def cliente_editar_projeto(request, uuid):
    """Editar projeto"""
    projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)

    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projet mis à jour avec succès!')
            return redirect('orcamentos:cliente_projeto_detail', uuid=projeto.uuid)
    else:
        form = ProjetoForm(instance=projeto)

    context = {
        'form': form,
        'projeto': projeto,
        'page_title': f'Éditer: {projeto.titulo}'
    }
    return render(request, 'orcamentos/cliente_editar_projeto.html', context)

@login_required
def cliente_excluir_projeto(request, uuid):
    """Excluir projeto"""
    projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)

    if request.method == 'POST':
        titulo = projeto.titulo
        projeto.delete()
        messages.success(request, f'Projet "{titulo}" supprimé avec succès!')
        return redirect('orcamentos:cliente_projetos')

    context = {
        'projeto': projeto,
        'page_title': f'Supprimer: {projeto.titulo}'
    }
    return render(request, 'orcamentos/cliente_excluir_projeto.html', context)

@login_required
def cliente_solicitar_orcamento_projeto(request, uuid):
    """Solicitar orçamento para um projeto específico"""
    projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)

    if request.method == 'POST':
        form = SolicitacaoOrcamentoProjetoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)

            # Preencher dados do usuário e projeto
            solicitacao.cliente = request.user
            solicitacao.projeto = projeto
            solicitacao.nome_solicitante = f"{request.user.first_name} {request.user.last_name}"
            solicitacao.email_solicitante = request.user.email
            solicitacao.telefone_solicitante = getattr(request.user, 'telefone', '')

            # Copiar dados do projeto
            solicitacao.endereco = projeto.endereco_projeto
            solicitacao.cidade = projeto.cidade_projeto
            solicitacao.cep = projeto.cep_projeto
            solicitacao.tipo_servico = projeto.tipo_servico
            solicitacao.descricao_servico = projeto.descricao
            solicitacao.area_aproximada = projeto.area_aproximada
            solicitacao.urgencia = projeto.urgencia
            solicitacao.data_inicio_desejada = projeto.data_inicio_desejada
            solicitacao.orcamento_maximo = projeto.orcamento_estimado

            solicitacao.save()

            messages.success(
                request,
                f'Demande de devis #{solicitacao.numero} envoyée avec succès!'
            )
            return redirect('orcamentos:cliente_projeto_detail', uuid=projeto.uuid)
    else:
        form = SolicitacaoOrcamentoProjetoForm()

    context = {
        'form': form,
        'projeto': projeto,
        'page_title': f'Demander un devis: {projeto.titulo}'
    }
    return render(request, 'orcamentos/cliente_solicitar_orcamento.html', context)

@login_required
def cliente_orcamentos(request):
    """Lista de orçamentos do cliente"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    # Solicitações do cliente
    solicitacoes = SolicitacaoOrcamento.objects.filter(
        cliente=request.user
    ).order_by('-created_at')

    # Orçamentos recebidos
    orcamentos = Orcamento.objects.filter(
        solicitacao__cliente=request.user
    ).order_by('-data_elaboracao')

    context = {
        'solicitacoes': solicitacoes,
        'orcamentos': orcamentos,
        'page_title': 'Mes Devis'
    }
    return render(request, 'orcamentos/cliente_orcamentos.html', context)

@login_required
def cliente_devis_detail(request, numero):
    """Detalhes do orçamento para o cliente"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
        solicitacao__cliente=request.user
    )

    context = {
        'orcamento': orcamento,
        'page_title': f'Devis #{orcamento.numero}'
    }
    return render(request, 'orcamentos/cliente_devis_detail.html', context)

@login_required
@require_http_methods(["POST"])
def cliente_devis_accepter(request, numero):
    """Aceitar orçamento via AJAX"""
    if request.user.account_type != 'CLIENT':
        return JsonResponse({'success': False, 'error': 'Accès non autorisé'})

    try:
        orcamento = get_object_or_404(
            Orcamento,
            numero=numero,
            solicitacao__cliente=request.user,
            status=StatusOrcamento.ENVIADO
        )

        # Atualizar status do orçamento
        orcamento.status = StatusOrcamento.ACEITO
        orcamento.data_resposta_cliente = timezone.now()
        orcamento.save()

        # Atualizar status da solicitação
        orcamento.solicitacao.status = StatusOrcamento.ACEITO
        orcamento.solicitacao.save()

        return JsonResponse({
            'success': True,
            'message': 'Devis accepté avec succès!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de l\'acceptation du devis'
        })

@login_required
@require_http_methods(["POST"])
def cliente_devis_refuser(request, numero):
    """Recusar orçamento via AJAX"""
    if request.user.account_type != 'CLIENT':
        return JsonResponse({'success': False, 'error': 'Accès non autorisé'})

    try:
        orcamento = get_object_or_404(
            Orcamento,
            numero=numero,
            solicitacao__cliente=request.user,
            status=StatusOrcamento.ENVIADO
        )

        # Atualizar status do orçamento
        orcamento.status = StatusOrcamento.RECUSADO
        orcamento.data_resposta_cliente = timezone.now()
        orcamento.save()

        # Atualizar status da solicitação
        orcamento.solicitacao.status = StatusOrcamento.RECUSADO
        orcamento.solicitacao.save()

        return JsonResponse({
            'success': True,
            'message': 'Devis refusé'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors du refus du devis'
        })

@login_required
def cliente_devis_pdf(request, numero):
    """Gerar PDF do orçamento para o cliente"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
        solicitacao__cliente=request.user
    )

    # Usar a mesma lógica do admin_orcamento_pdf
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from decimal import Decimal
    from datetime import datetime

    # Calcular totais para o PDF
    subtotal_ht = Decimal('0.00')
    total_taxe = Decimal('0.00')

    items_data = []
    for i, item in enumerate(orcamento.itens.all(), 1):
        pu_ht = item.preco_unitario
        pu_ttc = pu_ht * Decimal('1.20')  # + 20% TVA
        total_item_ht = item.quantidade * pu_ht
        total_item_ttc = total_item_ht * Decimal('1.20')
        taxe_item = total_item_ht * Decimal('0.20')

        subtotal_ht += total_item_ht
        total_taxe += taxe_item

        items_data.append({
            'ref': f"REF{i:03d}",
            'designation': item.descricao,
            'unite': item.unidade,
            'quantite': item.quantidade,
            'pu_ht': pu_ht,
            'pu_ttc': pu_ttc,
            'remise': Decimal('0.00'),
            'total_ht': total_item_ht,
            'total_ttc': total_item_ttc,
            'taxe': taxe_item
        })

    # Aplicar desconto global
    remise_global = orcamento.desconto or Decimal('0.00')
    valor_remise = subtotal_ht * (remise_global / 100)
    subtotal_apres_remise_ht = subtotal_ht - valor_remise
    subtotal_apres_remise_ttc = subtotal_apres_remise_ht * Decimal('1.20')
    taxe_finale = subtotal_apres_remise_ht * Decimal('0.20')

    # Context para o template
    context = {
        'orcamento': orcamento,
        'items_data': items_data,
        'subtotal_ht': subtotal_ht,
        'remise_global': remise_global,
        'valor_remise': valor_remise,
        'subtotal_apres_remise_ht': subtotal_apres_remise_ht,
        'taxe_finale': taxe_finale,
        'subtotal_apres_remise_ttc': subtotal_apres_remise_ttc,
        'date_generation': datetime.now(),
        'company_info': {
            'name': 'LOPES PEINTURE',
            'address': '123 Rue de la Peinture',
            'city': '75001 Paris, France',
            'phone': '+33 1 23 45 67 89',
            'email': 'contact@lopes-peinture.fr',
            'siret': '12345678901234',
            'ape': '4334Z',
            'tva': 'FR12345678901'
        }
    }

    # Renderizar template HTML
    html_content = render_to_string('orcamentos/devis_pdf_html.html', context)

    # Verificar se é para visualizar ou baixar
    download = request.GET.get('download', 'true')

    if download == 'false':
        # Exibir no navegador
        return HttpResponse(html_content, content_type='text/html')
    else:
        # Preparar para download como PDF (usando print do navegador)
        response = HttpResponse(html_content, content_type='text/html')
        filename = f"devis_{orcamento.numero}_{orcamento.solicitacao.nome_solicitante.replace(' ', '_')}.html"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

# ============ VIEWS AJAX ============

@login_required
@require_http_methods(["POST"])
def upload_anexo_projeto(request, uuid):
    """Upload de anexo via AJAX"""
    projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)

    form = AnexoProjetoForm(request.POST, request.FILES)
    if form.is_valid():
        anexo = form.save(commit=False)
        anexo.projeto = projeto
        anexo.save()

        return JsonResponse({
            'success': True,
            'anexo': {
                'id': anexo.id,
                'arquivo': anexo.arquivo.url,
                'descricao': anexo.descricao,
                'created_at': anexo.created_at.strftime('%d/%m/%Y %H:%M')
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })

@login_required
@require_http_methods(["DELETE"])
def excluir_anexo_projeto(request, uuid, anexo_id):
    """Excluir anexo via AJAX"""
    projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)
    anexo = get_object_or_404(AnexoProjeto, id=anexo_id, projeto=projeto)

    anexo.delete()
    return JsonResponse({'success': True})

# ============ DASHBOARD STATS ============

def get_cliente_stats(user):
    """Estatísticas para dashboard do cliente"""
    if user.account_type != 'CLIENT':
        return {}

    stats = {
        'client_projects': Projeto.objects.filter(cliente=user).count(),
        'client_quotes': SolicitacaoOrcamento.objects.filter(cliente=user).count(),
        'client_investment': Orcamento.objects.filter(
            solicitacao__cliente=user,
            status=StatusOrcamento.ACEITO
        ).aggregate(Sum('total'))['total__sum'] or 0,
        'recent_projects': Projeto.objects.filter(cliente=user).order_by('-created_at')[:3],
        'recent_quotes': SolicitacaoOrcamento.objects.filter(cliente=user).order_by('-created_at')[:3]
    }
    return stats

def get_admin_stats():
    """Estatísticas para dashboard do administrador"""
    stats = {
        'total_projects': Projeto.objects.count(),
        'total_clients': Projeto.objects.values('cliente').distinct().count(),
        'monthly_revenue': Orcamento.objects.filter(
            data_envio__month=timezone.now().month,
            status=StatusOrcamento.ACEITO
        ).aggregate(Sum('total'))['total__sum'] or 0,
        'pending_requests': SolicitacaoOrcamento.objects.filter(
            status=StatusOrcamento.PENDENTE
        ).count()
    }
    return stats
