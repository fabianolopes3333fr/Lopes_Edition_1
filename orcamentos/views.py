from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from datetime import timedelta
import json

from .models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    AnexoProjeto, StatusOrcamento, StatusProjeto, Facture, ItemFacture
)
from .forms import (
    ProjetoForm, SolicitacaoOrcamentoPublicoForm, SolicitacaoOrcamentoProjetoForm,
    OrcamentoForm, AnexoProjetoForm, FactureForm
)
from .services import NotificationService

# ============ VIEWS PÚBLICAS (SEM LOGIN) ============

def solicitar_orcamento_publico(request):
    """Página pública para solicitação de orçamento"""
    if request.method == 'POST':
        form = SolicitacaoOrcamentoPublicoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save()

            # Enviar notificações e emails para admins
            NotificationService.enviar_email_nova_solicitacao(solicitacao)

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

            # Notificar admins sobre novo projeto
            NotificationService.notificar_projeto_criado(projeto)

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
            try:
                solicitacao = form.save(commit=False)

                # Preencher dados do usuário e projeto
                solicitacao.cliente = request.user
                solicitacao.projeto = projeto
                solicitacao.nome_solicitante = f"{request.user.first_name} {request.user.last_name}"
                solicitacao.email_solicitante = request.user.email
                # Corrigir: usar valor padrão se telefone não existir
                solicitacao.telefone_solicitante = getattr(request.user, 'telefone', '11999999999')

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

                # Enviar notificações para admins
                try:
                    # Comentar temporariamente para testes
                    # NotificationService.enviar_email_nova_solicitacao(solicitacao)
                    print(f"DEBUG: Solicitação {solicitacao.numero} criada com sucesso")
                except Exception as e:
                    print(f"Erro ao enviar notificações: {e}")
                    # Continua mesmo se o email falhar

                messages.success(
                    request,
                    f'Demande de devis #{solicitacao.numero} envoyée avec succès!'
                )
                return redirect('orcamentos:cliente_projeto_detail', uuid=projeto.uuid)

            except Exception as e:
                messages.error(
                    request,
                    'Une erreur est survenue lors de l\'envoi de votre demande. Veuillez réessayer.'
                )
                print(f"Erro ao criar solicitação: {e}")
                import traceback
                traceback.print_exc()
        else:
            messages.error(
                request,
                'Veuillez corriger les erreurs dans le formulaire.'
            )
            print(f"DEBUG: Erros no formulário: {form.errors}")
    else:
        # Pré-preencher o formulário com dados do projeto
        initial_data = {
            'tipo_servico': projeto.tipo_servico,
            'descricao_servico': projeto.descricao,
            'area_aproximada': projeto.area_aproximada,
            'urgencia': projeto.urgencia,
            'data_inicio_desejada': projeto.data_inicio_desejada,
            'orcamento_maximo': projeto.orcamento_estimado,
        }
        form = SolicitacaoOrcamentoProjetoForm(initial=initial_data)

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

        # Atualizar status do projeto para EM_ANDAMENTO se houver projeto
        if orcamento.solicitacao.projeto:
            orcamento.solicitacao.projeto.status = StatusProjeto.EM_ANDAMENTO
            orcamento.solicitacao.projeto.save()

        # Enviar notificações para admins
        try:
            NotificationService.enviar_email_orcamento_aceito(orcamento)
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")

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

        # Enviar notificações para admins
        NotificationService.enviar_email_orcamento_recusado(orcamento)

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
    total_ttc = Decimal('0.00')

    items_data = []
    for i, item in enumerate(orcamento.itens.all(), 1):
        # Usar a TVA real do item, não fixa
        taxa_tva_decimal = Decimal(item.taxa_tva) / 100

        pu_ht = item.preco_unitario_ht
        pu_ttc = pu_ht * (1 + taxa_tva_decimal)
        total_item_ht = item.total_ht  # Já calculado com remise
        total_item_ttc = item.total_ttc  # Já calculado com remise e TVA
        taxe_item = total_item_ttc - total_item_ht

        subtotal_ht += total_item_ht
        total_taxe += taxe_item
        total_ttc += total_item_ttc

        items_data.append({
            'ref': item.referencia or f"REF{i:03d}",
            'designation': item.descricao,
            'unite': item.get_unidade_display(),
            'quantite': item.quantidade,
            'pu_ht': pu_ht,
            'pu_ttc': pu_ttc,
            'remise': (item.quantidade * pu_ht * item.remise_percentual / 100) if item.remise_percentual else Decimal('0.00'),
            'total_ht': total_item_ht,
            'total_ttc': total_item_ttc,
            'taxe': taxe_item,
            'taxa_tva': item.taxa_tva  # Adicionar a taxa para usar no template
        })

    # Aplicar desconto global se houver
    remise_global = orcamento.desconto or Decimal('0.00')
    valor_remise_global = (subtotal_ht * remise_global / 100) if remise_global else Decimal('0.00')

    # Calcular taxa média de TVA para exibir no resumo
    taxa_tva_media = "Variável"
    if total_ttc > 0 and subtotal_ht > 0:
        percentual_tva = ((total_taxe / subtotal_ht) * 100)
        # Se for um valor "redondo", mostrar como percentual fixo
        if abs(percentual_tva - 20) < 0.01:
            taxa_tva_media = "20"
        elif abs(percentual_tva - 10) < 0.01:
            taxa_tva_media = "10"
        elif abs(percentual_tva - 5.5) < 0.01:
            taxa_tva_media = "5.5"
        elif abs(percentual_tva - 0) < 0.01:
            taxa_tva_media = "0"
        else:
            taxa_tva_media = f"{percentual_tva:.1f}"

    # Totais finais (já com desconto global aplicado via model)
    subtotal_final_ht = orcamento.total
    taxe_finale = orcamento.valor_tva
    subtotal_final_ttc = orcamento.total_ttc

    # Context para o template
    context = {
        'orcamento': orcamento,
        'items_data': items_data,
        'subtotal_ht': subtotal_ht,
        'remise_global': remise_global,
        'valor_remise': valor_remise_global,
        'subtotal_apres_remise_ht': subtotal_final_ht,
        'taxe_finale': taxe_finale,
        'subtotal_apres_remise_ttc': subtotal_final_ttc,
        'taxa_tva_media': taxa_tva_media,  # Adicionar a taxa média calculada
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

@staff_member_required
def admin_dashboard(request):
    """Dashboard administrativo"""
    # Estatísticas gerais
    total_solicitacoes = SolicitacaoOrcamento.objects.count()
    solicitacoes_pendentes = SolicitacaoOrcamento.objects.filter(status=StatusOrcamento.PENDENTE).count()
    orcamentos_enviados = Orcamento.objects.filter(status=StatusOrcamento.ENVIADO).count()
    orcamentos_aceitos = Orcamento.objects.filter(status=StatusOrcamento.ACEITO).count()

    # Solicitações recentes
    solicitacoes_recentes = SolicitacaoOrcamento.objects.order_by('-created_at')[:5]

    # Orçamentos recentes
    orcamentos_recentes = Orcamento.objects.order_by('-data_elaboracao')[:5]

    # Receita do mês
    receita_mes = Orcamento.objects.filter(
        status=StatusOrcamento.ACEITO,
        data_resposta_cliente__month=timezone.now().month
    ).aggregate(Sum('total'))['total__sum'] or 0

    context = {
        'total_solicitacoes': total_solicitacoes,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'orcamentos_enviados': orcamentos_enviados,
        'orcamentos_aceitos': orcamentos_aceitos,
        'solicitacoes_recentes': solicitacoes_recentes,
        'orcamentos_recentes': orcamentos_recentes,
        'receita_mes': receita_mes,
        'page_title': 'Dashboard Admin'
    }
    return render(request, 'orcamentos/admin_dashboard.html', context)

# ============ VIEWS ADMINISTRATIVAS ============

@staff_member_required
def admin_solicitacoes(request):
    """Lista todas as solicitações de orçamento para administradores"""
    solicitacoes = SolicitacaoOrcamento.objects.all().order_by('-created_at')

    # Filtros opcionais
    status_filter = request.GET.get('status')
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)

    # Paginação
    paginator = Paginator(solicitacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': StatusOrcamento.choices,
        'current_status': status_filter,
        'page_title': 'Solicitações de Orçamento - Admin',
    }
    return render(request, 'orcamentos/admin_solicitacoes.html', context)


