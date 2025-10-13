# ============ VIEWS DE FATURAS ============
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
import json
from django.shortcuts import render, get_object_or_404, redirect

from . auditoria import AuditoriaManager, TipoAcao
from . forms import FactureForm
from . models import Facture, ItemFacture, Orcamento, StatusOrcamento


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

            # Auditoria: criação de fatura manual
            try:
                AuditoriaManager.registrar_criacao_fatura(
                    usuario=request.user,
                    fatura=fatura,
                    request=request,
                    origem="manual"
                )
            except Exception:
                pass

            action = request.POST.get('action', 'draft')
            if action == 'send':
                fatura.status = 'envoyee'
                fatura.data_envio = timezone.now()
                fatura.save()
                # Auditoria: envio de fatura
                try:
                    AuditoriaManager.registrar_envio_fatura(request.user, fatura, request=request)
                except Exception:
                    pass
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
        messages.warning(request, "Attention: le devis n'a pas encore été accepté par le client.")

    # Buscar cliente
    cliente = None
    if orcamento.solicitacao.cliente:
        cliente = orcamento.solicitacao.cliente
    else:
        # Se não tem cliente cadastrado, não pode criar fatura
        messages.error(request, "Impossible de créer une facture: le devis n'a pas de client associé.")
        return redirect('orcamentos:admin_orcamento_detail', numero=orcamento_numero)

    if request.method == 'POST':
        print(f"DEBUG: POST data recebido: {request.POST}")  # Debug completo

        form = FactureForm(request.POST, cliente_predefinido=cliente)

        # IMPORTANTE: Debug detalhado dos erros do formulário
        print(f"DEBUG: Form is_valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Erros do formulário completos: {form.errors}")
            print(f"DEBUG: Erros por campo:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {errors}")

        if form.is_valid():
            try:
                # CORREÇÃO: Definir cliente corretamente antes de salvar
                fatura = form.save(commit=False)
                fatura.orcamento = orcamento
                fatura.cliente = cliente
                fatura.elaborado_por = request.user
                fatura.save()

                # Processar itens do orçamento enviados via AJAX
                itens_data = request.POST.get('itens_json', '[]')
                print(f"DEBUG: itens_data recebido: {itens_data}")  # Debug

                try:
                    itens = json.loads(itens_data)
                    print(f"DEBUG: itens parseados: {itens}")  # Debug

                    for item_data in itens:
                        print(f"DEBUG: processando item: {item_data}")  # Debug
                        if item_data.get('descricao'):  # Só criar se tiver descrição
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
                    print(f"DEBUG: erro ao processar itens: {str(e)}")  # Debug
                    # Se não conseguir processar via JSON, copiar itens do orçamento
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

                # Auditoria: criação de fatura a partir de devis
                try:
                    AuditoriaManager.registrar_criacao_fatura(
                        usuario=request.user,
                        fatura=fatura,
                        request=request,
                        origem="devis",
                        orcamento_vinculado=orcamento
                    )
                except Exception:
                    pass

                action = request.POST.get('action', 'draft')
                if action == 'send':
                    fatura.status = 'envoyee'
                    fatura.data_envio = timezone.now()
                    fatura.save()
                    # Auditoria: envio de fatura
                    try:
                        AuditoriaManager.registrar_envio_fatura(request.user, fatura, request=request)
                    except Exception:
                        pass
                    messages.success(request, f'Facture {fatura.numero} créée et envoyée avec succès!')
                else:
                    messages.success(request, f'Facture {fatura.numero} créée à partir du devis {orcamento_numero}.')

                return redirect('orcamentos:admin_fatura_detail', numero=fatura.numero)

            except Exception as e:
                messages.error(request, f'Erreur lors de la création de la facture: {str(e)}')
                print(f"DEBUG: Erro na criação da fatura: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
            print(f"DEBUG: Erros no formulário: {form.errors}")

    else:
        # Pré-preencher o formulário com dados do orçamento
        initial_data = {
            'titulo': orcamento.titulo,
            'descricao': orcamento.descricao,
            'condicoes_pagamento': orcamento.condicoes_pagamento,
            'tipo_pagamento': orcamento.tipo_pagamento,
            'desconto': orcamento.desconto,
            'data_vencimento': timezone.now().date() + timedelta(days=30),
            'observacoes': orcamento.observacoes,
        }
        print(f"DEBUG: Initial data: {initial_data}")  # Debug

        # CORREÇÃO: Passar cliente como parâmetro especial para o formulário
        form = FactureForm(initial=initial_data, cliente_predefinido=cliente)

        # CORREÇÃO: Pré-preencher campo de busca com nome do cliente
        if cliente:
            form.initial['cliente_search'] = f"{cliente.first_name} {cliente.last_name}".strip() or cliente.email

    from .models import Produto
    produtos = Produto.objects.filter(ativo=True).order_by('referencia')

    # CORREÇÃO: Passar dados de acomptes para o template
    acomptes_list = []
    total_acomptes_pagos = Decimal('0.00')
    total_acomptes_pendentes = Decimal('0.00')
    
    if orcamento.acomptes.exists():
        for acompte in orcamento.acomptes.all():
            acomptes_list.append({
                'numero': acompte.numero,
                'descricao': acompte.descricao,
                'percentual': float(acompte.percentual),
                'valor_ttc': float(acompte.valor_ttc),
                'status': acompte.get_status_display(),
                'status_code': acompte.status,
            })
            if acompte.status == 'pago':
                total_acomptes_pagos += acompte.valor_ttc
            else:
                total_acomptes_pendentes += acompte.valor_ttc

    # Calcular saldo real a ser faturado
    saldo_a_faturar = orcamento.total_ttc - total_acomptes_pagos

    context = {
        'form': form,
        'orcamento': orcamento,
        'cliente': cliente,
        'produtos': produtos,
        'itens_orcamento': orcamento.itens.all(),
        'acomptes_list': acomptes_list,
        'total_acomptes_pagos': total_acomptes_pagos,
        'total_acomptes_pendentes': total_acomptes_pendentes,
        'saldo_a_faturar': saldo_a_faturar,
        'page_title': f'Criar Facture depuis Devis #{orcamento_numero}',
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
                pass

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
    try:
        fatura = get_object_or_404(Facture, numero=numero)

        if request.method == 'POST':
            # Capturar dados anteriores para auditoria
            dados_anteriores = {
                'status': fatura.status,
                'data_pagamento': fatura.data_pagamento.isoformat() if fatura.data_pagamento else None
            }

            data_pagamento = request.POST.get('data_pagamento')
            if data_pagamento:
                fatura.status = 'payee'
                fatura.data_pagamento = data_pagamento
            else:
                fatura.status = 'payee'
                fatura.data_pagamento = timezone.now()

            fatura.save()

            # Registrar na auditoria (mantido compatível)
            AuditoriaManager.registrar_acao(
                usuario=request.user,
                acao=TipoAcao.EDICAO,
                objeto=fatura,
                descricao=f"Fatura {fatura.numero} marcada como paga",
                dados_anteriores=dados_anteriores,
                dados_posteriores={
                    'status': fatura.status,
                    'data_pagamento': fatura.data_pagamento.isoformat()
                },
                request=request
            )

            messages.success(request, f'Facture {fatura.numero} marquée comme payée!')
            return redirect('orcamentos:admin_fatura_detail', numero=numero)

        context = {
            'fatura': fatura,
            'page_title': f'Marcar Fatura #{fatura.numero} como Paga'
        }

        return render(request, 'orcamentos/admin_marcar_fatura_paga.html', context)

    except Exception as e:
        messages.error(request, 'Fatura não encontrada ou erro ao processar.')
        return redirect('orcamentos:admin_faturas_list')

@staff_member_required
def admin_fatura_pdf(request, numero):
    """Gerar PDF da fatura para o painel administrativo"""
    fatura = get_object_or_404(Facture, numero=numero)

    # Usar a mesma lógica do sistema de orçamentos adaptada para faturas
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from decimal import Decimal
    from datetime import datetime

    # Calcular totais para o PDF
    subtotal_ht = Decimal('0.00')
    total_taxe = Decimal('0.00')
    total_ttc = Decimal('0.00')

    items_data = []
    if hasattr(fatura, 'itens') and fatura.itens.exists():
        for i, item in enumerate(fatura.itens.all(), 1):
            # Usar a TVA real do item
            taxa_tva_decimal = Decimal(item.taxa_tva) / 100

            pu_ht = item.preco_unitario_ht
            pu_ttc = pu_ht * (1 + taxa_tva_decimal)
            total_item_ht = item.total_ht
            total_item_ttc = item.total_ttc
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
                'total_ht': total_item_ht,
                'total_ttc': total_item_ttc,
                'taxe': taxe_item,
                'taxa_tva': item.taxa_tva
            })

    # Context para o template
    context = {
        'fatura': fatura,
        'items': items_data,
        'subtotal_ht': subtotal_ht,
        'total_taxe': total_taxe,
        'total_ttc': total_ttc,
        'empresa': {
            'name': 'LOPES DE SOUZA fabiano',
            'address': '261 Chemin de La Castellane',
            'city': '31790 Saint Sauveur, France',
            'phone': '+33 7 69 27 37 76',
            'email': 'contact@lopespeinture.fr',
            'siret': '978 441 756 00019',
            'ape': '4334Z',
            'tva': 'FR35978441756',
            'site': 'www.lopespeinture.fr'
        },
        'data_impressao': datetime.now(),
    }

    # Renderizar template HTML
    html_content = render_to_string('orcamentos/admin/fatura_pdf.html', context)

    # Registrar auditoria de download de PDF
    try:
        AuditoriaManager.registrar_download_fatura_pdf(request.user, fatura, request=request)
    except Exception:
        pass

    # Para desenvolvimento, retornar HTML diretamente
    if request.GET.get('debug') == '1':
        return HttpResponse(html_content, content_type='text/html')
    else:
        # Preparar para download como PDF (usando print do navegador)
        response = HttpResponse(html_content, content_type='text/html')
        filename = f"facture_{fatura.numero}_{fatura.cliente.first_name}_{fatura.cliente.last_name}.html"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    
