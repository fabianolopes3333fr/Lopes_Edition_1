from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from decimal import Decimal
import json

from accounts.models import User
from . models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    AnexoProjeto, StatusOrcamento, StatusProjeto, Facture, ItemFacture,
    AcompteOrcamento, AgendamentoOrcamento, StatusAgendamento, TipoAgendamento
)
from .forms import (
	ProjetoForm, SolicitacaoOrcamentoPublicoForm, SolicitacaoOrcamentoProjetoForm,
	OrcamentoForm, AnexoProjetoForm, FactureForm, ItemOrcamentoFormSet,
)
from .auditoria import TipoAcao
from .services import NotificationService

# Adicionar importações faltantes
from .auditoria import AuditoriaManager
from datetime import datetime  # adicionado para parse de datas
from django.utils.dateparse import parse_datetime


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


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

    # MELHORIA: Verificar se há orçamentos órfãos com o mesmo email
    solicitacoes_orfas = SolicitacaoOrcamento.objects.filter(
        cliente__isnull=True,
        email_solicitante__iexact=request.user.email
    )

    # Se encontrar orçamentos órfãos, vincular automaticamente e notificar
    if solicitacoes_orfas.exists():
        count = solicitacoes_orfas.count()

        # Registrar detecção na auditoria
        from .auditoria import AuditoriaManager
        AuditoriaManager.registrar_deteccao_orcamento_orfao(
            usuario=request.user,
            email=request.user.email,
            quantidade_encontrada=count,
            request=request
        )

        # Registrar vinculações individuais na auditoria
        for solicitacao in solicitacoes_orfas:
            AuditoriaManager.registrar_vinculacao_orcamento_orfao(
                usuario=request.user,
                solicitacao=solicitacao,
                request=request,
                origem="dashboard_cliente"
            )

        solicitacoes_orfas.update(cliente=request.user)

        messages.info(
            request,
            f'🎉 Nous avons trouvé et associé {count} demande{"s" if count > 1 else ""} de devis '
            f'précédente{"s" if count > 1 else ""} à votre compte!'
        )

        # Atualizar as queries para incluir os recém-vinculados
        solicitacoes = SolicitacaoOrcamento.objects.filter(
            cliente=request.user
        ).order_by('-created_at')

        orcamentos = Orcamento.objects.filter(
            solicitacao__cliente=request.user
        ).order_by('-data_elaboracao')

    context = {
        'solicitacoes': solicitacoes,
        'orcamentos': orcamentos,
    }

    return render(request, 'orcamentos/cliente_orcamentos.html', context)


@login_required
def cliente_devis_detail(request, numero):
    """Detalhes de um orçamento específico do cliente"""
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
def cliente_devis_accepter(request, numero):
    """Aceitar um orçamento"""
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

    # Usar a mesma lógica do admin_orcamento_pdf_html
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
        if abs(percentual_tva - Decimal('20')) < Decimal('0.01'):
            taxa_tva_media = "20"
        elif abs(percentual_tva - Decimal('10')) < Decimal('0.01'):
            taxa_tva_media = "10"
        elif abs(percentual_tva - Decimal('5.5')) < Decimal('0.01'):
            taxa_tva_media = "5.5"
        elif abs(percentual_tva - Decimal('0')) < Decimal('0.01'):
            taxa_tva_media = "0"
        else:
            taxa_tva_media = f"{percentual_tva:.1f}"

    # Totais finais (já com desconto global aplicado via model)
    subtotal_final_ht = orcamento.total
    taxe_finale = orcamento.valor_tva
    subtotal_final_ttc = orcamento.total_ttc

    # Acomptes e saldo (baseado nos acomptes configurados para este devis)
    total_acomptes_ttc = sum((a.valor_ttc for a in orcamento.acomptes.all()), Decimal('0.00'))
    solde_ttc = max(Decimal('0.00'), subtotal_final_ttc - total_acomptes_ttc)

    context = {
        'orcamento': orcamento,
        'items_data': items_data,
        'subtotal_ht': subtotal_ht,
        'remise_global': remise_global,
        'valor_remise': valor_remise_global,
        'subtotal_apres_remise_ht': subtotal_final_ht,
        'taxe_finale': taxe_finale,
        'subtotal_apres_remise_ttc': subtotal_final_ttc,
        'taxa_tva_media': taxa_tva_media,
        'total_acomptes_ttc': total_acomptes_ttc,
        'solde_ttc': solde_ttc,
        'date_generation': datetime.now(),
        'company_info': {
            'name': 'LOPES DE SOUZA fabiano',
            'address': '261 Chemin de La Castellane',
            'city': '31790 Saint Sauveur, France',
            'phone': '+33 7 69 27 37 76',
            'email': 'contact@lopespeinture.fr',
            'siret': '978 441 756 00019',
            'ape': '4334Z',
            'tva': 'FR35978441756',
            'site': 'www.lopespeinture.fr'
        }
    }

    html_content = render_to_string('orcamentos/admin/devis_pdf_html.html', context)

    # Para desenvolvimento, retornar HTML diretamente
    if request.GET.get('debug') == '1':
        return HttpResponse(html_content, content_type='text/html')
    else:
        # Preparar para download como PDF (usando print do navegador)
        response = HttpResponse(html_content, content_type='text/html')
        filename = f"devis_{orcamento.numero}_{orcamento.solicitacao.nome_solicitante.replace(' ', '_')}.html"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response



