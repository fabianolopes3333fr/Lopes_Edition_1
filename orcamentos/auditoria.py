from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json

User = get_user_model()


class TipoAcao(models.TextChoices):
    CRIACAO = "criacao", "Création"
    EDICAO = "edicao", "Modification"
    EXCLUSAO = "exclusao", "Suppression"
    VISUALIZACAO = "visualizacao", "Consultation"
    ENVIO = "envio", "Envoi"
    APROVACAO = "aprovacao", "Approbation"
    REJEICAO = "rejeicao", "Rejet"
    CANCELAMENTO = "cancelamento", "Annulation"


class LogAuditoria(models.Model):
    """Model para auditoria de alterações no sistema"""

    # Identificação da ação
    timestamp = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria'
    )
    sessao_id = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Ação realizada
    acao = models.CharField(
        max_length=20,
        choices=TipoAcao.choices,
        verbose_name="Action"
    )
    descricao = models.TextField(verbose_name="Description")

    # Objeto afetado (usando GenericForeignKey para flexibilidade)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    objeto_afetado = GenericForeignKey('content_type', 'object_id')

    # Dados da alteração
    dados_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Données précédentes"
    )
    dados_posteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Nouvelles données"
    )
    campos_alterados = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Champs modifiés"
    )

    # Contexto adicional
    modulo = models.CharField(max_length=50, verbose_name="Module")
    funcionalidade = models.CharField(max_length=100, verbose_name="Fonctionnalité")

    # Metadados
    sucesso = models.BooleanField(default=True)
    erro_mensagem = models.TextField(blank=True)

    class Meta:
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['usuario']),
            models.Index(fields=['acao']),
            models.Index(fields=['modulo']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        usuario_nome = self.usuario.get_full_name() if self.usuario else "Anonyme"
        return f"{self.timestamp.strftime('%d/%m/%Y %H:%M')} - {usuario_nome} - {self.get_acao_display()}"

    @property
    def resumo_alteracao(self):
        """Retorna um resumo das alterações realizadas"""
        if not self.campos_alterados:
            return "Aucune modification détectée"

        resumo = []
        for campo, dados in self.campos_alterados.items():
            valor_anterior = dados.get('anterior', 'N/A')
            valor_novo = dados.get('novo', 'N/A')
            resumo.append(f"{campo}: {valor_anterior} → {valor_novo}")

        return "; ".join(resumo)


class AuditoriaManager:
    """Manager para facilitar o registro de logs de auditoria"""

    @staticmethod
    def registrar_acao(
        usuario,
        acao,
        objeto,
        descricao,
        request=None,
        dados_anteriores=None,
        dados_posteriores=None,
        campos_alterados=None,
        sucesso=True,
        erro_mensagem="",
        modulo="orcamentos",
        funcionalidade=""
    ):
        """
        Registra uma ação de auditoria

        Args:
            usuario: User que realizou a ação
            acao: Tipo da ação (TipoAcao)
            objeto: Objeto Django afetado
            descricao: Descrição da ação
            request: HttpRequest para extrair metadados
            dados_anteriores: Estado anterior do objeto
            dados_posteriores: Estado posterior do objeto
            campos_alterados: Dict com campos que foram alterados
            sucesso: Se a ação foi bem-sucedida
            erro_mensagem: Mensagem de erro se houver
            modulo: Nome do módulo
            funcionalidade: Nome da funcionalidade
        """

        # Extrair metadados da requisição
        ip_address = None
        user_agent = ""
        sessao_id = ""

        if request:
            ip_address = AuditoriaManager._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            sessao_id = request.session.session_key or ""

        # Determinar o tipo de conteúdo
        content_type = ContentType.objects.get_for_model(objeto)

        # Criar log
        log = LogAuditoria.objects.create(
            usuario=usuario,
            sessao_id=sessao_id,
            ip_address=ip_address,
            user_agent=user_agent,
            acao=acao,
            descricao=descricao,
            content_type=content_type,
            object_id=objeto.pk,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            modulo=modulo,
            funcionalidade=funcionalidade,
            sucesso=sucesso,
            erro_mensagem=erro_mensagem
        )

        return log

    @staticmethod
    def _get_client_ip(request):
        """Extrai o IP do cliente da requisição"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def registrar_criacao(usuario, objeto, request=None, dados_objeto=None):
        """Registra criação de objeto"""
        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.CRIACAO,
            objeto=objeto,
            descricao=f"Création de {objeto._meta.verbose_name}: {str(objeto)}",
            request=request,
            dados_posteriores=dados_objeto,
            funcionalidade="Création"
        )

    @staticmethod
    def registrar_edicao(usuario, objeto, dados_anteriores, dados_posteriores, request=None):
        """Registra edição de objeto"""

        # Calcular campos alterados
        campos_alterados = {}
        if dados_anteriores and dados_posteriores:
            for campo, valor_novo in dados_posteriores.items():
                valor_anterior = dados_anteriores.get(campo)
                if valor_anterior != valor_novo:
                    campos_alterados[campo] = {
                        'anterior': valor_anterior,
                        'novo': valor_novo
                    }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.EDICAO,
            objeto=objeto,
            descricao=f"Modification de {objeto._meta.verbose_name}: {str(objeto)}",
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Modification"
        )

    @staticmethod
    def registrar_exclusao(usuario, objeto, request=None, dados_objeto=None):
        """Registra exclusão de objeto"""
        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.EXCLUSAO,
            objeto=objeto,
            descricao=f"Suppression de {objeto._meta.verbose_name}: {str(objeto)}",
            request=request,
            dados_anteriores=dados_objeto,
            funcionalidade="Suppression"
        )

    @staticmethod
    def registrar_visualizacao(usuario, objeto, request=None):
        """Registra visualização de objeto"""
        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.VISUALIZACAO,
            objeto=objeto,
            descricao=f"Consultation de {objeto._meta.verbose_name}: {str(objeto)}",
            request=request,
            funcionalidade="Consultation"
        )

    @staticmethod
    def registrar_envio_orcamento(usuario, orcamento, request=None):
        """Registra envio de orçamento específico"""
        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.ENVIO,
            objeto=orcamento,
            descricao=f"Envoi du devis {orcamento.numero} au client",
            request=request,
            funcionalidade="Envoi de devis"
        )

    @staticmethod
    def registrar_aprovacao_orcamento(usuario, orcamento, request=None):
        """Registra aprovação de orçamento"""
        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.APROVACAO,
            objeto=orcamento,
            descricao=f"Acceptation du devis {orcamento.numero} par le client",
            request=request,
            funcionalidade="Acceptation de devis"
        )

    @staticmethod
    def registrar_rejeicao_orcamento(usuario, orcamento, motivo="", request=None):
        """Registra rejeição de orçamento"""
        descricao = f"Rejet du devis {orcamento.numero} par le client"
        if motivo:
            descricao += f" - Motif: {motivo}"

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.REJEICAO,
            objeto=orcamento,
            descricao=descricao,
            request=request,
            funcionalidade="Rejet de devis"
        )

    @staticmethod
    def obter_historico_objeto(objeto, limit=50):
        """Obtém histórico de alterações de um objeto"""
        content_type = ContentType.objects.get_for_model(objeto)

        return LogAuditoria.objects.filter(
            content_type=content_type,
            object_id=objeto.pk
        ).order_by('-timestamp')[:limit]

    @staticmethod
    def obter_atividades_usuario(usuario, dias=30, limit=100):
        """Obtém atividades recentes de um usuário"""
        data_limite = timezone.now() - timezone.timedelta(days=dias)

        return LogAuditoria.objects.filter(
            usuario=usuario,
            timestamp__gte=data_limite
        ).order_by('-timestamp')[:limit]

    @staticmethod
    def obter_estatisticas_periodo(data_inicio, data_fim):
        """Obtém estatísticas de atividades em um período"""
        logs = LogAuditoria.objects.filter(
            timestamp__gte=data_inicio,
            timestamp__lte=data_fim
        )

        estatisticas = {
            'total_acoes': logs.count(),
            'acoes_por_tipo': {},
            'usuarios_mais_ativos': {},
            'modulos_mais_usados': {},
            'acoes_por_dia': {}
        }

        # Contar ações por tipo
        for acao, nome in TipoAcao.choices:
            count = logs.filter(acao=acao).count()
            if count > 0:
                estatisticas['acoes_por_tipo'][nome] = count

        # Usuários mais ativos
        usuarios_count = logs.values('usuario__first_name', 'usuario__last_name').annotate(
            total=models.Count('id')
        ).order_by('-total')[:10]

        for usuario in usuarios_count:
            nome = f"{usuario['usuario__first_name']} {usuario['usuario__last_name']}"
            estatisticas['usuarios_mais_ativos'][nome] = usuario['total']

        # Módulos mais usados
        modulos_count = logs.values('modulo').annotate(
            total=models.Count('id')
        ).order_by('-total')

        for modulo in modulos_count:
            estatisticas['modulos_mais_usados'][modulo['modulo']] = modulo['total']

        return estatisticas


# Decorator para auditoria automática
def auditar_acao(acao, descricao_func=None, modulo="orcamentos", funcionalidade=""):
    """
    Decorator para auditoria automática de views

    Usage:
        @auditar_acao(TipoAcao.CRIACAO, "Criação de projeto")
        def criar_projeto(request):
            # ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                # Executar a view
                response = view_func(request, *args, **kwargs)

                # Se a view foi bem-sucedida, registrar auditoria
                if hasattr(response, 'status_code') and 200 <= response.status_code < 400:
                    descricao = descricao_func(request, *args, **kwargs) if callable(descricao_func) else descricao_func

                    # Tentar obter objeto do contexto ou kwargs
                    objeto = None
                    if hasattr(response, 'context_data') and response.context_data:
                        for key in ['objeto', 'object', 'projeto', 'orcamento', 'solicitacao']:
                            if key in response.context_data:
                                objeto = response.context_data[key]
                                break

                    if objeto:
                        AuditoriaManager.registrar_acao(
                            usuario=request.user if request.user.is_authenticated else None,
                            acao=acao,
                            objeto=objeto,
                            descricao=descricao or f"Ação {acao} realizada",
                            request=request,
                            modulo=modulo,
                            funcionalidade=funcionalidade
                        )

                return response

            except Exception as e:
                # Registrar erro na auditoria
                if request.user.is_authenticated:
                    # Criar um objeto dummy para registrar o erro
                    from django.contrib.contenttypes.models import ContentType
                    ct = ContentType.objects.get_for_model(User)

                    AuditoriaManager.registrar_acao(
                        usuario=request.user,
                        acao=acao,
                        objeto=request.user,  # Usar usuário como objeto em caso de erro
                        descricao=f"Erro ao executar {funcionalidade}",
                        request=request,
                        sucesso=False,
                        erro_mensagem=str(e),
                        modulo=modulo,
                        funcionalidade=funcionalidade
                    )

                # Re-lançar a exceção
                raise

        return wrapper
    return decorator
