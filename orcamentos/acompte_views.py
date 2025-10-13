from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from .models import Orcamento, AcompteOrcamento, StatusOrcamento, Facture, ItemFacture
from .auditoria import AuditoriaManager, TipoAcao


@staff_member_required
def admin_marcar_acompte_pago(request, acompte_id):
    """Marcar acompte como pago"""
    acompte = get_object_or_404(AcompteOrcamento, id=acompte_id)

    if acompte.status == 'pago':
        messages.info(request, 'Cet acompte est déjà marqué comme payé.')
        return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)

    if request.method == 'POST':
        try:
            # Dados anteriores para auditoria
            dados_anteriores = {'status': acompte.status}

            acompte.status = 'pago'
            acompte.data_pagamento = timezone.now()
            acompte.save()

            # Registrar na auditoria
            AuditoriaManager.registrar_acao(
                usuario=request.user,
                acao=TipoAcao.EDICAO,
                objeto=acompte,
                descricao=f"Acompte {acompte.numero} marqué comme payé",
                dados_anteriores=dados_anteriores,
                dados_posteriores={'status': acompte.status},
                request=request
            )

            messages.success(request, 'Acompte marqué comme payé avec succès!')
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour de l\'acompte: {e}')

        return redirect('orcamentos:admin_orcamento_acomptes', numero=acompte.orcamento.numero)

    context = {
        'acompte': acompte,
        'page_title': f'Marquer Acompte #{acompte.numero} comme Payé',
    }

    return render(request, 'orcamentos/admin_marcar_acompte_pago.html', context)

