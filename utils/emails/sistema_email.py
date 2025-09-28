"""
Sistema de Email - Lopes Peinture
Centraliza todo o envio de emails do sistema com templates profissionais.
"""

import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Obtém o IP real do cliente considerando proxies.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def send_password_reset_email(user, reset_url, request):
    """
    Envia email de reset de senha.
    """
    try:
        html_message = render_to_string(
            "accounts/emails/password_reset_email.html",
            {
                "user": user,
                "reset_url": reset_url,
                "site_name": "Lopes Peinture",
                "ip_address": get_client_ip(request),
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=_("Réinitialisation de mot de passe - Lopes Peinture"),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email de reset de senha enviado com sucesso para: {user.email}")
        return True

    except Exception as e:
        logger.error(
            f"Erro ao enviar email de reset de senha para {user.email}: {str(e)}"
        )
        return False


def send_password_changed_email(user, request):
    """
    Envia email de confirmação de alteração de senha.
    """
    try:
        html_message = render_to_string(
            "accounts/emails/password_changed_email.html",
            {
                "user": user,
                "site_name": "Lopes Peinture",
                "ip_address": get_client_ip(request),
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=_("Mot de passe modifié - Lopes Peinture"),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(
            f"Email de confirmação de alteração de senha enviado para: {user.email}"
        )
        return True

    except Exception as e:
        logger.error(
            f"Erro ao enviar email de confirmação de senha para {user.email}: {str(e)}"
        )
        return False


def send_verification_email(user, verification_url, request):
    """
    Envia email de verificação de conta.
    """
    try:
        html_message = render_to_string(
            "accounts/emails/verification_email.html",
            {
                "user": user,
                "verification_url": verification_url,
                "site_name": "Lopes Peinture",
                "ip_address": get_client_ip(request),
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=_("Vérifiez votre email - Lopes Peinture"),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email de verificação enviado para: {user.email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email de verificação para {user.email}: {str(e)}")
        return False


def send_welcome_email(user, request):
    """
    Envia email de boas-vindas após registro.
    """
    try:
        html_message = render_to_string(
            "accounts/emails/welcome_email.html",
            {
                "user": user,
                "site_name": "Lopes Peinture",
                "login_url": request.build_absolute_uri("/accounts/login/"),
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=_("Bienvenue chez Lopes Peinture!"),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email de boas-vindas enviado para: {user.email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas para {user.email}: {str(e)}")
        return False


def send_contact_form_email(name, email, subject, message, request):
    """
    Envia email de formulário de contato.
    """
    try:
        html_message = render_to_string(
            "emails/contact_form_email.html",
            {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "ip_address": get_client_ip(request),
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f"Contact - {subject}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email de contato enviado de: {email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email de contato de {email}: {str(e)}")
        return False


def send_quote_request_email(user, quote_data, request):
    """
    Envia email de solicitação de orçamento.
    """
    try:
        html_message = render_to_string(
            "emails/quote_request_email.html",
            {
                "user": user,
                "quote_data": quote_data,
                "site_name": "Lopes Peinture",
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)

        # Enviar para o cliente
        send_mail(
            subject=_("Demande de devis reçue - Lopes Peinture"),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        # Enviar para a empresa
        send_mail(
            subject=f"Nouvelle demande de devis - {user.get_full_name()}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.QUOTES_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email de solicitação de orçamento enviado para: {user.email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email de orçamento para {user.email}: {str(e)}")
        return False
