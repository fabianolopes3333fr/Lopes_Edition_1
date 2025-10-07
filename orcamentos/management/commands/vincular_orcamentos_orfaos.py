from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from orcamentos.models import SolicitacaoOrcamento
from orcamentos.services import NotificationService
from orcamentos.auditoria import AuditoriaManager, TipoAcao

User = get_user_model()

class Command(BaseCommand):
    help = 'Vincular orçamentos órfãos a usuários existentes baseado no email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executar sem fazer alterações (apenas mostrar o que seria feito)',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Processar apenas um email específico',
        )
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Enviar notificações para usuários sobre orçamentos vinculados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        email_especifico = options['email']
        enviar_notificacoes = options['notify']

        self.stdout.write(self.style.SUCCESS('🔍 Iniciando busca por orçamentos órfãos...'))

        # Filtrar solicitações órfãs
        query = SolicitacaoOrcamento.objects.filter(cliente__isnull=True)

        if email_especifico:
            query = query.filter(email_solicitante__iexact=email_especifico)
            self.stdout.write(f"📧 Processando apenas email: {email_especifico}")

        solicitacoes_orfas = query.select_related()
        total_orfas = solicitacoes_orfas.count()

        if total_orfas == 0:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum orçamento órfão encontrado.'))
            return

        self.stdout.write(f"📊 Encontradas {total_orfas} solicitações órfãs")

        # Processar cada solicitação órfã
        vinculadas = 0
        usuarios_notificados = set()
        emails_processados = set()

        for solicitacao in solicitacoes_orfas:
            try:
                # Tentar encontrar usuário com mesmo email
                usuarios = User.objects.filter(email__iexact=solicitacao.email_solicitante)

                if usuarios.exists():
                    usuario = usuarios.first()
                    emails_processados.add(solicitacao.email_solicitante)

                    if not dry_run:
                        # Registrar vinculação na auditoria
                        AuditoriaManager.registrar_vinculacao_orcamento_orfao(
                            usuario=usuario,
                            solicitacao=solicitacao,
                            origem="comando_gerenciamento"
                        )

                        solicitacao.cliente = usuario
                        solicitacao.save()

                    vinculadas += 1
                    usuarios_notificados.add(usuario.email)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {'[DRY-RUN] ' if dry_run else ''}Vinculada solicitação {solicitacao.numero} "
                            f"({solicitacao.email_solicitante}) ao usuário {usuario.email}"
                        )
                    )

                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Usuário não encontrado para email: {solicitacao.email_solicitante} "
                            f"(Solicitação: {solicitacao.numero})"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Erro ao processar solicitação {solicitacao.numero}: {str(e)}"
                    )
                )

        # Registrar processamento em lote na auditoria
        if not dry_run and vinculadas > 0:
            admin_user = User.objects.filter(is_staff=True).first()
            AuditoriaManager.registrar_processamento_lote_orfaos(
                usuario_comando=admin_user,
                total_processadas=total_orfas,
                total_vinculadas=vinculadas,
                emails_processados=emails_processados
            )

        # Enviar notificações se solicitado
        if enviar_notificacoes and not dry_run and usuarios_notificados:
            self.stdout.write('\n📧 Enviando notificações...')

            for email in usuarios_notificados:
                try:
                    usuario = User.objects.get(email__iexact=email)
                    quantidade = SolicitacaoOrcamento.objects.filter(
                        cliente=usuario,
                        email_solicitante__iexact=email
                    ).count()

                    NotificationService.notificar_orcamentos_vinculados(usuario, quantidade)

                    # Registrar notificação na auditoria
                    AuditoriaManager.registrar_notificacao_vinculacao(
                        usuario_notificado=usuario,
                        quantidade_orcamentos=quantidade,
                        metodo_vinculacao="comando_com_notificacao"
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"📬 Notificação enviada para {email} ({quantidade} orçamentos)"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Erro ao notificar {email}: {str(e)}")
                    )

        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📋 RESUMO DA OPERAÇÃO:'))
        self.stdout.write(f"🔍 Total de solicitações órfãs encontradas: {total_orfas}")
        self.stdout.write(f"🔗 Solicitações vinculadas: {vinculadas}")
        self.stdout.write(f"👥 Usuários únicos beneficiados: {len(usuarios_notificados)}")
        self.stdout.write(f"📧 Emails processados: {len(emails_processados)}")

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: Nenhuma alteração foi feita no banco de dados'))
            self.stdout.write('💡 Execute novamente sem --dry-run para aplicar as alterações')
        elif enviar_notificacoes:
            self.stdout.write(self.style.SUCCESS('📧 Notificações enviadas para todos os usuários beneficiados'))

        if not dry_run:
            self.stdout.write(self.style.SUCCESS('📝 Todas as operações foram registradas nos logs de auditoria'))

        self.stdout.write('='*50)