@staff_member_required
def admin_solicitacao_detail(request, numero):
    """Detalhes de uma solicitação específica"""
    solicitacao = get_object_or_404(SolicitacaoOrcamento, numero=numero)

    context = {
        'solicitacao': solicitacao,
        'page_title': f'Solicitação #{numero}',
    }
    return render(request, 'orcamentos/admin_solicitacao_detail.html', context)


@staff_member_required
def admin_criar_orcamento(request, numero):
    """Criar orçamento para uma solicitação"""
    solicitacao = get_object_or_404(SolicitacaoOrcamento, numero=numero)

    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        formset = ItemOrcamentoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            orcamento = form.save(commit=False)
            orcamento.solicitacao = solicitacao
            orcamento.elaborado_por = request.user  # Adicionar o usuário que está criando
            orcamento.save()

            # Salvar itens do orçamento
            instances = formset.save(commit=False)
            for instance in instances:
                instance.orcamento = orcamento
                instance.save()

            # Recalcular totais
            orcamento.calcular_totais()

            # Atualizar status da solicitação
            solicitacao.status = StatusOrcamento.EM_ELABORACAO
            solicitacao.save()

            messages.success(request, f'Orçamento #{orcamento.numero} criado com sucesso!')
            return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)
    else:
        form = OrcamentoForm()
        formset = ItemOrcamentoFormSet()

    context = {
        'form': form,
        'formset': formset,
        'solicitacao': solicitacao,
        'page_title': f'Criar Orçamento - Solicitação #{numero}',
    }
    return render(request, 'orcamentos/admin_criar_orcamento.html', context)