# ============ VIEWS ADMINISTRATIVAS ============



@staff_member_required
def admin_criar_orcamento(request, numero):
   
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
            data_inicio_desejada=timezone.now().date() + timedelta(days=30),
            status=StatusOrcamento.EM_ELABORACAO
        )

        # Criar o orçamento
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            fatura = form.save(commit=False)
            fatura.solicitacao = solicitacao
            fatura.elaborado_por = request.user
            fatura.save()

            # Processar itens do orçamento enviados via AJAX
            itens_data = request.POST.get('itens_json', '[]')
            try:
                itens = json.loads(itens_data)
                for item_data in itens:
                    if item_data.get('descricao'):
                        ItemOrcamento.objects.create(
                            orcamento=fatura,
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

                solicitacao.status = StatusOrcamento.ENVIADO
                solicitacao.save()

                messages.success(request, f'Devis {fatura.numero} créé et envoyé avec succès pour {cliente.nom_complet}!')
            else:
                messages.success(request, f'Devis {fatura.numero} sauvegardé en brouillon pour {cliente.nom_complet}.')

            return redirect('orcamentos:admin_orcamento_detail', numero=fatura.numero)
    else:
        form = OrcamentoForm()

    # Lista de clientes para o formulário
    clientes = User.objects.filter(is_active=True).exclude(is_staff=True).order_by('first_name', 'last_name')

    from .models import Produto
    produtos = Produto.objects.filter(ativo=True).order_by('referencia')

    context = {
        'form': form,
        'clientes': clientes,
        'produtos': produtos,
        'page_title': f'Criar Devis para {cliente.nom_complet}',
        'is_cliente_direto': True,  # Flag para identificar que é criação direta
    }

    return render(request, 'orcamentos/admin_elaborar_orcamento.html', context)












@staff_member_required
def admin_orcamentos(request):
    """Lista de orçamentos para administradores"""
    orcamentos = Orcamento.objects.all().order_by('-data_elaboracao')

    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        orcamentos = orcamentos.filter(status=status_filter)

    # Paginação
    paginator = Paginator(orcamentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': StatusOrcamento.choices,
        'current_status': status_filter,
        'page_title': 'Devis'
    }

    return render(request, 'orcamentos/admin_orcamentos.html', context)


@staff_member_required
def admin_orcamento_detail(request, numero):
    """Detalhes de um orçamento específico"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    # Registrar visualização na auditoria
    from .auditoria import AuditoriaManager
    AuditoriaManager.registrar_visualizacao(
        usuario=request.user,
        objeto=orcamento,
        request=request
    )

    context = {
        'orcamento': orcamento,
        'page_title': f'Devis #{orcamento.numero}'
    }

    return render(request, 'orcamentos/admin_orcamento_detail.html', context)


@staff_member_required
def admin_editar_orcamento(request, numero):
    """Editar um orçamento existente."""
    orcamento = get_object_or_404(Orcamento, numero=numero)
    solicitacao = orcamento.solicitacao

    if request.method == 'POST':
        form = OrcamentoForm(request.POST, instance=orcamento)
        if form.is_valid():
            orcamento = form.save(commit=False)

            # Salvar itens do orçamento a partir do JSON
            itens_json_str = request.POST.get('itens_json', '[]')
            itens_data = json.loads(itens_json_str)

            # Deletar itens antigos para substituí-los
            orcamento.itens.all().delete()
            for item_data in itens_data:
                ItemOrcamento.objects.create(
                    orcamento=orcamento,
                    referencia=item_data.get('referencia'),
                    descricao=item_data.get('descricao'),
                    unidade=item_data.get('unidade'),
                    atividade=item_data.get('atividade'),
                    quantidade=Decimal(str(item_data.get('quantidade', '0'))),
                    preco_unitario_ht=Decimal(str(item_data.get('preco_unitario_ht', '0'))),
                    taxa_tva=item_data.get('taxa_tva', '20'),
                    remise_percentual=Decimal(str(item_data.get('remise_percentual', '0')))
                )

            # Salvar acomptes a partir do JSON
            acomptes_json_str = request.POST.get('acomptes_json', '[]')
            acomptes_data = json.loads(acomptes_json_str)
            # Simplificação: deletar e recriar
            orcamento.acomptes.all().delete()
            for acompte_data in acomptes_data:
                try:
                    data_venc = acompte_data.get('data_vencimento')
                    data_vencimento = datetime.strptime(data_venc, '%Y-%m-%d').date() if data_venc else None
                except Exception:
                    data_vencimento = None
                acompte = AcompteOrcamento.objects.create(
                    orcamento=orcamento,
                    criado_por=request.user,
                    tipo=acompte_data.get('tipo'),
                    descricao=acompte_data.get('descricao'),
                    percentual=Decimal(str(acompte_data.get('percentual', '0'))),
                    data_vencimento=data_vencimento,
                    tipo_pagamento=acompte_data.get('tipo_pagamento')
                )
                # Calcular valores (HT/TVA/TTC) com base no orçamento atual
                acompte.calcular_valores()
                acompte.save()

            orcamento.save() # Salva o orçamento principal
            form.save_m2m() # Salva relações ManyToMany se houver

            messages.success(request, f'Devis #{orcamento.numero} mis à jour avec succès!')
            
            action = request.POST.get('action')
            if action == 'send':
                # Lógica para enviar o orçamento (mudar status, enviar email, etc.)
                orcamento.status = StatusOrcamento.ENVIADO
                orcamento.data_envio = timezone.now()
                orcamento.save()
                NotificationService.enviar_email_orcamento_enviado(orcamento)
                messages.info(request, f'Devis #{orcamento.numero} envoyé au client.')

            return redirect('orcamentos:admin_orcamento_detail', numero=orcamento.numero)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")

    else:
        form = OrcamentoForm(instance=orcamento)

    # Passar os itens e acomptes existentes para o template em formato JSON
    itens_list = list(orcamento.itens.values(
        'referencia', 'descricao', 'unidade', 'atividade', 'quantidade',
        'preco_unitario_ht', 'taxa_tva', 'remise_percentual'
    ))
    itens_json = json.dumps(itens_list, cls=DecimalEncoder)

    acomptes_list = list(orcamento.acomptes.values(
        'id', 'tipo', 'descricao', 'percentual', 'data_vencimento', 'status', 'tipo_pagamento'
    ))
    acomptes_json = json.dumps(acomptes_list, cls=DecimalEncoder, default=str)


    context = {
        'form': form,
        'orcamento': orcamento,
        'solicitacao': solicitacao,
        'itens_json': itens_json,
        'acomptes_json': acomptes_json,
        'page_title': f'Éditer Devis #{orcamento.numero}'
    }
    return render(request, 'orcamentos/admin_editar_orcamento.html', context)


@staff_member_required
def admin_enviar_orcamento(request, numero):
    """Enviar orçamento para o cliente"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    if orcamento.status not in [StatusOrcamento.PENDENTE, StatusOrcamento.EM_ELABORACAO]:
        messages.error(request, 'Ce devis ne peut pas être envoyé.')
        return redirect('orcamentos:admin_orcamento_detail', numero=numero)

    if request.method == 'POST':
        # Atualizar status
        dados_anteriores = {'status': orcamento.status}

        orcamento.status = StatusOrcamento.ENVIADO
        orcamento.data_envio = timezone.now()
        orcamento.save()

        # Atualizar status da solicitação
        orcamento.solicitacao.status = StatusOrcamento.ENVIADO
        orcamento.solicitacao.save()

        # Registrar envio na auditoria
        AuditoriaManager.registrar_envio_orcamento(
            usuario=request.user,
            orcamento=orcamento,
            request=request
        )

        # Enviar email para o cliente
        try:
            NotificationService.enviar_email_orcamento_enviado(orcamento)
            messages.success(request, 'Devis envoyé avec succès!')
        except Exception as e:
            messages.warning(request, 'Devis mis à jour mais erro lors de l\'envoi de l\'email.')
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao enviar email do orçamento {numero}: {e}")

        return redirect('orcamentos:admin_orcamento_detail', numero=numero)

    context = {
        'orcamento': orcamento,
        'page_title': f'Envoyer Devis #{orcamento.numero}'
    }

    return render(request, 'orcamentos/admin_enviar_orcamento.html', context)


@staff_member_required
def admin_orcamento_pdf(request, numero):
    """Gerar PDF do orçamento para administradores"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    # Registrar download na auditoria
    from .auditoria import AuditoriaManager
    AuditoriaManager.registrar_acao(
        usuario=request.user,
        acao=TipoAcao.DOWNLOAD,
        objeto=orcamento,
        descricao=f"Téléchargement PDF du devis {orcamento.numero} par l'admin",
        funcionalidade="Download PDF Admin",
        request=request
    )
    from .pdf_generator import gerar_pdf_orcamento
    try:
        pdf_buffer = gerar_pdf_orcamento(orcamento)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{numero}.pdf"'
        return response
    except Exception as e:
        messages.error(request, 'Erreur lors de la génération du PDF.')
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar PDF do orçamento {numero}: {e}")
        return redirect('orcamentos:admin_orcamento_detail', numero=numero)


@staff_member_required
def admin_orcamento_pdf_html(request, numero):
    """Gerar PDF HTML do orçamento para administradores (nova versão completa)"""
    orcamento = get_object_or_404(Orcamento, numero=numero)

    # Registrar download na auditoria
    from .auditoria import AuditoriaManager
    AuditoriaManager.registrar_acao(
        usuario=request.user,
        acao=TipoAcao.DOWNLOAD,
        objeto=orcamento,
        descricao=f"Téléchargement PDF HTML du devis {orcamento.numero} par l'admin",
        funcionalidade="Download PDF HTML Admin",
        request=request
    )

    # Usar a mesma lógica do cliente_devis_pdf mas com template admin
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
        if abs(percentual_tva - Decimal('20')) < Decimal('0.01'):
            taxa_tva_media = "20"
        elif abs(percentual_tva - Decimal('10')) < Decimal('0.01'):
            taxa_tva_media = "10"
        elif abs(percentual_tva - Decimal('5.5')) < Decimal('0.01'):
            taxa_tva_media = "5.5"
        elif abs(percentual_tva - Decimal('0')) < Decimal('0.01'):
            taxa_tva_media = "0"
        else:
            taxa_tva_media = f"{percentual_tva:.1f}"

    # Totais finais (já com desconto global aplicado via model)
    subtotal_final_ht = orcamento.total
    taxe_finale = orcamento.valor_tva
    subtotal_final_ttc = orcamento.total_ttc

    # Acomptes e saldo
    total_acomptes_ttc = sum((a.valor_ttc for a in orcamento.acomptes.all()), Decimal('0.00'))
    solde_ttc = max(Decimal('0.00'), subtotal_final_ttc - total_acomptes_ttc)

    context = {
        'orcamento': orcamento,
        'items_data': items_data,
        'subtotal_ht': subtotal_ht,
        'remise_global': remise_global,
        'valor_remise': valor_remise_global,
        'subtotal_apres_remise_ht': subtotal_final_ht,
        'taxe_finale': taxe_finale,
        'subtotal_apres_remise_ttc': subtotal_final_ttc,
        'taxa_tva_media': taxa_tva_media,
        'total_acomptes_ttc': total_acomptes_ttc,
        'solde_ttc': solde_ttc,
        'date_generation': datetime.now(),
        'company_info': {
            'name': 'LOPES DE SOUZA fabiano',
            'address': '261 Chemin de La Castellane',
            'city': '31790 Saint Sauveur, France',
            'phone': '+33 7 69 27 37 76',
            'email': 'contact@lopespeinture.fr',
            'siret': '978 441 756 00019',
            'ape': '4334Z',
            'tva': 'FR35978441756',
            'site': 'www.lopespeinture.fr'
        }
    }

    html_content = render_to_string('orcamentos/admin/devis_pdf_html.html', context)

    # Verificar se é para visualizar ou baixar
    download = request.GET.get('download', 'true')

    if download == 'false' or request.GET.get('debug') == '1':
        # Exibir no navegador
        return HttpResponse(html_content, content_type='text/html')
    else:
        # Preparar para download como PDF (usando print do navegador)
        response = HttpResponse(html_content, content_type='text/html')
        filename = f"devis_{orcamento.numero}_{orcamento.solicitacao.nome_solicitante.replace(' ', '_')}.html"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response




# ============ VIEWS PARA ACOMPTES ============

@staff_member_required
def admin_orcamento_acomptes(request, numero):
    """Lista de acomptes de um orçamento específico"""
    orcamento = get_object_or_404(Orcamento, numero=numero)
    
    # Buscar todos os acomptes deste orçamento
    acomptes = AcompteOrcamento.objects.filter(orcamento=orcamento).order_by('data_vencimento')
    
    # Calcular estatísticas
    total_acomptes_valor = acomptes.aggregate(Sum('valor_ttc'))['valor_ttc__sum'] or Decimal('0.00')
    total_acomptes_percentual = acomptes.aggregate(Sum('percentual'))['percentual__sum'] or Decimal('0.00')
    
    # Calcular total pago
    acomptes_pagos = acomptes.filter(status='pago')
    total_pago = acomptes_pagos.aggregate(Sum('valor_ttc'))['valor_ttc__sum'] or Decimal('0.00')
    
    # Calcular saldo restante
    saldo_restante = orcamento.total_ttc - total_pago
    
    # Verificar se pode criar novos acomptes (não ultrapassar 100% e não ter saldo negativo)
    pode_criar_acompte = (
        total_acomptes_percentual < 100 and
        saldo_restante > 0 and
        orcamento.status in [StatusOrcamento.ACEITO, StatusOrcamento.EM_ELABORACAO, StatusOrcamento.ENVIADO]
    )
    
    context = {
        'orcamento': orcamento,
        'acomptes': acomptes,
        'total_acomptes_valor': total_acomptes_valor,
        'total_acomptes_percentual': total_acomptes_percentual,
        'total_pago': total_pago,
        'saldo_restante': saldo_restante,
        'pode_criar_acompte': pode_criar_acompte,
        'page_title': f'Acomptes - Devis #{numero}',
    }
    
    return render(request, 'orcamentos/admin_orcamento_acomptes.html', context)


@staff_member_required
def admin_criar_acompte(request, numero):
    """Criar novo acompte para um orçamento"""
    orcamento = get_object_or_404(Orcamento, numero=numero)
    
    # Verificar se ainda pode criar acomptes
    acomptes_existentes = AcompteOrcamento.objects.filter(orcamento=orcamento)
    total_percentual = acomptes_existentes.aggregate(Sum('percentual'))['percentual__sum'] or Decimal('0.00')
    
    if total_percentual >= 100:
        messages.error(request, 'Impossible de créer un nouvel acompte: 100% déjà atteint.')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=numero)
    
    if request.method == 'POST':
        try:
            # Extrair dados do formulário
            tipo = request.POST.get('tipo', 'inicial')
            descricao = request.POST.get('descricao', '')
            percentual = Decimal(request.POST.get('percentual', '30'))
            data_vencimento = request.POST.get('data_vencimento')
            tipo_pagamento = request.POST.get('tipo_pagamento', 'virement')
            
            # Validar percentual
            if percentual <= 0 or percentual > 100:
                messages.error(request, 'Le pourcentage doit être entre 1 et 100.')
                return redirect('orcamentos:admin_orcamento_acomptes', numero=numero)
            
            # Verificar se não ultrapassa 100%
            if total_percentual + percentual > 100:
                messages.error(request, f'Le pourcentage total ne peut pas dépasser 100%. Disponible: {100 - total_percentual}%')
                return redirect('orcamentos:admin_orcamento_acomptes', numero=numero)
            
            # Converter data
            if data_vencimento:
                from datetime import datetime
                data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            else:
                data_vencimento = timezone.now().date() + timedelta(days=30)
            
            # Criar acompte
            acompte = AcompteOrcamento.objects.create(
                orcamento=orcamento,
                criado_por=request.user,
                tipo=tipo,
                descricao=descricao,
                percentual=percentual,
                data_vencimento=data_vencimento,
                tipo_pagamento=tipo_pagamento,
            )
            
            # Calcular valores automaticamente
            acompte.calcular_valores()
            acompte.save()
            
            # Registrar na auditoria
            AuditoriaManager.registrar_acao(
                usuario=request.user,
                acao=TipoAcao.CRIACAO,
                objeto=acompte,
                descricao=f"Acompte {acompte.numero} créé pour le devis {orcamento.numero}",
                request=request
            )
            
            messages.success(request, f'Acompte de {acompte.valor_ttc:.2f}€ créé avec succès!')
            return redirect('orcamentos:admin_orcamento_acomptes', numero=numero)
            
        except ValueError as e:
            messages.error(request, f'Erreur dans les données: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            
        return redirect('orcamentos:admin_orcamento_acomptes', numero=numero)
    
    # GET - mostrar formulário
    percentual_disponivel = 100 - total_percentual
    
    context = {
        'orcamento': orcamento,
        'percentual_disponivel': percentual_disponivel,
        # Adição: informar ao template quanto já foi utilizado
        'total_percentual_usado': total_percentual,
        'page_title': f'Criar Acompte - Devis #{numero}',
    }
    
    return render(request, 'orcamentos/admin_criar_acompte.html', context)


@staff_member_required
def admin_editar_acompte(request, acompte_id):
    """Editar um acompte existente"""
    acompte = get_object_or_404(AcompteOrcamento, id=acompte_id)
    
    if acompte.status == 'pago':
        messages.error(request, 'Impossible de modifier un acompte déjà payé.')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)
    
    if request.method == 'POST':
        try:
            # Dados anteriores para auditoria
            dados_anteriores = {
                'tipo': acompte.tipo,
                'descricao': acompte.descricao,
                'percentual': float(acompte.percentual),
                'data_vencimento': acompte.data_vencimento.isoformat(),
                'tipo_pagamento': acompte.tipo_pagamento,
            }
            
            # Extrair dados do formulário
            tipo = request.POST.get('tipo', acompte.tipo)
            descricao = request.POST.get('descricao', acompte.descricao)
            percentual = Decimal(request.POST.get('percentual', str(acompte.percentual)))
            data_vencimento = request.POST.get('data_vencimento')
            tipo_pagamento = request.POST.get('tipo_pagamento', acompte.tipo_pagamento)
            
            # Verificar se percentual não ultrapassa 100%
            outros_acomptes = AcompteOrcamento.objects.filter(
                orcamento=acompte.orcamento
            ).exclude(id=acompte.id)
            total_outros = outros_acomptes.aggregate(Sum('percentual'))['percentual__sum'] or Decimal('0.00')
            
            if total_outros + percentual > 100:
                messages.error(request, f'Le pourcentage total ne peut pas dépasser 100%. Disponible: {100 - total_outros}%')
                return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)
            
            # Converter data
            if data_vencimento:
                from datetime import datetime
                data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            
            # Atualizar acompte
            acompte.tipo = tipo
            acompte.descricao = descricao
            acompte.percentual = percentual
            acompte.data_vencimento = data_vencimento
            acompte.tipo_pagamento = tipo_pagamento
            
            # Recalcular valores
            acompte.calcular_valores()
            acompte.save()
            
            # Registrar na auditoria
            AuditoriaManager.registrar_acao(
                usuario=request.user,
                acao=TipoAcao.EDICAO,
                objeto=acompte,
                descricao=f"Acompte {acompte.numero} modifié",
                dados_anteriores=dados_anteriores,
                dados_posteriores={
                    'tipo': acompte.tipo,
                    'descricao': acompte.descricao,
                    'percentual': float(acompte.percentual),
                    'data_vencimento': acompte.data_vencimento.isoformat(),
                    'tipo_pagamento': acompte.tipo_pagamento,
                },
                request=request
            )
            
            messages.success(request, f'Acompte {acompte.numero} mis à jour avec succès!')
            return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)
            
        except ValueError as e:
            messages.error(request, f'Erreur dans les données: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    context = {
        'acompte': acompte,
        'page_title': f'Modifier Acompte #{acompte.numero}',
    }
    
    return render(request, 'orcamentos/admin_editar_acompte.html', context)


@staff_member_required
def admin_gerar_fatura_acompte(request, acompte_id):
    """Gerar fatura automática para um acompte"""
    acompte = get_object_or_404(AcompteOrcamento, id=acompte_id)
    
    # Verificar se já tem fatura
    if hasattr(acompte, 'fatura_acompte') and acompte.fatura_acompte:
        messages.info(request, 'Cet acompte a déjà une facture associée.')
        return redirect('orcamentos:admin_fatura_detail', numero=acompte.fatura_acompte.numero)
    
    # Verificar se o orçamento tem cliente
    if not acompte.orcamento.solicitacao.cliente:
        messages.error(request, 'Impossible de créer une facture: pas de client associé au devis.')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)
    
    try:
        # Criar fatura para o acompte (usar HT como total base; itens calcularão TTC/TVA)
        fatura = Facture.objects.create(
            cliente=acompte.orcamento.solicitacao.cliente,
            orcamento=acompte.orcamento,
            elaborado_por=request.user,
            titulo=f"Facture d'acompte - {acompte.get_tipo_display()}",
            descricao=f"Acompte {acompte.numero} pour le devis {acompte.orcamento.numero}",
            subtotal=acompte.valor_ht,
            total=acompte.valor_ht,
            data_vencimento=acompte.data_vencimento,
            condicoes_pagamento=acompte.orcamento.condicoes_pagamento,
            tipo_pagamento=acompte.tipo_pagamento,
            status='envoyee'
        )
        
        # Criar item da fatura baseado no acompte
        ItemFacture.objects.create(
            facture=fatura,
            descricao=f"Acompte {acompte.get_tipo_display()} - {acompte.percentual}%",
            unidade='unite',
            atividade='service',
            quantidade=Decimal('1'),
            preco_unitario_ht=acompte.valor_ht,
            remise_percentual=Decimal('0'),
            taxa_tva='20',  # ou usar uma TVA padrão; os cálculos ajustarão o TTC
        )
        
        # Associar fatura ao acompte
        acompte.fatura_acompte = fatura
        acompte.save()
        
        # Recalcular totais da fatura
        fatura.calcular_totais()
        
        # Registrar na auditoria
        AuditoriaManager.registrar_acao(
            usuario=request.user,
            acao=TipoAcao.CRIACAO,
            objeto=fatura,
            descricao=f"Facture d'acompte générée automatiquement pour l'acompte {acompte.numero}",
            request=request
        )
        
        messages.success(request, f"Facture {fatura.numero} créée avec succès pour l'acompte {acompte.numero}!")
        return redirect('orcamentos:admin_fatura_detail', numero=fatura.numero)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création de la facture: {str(e)}')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)


@staff_member_required
def admin_deletar_acompte(request, acompte_id):
    """Deletar um acompte"""
    acompte = get_object_or_404(AcompteOrcamento, id=acompte_id)
    orcamento_numero = acompte.orcamento.numero
    
    if acompte.status == 'pago':
        messages.error(request, 'Impossible de supprimer un acompte déjà payé.')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=orcamento_numero)
    
    if request.method == 'POST':
        # Registrar na auditoria antes de deletar
        AuditoriaManager.registrar_acao(
            usuario=request.user,
            acao=TipoAcao.EXCLUSAO,
            objeto=acompte,
            descricao=f"Acompte {acompte.numero} supprimé du devis {orcamento_numero}",
            request=request
        )

        # Deletar registro
        acompte.delete()
        
        messages.success(request, f'Acompte {acompte.numero} supprimé avec succès!')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=orcamento_numero)
    
    context = {
        'acompte': acompte,
        'page_title': f'Supprimer Acompte #{acompte.numero}',
    }
    
    return render(request, 'orcamentos/admin_deletar_acompte.html', context)


# ==================== ESTATÍSTICAS PARA DASHBOARD ====================
def get_cliente_stats(user):
    """Retorna estatísticas básicas para o dashboard do cliente.

    Adiciona também listas recentes de projetos e solicitações de orçamento
    para que o template dashboard exiba corretamente sem cair sempre no estado vazio.
    """
    try:
        # Importes locais para evitar ciclos (caso views seja importado em outros locais)
        from .models import Projeto, SolicitacaoOrcamento, Orcamento, StatusOrcamento
        from django.db.models import Sum

        total_projects = Projeto.objects.filter(cliente=user).count()
        total_quotes = SolicitacaoOrcamento.objects.filter(cliente=user).count()
        pending_requests = SolicitacaoOrcamento.objects.filter(cliente=user, status=StatusOrcamento.PENDENTE).count()

        # Projetos e orçamentos recentes (limitados a 5)
        recent_projects = list(Projeto.objects.filter(cliente=user).order_by('-created_at')[:5])
        recent_quotes = list(SolicitacaoOrcamento.objects.filter(cliente=user).order_by('-created_at')[:5])

        # Investimento do cliente: soma de orçamentos aceitos vinculados às suas solicitações
        client_investment = (
            Orcamento.objects.filter(
                solicitacao__cliente=user,
                status=StatusOrcamento.ACEITO
            ).aggregate(Sum('total')).get('total__sum') or 0
        )

        return {
            'client_projects': total_projects,
            'client_quotes': total_quotes,
            'pending_requests': pending_requests,
            'client_investment': client_investment,
            'recent_projects': recent_projects,
            'recent_quotes': recent_quotes,
        }
    except Exception:
        # Em caso de falha (ex.: migrações pendentes), retorna valores neutros
        return {
            'client_projects': 0,
            'client_quotes': 0,
            'pending_requests': 0,
            'client_investment': 0,
            'recent_projects': [],
            'recent_quotes': [],
        }

def get_admin_stats():
    """Retorna estatísticas básicas para o dashboard do administrador."""
    total_projects = Projeto.objects.count()
    total_clients = Projeto.objects.values('cliente').distinct().count()
    pending_requests = SolicitacaoOrcamento.objects.filter(status=StatusOrcamento.PENDENTE).count()
    monthly_revenue = Orcamento.objects.filter(status=StatusOrcamento.ACEITO).aggregate(Sum('total')).get('total__sum') or 0
    return {
        'total_projects': total_projects,
        'total_clients': total_clients,
        'pending_requests': pending_requests,
        'monthly_revenue': monthly_revenue,
    }

# ========================= AGENDAMENTOS (RENDEZ-VOUS) =========================

@login_required
@require_http_methods(["POST"])  # Apenas POST para criar proposta de agendamento
def cliente_devis_agendar(request, numero):
    """Cliente propõe um rendez-vous para um devis"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
        solicitacao__cliente=request.user
    )

    # Somente permitir agendar se o devis foi enviado ou aceito
    if orcamento.status not in [StatusOrcamento.ENVIADO, StatusOrcamento.ACEITO]:
        messages.warning(request, "Vous pouvez proposer un rendez-vous seulement pour un devis envoyé ou accepté.")
        return redirect('orcamentos:cliente_devis_detail', numero=numero)

    # Esperamos um input type="datetime-local"
    data_horario_str = request.POST.get('data_horario')  # formato 'YYYY-MM-DDTHH:MM'
    tipo = request.POST.get('tipo') or TipoAgendamento.VISITA_TECHNIQUE
    mensagem = request.POST.get('mensagem', '').strip()

    # Validações básicas
    if not data_horario_str:
        messages.error(request, "Veuillez choisir une date et heure pour le rendez-vous.")
        return redirect('orcamentos:cliente_devis_detail', numero=numero)

    try:
        from datetime import datetime as _dt
        # Parse formato datetime-local
        dt = _dt.strptime(data_horario_str, '%Y-%m-%dT%H:%M')
        # Tornar consciente do timezone atual
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
    except Exception:
        messages.error(request, "Format de date/heure invalide.")
        return redirect('orcamentos:cliente_devis_detail', numero=numero)

    if dt < timezone.now():
        messages.error(request, "La date/heure doit être dans le futur.")
        return redirect('orcamentos:cliente_devis_detail', numero=numero)

    if tipo not in [c[0] for c in TipoAgendamento.choices]:
        tipo = TipoAgendamento.VISITA_TECHNIQUE

    # Criar o agendamento
    AgendamentoOrcamento.objects.create(
        orcamento=orcamento,
        cliente=request.user,
        data_horario=dt,
        tipo=tipo,
        mensagem=mensagem,
        status=StatusAgendamento.PENDENTE,
    )

    messages.success(request, "Votre proposition de rendez-vous a été envoyée. Nous vous confirmerons bientôt.")
    return redirect('orcamentos:cliente_devis_detail', numero=numero)


