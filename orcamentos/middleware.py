from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from orcamentos.auditoria import AuditoriaManager, TipoAcao
import threading

# Thread local para armazenar dados da requisição atual
_thread_locals = threading.local()


class AuditoriaMiddleware(MiddlewareMixin):
    """Middleware para integração automática do sistema de auditoria"""

    def process_request(self, request):
        """Armazena dados da requisição para uso nos models"""
        # Armazenar request no thread local
        _thread_locals.request = request
        _thread_locals.user = getattr(request, 'user', None)

        return None

    def process_response(self, request, response):
        """Limpa dados do thread local após a requisição"""
        # Limpar thread locals
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user

        return response

    def process_exception(self, request, exception):
        """Registra exceções na auditoria"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Registrar erro na auditoria usando o usuário como objeto
                AuditoriaManager.registrar_acao(
                    usuario=request.user,
                    acao=TipoAcao.VISUALIZACAO,  # Usar visualização para erros
                    objeto=request.user,
                    descricao=f"Erro na requisição: {request.path}",
                    request=request,
                    sucesso=False,
                    erro_mensagem=str(exception)[:500],
                    modulo="orcamentos",
                    funcionalidade="Sistema"
                )
            except Exception:
                # Se falhar, não interromper o processamento normal
                pass

        return None


def get_current_request():
    """Retorna a requisição atual do thread local"""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Retorna o usuário atual do thread local"""
    return getattr(_thread_locals, 'user', None)


# Mixin para models que precisam de auditoria automática
class AuditoriaMixin:
    """Mixin para adicionar auditoria automática aos models"""

    def save(self, *args, **kwargs):
        """Override do save para capturar dados para auditoria"""
        # Capturar usuário atual
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            self._current_user = current_user

        # Capturar estado anterior se for uma atualização
        if self.pk:
            try:
                estado_anterior = self.__class__.objects.get(pk=self.pk)
                self._estado_anterior = estado_anterior
            except self.__class__.DoesNotExist:
                self._estado_anterior = None

        # Executar save normal
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override do delete para capturar dados para auditoria"""
        # Capturar usuário atual
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            self._current_user = current_user

        # Executar delete normal
        super().delete(*args, **kwargs)
