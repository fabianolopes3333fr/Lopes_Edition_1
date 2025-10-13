from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from orcamentos.forms import OrcamentoForm, ItemOrcamentoFormSet
from orcamentos.models import SolicitacaoOrcamento, StatusOrcamento, Orcamento, ItemOrcamento
from orcamentos.services import NotificationService
# NOVO: importar agendamentos
from orcamentos.models import AgendamentoOrcamento, StatusAgendamento


@staff_member_required
def admin_dashboard(request):
    """Dashboard administrativo"""
    # Estatísticas gerais
    total_solicitacoes = SolicitacaoOrcamento.objects.count()
    solicitacoes_pendentes = SolicitacaoOrcamento.objects.filter(status=StatusOrcamento.PENDENTE).count()
    orcamentos_enviados = Orcamento.objects.filter(status=StatusOrcamento.ENVIADO).count()
    orcamentos_aceitos = Orcamento.objects.filter(status=StatusOrcamento.ACEITO).count()

    # Estatísticas de órfãos adicionais exigidas pelos testes
    qs_orfas = SolicitacaoOrcamento.objects.filter(cliente__isnull=True)
    solicitacoes_orfas = qs_orfas.count()

    # Emails de órfãos que possuem usuários correspondentes (vinculáveis)
    emails_orfas = list(qs_orfas.values_list('email_solicitante', flat=True))
    emails_unicos = set(emails_orfas)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    orfaos_vinculaveis = sum(1 for email in emails_unicos if User.objects.filter(email__iexact=email).exists())

    # Solicitações recentes
    solicitacoes_recentes = SolicitacaoOrcamento.objects.order_by('-created_at')[:5]

    # Orçamentos recentes
    orcamentos_recentes = Orcamento.objects.order_by('-data_elaboracao')[:5]

    # Receita do mês
    receita_mes = Orcamento.objects.filter(
        status=StatusOrcamento.ACEITO,
        data_resposta_cliente__month=timezone.now().month
    ).aggregate(Sum('total'))['total__sum'] or 0

    # Rendez-vous (agendamentos): pendentes e próximos
    agendamentos_pendentes = AgendamentoOrcamento.objects.filter(
        status=StatusAgendamento.PENDENTE
    ).order_by('data_horario')[:5]

    agendamentos_proximos = AgendamentoOrcamento.objects.filter(
        status=StatusAgendamento.CONFIRMADO,
        data_horario__gte=timezone.now()
    ).order_by('data_horario')[:5]

    context = {
        'total_solicitacoes': total_solicitacoes,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'orcamentos_enviados': orcamentos_enviados,
        'orcamentos_aceitos': orcamentos_aceitos,
        'solicitacoes_recentes': solicitacoes_recentes,
        'orcamentos_recentes': orcamentos_recentes,
        'receita_mes': receita_mes,
        'page_title': 'Dashboard Admin',
        # novas chaves para testes
        'solicitacoes_orfas': solicitacoes_orfas,
        'orfaos_vincuLaveis': orfaos_vinculaveis,
        # NOVO: agendamentos
        'agendamentos_pendentes': agendamentos_pendentes,
        'agendamentos_proximos': agendamentos_proximos,
    }
    return render(request, 'orcamentos/admin_dashboard.html', context)


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

    # Registrar visualização na auditoria
    from .auditoria import AuditoriaManager
    AuditoriaManager.registrar_visualizacao(
        usuario=request.user,
        objeto=solicitacao,
        request=request
    )

    context = {
        'solicitacao': solicitacao,
        'page_title': f'Demande #{solicitacao.numero}'
    }

    return render(request, 'orcamentos/admin_solicitacao_detail.html', context)


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

                for item in itens:
                    print(f"DEBUG: processando item: {item}")  # Debug
                    if item.get('descricao'):  # Só criar se tiver descrição
                        item_criado = ItemOrcamento.objects.create(
                            orcamento=orcamento,
                            produto_id=item.get('produto_id') if item.get('produto_id') else None,
                            referencia=item.get('referencia', ''),
                            descricao=item.get('descricao'),
                            unidade=item.get('unidade', 'unite'),
                            atividade=item.get('atividade', 'marchandise'),
                            quantidade=Decimal(str(item.get('quantidade', 1))),
                            preco_unitario_ht=Decimal(str(item.get('preco_unitario_ht', 0))),
                            remise_percentual=Decimal(str(item.get('remise_percentual', 0))),
                            taxa_tva=item.get('taxa_tva', '20'),
                        )
                        print(f"DEBUG: item criado com ID: {item_criado.id}")  # Debug
                    else:
                        print(f"DEBUG: item ignorado - sem descrição")  # Debug
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"DEBUG: erro ao processar itens: {str(e)}")  # Debug
                messages.warning(request, f'Erro ao processar itens: {str(e)}')
                pass

            # Processar acomptes atualizados
            acomptes_data = request.POST.get('acomptes_json', '[]')
            print(f"DEBUG: acomptes_data recebido: {acomptes_data}") # Debug

            try:
                from .models import AcompteOrcamento
                from datetime import datetime

                # Remover acomptes existentes para recriá-los
                orcamento.acomptes.all().delete()

                acomptes = json.loads(acomptes_data)
                print(f"DEBUG: acomptes parseados: {acomptes}") # Debug

                for acompte_data in acomptes:
                    print(f"DEBUG: processando acompte: {acompte_data}") # Debug
                    if acompte_data.get('descricao') and acompte_data.get('data_vencimento'):
                        data_vencimento = datetime.strptime(acompte_data.get('data_vencimento'), '%Y-%m-%d').date()

                        acompte_criado = AcompteOrcamento.objects.create(
                            orcamento=orcamento,
                            criado_por=request.user,
                            tipo=acompte_data.get('tipo', 'inicial'),
                            descricao=acompte_data.get('descricao'),
                            percentual=Decimal(str(acompte_data.get('percentual', 0))),
                            data_vencimento=data_vencimento,
                            tipo_pagamento=acompte_data.get('tipo_pagamento', 'virement'),
                        )
                        acompte_criado.calcular_valores()
                        acompte_criado.save()
                        print(f"DEBUG: acompte criado com ID: {acompte_criado.id}") # Debug
                    else:
                        print(f"DEBUG: acompte ignorado - dados incompletos") # Debug

            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"DEBUG: erro ao processar acomptes: {str(e)}") # Debug
                messages.warning(request, f'Erro ao processar acomptes: {str(e)}')
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

                # Enviar notificações
                NotificationService.enviar_email_orcamento_enviado(orcamento)

                messages.success(request, f'Devis {orcamento.numero} créé et envoyé avec succès!')
                return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)
            else:
                messages.success(request, f'Devis {orcamento.numero} sauvegardé comme brouillon.')
                return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)

    else:
        # Pré-preencher o formulário com dados da solicitação
        initial_data = {
            'titulo': f"Devis pour {solicitacao.get_tipo_servico_display()}",
            'descricao': solicitacao.descricao_servico,
            'prazo_execucao': 30,
            'validade_orcamento': timezone.now().date() + timedelta(days=30),
            # Correção: usar chave válida para condições de pagamento com acompte inicial 30%
            'condicoes_pagamento': 'acompte_30',
            'desconto': 0,
        }
        form = OrcamentoForm(initial=initial_data)

    context = {
        'form': form,
        'solicitacao': solicitacao,
        'page_title': f'Élaborer Devis - #{solicitacao.numero}',
    }
    return render(request, 'orcamentos/admin_elaborar_orcamento.html', context)

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