@staff_member_required
@require_http_methods(["POST"])  # Confirmar via POST
def admin_confirmar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(AgendamentoOrcamento, pk=agendamento_id)

    agendamento.status = StatusAgendamento.CONFIRMADO
    agendamento.confirmado_por = request.user
    agendamento.confirmado_em = timezone.now()
    resposta = request.POST.get('resposta_admin', '').strip()
    if resposta:
        agendamento.resposta_admin = resposta
    agendamento.save()

    messages.success(request, "Rendez-vous confirmé avec succès.")
    return redirect('orcamentos:admin_orcamento_detail', numero=agendamento.orcamento.numero)


@staff_member_required
@require_http_methods(["POST"])  # Recusar via POST
def admin_recusar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(AgendamentoOrcamento, pk=agendamento_id)

    agendamento.status = StatusAgendamento.RECUSADO
    agendamento.confirmado_por = request.user
    agendamento.confirmado_em = timezone.now()
    resposta = request.POST.get('resposta_admin', '').strip()
    if resposta:
        agendamento.resposta_admin = resposta
    agendamento.save()

    messages.info(request, "Rendez-vous refusé.")
    return redirect('orcamentos:admin_orcamento_detail', numero=agendamento.orcamento.numero)

# ======================= FIM: AGENDAMENTOS =======================