@staff_member_required
def admin_orcamentos(request):
    """Lista todos os orçamentos para administradores"""
    orcamentos = Orcamento.objects.all().order_by('-data_elaboracao')

    # Filtros opcionais
    status_filter = request.GET.get('status')
    if status_filter:
        orcamentos = orcamentos.filter(status=status_filter)

    # Paginação
    paginator = Paginator(orcamentos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': StatusOrcamento.choices,
        'current_status': status_filter,
        'page_title': 'Gestion des Devis',
    }
    return render(request, 'orcamentos/admin_orcamentos.html', context)

@staff_member_required
def admin_orcamento_detail(request, numero):
    """Detalhes de um orçamento específico"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    context = {
        'orcamento': orcamento,
        'page_title': f'Devis #{numero}',
    }
    return render(request, 'orcamentos/admin_orcamento_detail.html', context)

@staff_member_required
def admin_editar_orcamento(request, numero):
    """Editar um orçamento existente"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    if request.method == 'POST':
        form = OrcamentoForm(request.POST, instance=orcamento)
        if form.is_valid():
            orcamento = form.save()

            # Processar itens atualizados
            itens_data = request.POST.get('itens_json', '[]')
            try:
                # Remover itens existentes
                orcamento.itens.all().delete()

                # Criar novos itens
                itens = json.loads(itens_data)
                for item_data in itens:
                    if item_data.get('descricao'):
                        ItemOrcamento.objects.create(
                            orcamento=orcamento,
                            produto_id=item_data.get('produto_id') if item_data.get('produto_id') else None,
                            referencia=item_data.get('referencia', ''),
                            descricao=item_data.get('descricao'),
                            unidade=item_data.get('unidade', 'unite'),
                            atividade=item_data.get('atividade', 'marchandise'),
                            quantidade=Decimal(str(item_data.get('quantidade', 1))),
                            preco_unitario_ht=Decimal(str(item_data.get('preco_unitario_ht', 0))),
                            remise_percentual=Decimal(str(item_data.get('remise_percentual', 0))),
                            taxa_tva=item_data.get('taxa_tva', '20'),
                            preco_compra_unitario=Decimal(str(item_data.get('preco_compra_unitario', 0))),
                        )
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                messages.warning(request, f'Erro ao processar itens: {str(e)}')
                pass

            # Recalcular totais
            orcamento.calcular_totais()

            action = request.POST.get('action', 'draft')
            if action == 'send':
                orcamento.status = StatusOrcamento.ENVIADO
                orcamento.data_envio = timezone.now()
                orcamento.save()

                orcamento.solicitacao.status = StatusOrcamento.ENVIADO
                orcamento.solicitacao.save()

                messages.success(request, f'Devis {orcamento.numero} mis à jour et envoyé!')
            else:
                messages.success(request, f'Devis {orcamento.numero} mis à jour.')

            return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)
    else:
        form = OrcamentoForm(instance=orcamento)

    # Preparar dados dos itens existentes para o JavaScript
    existing_items = []
    for item in orcamento.itens.all():
        existing_items.append({
            'produto_id': item.produto_id,
            'referencia': item.referencia,
            'descricao': item.descricao,
            'unidade': item.unidade,
            'atividade': item.atividade,
            'quantidade': float(item.quantidade),
            'preco_unitario_ht': float(item.preco_unitario_ht),
            'remise_percentual': float(item.remise_percentual),
            'taxa_tva': item.taxa_tva,
            'preco_compra_unitario': float(item.preco_compra_unitario)
        })

    context = {
        'form': form,
        'orcamento': orcamento,
        'solicitacao': orcamento.solicitacao,
        'page_title': f'Éditer Devis - {orcamento.numero}',
        'existing_items': existing_items
    }

    return render(request, 'orcamentos/admin_editar_orcamento.html', context)


