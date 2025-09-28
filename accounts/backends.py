from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailBackend(ModelBackend):
    """
    ✅ Backend customizado para autenticação por email
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica usuário usando email como username
        """
        if username is None:
            username = kwargs.get("email")

        if username is None or password is None:
            return None

        try:
            # ✅ CORRIGIDO: Buscar usuário por email (case-insensitive)
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )

            # ✅ DEBUG: Log para verificar se backend está sendo chamado
            logger.debug(f"Backend tentando autenticar: {username}")

            # Verificar senha
            if user.check_password(password) and self.user_can_authenticate(user):
                logger.debug(f"Autenticação bem-sucedida para: {user.email}")
                return user
            else:
                logger.debug(f"Senha incorreta ou usuário inativo: {username}")

        except User.DoesNotExist:
            logger.debug(f"Usuário não encontrado: {username}")
            # Executar verificação de senha mesmo se usuário não existir
            # para evitar timing attacks
            User().set_password(password)
            return None
        except Exception as e:
            logger.error(f"Erro no backend de autenticação: {e}")

        return None

    def get_user(self, user_id):
        """Recuperar usuário por ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
