from django.contrib.admin.views.decorators import staff_member_required
import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render
from urllib.parse import parse_qs

from orcamentos.models import SolicitacaoOrcamento


@staff_member_required
def admin_orcamentos_orfaos(request):
    """Lista de orçamentos órfãos para administradores com estatísticas e agrupamentos."""
    # Buscar órfãs ordenadas
    qs_orfas = SolicitacaoOrcamento.objects.filter(
        cliente__isnull=True
    ).order_by('-created_at')

    # Paginação manual: exibir no máximo 20 no contexto conforme testes
    solicitacoes_orfas = list(qs_orfas[:20])

    # Estatísticas
    total_orfas = qs_orfas.count()
    emails_orfaos = list(qs_orfas.values_list('email_solicitante', flat=True))
    emails_unicos = len(set(emails_orfaos))

    # Agrupar por email com contagem
    from collections import Counter
    contagem = Counter(emails_orfaos)

    # Verificar usuários existentes por email
    from django.contrib.auth import get_user_model
    User = get_user_model()

    emails_com_usuarios = []
    emails_sem_usuarios = []
    for email, count in contagem.items():
        try:
            usuario = User.objects.get(email__iexact=email)
            emails_com_usuarios.append({
                'email_solicitante': email,
                'count': count,
                'pode_vincular': True,
                'usuario': usuario,
            })
        except User.DoesNotExist:
            emails_sem_usuarios.append({
                'email_solicitante': email,
                'count': count,
                'pode_vincular': False,
            })

    stats = {
        'total_orfas': total_orfas,
        'emails_unicos': emails_unicos,
        'podem_ser_vinculadas': len(emails_com_usuarios),
        'sem_usuario': len(emails_sem_usuarios),
    }

    context = {
        'solicitacoes_orfas': solicitacoes_orfas,
        'total_orfas': total_orfas,
        'total_emails_unicos': emails_unicos,
        'emails_com_usuarios': emails_com_usuarios,
        'emails_sem_usuarios': emails_sem_usuarios,
        'stats': stats,
    }

    return render(request, 'orcamentos/admin_orcamentos_orfaos.html', context)


@staff_member_required
def admin_vincular_orcamentos_orfaos(request):
    """Vincular orçamentos órfãos em lote via AJAX (aceita form-encoded ou JSON)."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    content_type = (request.META.get('CONTENT_TYPE') or '').lower()
    email = ''

    if 'application/json' in content_type:
        try:
            payload = json.loads(request.body.decode('utf-8') if request.body else '{}')
            email = (payload.get('email') or payload.get('email_solicitante') or '').strip()
        except (ValueError, json.JSONDecodeError, AttributeError):
            email = ''
    elif 'application/x-www-form-urlencoded' in content_type:
        try:
            raw = request.body.decode('utf-8') if request.body else ''
            data = parse_qs(raw)
            # parse_qs retorna listas
            email_vals = data.get('email') or data.get('email_solicitante') or []
            if email_vals:
                email = (email_vals[0] or '').strip()
        except Exception:
            email = ''
    else:
        # multipart/form-data e outros: depender do parser de Django
        email = (request.POST.get('email') or request.POST.get('email_solicitante') or '').strip()

    if not email:
        return JsonResponse({'success': False, 'error': 'Email não fornecido'})

    # Buscar usuário com esse email
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        usuario = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Aucun utilisateur trouvé'})

    # Buscar solicitações órfãs do email
    solicitacoes_orfas = SolicitacaoOrcamento.objects.filter(
        cliente__isnull=True,
        email_solicitante__iexact=email
    )

    if not solicitacoes_orfas.exists():
        return JsonResponse({'success': False, 'error': 'Aucune demande orpheline trouvée'})

    count = solicitacoes_orfas.count()
    numeros_vinculados = list(solicitacoes_orfas.values_list('numero', flat=True))

    # Registrar vinculações na auditoria e vincular
    from .auditoria import AuditoriaManager
    for solicitacao in solicitacoes_orfas:
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=usuario,
            solicitacao=solicitacao,
            request=request,
            origem="admin_manual"
        )
    solicitacoes_orfas.update(cliente=usuario)

    # Registrar processamento em lote
    AuditoriaManager.registrar_processamento_lote_orfaos(
        usuario_comando=request.user,
        total_processadas=count,
        total_vinculadas=count,
        emails_processados={email}
    )

    # Enviar notificação ao usuário exatamente uma vez
    try:
        from .services import NotificationService
        NotificationService.notificar_orcamentos_vinculados(usuario, count)
        AuditoriaManager.registrar_notificacao_vinculacao(
            usuario_notificado=usuario,
            quantidade_orcamentos=count,
            metodo_vinculacao="admin_manual"
        )
    except Exception as e:
        # Logar silenciosamente sem falhar a operação
        import logging
        logging.getLogger(__name__).error(f"Erro ao notificar usuário {email}: {e}")

    mensagem = f"{count} demande{'s' if count > 1 else ''} liée{'s' if count > 1 else ''} avec succès"

    return JsonResponse({
        'success': True,
        'message': mensagem,
        'count': count,
        'vinculadas': numeros_vinculados,
        'usuario': f"{usuario.first_name} {usuario.last_name}".strip() or usuario.email,
    })