@staff_member_required
def admin_enviar_orcamento(request, numero):
    """Enviar orçamento para o cliente"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    if request.method == 'POST':
        # Marcar como enviado
        orcamento.status = StatusOrcamento.ENVIADO
        orcamento.data_envio = timezone.now()
        orcamento.save()

        # Atualizar status da solicitação
        orcamento.solicitacao.status = StatusOrcamento.ENVIADO
        orcamento.solicitacao.save()

        # Enviar email e notificações para cliente
        NotificationService.enviar_email_orcamento_enviado(orcamento)

        messages.success(request, f'Orçamento #{numero} enviado com sucesso!')
        return redirect('orcamentos:admin_orcamento_detail', numero=numero)

    context = {
        'orcamento': orcamento,
        'page_title': f'Enviar Orçamento #{numero}',
    }
    return render(request, 'orcamentos/admin_enviar_orcamento.html', context)


@staff_member_required
def admin_orcamento_pdf(request, numero):
    """Gerar PDF do orçamento para administradores"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    # Importar o gerador de PDF aqui para evitar dependências circulares
    from .pdf_generator import gerar_pdf_orcamento

    try:
        pdf_buffer = gerar_pdf_orcamento(orcamento)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{numero}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('orcamentos:admin_orcamento_detail', numero=numero)

@login_required
@staff_member_required
def admin_elaborar_orcamento(request, numero):
    """Elaborar orçamento a partir de uma solicitação"""
    solicitacao = get_object_or_404(SolicitacaoOrcamento, numero=numero)

    # Verificar se já existe orçamento
    if hasattr(solicitacao, 'orcamento'):
        messages.info(request, 'Cette demande a déjà un devis associé.')
        return redirect('orcamentos:admin_editar_orcamento', numero=solicitacao.orcamento.numero)

    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            orcamento = form.save(commit=False)
            orcamento.solicitacao = solicitacao
            orcamento.elaborado_por = request.user
            orcamento.save()

            # Processar itens do orçamento enviados via AJAX
            itens_data = request.POST.get('itens_json', '[]')
            print(f"DEBUG: itens_data recebido: {itens_data}")  # Debug

            try:
                itens = json.loads(itens_data)
                print(f"DEBUG: itens parseados: {itens}")  # Debug

                for item_data in itens:
                    print(f"DEBUG: processando item: {item_data}")  # Debug
                    if item_data.get('descricao'):  # Só criar se tiver descrição
                        item_criado = ItemOrcamento.objects.create(
                            orcamento=orcamento,
                            produto_id=item_data.get('produto_id') if item_data.get('produto_id') else None,
                            referencia=item_data.get('referencia', ''),
                            descricao=item_data.get('descricao'),
                            unidade=item_data.get('unidade', 'unite'),
                            atividade=item_data.get('atividade', 'marchandise'),
                            quantidade=Decimal(str(item_data.get('quantidade', 1))),
                            preco_unitario_ht=Decimal(str(item_data.get('preco_unitario_ht', 0))),
                            remise_percentual=Decimal(str(item_data.get('remise_percentual', 0))),
                            taxa_tva=item_data.get('taxa_tva', '20'),
                            preco_compra_unitario=Decimal(str(item_data.get('preco_compra_unitario', 0))),
                        )
                        print(f"DEBUG: item criado com ID: {item_criado.id}")  # Debug
                    else:
                        print(f"DEBUG: item ignorado - sem descrição")  # Debug
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"DEBUG: erro ao processar itens: {str(e)}")  # Debug
                messages.warning(request, f'Erro ao processar itens: {str(e)}')
                pass

            # Recalcular totais
            orcamento.calcular_totais()

            # Atualizar status da solicitação
            solicitacao.status = StatusOrcamento.EM_ELABORACAO
            solicitacao.save()

            action = request.POST.get('action', 'draft')
            if action == 'send':
                orcamento.status = StatusOrcamento.ENVIADO
                orcamento.data_envio = timezone.now()
                orcamento.save()

                solicitacao.status = StatusOrcamento.ENVIADO
                solicitacao.save()

                messages.success(request, f'Devis {orcamento.numero} créé et envoyé avec succès!')
            else:
                messages.success(request, f'Devis {orcamento.numero} sauvegardé en brouillon.')

            return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)
    else:
        # Pré-preencher com dados da solicitação
        initial_data = {
            'titulo': f"Devis pour {solicitacao.get_tipo_servico_display()}",
            'descricao': solicitacao.descricao_servico,
            'prazo_execucao': 30,
            'validade_orcamento': timezone.now().date() + timezone.timedelta(days=30),
            'condicoes_pagamento': "30% à la signature, 70% à la fin des travaux",
            'desconto': 0,
        }
        form = OrcamentoForm(initial=initial_data)

    context = {
        'form': form,
        'solicitacao': solicitacao,
        'page_title': f'Elaborer Devis - {solicitacao.numero}',
    }

    return render(request, 'orcamentos/admin_elaborar_orcamento.html', context)

