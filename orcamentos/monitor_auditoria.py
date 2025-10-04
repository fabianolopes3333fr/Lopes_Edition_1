import os
import django
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from orcamentos.models import Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento
from orcamentos.auditoria import AuditoriaManager, LogAuditoria, TipoAcao

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auditoria_orcamentos.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MonitorOrcamentos:
    """Sistema de monitoramento para o app de orçamentos"""

    def __init__(self):
        self.modelos_monitorados = [
            Projeto,
            SolicitacaoOrcamento,
            Orcamento,
            ItemOrcamento
        ]
        self.conectar_signals()

    def conectar_signals(self):
        """Conecta os signals para monitoramento automático"""
        for modelo in self.modelos_monitorados:
            # Signal para capturar estado antes da alteração
            pre_save.connect(
                self.pre_save_handler,
                sender=modelo,
                dispatch_uid=f"pre_save_{modelo.__name__}"
            )

            # Signal para registrar criação/alteração
            post_save.connect(
                self.post_save_handler,
                sender=modelo,
                dispatch_uid=f"post_save_{modelo.__name__}"
            )

            # Signal para registrar exclusão
            post_delete.connect(
                self.post_delete_handler,
                sender=modelo,
                dispatch_uid=f"post_delete_{modelo.__name__}"
            )

    def pre_save_handler(self, sender, instance, **kwargs):
        """Captura estado anterior do objeto antes da alteração"""
        if instance.pk:  # Só para objetos existentes
            try:
                # Buscar estado anterior
                estado_anterior = sender.objects.get(pk=instance.pk)

                # Serializar dados anteriores
                dados_anteriores = self.serializar_objeto(estado_anterior)

                # Armazenar temporariamente no objeto
                instance._dados_anteriores = dados_anteriores

            except sender.DoesNotExist:
                instance._dados_anteriores = None

    def post_save_handler(self, sender, instance, created, **kwargs):
        """Registra criação ou alteração de objeto"""
        try:
            # Serializar estado atual
            dados_posteriores = self.serializar_objeto(instance)

            if created:
                # Registro de criação
                logger.info(f"CRIAÇÃO: {sender.__name__} - {instance}")

                AuditoriaManager.registrar_criacao(
                    usuario=getattr(instance, '_current_user', None),
                    objeto=instance,
                    dados_objeto=dados_posteriores
                )

            else:
                # Registro de alteração
                dados_anteriores = getattr(instance, '_dados_anteriores', None)

                if dados_anteriores:
                    # Verificar se houve alterações reais
                    alteracoes = self.detectar_alteracoes(dados_anteriores, dados_posteriores)

                    if alteracoes:
                        logger.info(f"ALTERAÇÃO: {sender.__name__} - {instance}")
                        logger.info(f"Campos alterados: {list(alteracoes.keys())}")

                        AuditoriaManager.registrar_edicao(
                            usuario=getattr(instance, '_current_user', None),
                            objeto=instance,
                            dados_anteriores=dados_anteriores,
                            dados_posteriores=dados_posteriores
                        )

                        # Log detalhado das alterações
                        for campo, dados in alteracoes.items():
                            logger.info(
                                f"  {campo}: {dados['anterior']} → {dados['novo']}"
                            )

        except Exception as e:
            logger.error(f"Erro no post_save_handler: {e}")

    def post_delete_handler(self, sender, instance, **kwargs):
        """Registra exclusão de objeto"""
        try:
            dados_objeto = self.serializar_objeto(instance)

            logger.warning(f"EXCLUSÃO: {sender.__name__} - {instance}")

            AuditoriaManager.registrar_exclusao(
                usuario=getattr(instance, '_current_user', None),
                objeto=instance,
                dados_objeto=dados_objeto
            )

        except Exception as e:
            logger.error(f"Erro no post_delete_handler: {e}")

    def serializar_objeto(self, obj):
        """Serializa objeto para JSON mantendo informações relevantes"""
        dados = {}

        # Campos que queremos rastrear
        campos_relevantes = {
            'Projeto': [
                'titulo', 'descricao', 'tipo_servico', 'status', 'urgencia',
                'endereco_projeto', 'cidade_projeto', 'area_aproximada',
                'orcamento_estimado', 'data_inicio_desejada'
            ],
            'SolicitacaoOrcamento': [
                'numero', 'status', 'nome_solicitante', 'email_solicitante',
                'telefone_solicitante', 'tipo_servico', 'descricao_servico',
                'urgencia', 'orcamento_maximo'
            ],
            'Orcamento': [
                'numero', 'status', 'titulo', 'subtotal', 'desconto',
                'total', 'prazo_execucao', 'validade_orcamento',
                'condicoes_pagamento', 'data_envio', 'data_resposta_cliente'
            ],
            'ItemOrcamento': [
                'referencia', 'descricao', 'quantidade', 'preco_unitario_ht',
                'preco_unitario_ttc', 'total_ht', 'total_ttc', 'taxa_tva',
                'remise_percentual'
            ]
        }

        nome_modelo = obj.__class__.__name__
        campos = campos_relevantes.get(nome_modelo, [])

        for campo in campos:
            if hasattr(obj, campo):
                valor = getattr(obj, campo)

                # Serializar tipos especiais
                if hasattr(valor, 'isoformat'):  # Data/DateTime
                    valor = valor.isoformat()
                elif hasattr(valor, 'quantize'):  # Decimal
                    valor = str(valor)
                elif valor is None:
                    valor = None
                else:
                    valor = str(valor)

                dados[campo] = valor

        # Adicionar metadados
        dados['_id'] = obj.pk
        dados['_modelo'] = nome_modelo
        dados['_timestamp'] = timezone.now().isoformat()

        return dados

    def detectar_alteracoes(self, dados_anteriores, dados_posteriores):
        """Detecta alterações entre dois estados de um objeto"""
        alteracoes = {}

        for campo, valor_novo in dados_posteriores.items():
            if campo.startswith('_'):  # Ignorar metadados
                continue

            valor_anterior = dados_anteriores.get(campo)

            if str(valor_anterior) != str(valor_novo):
                alteracoes[campo] = {
                    'anterior': valor_anterior,
                    'novo': valor_novo
                }

        return alteracoes

    def gerar_relatorio_diario(self):
        """Gera relatório diário de atividades"""
        hoje = timezone.now().date()
        inicio_dia = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
        fim_dia = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))

        logs_hoje = LogAuditoria.objects.filter(
            timestamp__gte=inicio_dia,
            timestamp__lte=fim_dia
        )

        relatorio = {
            'data': hoje.isoformat(),
            'total_atividades': logs_hoje.count(),
            'atividades_por_tipo': {},
            'usuarios_ativos': set(),
            'modelos_afetados': {},
            'atividades_detalhadas': []
        }

        for log in logs_hoje:
            # Contar por tipo de ação
            acao = log.get_acao_display()
            relatorio['atividades_por_tipo'][acao] = relatorio['atividades_por_tipo'].get(acao, 0) + 1

            # Usuários ativos
            if log.usuario:
                relatorio['usuarios_ativos'].add(log.usuario.get_full_name())

            # Modelos afetados
            modelo = log.content_type.model
            relatorio['modelos_afetados'][modelo] = relatorio['modelos_afetados'].get(modelo, 0) + 1

            # Detalhes da atividade
            relatorio['atividades_detalhadas'].append({
                'timestamp': log.timestamp.isoformat(),
                'usuario': log.usuario.get_full_name() if log.usuario else 'Anonyme',
                'acao': acao,
                'objeto': str(log.objeto_afetado) if log.objeto_afetado else 'N/A',
                'descricao': log.descricao,
                'alteracoes': log.resumo_alteracao
            })

        # Converter set para list para JSON
        relatorio['usuarios_ativos'] = list(relatorio['usuarios_ativos'])

        return relatorio

    def gerar_relatorio_semanal(self):
        """Gera relatório semanal de atividades"""
        hoje = timezone.now().date()
        inicio_semana = hoje - timedelta(days=7)

        logs_semana = LogAuditoria.objects.filter(
            timestamp__gte=inicio_semana
        )

        relatorio = {
            'periodo': f"{inicio_semana.isoformat()} - {hoje.isoformat()}",
            'total_atividades': logs_semana.count(),
            'estatisticas_diarias': {},
            'usuarios_mais_ativos': {},
            'modelos_mais_alterados': {},
            'acoes_mais_frequentes': {}
        }

        # Estatísticas diárias
        for i in range(8):
            data = hoje - timedelta(days=i)
            inicio_dia = timezone.make_aware(datetime.combine(data, datetime.min.time()))
            fim_dia = timezone.make_aware(datetime.combine(data, datetime.max.time()))

            count = logs_semana.filter(
                timestamp__gte=inicio_dia,
                timestamp__lte=fim_dia
            ).count()

            relatorio['estatisticas_diarias'][data.isoformat()] = count

        # Usuários mais ativos
        from django.db.models import Count
        usuarios = logs_semana.values(
            'usuario__first_name', 'usuario__last_name'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:5]

        for usuario in usuarios:
            nome = f"{usuario['usuario__first_name']} {usuario['usuario__last_name']}"
            relatorio['usuarios_mais_ativos'][nome] = usuario['total']

        return relatorio

    def salvar_relatorio(self, relatorio, nome_arquivo=None):
        """Salva relatório em arquivo JSON"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"relatorio_auditoria_{timestamp}.json"

        caminho = os.path.join('logs', nome_arquivo)

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório salvo em: {caminho}")
        return caminho


def executar_monitoramento():
    """Função principal para executar monitoramento"""
    logger.info("=== INICIANDO MONITORAMENTO DE ORÇAMENTOS ===")

    monitor = MonitorOrcamentos()

    # Gerar relatório diário
    relatorio_diario = monitor.gerar_relatorio_diario()
    arquivo_diario = monitor.salvar_relatorio(
        relatorio_diario,
        f"relatorio_diario_{datetime.now().strftime('%Y%m%d')}.json"
    )

    # Gerar relatório semanal (apenas às segundas)
    if datetime.now().weekday() == 0:  # Segunda-feira
        relatorio_semanal = monitor.gerar_relatorio_semanal()
        arquivo_semanal = monitor.salvar_relatorio(
            relatorio_semanal,
            f"relatorio_semanal_{datetime.now().strftime('%Y%m%d')}.json"
        )
        logger.info(f"Relatório semanal gerado: {arquivo_semanal}")

    # Log resumo
    logger.info(f"Relatório diário: {relatorio_diario['total_atividades']} atividades")
    logger.info(f"Usuários ativos hoje: {len(relatorio_diario['usuarios_ativos'])}")

    return relatorio_diario


def comando_relatorio():
    """Comando para gerar relatório manualmente"""
    import argparse

    parser = argparse.ArgumentParser(description='Gerador de relatórios de auditoria')
    parser.add_argument('--tipo', choices=['diario', 'semanal'], default='diario',
                        help='Tipo de relatório a gerar')
    parser.add_argument('--arquivo', help='Nome do arquivo de saída')
    parser.add_argument('--periodo', type=int, default=7,
                        help='Período em dias para relatório personalizado')

    args = parser.parse_args()

    monitor = MonitorOrcamentos()

    if args.tipo == 'diario':
        relatorio = monitor.gerar_relatorio_diario()
    elif args.tipo == 'semanal':
        relatorio = monitor.gerar_relatorio_semanal()

    arquivo = monitor.salvar_relatorio(relatorio, args.arquivo)
    print(f"Relatório gerado: {arquivo}")

    # Mostrar resumo no console
    print("\n=== RESUMO DO RELATÓRIO ===")
    print(f"Total de atividades: {relatorio['total_atividades']}")

    if 'atividades_por_tipo' in relatorio:
        print("\nAtividades por tipo:")
        for tipo, count in relatorio['atividades_por_tipo'].items():
            print(f"  {tipo}: {count}")

    if 'usuarios_ativos' in relatorio:
        print(f"\nUsuários ativos: {len(relatorio['usuarios_ativos'])}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'relatorio':
        comando_relatorio()
    else:
        executar_monitoramento()
