"""
Views para funcionalidades de parâmetros e configurações do usuário
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from .models import User


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
                'notifications_email': getattr(user.profile, 'notifications_email', False),
                'newsletter': getattr(user.profile, 'newsletter', False),
                'project_notifications': getattr(user.profile, 'project_notifications', False),
                'two_factor_enabled': getattr(user.profile, 'two_factor_enabled', False),
            },
            'projects': [],
            'quotes': [],
            'export_date': datetime.now().isoformat()
        }

        # Adicionar projetos se existirem
        if hasattr(user, 'projetos_set'):
            for projeto in user.projetos_set.all():
                user_data['projects'].append({
                    'title': projeto.titulo,
                    'description': projeto.descricao,
                    'status': projeto.status,
                    'created_date': projeto.data_criacao.isoformat(),
                })

        # Adicionar solicitações de orçamento se existirem
        if hasattr(user, 'solicitacaoorcamento_set'):
            for orcamento in user.solicitacaoorcamento_set.all():
                user_data['quotes'].append({
                    'numero': orcamento.numero,
                    'tipo_servico': orcamento.tipo_servico,
                    'status': orcamento.status,
                    'data_solicitacao': orcamento.data_solicitacao.isoformat(),
                })

        # Preparar resposta JSON
        response = HttpResponse(
            json.dumps(user_data, indent=2, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="dados_lopes_peinture_{user.id}_{datetime.now().strftime("%Y%m%d")}.json"'

        return response

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'export: {str(e)}'
        })


@login_required
@require_POST
def delete_account(request):
    """
    Deleta permanentemente a conta do usuário
    """
    try:
        user = request.user

        # Log da ação
        import logging
        logger = logging.getLogger('accounts')
        logger.info(f"Usuário {user.email} solicitou exclusão de conta")

        # Deletar dados relacionados primeiro (se necessário)
        # Por exemplo, projetos, orçamentos, etc.

        # Deletar o usuário (isso também deletará o perfil via CASCADE)
        user_email = user.email
        user.delete()

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