@staff_member_required
def admin_criar_orcamento_cliente(request, cliente_id):
    """Criar orçamento diretamente para um cliente específico"""
    from clientes.models import Cliente

    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        # Primeiro, criar uma solicitação temporária para o cliente
        solicitacao = SolicitacaoOrcamento.objects.create(
            nome_solicitante=cliente.nom_complet,
            email_solicitante=cliente.email or 'nao-informado@exemplo.com',
            telefone_solicitante=cliente.telephone or '',
            endereco=cliente.adresse,
            cidade=cliente.ville,
            cep=cliente.code_postal,
            tipo_servico='outro',
            descricao_servico=f'Orçamento personalizado para {cliente.nom_complet}',
            orcamento_maximo=5000.00,
            data_inicio_desejada=timezone.now().date() + timezone.timedelta(days=30),
            status=StatusOrcamento.EM_ELABORACAO
        )

        # Criar o orçamento
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            orcamento = form.save(commit=False)
            orcamento.solicitacao = solicitacao
            orcamento.elaborado_por = request.user
            orcamento.save()

            # Processar itens do orçamento enviados via AJAX
            itens_data = request.POST.get('itens_json', '[]')
            try:
                itens = json.loads(itens_data)
                for item_data in itens:
                    if item_data.get('descricao'):
                        ItemOrcamento.objects.create(
                            orcamento=orcamento,
                            produto_id=item_data.get('produto_id') if item_data.get('produto_id') else None,
                            referencia=item_data.get('referencia', ''),
                            descricao=item_data.get('descricao'),
                            unidade=item_data.get('unidade', 'unite'),
                            atividade=item_data.get('atividade', 'marchandise'),
                            quantidade=Decimal(str(item_data.get('quantidade', 1))),
                            preco_unitario_ht=Decimal(str(item_data.get('preco_unitario_ht', 0))),
                            remise_percentual=Decimal(str(item_data.get('remise_percentual', 0))),
                            taxa_tva=item_data.get('taxa_tva', '20'),
                            preco_compra_unitario=Decimal(str(item_data.get('preco_compra_unitario', 0))),
                        )
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                messages.warning(request, f'Erro ao processar itens: {str(e)}')

            # Recalcular totais
            orcamento.calcular_totais()

            action = request.POST.get('action', 'draft')
            if action == 'send':
                orcamento.status = StatusOrcamento.ENVIADO
                orcamento.data_envio = timezone.now()
                orcamento.save()

                solicitacao.status = StatusOrcamento.ENVIADO
                solicitacao.save()

                messages.success(request, f'Devis {orcamento.numero} créé et envoyé avec succès pour {cliente.nom_complet}!')
            else:
                messages.success(request, f'Devis {orcamento.numero} sauvegardé en brouillon pour {cliente.nom_complet}.')

            return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)
    else:
        # Pré-preencher com dados do cliente
        initial_data = {
            'titulo': f"Devis pour {cliente.nom_complet}",
            'descricao': f'Orçamento personalizado elaborado para {cliente.nom_complet}',
            'prazo_execucao': 30,
            'validade_orcamento': timezone.now().date() + timezone.timedelta(days=30),
            'condicoes_pagamento': cliente.get_conditions_paiement_display() if cliente.conditions_paiement else "30% à la signature, 70% à la fin des travaux",
            'desconto': float(cliente.remise_globale) if cliente.remise_globale else 0,
        }
        form = OrcamentoForm(initial=initial_data)

    context = {
        'form': form,
        'cliente': cliente,
        'page_title': f'Criar Devis para {cliente.nom_complet}',
        'is_cliente_direto': True,  # Flag para identificar que é criação direta
    }

    return render(request, 'orcamentos/admin_elaborar_orcamento.html', context)

