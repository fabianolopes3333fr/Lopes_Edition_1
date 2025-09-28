"""
Utilitários para o módulo accounts.
"""

import secrets
import uuid
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def generate_verification_token(user):
    """
    Gera um token de verificação para o usuário.

    Args:
        user: Instância do usuário

    Returns:
        str: Token de verificação
    """
    # Gerar UUID único
    token = str(uuid.uuid4())

    # Salvar no usuário
    user.verification_token = token
    user.save(update_fields=["verification_token"])

    return token


def get_client_ip(request):
    """
    Obtém o IP real do cliente considerando proxies.

    Args:
        request: Requisição HTTP

    Returns:
        str: Endereço IP do cliente
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip or "unknown"


def export_user_data_to_csv(users):
    """
    Exporta dados de usuários para CSV (placeholder).
    """
    # Implementar conforme necessário
    pass
