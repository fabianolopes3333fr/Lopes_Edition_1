# ============ VIEWS PARA CLIENTES ============
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404

from orcamentos.auditoria import AuditoriaManager
from orcamentos.forms import ProjetoForm, SolicitacaoOrcamentoProjetoForm
from orcamentos.models import Projeto, StatusProjeto, Orcamento
from orcamentos.services import NotificationService


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

    # Orçamentos do projeto
    orcamentos = Orcamento.objects.filter(
        solicitacao__projeto=projeto
    ).order_by('-data_elaboracao')

    context = {
        'projeto': projeto,
        'anexos': anexos,
        'solicitacoes': solicitacoes,
        'orcamentos': orcamentos,
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


# ============ VIEWS ADMINISTRATIVAS DE PROJETOS ============

@login_required
def admin_projetos_list(request):
    """Lista administrativa de projetos"""
    if request.user.account_type != 'ADMINISTRATOR':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    # Filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    cliente_filter = request.GET.get('cliente', '')

    # Query inicial
    projetos = Projeto.objects.all()

    # Aplicar filtros
    if search:
        projetos = projetos.filter(
            Q(titulo__icontains=search) |
            Q(descricao__icontains=search) |
            Q(cliente__first_name__icontains=search) |
            Q(cliente__last_name__icontains=search) |
            Q(cliente__email__icontains=search)
        )

    if status_filter:
        projetos = projetos.filter(status=status_filter)

    if cliente_filter:
        projetos = projetos.filter(
            Q(cliente__first_name__icontains=cliente_filter) |
            Q(cliente__last_name__icontains=cliente_filter) |
            Q(cliente__email__icontains=cliente_filter)
        )

    # Ordenação
    projetos = projetos.order_by('-created_at')

    # Paginação
    paginator = Paginator(projetos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Estatísticas
    total_projetos = Projeto.objects.count()
    projetos_planejando = Projeto.objects.filter(status=StatusProjeto.PLANEJANDO).count()
    projetos_em_andamento = Projeto.objects.filter(status=StatusProjeto.EM_ANDAMENTO).count()
    projetos_concluido = Projeto.objects.filter(status=StatusProjeto.CONCLUIDO).count()
    projetos_pausado = Projeto.objects.filter(status=StatusProjeto.PAUSADO).count()
    projetos_cancelado = Projeto.objects.filter(status=StatusProjeto.CANCELADO).count()

    # Listas para filtros
    status_choices = StatusProjeto.choices
    clientes = Projeto.objects.select_related('cliente').values_list(
        'cliente__first_name', 'cliente__last_name', 'cliente__email'
    ).distinct().order_by('cliente__first_name')

    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'cliente_filter': cliente_filter,
        'status_choices': status_choices,
        'clientes': clientes,
        'stats': {
            'total_projetos': total_projetos,
            'projetos_planejando': projetos_planejando,
            'projetos_em_andamento': projetos_em_andamento,
            'projetos_concluido': projetos_concluido,
            'projetos_pausado': projetos_pausado,
            'projetos_cancelado': projetos_cancelado,
        }
    }

    return render(request, 'dashboard/admin_projetos_list.html', context)


@login_required
def admin_projeto_detail(request, uuid):
    """Detalhes administrativos do projeto"""
    if request.user.account_type != 'ADMINISTRATOR':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    projeto = get_object_or_404(Projeto, uuid=uuid)

    # Anexos do projeto
    anexos = projeto.anexos.all()

    # Solicitações de orçamento deste projeto
    solicitacoes = projeto.solicitacoes_orcamento.all().order_by('-created_at')

    # Orçamentos do projeto
    orcamentos = Orcamento.objects.filter(
        solicitacao__projeto=projeto
    ).order_by('-data_elaboracao')

    context = {
        'projeto': projeto,
        'anexos': anexos,
        'solicitacoes': solicitacoes,
        'orcamentos': orcamentos,
        'status_choices': StatusProjeto.choices,  # Adicionar as choices de status
    }

    return render(request, 'dashboard/admin_projeto_detail.html', context)


@login_required
def admin_projeto_change_status(request, uuid):
    """Alterar status do projeto"""
    if request.user.account_type != 'ADMINISTRATOR':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    projeto = get_object_or_404(Projeto, uuid=uuid)

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in [choice[0] for choice in StatusProjeto.choices]:
            status_anterior = projeto.get_status_display()
            projeto.status = novo_status
            projeto.save()

            # Registrar na auditoria
            AuditoriaManager.registrar_mudanca_status_projeto(
                usuario=request.user,
                projeto=projeto,
                status_anterior=status_anterior,
                status_novo=projeto.get_status_display(),
                request=request
            )

            messages.success(
                request,
                f"Status do projeto '{projeto.titulo}' alterado para '{projeto.get_status_display()}'"
            )
        else:
            messages.error(request, "Status inválido.")

    return redirect('orcamentos:admin_projeto_detail', uuid=projeto.uuid)


@login_required
def admin_criar_orcamento_projeto(request, uuid):
    """Criar orçamento vinculado a um projeto específico"""
    if request.user.account_type != 'ADMINISTRATOR':
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    from orcamentos.models import SolicitacaoOrcamento, StatusOrcamento

    projeto = get_object_or_404(Projeto, uuid=uuid)

    if not projeto.cliente:
        messages.error(request, "Ce projeto n'a pas de client associé. Veuillez d'abord associer un client au projeto.")
        return redirect('orcamentos:admin_projeto_detail', uuid=projeto.uuid)

    # Verificar se já existe uma solicitação para este projeto
    solicitacao = projeto.solicitacoes_orcamento.first()
    
    if not solicitacao:
        # Criar uma solicitação vinculada ao projeto
        solicitacao = SolicitacaoOrcamento.objects.create(
            cliente=projeto.cliente,
            projeto=projeto,
            nome_solicitante=projeto.cliente.get_full_name(),
            email_solicitante=projeto.cliente.email,
            telefone_solicitante=projeto.cliente.phone or '',
            endereco=projeto.endereco_projeto or '',
            cidade=projeto.cidade_projeto or '',
            cep=projeto.cep_projeto or '',
            tipo_servico=projeto.tipo_servico or 'outro',
            descricao_servico=projeto.descricao or f'Orçamento para projeto: {projeto.titulo}',
            orcamento_maximo=projeto.orcamento_estimado or Decimal('5000.00'),
            data_inicio_desejada=projeto.data_inicio_desejada or (timezone.now().date() + timedelta(days=30)),
            status=StatusOrcamento.EM_ELABORACAO
        )

        messages.success(request, f"Demande de devis créée para o projeto '{projeto.titulo}'")

    # Redirecionar para a página de elaboração do orçamento
    return redirect('orcamentos:admin_elaborar_orcamento', numero=solicitacao.numero)
