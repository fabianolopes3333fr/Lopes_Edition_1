# ============ VIEWS PÚBLICAS (SEM LOGIN) ============
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404

from orcamentos.forms import SolicitacaoOrcamentoPublicoForm
from orcamentos.models import SolicitacaoOrcamento, Orcamento, StatusOrcamento, StatusProjeto
from orcamentos.services import NotificationService
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.urls import reverse
from django.conf import settings


def solicitar_orcamento_publico(request):
    """Página pública para solicitação de orçamento"""
    if request.method == 'POST':
        form = SolicitacaoOrcamentoPublicoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)

            # MELHORIA: Se usuário está logado, vincular automaticamente
            usuario_logado_usando_url_publica = False
            if request.user.is_authenticated and not request.user.is_staff:
                solicitacao.cliente = request.user
                usuario_logado_usando_url_publica = True

                # Verificar se o email coincide com o do usuário logado
                if solicitacao.email_solicitante.lower() != request.user.email.lower():
                    messages.warning(
                        request,
                        f"Attention: L'email de la demande ({solicitacao.email_solicitante}) "
                        f"diffère de votre email de compte ({request.user.email}). "
                        f"La demande sera associée à votre compte."
                    )

            solicitacao.save()

            # Registrar na auditoria APÓS salvar (agora o objeto tem pk)
            if usuario_logado_usando_url_publica:
                from .auditoria import AuditoriaManager
                AuditoriaManager.registrar_solicitacao_publica_usuario_logado(
                    usuario=request.user,
                    solicitacao=solicitacao,
                    request=request
                )

            # Enviar notificações e emails para admins
            NotificationService.enviar_email_nova_solicitacao(solicitacao)

            messages.success(
                request,
                f"Votre demande de devis #{solicitacao.numero} a été envoyée avec succès! "
                f"Nous vous contacterons sous 24h."
            )
            return redirect('orcamentos:sucesso_solicitacao', numero=solicitacao.numero)
    else:
        form = SolicitacaoOrcamentoPublicoForm()

        # MELHORIA: Pré-preencher com dados do usuário logado
        if request.user.is_authenticated and not request.user.is_staff:
            form.fields['nome_solicitante'].initial = f"{request.user.first_name} {request.user.last_name}".strip()
            form.fields['email_solicitante'].initial = request.user.email

    context = {
        'form': form,
        'page_title': 'Demander un devis gratuit',
        'user_logged_in': request.user.is_authenticated and not request.user.is_staff,
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


# ============ NOVAS VIEWS PÚBLICAS PARA DEVIS ============

def _empresa_context():
    return {
        'nome': 'LOPES DE SOUZA fabiano',
        'endereco': '261 Chemin de La Castellane',
        'telefone': '+33 7 69 27 37 76',
        'email': 'contact@lopespeinture.fr',
        'site': 'www.lopespeinture.fr',
        'siret': '978 441 756 00019',
    }


def orcamento_publico_detail(request, uuid):
    """Página pública para visualizar um devis por UUID"""
    orcamento = get_object_or_404(Orcamento, uuid=uuid)

    signer = TimestampSigner()
    accept_token = signer.sign(f"{orcamento.uuid}:accept")
    refuse_token = signer.sign(f"{orcamento.uuid}:refuse")

    context = {
        'orcamento': orcamento,
        'empresa': _empresa_context(),
        'page_title': f'Devis {orcamento.numero}',
        'accept_token': accept_token,
        'refuse_token': refuse_token,
    }
    return render(request, 'orcamentos/visualizar_publico.html', context)


def _validate_token(request, expected_uuid_str: str, expected_action: str, max_age_seconds: int | None = None):
    """Valida o token assinado (TimestampSigner) presente em GET ou POST.
    expected_action deve ser 'accept', 'refuse' ou 'pdf'.
    Retorna None se válido; caso contrário, retorna um HttpResponse com erro.
    """
    token = request.GET.get('token') or request.POST.get('token')
    if not token:
        return HttpResponseBadRequest('Token manquant')

    # Usar validade configurável
    if max_age_seconds is None:
        max_age_seconds = getattr(settings, 'PUBLIC_LINK_TOKEN_MAX_AGE_SECONDS', 60 * 60 * 24 * 90)

    signer = TimestampSigner()
    try:
        value = signer.unsign(token, max_age=max_age_seconds)
    except SignatureExpired:
        return HttpResponseBadRequest('Token expiré')
    except BadSignature:
        return HttpResponseBadRequest('Token invalide')

    try:
        uuid_part, action_part = value.split(':', 1)
    except ValueError:
        return HttpResponseBadRequest('Token mal formé')

    if uuid_part != expected_uuid_str or action_part != expected_action:
        return HttpResponseBadRequest('Token non correspondant')

    return None


@require_http_methods(["POST"])
def orcamento_publico_aceitar(request, uuid):
    """Aceitar um devis via link público (sem login)
    Agora com token assinado, exigindo CSRF e resposta HTML de confirmação.
    Idempotente: se já não estiver ENVIADO, apenas mostra confirmação do status atual.
    """
    # Validar token
    error = _validate_token(request, str(uuid), 'accept')
    if error:
        return error

    try:
        orcamento = get_object_or_404(Orcamento, uuid=uuid)

        # Preparar link de PDF público com token (para qualquer status)
        signer = TimestampSigner()
        pdf_token = signer.sign(f"{orcamento.uuid}:pdf")
        pdf_url = reverse('orcamentos:orcamento_publico_pdf', kwargs={'uuid': orcamento.uuid}) + f"?token={pdf_token}"

        if orcamento.status != StatusOrcamento.ENVIADO:
            # Já processado: apenas renderizar confirmação
            context = {'orcamento': orcamento, 'pdf_url': pdf_url}
            return render(request, 'orcamentos/devis_confirmacao.html', context)

        # Processar aceite
        orcamento.status = StatusOrcamento.ACEITO
        orcamento.data_resposta_cliente = timezone.now()
        orcamento.save()

        # Atualizar status da solicitação
        orcamento.solicitacao.status = StatusOrcamento.ACEITO
        orcamento.solicitacao.save()

        # Se houver projeto, marcar em andamento
        if orcamento.solicitacao.projeto:
            orcamento.solicitacao.projeto.status = StatusProjeto.EM_ANDAMENTO
            orcamento.solicitacao.projeto.save()

        try:
            NotificationService.enviar_email_orcamento_aceito(orcamento)
        except Exception:
            pass

        # Registrar auditoria com IP/UA
        try:
            from .auditoria import AuditoriaManager
            AuditoriaManager.registrar_aprovacao_orcamento(usuario=None, orcamento=orcamento, request=request)
        except Exception:
            pass

        context = {'orcamento': orcamento, 'pdf_url': pdf_url}
        return render(request, 'orcamentos/devis_confirmacao.html', context)
    except Exception as e:
        return HttpResponse(f"Erreur lors de l'acceptation du devis: {str(e)}", status=500)


@require_http_methods(["POST"])
def orcamento_publico_recusar(request, uuid):
    """Recusar um devis via link público (sem login)
    Agora com token assinado, exigindo CSRF e resposta HTML de confirmação.
    Idempotente: se já não estiver ENVIADO, apenas mostra confirmação do status atual.
    """
    # Validar token
    error = _validate_token(request, str(uuid), 'refuse')
    if error:
        return error

    try:
        orcamento = get_object_or_404(Orcamento, uuid=uuid)

        # Preparar link de PDF público com token (para qualquer status)
        signer = TimestampSigner()
        pdf_token = signer.sign(f"{orcamento.uuid}:pdf")
        pdf_url = reverse('orcamentos:orcamento_publico_pdf', kwargs={'uuid': orcamento.uuid}) + f"?token={pdf_token}"

        if orcamento.status != StatusOrcamento.ENVIADO:
            context = {'orcamento': orcamento, 'pdf_url': pdf_url}
            return render(request, 'orcamentos/devis_confirmacao.html', context)

        # Processar recusa
        orcamento.status = StatusOrcamento.RECUSADO
        orcamento.data_resposta_cliente = timezone.now()
        orcamento.save()

        # Atualizar status da solicitação
        orcamento.solicitacao.status = StatusOrcamento.RECUSADO
        orcamento.solicitacao.save()

        try:
            NotificationService.enviar_email_orcamento_recusado(orcamento)
        except Exception:
            pass

        # Registrar auditoria com IP/UA
        try:
            from .auditoria import AuditoriaManager
            AuditoriaManager.registrar_rejeicao_orcamento(usuario=None, orcamento=orcamento, request=request)
        except Exception:
            pass

        context = {'orcamento': orcamento, 'pdf_url': pdf_url}
        return render(request, 'orcamentos/devis_confirmacao.html', context)
    except Exception as e:
        return HttpResponse(f"Erreur lors du refus du devis: {str(e)}", status=500)


@require_http_methods(["GET"])
def orcamento_publico_pdf(request, uuid):
    """Endpoint público para baixar o PDF do devis via token assinado."""
    # Validar token
    error = _validate_token(request, str(uuid), 'pdf')
    if error:
        return error

    orcamento = get_object_or_404(Orcamento, uuid=uuid)

    try:
        from .utils import gerar_pdf_orcamento
        pdf_bytes = gerar_pdf_orcamento(orcamento)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="devis_{orcamento.numero}.pdf"'

        # Auditoria de download
        try:
            from .auditoria import AuditoriaManager, TipoAcao
            AuditoriaManager.registrar_acao(
                usuario=None,
                acao=TipoAcao.DOWNLOAD,
                objeto=orcamento,
                descricao=f"Téléchargement public du PDF du devis {orcamento.numero}",
                request=request,
                funcionalidade="Devis - PDF public"
            )
        except Exception:
            pass

        return response
    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF: {str(e)}", status=500)