# ============ VIEWS PARA FATURAS DOS CLIENTES ============

@login_required
def cliente_faturas(request):
    """Lista de faturas do cliente logado"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    # Buscar todas as faturas do cliente
    faturas = Facture.objects.filter(
        cliente=request.user
    ).order_by('-data_criacao')

    # Estatísticas
    total_faturas = faturas.count()
    faturas_pagas = faturas.filter(status='payee').count()
    faturas_pendentes = faturas.filter(status='envoyee').count()
    faturas_em_atraso = faturas.filter(status='en_retard').count()

    # Valor total - CORREÇÃO: usar Sum diretamente
    valor_total = faturas.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')

    valor_pago = faturas.filter(status='payee').aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')

    valor_pendente = faturas.exclude(status='payee').aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')

    # Registrar visualização da lista de faturas
    try:
        for f in faturas[:10]:  # registrar para algumas recentes para contexto
            AuditoriaManager.registrar_visualizacao_fatura(request.user, f, request=request, tipo_visualizacao='list')
    except Exception:
        pass

    context = {
        'faturas': faturas,
        'total_faturas': total_faturas,
        'faturas_pagas': faturas_pagas,
        'faturas_pendentes': faturas_pendentes,
        'faturas_em_atraso': faturas_em_atraso,
        'valor_total': valor_total,
        'valor_pago': valor_pago,
        'valor_pendente': valor_pendente,
    }

    return render(request, 'orcamentos/cliente/faturas_list.html', context)


@login_required
def cliente_fatura_detail(request, numero):
    """Detalhes de uma fatura específica do cliente"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    fatura = get_object_or_404(
        Facture,
        numero=numero,
        cliente=request.user
    )

    # Registrar visualização de detalhe
    try:
        AuditoriaManager.registrar_visualizacao_fatura(request.user, fatura, request=request, tipo_visualizacao='detail')
    except Exception:
        pass

    context = {
        'fatura': fatura,
    }

    return render(request, 'orcamentos/cliente/fatura_detail.html', context)