# ============ VIEWS DE FATURAS (ADMIN) ============

@staff_member_required
def admin_faturas_list(request):
    """Lista todas as faturas para administradores"""
    faturas = Facture.objects.all().select_related('cliente', 'orcamento', 'elaborado_por')

    # Filtros
    status = request.GET.get('status')
    if status:
        faturas = faturas.filter(status=status)

    cliente_id = request.GET.get('cliente')
    if cliente_id:
        faturas = faturas.filter(cliente_id=cliente_id)

    search = request.GET.get('search')
    if search:
        faturas = faturas.filter(
            Q(numero__icontains=search) |
            Q(titulo__icontains=search) |
            Q(cliente__first_name__icontains=search) |
            Q(cliente__last_name__icontains=search) |
            Q(cliente__email__icontains=search)
        )

    # Ordenação
    ordenar = request.GET.get('ordenar', '-data_criacao')
    faturas = faturas.order_by(ordenar)

    # Paginação
    paginator = Paginator(faturas, 20)
    page_number = request.GET.get('page')
    faturas_page = paginator.get_page(page_number)

    # Estatísticas
    stats = {
        'total': Facture.objects.count(),
        'brouillon': Facture.objects.filter(status='brouillon').count(),
        'envoyee': Facture.objects.filter(status='envoyee').count(),
        'payee': Facture.objects.filter(status='payee').count(),
        'en_retard': Facture.objects.filter(status='en_retard').count(),
        'total_a_payer': Facture.objects.filter(status='envoyee').aggregate(Sum('total'))['total__sum'] or 0,
        'total_paye': Facture.objects.filter(status='payee').aggregate(Sum('total'))['total__sum'] or 0,
    }

    # Lista de clientes para filtro
    from django.contrib.auth import get_user_model
    User = get_user_model()
    clientes = User.objects.filter(faturas_cliente__isnull=False).distinct()

    context = {
        'faturas': faturas_page,
        'stats': stats,
        'clientes': clientes,
        'page_title': 'Gestion des Factures',
    }
    return render(request, 'orcamentos/admin_faturas_list.html', context)

@staff_member_required
def admin_fatura_detail(request, numero):
    """Detalhes de uma fatura específica"""
    fatura = get_object_or_404(Facture.objects.select_related('cliente', 'orcamento', 'elaborado_por'), numero=numero)

    context = {
        'fatura': fatura,
        'page_title': f'Facture #{numero}',
    }
    return render(request, 'orcamentos/admin_fatura_detail.html', context)

