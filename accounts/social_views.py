"""
Views customizadas para login social
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login
from django.http import JsonResponse
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.helpers import complete_social_login
from .models import User
import logging

logger = logging.getLogger('accounts')


def social_login_success(request):
    """
    View chamada após sucesso no login social
    """
    if request.user.is_authenticated:
        # Log do login bem-sucedido
        social_accounts = SocialAccount.objects.filter(user=request.user)
        if social_accounts.exists():
            provider = social_accounts.first().provider
            logger.info(f"Login social bem-sucedido para usuário {request.user.email} via {provider}")

            messages.success(
                request,
                f"Bem-vindo à Lopes Peinture! Login realizado com sucesso via {provider.title()}."
            )

        # Redireciona para dashboard ou página inicial
        if hasattr(request.user, 'profile') and request.user.profile:
            return redirect('profiles:dashboard')
        else:
            return redirect('home:index')

    # Se não estiver autenticado, redireciona para login
    messages.error(request, "Erro no processo de autenticação. Tente novamente.")
    return redirect('accounts:login')


def social_login_error(request):
    """
    View chamada em caso de erro no login social
    """
    error_message = request.GET.get('error', 'Erro desconhecido')
    provider = request.GET.get('provider', 'social')

    logger.error(f"Erro no login social via {provider}: {error_message}")

    # Mensagens de erro personalizadas
    error_messages = {
        'access_denied': f"Acesso negado. Você cancelou a autorização com {provider.title()}.",
        'invalid_request': f"Solicitação inválida para {provider.title()}. Tente novamente.",
        'temporarily_unavailable': f"Serviço {provider.title()} temporariamente indisponível. Tente novamente em alguns minutos.",
    }

    user_message = error_messages.get(
        error_message,
        f"Erro na autenticação com {provider.title()}. Tente novamente ou use outro método de login."
    )

    messages.error(request, user_message)
    return redirect('accounts:login')


def social_account_connections(request):
    """
    View para gerenciar conexões de contas sociais
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Obter contas sociais conectadas
    social_accounts = SocialAccount.objects.filter(user=request.user)

    context = {
        'social_accounts': social_accounts,
        'available_providers': ['google', 'microsoft'],
    }

    return render(request, 'accounts/social_connections.html', context)


def disconnect_social_account(request, provider):
    """
    View para desconectar uma conta social
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    try:
        social_account = SocialAccount.objects.get(
            user=request.user,
            provider=provider
        )

        # Verifica se o usuário tem outras formas de login
        has_password = request.user.has_usable_password()
        other_social_accounts = SocialAccount.objects.filter(
            user=request.user
        ).exclude(id=social_account.id).exists()

        if not has_password and not other_social_accounts:
            messages.error(
                request,
                "Não é possível desconectar esta conta. Configure uma senha primeiro ou conecte outro método de login."
            )
            return redirect('accounts:social_connections')

        # Remove a conexão
        social_account.delete()
        messages.success(
            request,
            f"Conta {provider.title()} desconectada com sucesso."
        )

        logger.info(f"Usuário {request.user.email} desconectou conta {provider}")

    except SocialAccount.DoesNotExist:
        messages.error(request, "Conta social não encontrada.")

    return redirect('accounts:social_connections')


def ajax_social_login_status(request):
    """
    Endpoint AJAX para verificar status do login social
    """
    if request.user.is_authenticated:
        social_accounts = list(
            SocialAccount.objects.filter(user=request.user).values_list('provider', flat=True)
        )

        return JsonResponse({
            'authenticated': True,
            'user': {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            },
            'social_accounts': social_accounts,
        })

    return JsonResponse({'authenticated': False})
