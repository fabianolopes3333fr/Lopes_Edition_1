"""
Views para funcionalidades de parâmetros e configurações do usuário
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import json
from datetime import datetime
from utils.emails.sistema_email import send_2fa_status_email, send_account_deleted_email


@login_required
def parametros(request):
    """
    View principal da página de parâmetros
    """
    context = {
        'page_title': 'Paramètres du compte',
        'user': request.user,
    }
    return render(request, 'partials_dashboard/parametros.html', context)


@login_required
@require_POST
def update_preferences(request):
    """
    Atualiza preferências de notificação do usuário via AJAX
    """
    try:
        user = request.user
        profile = user.profile

        # Atualizar preferências
        profile.notifications_email = 'email_notifications' in request.POST
        profile.newsletter = 'newsletter' in request.POST
        profile.project_notifications = 'project_notifications' in request.POST
        profile.save()

        return JsonResponse({
            'success': True,
            'message': 'Préférences sauvegardées avec succès!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la sauvegarde: {str(e)}'
        })


@login_required
@require_POST
def toggle_2fa(request):
    """
    Ativa/desativa autenticação de dois fatores
    """
    try:
        data = json.loads(request.body)
        enabled = data.get('enabled', False)

        user = request.user
        profile = user.profile

        if enabled:
            # Aqui você implementaria a lógica para ativar 2FA
            # Por exemplo, gerar QR code, configurar TOTP, etc.
            profile.two_factor_enabled = True
            profile.save()
            message = 'Authentification à deux facteurs activée avec succès!'
        else:
            profile.two_factor_enabled = False
            profile.save()
            message = 'Authentification à deux facteurs désactivée.'

        # Notificar por email (falha silenciosa)
        try:
            send_2fa_status_email(user, enabled, request)
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'message': message
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        })


@login_required
@require_POST
def export_data(request):
    """
    Exporta todos os dados do usuário em formato JSON
    Correções:
    - Usar related_name corretos: projets, solicitacoes_orcamento
    - Usar campos created_at/updated_at existentes
    - Incluir consentimentos de marketing e dados
    - Evitar atributos inexistentes (data_criacao, data_solicitacao)
    """
    try:
        user = request.user

        # Coletar todos os dados do usuário
        user_data = {
            'user_info': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'account_type': user.account_type,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
            },
            'profile': {
                'phone': getattr(user.profile, 'phone', ''),
                'address': getattr(user.profile, 'address', ''),
                'city': getattr(user.profile, 'city', ''),
                'postal_code': getattr(user.profile, 'postal_code', ''),
                'country': getattr(user.profile, 'country', ''),
                'notifications_email': getattr(user.profile, 'notifications_email', False),
                'newsletter': getattr(user.profile, 'newsletter', False),
                'project_notifications': getattr(user.profile, 'project_notifications', False),
                'two_factor_enabled': getattr(user.profile, 'two_factor_enabled', False),
                'data_processing_consent': getattr(user.profile, 'data_processing_consent', False),
                'marketing_consent': getattr(user.profile, 'marketing_consent', False),
            },
            'projects': [],
            'quotes': [],
            'export_date': datetime.now().isoformat()
        }

        # Projetos (related_name='projetos')
        if hasattr(user, 'projetos'):
            for projeto in user.projetos.all():
                user_data['projects'].append({
                    'title': projeto.titulo,
                    'description': projeto.descricao,
                    'status': projeto.status,
                    'type_service': projeto.tipo_servico,
                    'urgency': projeto.urgencia,
                    'created_at': projeto.created_at.isoformat() if hasattr(projeto, 'created_at') else None,
                    'updated_at': projeto.updated_at.isoformat() if hasattr(projeto, 'updated_at') else None,
                })

        # Solicitações de orçamento (related_name='solicitacoes_orcamento')
        if hasattr(user, 'solicitacoes_orcamento'):
            for solicitacao in user.solicitacoes_orcamento.all():
                user_data['quotes'].append({
                    'numero': solicitacao.numero,
                    'tipo_servico': solicitacao.tipo_servico,
                    'status': solicitacao.status,
                    'created_at': solicitacao.created_at.isoformat() if hasattr(solicitacao, 'created_at') else None,
                    'updated_at': solicitacao.updated_at.isoformat() if hasattr(solicitacao, 'updated_at') else None,
                })

        # Preparar resposta JSON (download)
        response = HttpResponse(
            json.dumps(user_data, indent=2, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="dados_lopes_peinture_{user.id}_{datetime.now().strftime("%Y%m%d")}.json"'
        )
        return response

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Erreur lors de l'export: {str(e)}"
        })


@login_required
@require_POST
def delete_account(request):
    """Deleta permanentemente a conta do usuário com logs adequados"""
    # Garantir logger disponível também no except
    import logging
    logger = logging.getLogger('accounts')
    try:
        user = request.user
        user_email = user.email

        logger.info(f"Usuário {user_email} solicitou exclusão de conta")

        # (Opcional) Poderíamos anonimizar dados antes de deletar
        user.delete()

        # Enviar email de confirmação de exclusão (falha silenciosa)
        try:
            if user_email:
                send_account_deleted_email(user_email, request)
        except Exception:
            pass

        logger.info(f"Conta {user_email} deletada com sucesso")
        return JsonResponse({
            'success': True,
            'message': 'Compte supprimé avec succès. Redirection en cours...'
        })
    except Exception as e:
        logger.error(f"Erro ao deletar conta: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        })


@login_required
def account_settings(request):
    """
    View alternativa para parâmetros (alias)
    """
    return parametros(request)
