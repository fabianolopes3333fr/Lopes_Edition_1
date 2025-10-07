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
    DOWNLOAD = "download", "Téléchargement"
    # NOVOS TIPOS PARA ORÇAMENTOS ÓRFÃOS
    VINCULACAO_ORFAO = "vinculacao_orfao", "Liaison demande orpheline"
    DETECCAO_ORFAO = "deteccao_orfao", "Détection demande orpheline"
    PROCESSAMENTO_LOTE = "processamento_lote", "Traitement en lot"
    NOTIFICACAO_VINCULACAO = "notificacao_vinculacao", "Notification de liaison"
    # NOVOS TIPOS PARA FATURAS
    CRIACAO_FATURA = "criacao_fatura", "Création de facture"
    ENVIO_FATURA = "envio_fatura", "Envoi de facture"
    PAGAMENTO_FATURA = "pagamento_fatura", "Paiement de facture"
    VISUALIZACAO_FATURA = "visualizacao_fatura", "Consultation de facture"
    DOWNLOAD_FATURA_PDF = "download_fatura_pdf", "Téléchargement PDF facture"
    EDICAO_FATURA = "edicao_fatura", "Modification de facture"
    ANULACAO_FATURA = "anulacao_fatura", "Annulation de facture"


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
        max_length=30,
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

    # ============ MÉTODOS ESPECÍFICOS PARA ORÇAMENTOS ÓRFÃOS ============

    @staticmethod
    def registrar_vinculacao_orcamento_orfao(usuario, solicitacao, request=None, origem="manual"):
        """Registra vinculação de orçamento órfão a um usuário"""
        dados_anteriores = {'cliente': None, 'email_solicitante': solicitacao.email_solicitante}
        dados_posteriores = {
            'cliente': usuario.id if usuario else None,
            'cliente_nome': usuario.get_full_name() if usuario else '',
            'email_solicitante': solicitacao.email_solicitante
        }

        campos_alterados = {
            'cliente': {
                'anterior': None,
                'novo': f"{usuario.get_full_name()} ({usuario.email})" if usuario else None
            }
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.VINCULACAO_ORFAO,
            objeto=solicitacao,
            descricao=f"Liaison automatique de la demande orpheline {solicitacao.numero} à l'utilisateur {usuario.get_full_name() if usuario else 'Unknown'} - Origine: {origem}",
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Liaison demandes orphelines"
        )

    @staticmethod
    def registrar_deteccao_orcamento_orfao(usuario, email, quantidade_encontrada, request=None):
        """Registra detecção de orçamentos órfãos"""
        # Usar o usuário como objeto para este tipo de log
        dados_deteccao = {
            'email_verificado': email,
            'quantidade_orfas_encontradas': quantidade_encontrada,
            'data_deteccao': timezone.now().isoformat(),
            'usuario_beneficiado': usuario.id if usuario else None
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.DETECCAO_ORFAO,
            objeto=usuario,
            descricao=f"Détection de {quantidade_encontrada} demande{'s' if quantidade_encontrada > 1 else ''} orpheline{'s' if quantidade_encontrada > 1 else ''} pour l'email {email}",
            request=request,
            dados_posteriores=dados_deteccao,
            funcionalidade="Détection automatique"
        )

    @staticmethod
    def registrar_processamento_lote_orfaos(usuario_comando, total_processadas, total_vinculadas, emails_processados, request=None):
        """Registra processamento em lote de orçamentos órfãos via comando"""
        dados_processamento = {
            'total_orfas_encontradas': total_processadas,
            'total_vinculadas': total_vinculadas,
            'emails_processados': list(emails_processados),
            'data_processamento': timezone.now().isoformat(),
            'metodo': 'comando_gerenciamento'
        }

        # Usar o primeiro usuário como objeto ou criar um log genérico
        objeto = usuario_comando if usuario_comando else User.objects.filter(is_staff=True).first()

        return AuditoriaManager.registrar_acao(
            usuario=usuario_comando,
            acao=TipoAcao.PROCESSAMENTO_LOTE,
            objeto=objeto,
            descricao=f"Traitement en lot: {total_vinculadas}/{total_processadas} demandes orphelines liées - {len(emails_processados)} emails traités",
            request=request,
            dados_posteriores=dados_processamento,
            funcionalidade="Traitement en lot"
        )

    @staticmethod
    def registrar_notificacao_vinculacao(usuario_notificado, quantidade_orcamentos, metodo_vinculacao="automatico", request=None):
        """Registra envio de notificação sobre vinculação de orçamentos"""
        dados_notificacao = {
            'usuario_notificado': usuario_notificado.id,
            'email_notificado': usuario_notificado.email,
            'quantidade_orcamentos': quantidade_orcamentos,
            'metodo_vinculacao': metodo_vinculacao,
            'data_notificacao': timezone.now().isoformat()
        }

        return AuditoriaManager.registrar_acao(
            usuario=None,  # Notificação é do sistema
            acao=TipoAcao.NOTIFICACAO_VINCULACAO,
            objeto=usuario_notificado,
            descricao=f"Notification envoyée à {usuario_notificado.get_full_name()} ({usuario_notificado.email}) - {quantidade_orcamentos} demande{'s' if quantidade_orcamentos > 1 else ''} liée{'s' if quantidade_orcamentos > 1 else ''}",
            request=request,
            dados_posteriores=dados_notificacao,
            funcionalidade="Notification système"
        )

    @staticmethod
    def registrar_mudanca_status_projeto(usuario, projeto, status_anterior, status_novo, request=None):
        """Registra mudança de status de projeto"""
        dados_anteriores = {'status': status_anterior}
        dados_posteriores = {'status': status_novo}

        campos_alterados = {
            'status': {
                'anterior': status_anterior,
                'novo': status_novo
            }
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.EDICAO,
            objeto=projeto,
            descricao=f"Changement de statut du projet '{projeto.titulo}': {status_anterior} → {status_novo}",
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Changement de statut projet"
        )

    @staticmethod
    def registrar_solicitacao_publica_usuario_logado(usuario, solicitacao, request=None):
        """Registra quando usuário logado usa URL pública"""
        dados_contexto = {
            'usuario_logado': usuario.id,
            'email_formulario': solicitacao.email_solicitante,
            'emails_coincidem': solicitacao.email_solicitante.lower() == usuario.email.lower(),
            'vinculacao_automatica': True
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.CRIACAO,
            objeto=solicitacao,
            descricao=f"Demande de devis via URL publique par utilisateur connecté - Auto-liaison activée",
            request=request,
            dados_posteriores=dados_contexto,
            funcionalidade="Demande publique avec utilisateur connecté"
        )

    # ============ MÉTODOS ESPECÍFICOS PARA FATURAS ============

    @staticmethod
    def registrar_criacao_fatura(usuario, fatura, request=None, origem="manual", orcamento_vinculado=None):
        """Registra criação de nova fatura"""
        dados_fatura = {
            'numero': fatura.numero,
            'cliente_id': fatura.cliente.id if fatura.cliente else None,
            'cliente_nome': fatura.cliente.get_full_name() if fatura.cliente else None,
            'titulo': fatura.titulo,
            'total': str(fatura.total),
            'status': fatura.status,
            'data_emissao': fatura.data_emissao.isoformat() if fatura.data_emissao else None,
            'data_vencimento': fatura.data_vencimento.isoformat() if fatura.data_vencimento else None,
            'origem': origem,
            'orcamento_vinculado': orcamento_vinculado.numero if orcamento_vinculado else None
        }

        descricao = f"Création de la facture {fatura.numero} pour le client {fatura.cliente.get_full_name() if fatura.cliente else 'N/A'}"
        if orcamento_vinculado:
            descricao += f" (basée sur le devis {orcamento_vinculado.numero})"

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.CRIACAO_FATURA,
            objeto=fatura,
            descricao=descricao,
            request=request,
            dados_posteriores=dados_fatura,
            funcionalidade="Création de facture"
        )

    @staticmethod
    def registrar_envio_fatura(usuario, fatura, request=None):
        """Registra envio de fatura ao cliente"""
        dados_anteriores = {
            'status': 'brouillon',
            'data_envio': None
        }

        dados_posteriores = {
            'status': fatura.status,
            'data_envio': fatura.data_envio.isoformat() if fatura.data_envio else None,
            'cliente_email': fatura.cliente.email if fatura.cliente else None
        }

        campos_alterados = {
            'status': {
                'anterior': 'brouillon',
                'novo': fatura.status
            },
            'data_envio': {
                'anterior': None,
                'novo': fatura.data_envio.isoformat() if fatura.data_envio else None
            }
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.ENVIO_FATURA,
            objeto=fatura,
            descricao=f"Envoi de la facture {fatura.numero} au client {fatura.cliente.get_full_name() if fatura.cliente else 'N/A'}",
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Envoi de facture"
        )

    @staticmethod
    def registrar_pagamento_fatura(usuario, fatura, data_pagamento, request=None):
        """Registra marcação de fatura como paga"""
        dados_anteriores = {
            'status': fatura.status,
            'data_pagamento': fatura.data_pagamento.isoformat() if fatura.data_pagamento else None
        }

        dados_posteriores = {
            'status': 'payee',
            'data_pagamento': data_pagamento.isoformat() if data_pagamento else None,
            'total_pago': str(fatura.total)
        }

        campos_alterados = {
            'status': {
                'anterior': fatura.status,
                'novo': 'payee'
            },
            'data_pagamento': {
                'anterior': fatura.data_pagamento.isoformat() if fatura.data_pagamento else None,
                'novo': data_pagamento.isoformat() if data_pagamento else None
            }
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.PAGAMENTO_FATURA,
            objeto=fatura,
            descricao=f"Facture {fatura.numero} marquée comme payée - Montant: {fatura.total}€",
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Paiement de facture"
        )

    @staticmethod
    def registrar_visualizacao_fatura(usuario, fatura, request=None, tipo_visualizacao="detail"):
        """Registra visualização de fatura pelo cliente"""
        dados_visualizacao = {
            'fatura_numero': fatura.numero,
            'tipo_visualizacao': tipo_visualizacao,  # 'list', 'detail', 'pdf'
            'status_fatura': fatura.status,
            'cliente_id': fatura.cliente.id if fatura.cliente else None,
            'timestamp': timezone.now().isoformat()
        }

        descricao_tipo = {
            'list': 'liste des factures',
            'detail': 'détails de la facture',
            'pdf': 'PDF de la facture'
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.VISUALIZACAO_FATURA,
            objeto=fatura,
            descricao=f"Consultation de {descricao_tipo.get(tipo_visualizacao, 'facture')} {fatura.numero} par {usuario.get_full_name() if usuario else 'Anonyme'}",
            request=request,
            dados_posteriores=dados_visualizacao,
            funcionalidade="Consultation de facture"
        )

    @staticmethod
    def registrar_download_fatura_pdf(usuario, fatura, request=None):
        """Registra download do PDF da fatura"""
        dados_download = {
            'fatura_numero': fatura.numero,
            'formato': 'PDF',
            'timestamp': timezone.now().isoformat(),
            'usuario_id': usuario.id if usuario else None,
            'usuario_nome': usuario.get_full_name() if usuario else None
        }

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.DOWNLOAD_FATURA_PDF,
            objeto=fatura,
            descricao=f"Téléchargement PDF de la facture {fatura.numero} par {usuario.get_full_name() if usuario else 'Anonyme'}",
            request=request,
            dados_posteriores=dados_download,
            funcionalidade="Téléchargement PDF facture"
        )

    @staticmethod
    def registrar_edicao_fatura(usuario, fatura, dados_anteriores, dados_posteriores, request=None):
        """Registra edição de fatura"""
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
            acao=TipoAcao.EDICAO_FATURA,
            objeto=fatura,
            descricao=f"Modification de la facture {fatura.numero}",
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Modification de facture"
        )

    @staticmethod
    def registrar_anulacao_fatura(usuario, fatura, motivo="", request=None):
        """Registra anulação de fatura"""
        dados_anteriores = {
            'status': fatura.status,
            'total': str(fatura.total)
        }

        dados_posteriores = {
            'status': 'annulee',
            'motivo_anulacao': motivo,
            'data_anulacao': timezone.now().isoformat()
        }

        campos_alterados = {
            'status': {
                'anterior': fatura.status,
                'novo': 'annulee'
            }
        }

        descricao = f"Annulation de la facture {fatura.numero}"
        if motivo:
            descricao += f" - Motif: {motivo}"

        return AuditoriaManager.registrar_acao(
            usuario=usuario,
            acao=TipoAcao.ANULACAO_FATURA,
            objeto=fatura,
            descricao=descricao,
            request=request,
            dados_anteriores=dados_anteriores,
            dados_posteriores=dados_posteriores,
            campos_alterados=campos_alterados,
            funcionalidade="Annulation de facture"
        )

    @staticmethod
    def obter_historico_fatura(fatura):
        """Obtém histórico completo de uma fatura"""
        return AuditoriaManager.obter_historico_objeto(fatura)

    @staticmethod
    def obter_faturas_visualizadas_cliente(usuario, dias=30):
        """Obtém faturas visualizadas recentemente por um cliente"""
        data_limite = timezone.now() - timezone.timedelta(days=dias)

        return LogAuditoria.objects.filter(
            usuario=usuario,
            acao__in=[
                TipoAcao.VISUALIZACAO_FATURA,
                TipoAcao.DOWNLOAD_FATURA_PDF
            ],
            timestamp__gte=data_limite
        ).order_by('-timestamp')

    @staticmethod
    def obter_estatisticas_faturas(data_inicio=None, data_fim=None):
        """Obtém estatísticas de atividades relacionadas a faturas"""
        if not data_inicio:
            data_inicio = timezone.now() - timezone.timedelta(days=30)
        if not data_fim:
            data_fim = timezone.now()

        logs_faturas = LogAuditoria.objects.filter(
            timestamp__gte=data_inicio,
            timestamp__lte=data_fim,
            acao__in=[
                TipoAcao.CRIACAO_FATURA,
                TipoAcao.ENVIO_FATURA,
                TipoAcao.PAGAMENTO_FATURA,
                TipoAcao.VISUALIZACAO_FATURA,
                TipoAcao.DOWNLOAD_FATURA_PDF,
                TipoAcao.EDICAO_FATURA,
                TipoAcao.ANULACAO_FATURA
            ]
        )

        estatisticas = {
            'total_acoes_faturas': logs_faturas.count(),
            'faturas_criadas': logs_faturas.filter(acao=TipoAcao.CRIACAO_FATURA).count(),
            'faturas_enviadas': logs_faturas.filter(acao=TipoAcao.ENVIO_FATURA).count(),
            'faturas_pagas': logs_faturas.filter(acao=TipoAcao.PAGAMENTO_FATURA).count(),
            'visualizacoes': logs_faturas.filter(acao=TipoAcao.VISUALIZACAO_FATURA).count(),
            'downloads_pdf': logs_faturas.filter(acao=TipoAcao.DOWNLOAD_FATURA_PDF).count(),
            'edicoes': logs_faturas.filter(acao=TipoAcao.EDICAO_FATURA).count(),
            'anulacoes': logs_faturas.filter(acao=TipoAcao.ANULACAO_FATURA).count(),
        }

        return estatisticas

