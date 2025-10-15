"""
Sistema de Email - Lopes Peinture
Centraliza todo o envio de emails do sistema com templates profissionais.
"""

import logging
from django.conf import settings
from django.core.mail import send_mail, get_connection
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


# ==================== INTEGRAÇÃO COM SYSTEM_CONFIG ====================

def _get_active_email_settings():
    """Obtém as configurações de e-mail ativas do banco (system_config.EmailSettings)."""
    try:
        from system_config.models import EmailSettings
        cfg = (
            EmailSettings.objects.filter(actif=True).order_by("-updated_at").first()
        )
        return cfg
    except Exception as e:
        # Evitar qualquer quebra se app não estiver disponível
        logger.debug(f"EmailSettings indisponível ou erro ao carregar: {e}")
        return None


def _get_from_email():
    """Resolve o remetente com múltiplos fallbacks: DB -> settings -> SMTP username -> CompanySettings.email."""
    cfg = _get_active_email_settings()
    # 1) DB from_email
    if cfg and getattr(cfg, "from_email", None):
        from_email = (cfg.from_email or "").strip()
        if from_email:
            return from_email
    # 2) settings.DEFAULT_FROM_EMAIL
    default_from = (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
    if default_from:
        return default_from
    # 3) SMTP username (DB.username primeiro, depois settings.EMAIL_HOST_USER)
    if cfg and getattr(cfg, "username", None):
        username = (cfg.username or "").strip()
        if username:
            return username
    settings_user = (getattr(settings, "EMAIL_HOST_USER", "") or "").strip()
    if settings_user:
        return settings_user
    # 4) CompanySettings.email
    try:
        from system_config.models import CompanySettings
        company_email = (CompanySettings.get_solo().email or "").strip()
        if company_email:
            return company_email
    except Exception:
        pass
    # 5) None -> Django usará DEFAULT_FROM_EMAIL internamente
    return None


def _is_test_or_dev_backend():
    backend = (getattr(settings, "EMAIL_BACKEND", "") or "").lower()
    return (
        "locmem" in backend
        or "console" in backend
        or "dummy" in backend
    )


def _get_smtp_connection():
    """
    Cria uma conexão SMTP baseada nas configurações ativas do DB.
    Usa SMTP quando EmailSettings.actif=True, exceto se backend atual for de teste/dev (locmem/console/dummy).
    Pode ser forçado via settings.EMAIL_FORCE_DB_SMTP=True.
    """
    cfg = _get_active_email_settings()
    if not cfg:
        return None

    # Evitar forçar SMTP em backends de teste/dev, a menos que forçado por settings
    force_db_smtp = bool(getattr(settings, "EMAIL_FORCE_DB_SMTP", False))
    if _is_test_or_dev_backend() and not force_db_smtp:
        logger.debug("Email: backend de teste/dev detectado e force desativado; não forçando SMTP do DB.")
        return None
    if force_db_smtp:
        logger.debug("Email: forçando uso do SMTP do DB (EMAIL_FORCE_DB_SMTP=True).")

    try:
        conn = get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=cfg.host or getattr(settings, "EMAIL_HOST", None),
            port=cfg.port or getattr(settings, "EMAIL_PORT", None),
            username=cfg.username or getattr(settings, "EMAIL_HOST_USER", None),
            password=cfg.password or getattr(settings, "EMAIL_HOST_PASSWORD", None),
            use_tls=cfg.use_tls,
            use_ssl=cfg.use_ssl,
            fail_silently=False,
        )
        logger.debug(f"Email: conexão SMTP customizada criada para host={cfg.host}:{cfg.port} tls={cfg.use_tls} ssl={cfg.use_ssl}")
        return conn
    except Exception as e:
        logger.error(f"Erro ao criar conexão SMTP customizada: {e}")
        return None