@login_required
def cliente_fatura_pdf(request, numero):
    """Gerar PDF da fatura para o cliente"""
    if request.user.account_type != 'CLIENT':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')

    fatura = get_object_or_404(
        Facture,
        numero=numero,
        cliente=request.user
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
    for i, item in enumerate(fatura.itens.all(), 1):
        # Usar a TVA real do item
        taxa_tva_decimal = Decimal(item.taxa_tva) / 100

        pu_ht = item.preco_unitario_ht
        pu_ttc = pu_ht * (1 + taxa_tva_decimal)
        total_item_ht = item.total_ht
        total_item_ttc = item.total_ttc
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
            'total_ht': total_item_ht,
            'total_ttc': total_item_ttc,
            'taxe': taxe_item,
            'taxa_tva': item.taxa_tva
        })

    # Context para o template
    context = {
        'fatura': fatura,
        'items': items_data,
        'subtotal_ht': subtotal_ht,
        'total_taxe': total_taxe,
        'total_ttc': total_ttc,
        'empresa': {
            'name': 'LOPES DE SOUZA fabiano',
            'address': '261 Chemin de La Castellane',
            'city': '31790 Saint Sauveur, France',
            'phone': '+33 7 69 27 37 76',
            'email': 'contact@lopespeinture.fr',
            'siret': '978 441 756 00019',
            'ape': '4334Z',
            'tva': 'FR35978441756',
            'site': 'www.lopespeinture.fr'
        },
        'data_impressao': datetime.now(),
    }

    # Renderizar template HTML (reutilizado do admin para manter consistência visual)
    html_content = render_to_string('orcamentos/admin/fatura_pdf.html', context)

    # Registrar visualização/download de PDF pelo cliente
    try:
        AuditoriaManager.registrar_visualizacao_fatura(request.user, fatura, request=request, tipo_visualizacao='pdf')
        AuditoriaManager.registrar_download_fatura_pdf(request.user, fatura, request=request)
    except Exception:
        pass

    # Para desenvolvimento, retornar HTML diretamente
    if request.GET.get('debug') == '1':
        return HttpResponse(html_content, content_type='text/html')
    else:
        # Preparar para download como PDF (usando print do navegador)
        response = HttpResponse(html_content, content_type='text/html')
        filename = f"facture_{fatura.numero}_{fatura.cliente.first_name}_{fatura.cliente.last_name}.html"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
