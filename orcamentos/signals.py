from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import SolicitacaoOrcamento
from .auditoria import AuditoriaManager, TipoAcao
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def vincular_orcamentos_orfaos(sender, instance, created, **kwargs):
    """
    Signal que é executado quando um usuário é criado.
    Vincula automaticamente orçamentos solicitados anteriormente com o mesmo email.
    """
    if created and instance.email:
        # Buscar solicitações órfãs (sem cliente) com o mesmo email
        solicitacoes_orfas = SolicitacaoOrcamento.objects.filter(
            cliente__isnull=True,
            email_solicitante__iexact=instance.email
        )

        if solicitacoes_orfas.exists():
            count = solicitacoes_orfas.count()

            # Registrar detecção na auditoria
            AuditoriaManager.registrar_deteccao_orcamento_orfao(
                usuario=instance,
                email=instance.email,
                quantidade_encontrada=count
            )

            # Vincular as solicitações ao novo usuário e auditar cada vinculação
            for solicitacao in solicitacoes_orfas:
                # Registrar vinculação individual na auditoria
                AuditoriaManager.registrar_vinculacao_orcamento_orfao(
                    usuario=instance,
                    solicitacao=solicitacao,
                    origem="signal_cadastro"
                )

            # Fazer a vinculação no banco
            solicitacoes_orfas.update(cliente=instance)

            logger.info(
                f"Vinculadas {count} solicitações órfãs ao usuário {instance.email} (ID: {instance.id})"
            )

            # Criar uma notificação para o usuário sobre os orçamentos encontrados
            from .services import NotificationService
            try:
                NotificationService.notificar_orcamentos_vinculados(instance, count)

                # Registrar notificação na auditoria
                AuditoriaManager.registrar_notificacao_vinculacao(
                    usuario_notificado=instance,
                    quantidade_orcamentos=count,
                    metodo_vinculacao="signal_automatico"
                )
            except Exception as e:
                logger.error(f"Erro ao notificar sobre orçamentos vinculados: {e}")

        else:
            logger.info(f"Nenhum orçamento órfão encontrado para {instance.email}")

def verificar_e_vincular_orcamentos_existentes(email, usuario):
    """
    Função utilitária para verificar e vincular orçamentos existentes.
    Pode ser chamada manualmente se necessário.
    """
    solicitacoes_orfas = SolicitacaoOrcamento.objects.filter(
        cliente__isnull=True,
        email_solicitante__iexact=email
    )

    vinculadas = []
    for solicitacao in solicitacoes_orfas:
        # Registrar vinculação na auditoria antes de fazer a alteração
        AuditoriaManager.registrar_vinculacao_orcamento_orfao(
            usuario=usuario,
            solicitacao=solicitacao,
            origem="manual_admin"
        )

        solicitacao.cliente = usuario
        solicitacao.save()
        vinculadas.append(solicitacao.numero)

    # Se houve vinculações, registrar o processamento geral
    if vinculadas:
        AuditoriaManager.registrar_processamento_lote_orfaos(
            usuario_comando=None,  # Foi manual via admin
            total_processadas=len(vinculadas),
            total_vinculadas=len(vinculadas),
            emails_processados={email}
        )

    return vinculadas