def _send_mail(subject, plain_message, html_message, recipients):
    """Wrapper para send_mail usando conexão e remetente dinâmicos, com fallback seguro."""
    try:
        from_email = _get_from_email()
        connection = _get_smtp_connection()
        logger.debug(f"Email: subject={subject!r}, from={from_email}, to={recipients}, using_custom_connection={bool(connection)}")
        return send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=list(recipients or []),
            html_message=html_message,
            fail_silently=False,
            connection=connection,
        )
    except Exception as e:
        logger.error(f"Erro no envio de email (subject={subject!r}) para {recipients}: {e}")
        return 0


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

        _send_mail(
            subject=_("Réinitialisation de mot de passe - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
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

        _send_mail(
            subject=_("Mot de passe modifié - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
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

        _send_mail(
            subject=_("Vérifiez votre email - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
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
                "login_url": request.build_absolute_uri(settings.LOGIN_URL),
            },
        )
        plain_message = strip_tags(html_message)

        _send_mail(
            subject=_("Bienvenue chez Lopes Peinture!"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
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

        recipient = getattr(settings, "CONTACT_EMAIL", None)
        if not recipient:
            try:
                from system_config.models import CompanySettings
                recipient = (CompanySettings.get_solo().email or None)
            except Exception:
                recipient = None

        if not recipient:
            logger.warning("Contato: nenhum destinatário configurado (CONTACT_EMAIL/CompanySettings)")
            return False

        _send_mail(
            subject=f"Contact - {subject}",
            plain_message=plain_message,
            html_message=html_message,
            recipients=[recipient],
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
        _send_mail(
            subject=_("Demande de devis reçue - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
        )

        # Enviar para a empresa (fallback para CompanySettings.email)
        recipient = getattr(settings, "QUOTES_EMAIL", None)
        if not recipient:
            try:
                from system_config.models import CompanySettings
                recipient = (CompanySettings.get_solo().email or None)
            except Exception:
                recipient = None

        if recipient:
            _send_mail(
                subject=f"Nouvelle demande de devis - {user.get_full_name()}",
                plain_message=plain_message,
                html_message=html_message,
                recipients=[recipient],
            )
        else:
            logger.warning("Orçamentos: nenhum destinatário configurado (QUOTES_EMAIL/CompanySettings)")

        logger.info(f"Email de solicitação de orçamento enviado para: {user.email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email de orçamento para {user.email}: {str(e)}")
        return False


# ==================== NOVOS EMAILS DE EVENTOS DE CONTA ====================

def send_account_status_email(user, is_active, request):
    """Notifica usuário sobre ativação/desativação da conta."""
    try:
        status_label = _("activé") if is_active else _("désactivé")
        html_message = render_to_string(
            "accounts/emails/account_status_email.html",
            {
                "user": user,
                "site_name": "Lopes Peinture",
                "status_label": status_label,
                "ip_address": get_client_ip(request),
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)
        _send_mail(
            subject=_("Statut du compte mis à jour - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
        )
        logger.info(f"Email de statut de compte ({status_label}) enviado à: {user.email}")
        return True
    except Exception as e:
        logger.error(f"Erreur en envoyant email de statut de compte à {user.email}: {str(e)}")
        return False


def send_2fa_status_email(user, enabled, request):
    """Notifica usuário sobre ativação/desativação do 2FA."""
    try:
        status_label = _("activée") if enabled else _("désactivée")
        html_message = render_to_string(
            "accounts/emails/two_factor_status_email.html",
            {
                "user": user,
                "site_name": "Lopes Peinture",
                "status_label": status_label,
                "ip_address": get_client_ip(request),
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)
        _send_mail(
            subject=_("Authentification à deux facteurs mise à jour - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
        )
        logger.info(f"Email d'état 2FA ({status_label}) envoyé à: {user.email}")
        return True
    except Exception as e:
        logger.error(f"Erreur en envoyant email 2FA à {user.email}: {str(e)}")
        return False


def send_social_disconnect_email(user, provider, request):
    """Notifica usuário sobre desconexão de um provedor social."""
    try:
        provider_label = (provider or "social").title()
        html_message = render_to_string(
            "accounts/emails/social_disconnected_email.html",
            {
                "user": user,
                "site_name": "Lopes Peinture",
                "provider": provider_label,
                "ip_address": get_client_ip(request),
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)
        _send_mail(
            subject=_("Connexion sociale déconnectée - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[user.email],
        )
        logger.info(f"Email de déconnexion sociale ({provider_label}) enviado à: {user.email}")
        return True
    except Exception as e:
        logger.error(f"Erreur en envoyant email de déconnexion sociale à {user.email}: {str(e)}")
        return False


def send_account_deleted_email(email, request):
    """Confirma que a conta foi excluída. Aceita apenas o email como string."""
    try:
        html_message = render_to_string(
            "accounts/emails/account_deleted_email.html",
            {
                "site_name": "Lopes Peinture",
                "ip_address": get_client_ip(request),
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)
        _send_mail(
            subject=_("Compte supprimé - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=[email],
        )
        logger.info(f"Email de confirmation de suppression de compte envoyé à: {email}")
        return True
    except Exception as e:
        logger.error(f"Erreur en envoyant email de suppression à {email}: {str(e)}")
        return False


def send_email_changed_notification(old_email, new_email, request):
    """Notifica mudança de email (envia para antigo e novo endereço)."""
    try:
        html_message = render_to_string(
            "accounts/emails/email_changed_notification.html",
            {
                "site_name": "Lopes Peinture",
                "old_email": old_email,
                "new_email": new_email,
                "timestamp": timezone.now(),
            },
        )
        plain_message = strip_tags(html_message)
        recipients = [e for e in {old_email, new_email} if e]
        if not recipients:
            return False
        _send_mail(
            subject=_("Adresse email mise à jour - Lopes Peinture"),
            plain_message=plain_message,
            html_message=html_message,
            recipients=recipients,
        )
        logger.info(f"Email de notification de changement d'adresse envoyé à: {recipients}")
        return True
    except Exception as e:
        logger.error(f"Erreur en envoyant email de changement d'adresse à {old_email}/{new_email}: {str(e)}")
        return False