@staff_member_required
def admin_criar_fatura(request):
    """Criar uma nova fatura do zero (sem devis)"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            fatura = form.save(commit=False)
            fatura.elaborado_por = request.user
            fatura.save()

            # Processar itens
            itens_data = request.POST.get('itens_json', '[]')
            try:
                itens = json.loads(itens_data)
                for item_data in itens:
                    if item_data.get('descricao'):
                        ItemFacture.objects.create(
                            facture=fatura,
                            produto_id=item_data.get('produto_id') if item_data.get('produto_id') else None,
                            referencia=item_data.get('referencia', ''),
                            descricao=item_data.get('descricao'),
                            unidade=item_data.get('unidade', 'unite'),
                            atividade=item_data.get('atividade', 'marchandise'),
                            quantidade=Decimal(str(item_data.get('quantidade', 1))),
                            preco_unitario_ht=Decimal(str(item_data.get('preco_unitario_ht', 0))),
                            remise_percentual=Decimal(str(item_data.get('remise_percentual', 0))),
                            taxa_tva=item_data.get('taxa_tva', '20'),
                        )
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                messages.warning(request, f'Erro ao processar itens: {str(e)}')

            # Recalcular totais
            fatura.calcular_totais()

            action = request.POST.get('action', 'draft')
            if action == 'send':
                fatura.status = 'envoyee'
                fatura.data_envio = timezone.now()
                fatura.save()
                messages.success(request, f'Facture {fatura.numero} créée et envoyée avec succès!')
            else:
                messages.success(request, f'Facture {fatura.numero} créée en tant que brouillon.')

            return redirect('orcamentos:admin_fatura_detail', numero=fatura.numero)
    else:
        form = FactureForm()

    # Lista de clientes para o formulário
    clientes = User.objects.filter(is_active=True).exclude(is_staff=True).order_by('first_name', 'last_name')

    from .models import Produto
    produtos = Produto.objects.filter(ativo=True).order_by('referencia')

    context = {
        'form': form,
        'clientes': clientes,
        'produtos': produtos,
        'page_title': 'Créer une Facture',
    }
    return render(request, 'orcamentos/admin_elaborar_facture.html', context)

@staff_member_required
def admin_criar_fatura_from_orcamento(request, orcamento_numero):
    """Criar fatura a partir de um devis (orçamento)"""
    orcamento = get_object_or_404(Orcamento.objects.select_related('solicitacao'), numero=orcamento_numero)

    # Verificar se o orçamento foi aceito
    if orcamento.status != StatusOrcamento.ACEITO:
        messages.warning(request, 'Attention: le devis n\'a pas encore été accepté par le client.')

    # Buscar cliente
    cliente = None
    if orcamento.solicitacao.cliente:
        cliente = orcamento.solicitacao.cliente
    else:
        # Se não tem cliente cadastrado, não pode criar fatura
        messages.error(request, 'Impossible de créer une facture: le devis n\'a pas de client associé.')
        return redirect('orcamentos:admin_orcamento_detail', numero=orcamento_numero)

    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            fatura = form.save(commit=False)
            fatura.orcamento = orcamento
            fatura.cliente = cliente
            fatura.elaborado_por = request.user
            fatura.save()

            # Copiar itens do orçamento
            for item_orcamento in orcamento.itens.all():
                ItemFacture.objects.create(
                    facture=fatura,
                    produto=item_orcamento.produto,
                    referencia=item_orcamento.referencia,
                    descricao=item_orcamento.descricao,
                    unidade=item_orcamento.unidade,
                    atividade=item_orcamento.atividade,
                    quantidade=item_orcamento.quantidade,
                    preco_unitario_ht=item_orcamento.preco_unitario_ht,
                    remise_percentual=item_orcamento.remise_percentual,
                    taxa_tva=item_orcamento.taxa_tva,
                )

            # Recalcular totais
            fatura.calcular_totais()

            action = request.POST.get('action', 'draft')
            if action == 'send':
                fatura.status = 'envoyee'
                fatura.data_envio = timezone.now()
                fatura.save()
                messages.success(request, f'Facture {fatura.numero} créée et envoyée avec succès!')
            else:
                messages.success(request, f'Facture {fatura.numero} créée à partir du devis {orcamento_numero}.')

            return redirect('orcamentos:admin_fatura_detail', numero=fatura.numero)
    else:
        # Pré-preencher o formulário com dados do orçamento
        initial_data = {
            'titulo': orcamento.titulo,
            'descricao': orcamento.descricao,
            'cliente': cliente,
            'condicoes_pagamento': orcamento.condicoes_pagamento,
            'tipo_pagamento': orcamento.tipo_pagamento,
            'desconto': orcamento.desconto,
            'data_vencimento': timezone.now().date() + timezone.timedelta(days=30),
            'observacoes': orcamento.observacoes,
        }
        form = FactureForm(initial=initial_data)

    from .models import Produto
    produtos = Produto.objects.filter(ativo=True).order_by('referencia')

    context = {
        'form': form,
        'orcamento': orcamento,
        'cliente': cliente,
        'produtos': produtos,
        'itens_orcamento': orcamento.itens.all(),
        'page_title': f'Créer Facture depuis Devis #{orcamento_numero}',
    }
    return render(request, 'orcamentos/admin_elaborar_facture.html', context)

@staff_member_required
def admin_editar_fatura(request, numero):
    """Editar uma fatura existente"""
    fatura = get_object_or_404(Facture, numero=numero)

    if request.method == 'POST':
        form = FactureForm(request.POST, instance=fatura)
        if form.is_valid():
            fatura = form.save()

            # Processar itens atualizados
            itens_data = request.POST.get('itens_json', '[]')
            try:
                # Remover itens existentes
                fatura.itens.all().delete()

                # Criar novos itens
                itens = json.loads(itens_data)
                for item_data in itens:
                    if item_data.get('descricao'):
                        ItemFacture.objects.create(
                            facture=fatura,
                            produto_id=item_data.get('produto_id') if item_data.get('produto_id') else None,
                            referencia=item_data.get('referencia', ''),
                            descricao=item_data.get('descricao'),
                            unidade=item_data.get('unidade', 'unite'),
                            atividade=item_data.get('atividade', 'marchandise'),
                            quantidade=Decimal(str(item_data.get('quantidade', 1))),
                            preco_unitario_ht=Decimal(str(item_data.get('preco_unitario_ht', 0))),
                            remise_percentual=Decimal(str(item_data.get('remise_percentual', 0))),
                            taxa_tva=item_data.get('taxa_tva', '20'),
                        )
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                messages.warning(request, f'Erro ao processar itens: {str(e)}')

            # Recalcular totais
            fatura.calcular_totais()

            action = request.POST.get('action', 'draft')
            if action == 'send':
                fatura.status = 'envoyee'
                fatura.data_envio = timezone.now()
                fatura.save()
                messages.success(request, f'Facture {fatura.numero} mise à jour et envoyée!')
            else:
                messages.success(request, f'Facture {fatura.numero} mise à jour.')

            return redirect('orcamentos:admin_fatura_detail', numero=fatura.numero)
    else:
        form = FactureForm(instance=fatura)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    clientes = User.objects.filter(is_active=True).exclude(is_staff=True).order_by('first_name', 'last_name')

    from .models import Produto
    produtos = Produto.objects.filter(ativo=True).order_by('referencia')

    context = {
        'form': form,
        'fatura': fatura,
        'clientes': clientes,
        'produtos': produtos,
        'page_title': f'Éditer Facture #{numero}',
    }
    return render(request, 'orcamentos/admin_editar_facture.html', context)

@staff_member_required
def admin_deletar_fatura(request, numero):
    """Deletar uma fatura"""
    fatura = get_object_or_404(Facture, numero=numero)

    if request.method == 'POST':
        numero_fatura = fatura.numero
        fatura.delete()
        messages.success(request, f'Facture {numero_fatura} supprimée avec succès!')
        return redirect('orcamentos:admin_faturas_list')

    context = {
        'fatura': fatura,
        'page_title': f'Supprimer Facture #{numero}',
    }
    return render(request, 'orcamentos/admin_deletar_fatura.html', context)

@staff_member_required
def admin_marcar_fatura_paga(request, numero):
    """Marcar fatura como paga"""
    fatura = get_object_or_404(Facture, numero=numero)

    if request.method == 'POST':
        data_pagamento = request.POST.get('data_pagamento')
        if data_pagamento:
            fatura.marcar_como_paga(data_pagamento)
        else:
            fatura.marcar_como_paga()

        messages.success(request, f'Facture {fatura.numero} marquée comme payée!')
        return redirect('orcamentos:admin_fatura_detail', numero=numero)

    return redirect('orcamentos:admin_fatura_detail', numero=numero)

@login_required
@staff_member_required
def buscar_clientes_ajax(request):
    """Busca clientes via AJAX para uso nas faturas"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'clientes': []})

    clientes = User.objects.filter(
        is_active=True,
        is_staff=False
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(username__icontains=query)
    )[:10]

    clientes_data = []
    for cliente in clientes:
        nome_completo = f"{cliente.first_name} {cliente.last_name}".strip()
        if not nome_completo:
            nome_completo = cliente.username

        clientes_data.append({
            'id': cliente.id,
            'nome_completo': nome_completo,
            'email': cliente.email,
            'username': cliente.username,
            'first_name': cliente.first_name,
            'last_name': cliente.last_name
        })

    return JsonResponse({'clientes': clientes_data})

@login_required
@staff_member_required
def buscar_produtos_ajax(request):
    """Busca produtos via AJAX para uso nos orçamentos"""
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'produtos': []})

    try:
        from .models import Produto
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
                'nome': produto.descricao,  # Usando descricao como nome
                'descricao': produto.descricao,
                'preco_venda': float(produto.preco_venda_ht),  # Mudando para preco_venda que o JS espera
                'preco_venda_ht': float(produto.preco_venda_ht),
                'preco_compra_ht': float(produto.preco_compra),  # Campo correto é preco_compra
                'unidade': produto.unidade,
                'categoria': '',  # Removendo categoria por enquanto
                'fornecedor': produto.fornecedor.nome if produto.fornecedor else ''
            })

        return JsonResponse({'produtos': produtos_data})

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro na busca de produtos: {str(e)}")
        return JsonResponse({'produtos': [], 'error': str(e)})
