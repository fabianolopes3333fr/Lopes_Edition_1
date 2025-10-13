from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.signing import TimestampSigner
from .models import Notificacao, TipoNotificacao

User = get_user_model()

class NotificationService:
    """Serviço para gerenciar notificações e emails do sistema"""

    @staticmethod
    def criar_notificacao(usuario, tipo, titulo, mensagem, url_acao=None, **kwargs):
        """Criar uma nova notificação"""
        notificacao = Notificacao.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            url_acao=url_acao,
            **kwargs
        )
        return notificacao

    @staticmethod
    def enviar_email_nova_solicitacao(solicitacao):
        """Enviar email para admins sobre nova solicitação"""
        # Buscar todos os admins
        admins = User.objects.filter(is_staff=True)

        context = {
            'solicitacao': solicitacao,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }

        for admin in admins:
            # Criar notificação visual - URL corrigida
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.NOVA_SOLICITACAO,
                titulo=f"Nouvelle demande de devis #{solicitacao.numero}",
                mensagem=f"Une nouvelle demande de devis a été reçue de {solicitacao.nome_solicitante}",
                url_acao=f"/devis/admin/solicitacoes/{solicitacao.numero}/",
                solicitacao=solicitacao
            )

            # Enviar email
            try:
                html_content = render_to_string('orcamentos/emails/nova_solicitacao_admin.html', context)
                send_mail(
                    subject=f"Nouvelle demande de devis #{solicitacao.numero}",
                    message=f"Une nouvelle demande de devis a été reçue de {solicitacao.nome_solicitante}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    html_message=html_content,
                    fail_silently=False
                )
            except Exception as e:
                print(f"Erro ao enviar email para {admin.email}: {e}")

    @staticmethod
    def enviar_email_orcamento_enviado(orcamento):
        """Enviar email para cliente sobre orçamento enviado com links públicos tokenizados."""
        cliente = orcamento.solicitacao.cliente

        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

        # Construir URLs públicas
        public_detail_path = reverse('orcamentos:orcamento_publico_detail', kwargs={'uuid': orcamento.uuid})
        signer = TimestampSigner()
        accept_token = signer.sign(f"{orcamento.uuid}:accept")
        refuse_token = signer.sign(f"{orcamento.uuid}:refuse")
        pdf_token = signer.sign(f"{orcamento.uuid}:pdf")

        public_detail_url = f"{site_url}{public_detail_path}"
        public_accept_url = f"{public_detail_url}?auto=accept&token={accept_token}"
        public_refuse_url = f"{public_detail_url}?auto=refuse&token={refuse_token}"
        public_pdf_path = reverse('orcamentos:orcamento_publico_pdf', kwargs={'uuid': orcamento.uuid}) + f"?token={pdf_token}"
        public_pdf_url = f"{site_url}{public_pdf_path}"

        context = {
            'orcamento': orcamento,
            'cliente': cliente,
            'site_url': site_url,
            'public_detail_url': public_detail_url,
            'public_accept_url': public_accept_url,
            'public_refuse_url': public_refuse_url,
            'public_pdf_url': public_pdf_url,
        }

        if cliente:
            # Criar notificação visual para cliente logado - URL corrigida
            NotificationService.criar_notificacao(
                usuario=cliente,
                tipo=TipoNotificacao.ORCAMENTO_ENVIADO,
                titulo=f"Votre devis #{orcamento.numero} est prêt",
                mensagem=f"Votre devis pour le projet '{orcamento.solicitacao.descricao_servico[:50]}...' est maintenant disponible",
                url_acao=f"/devis/devis/{orcamento.numero}/",
                orcamento=orcamento
            )

        # Enviar email (sempre para o email do solicitante)
        try:
            html_content = render_to_string('orcamentos/emails/orcamento_enviado_cliente.html', context)
            send_mail(
                subject=f"Votre devis #{orcamento.numero} - LOPES PEINTURE",
                message=f"Votre devis #{orcamento.numero} est maintenant disponible",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[orcamento.solicitacao.email_solicitante],
                html_message=html_content,
                fail_silently=False
            )
        except Exception as e:
            print(f"Erro ao enviar email para {orcamento.solicitacao.email_solicitante}: {e}")

    @staticmethod
    def enviar_email_orcamento_aceito(orcamento):
        """Enviar email para admins sobre orçamento aceito"""
        admins = User.objects.filter(is_staff=True)

        context = {
            'orcamento': orcamento,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }

        for admin in admins:
            # Criar notificação visual - URL corrigida
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.ORCAMENTO_ACEITO,
                titulo=f"Devis #{orcamento.numero} accepté!",
                mensagem=f"Le devis #{orcamento.numero} a été accepté par {orcamento.solicitacao.nome_solicitante}",
                url_acao=f"/devis/admin/orcamentos/{orcamento.numero}/",
                orcamento=orcamento
            )

            # Enviar email
            try:
                html_content = render_to_string('orcamentos/emails/orcamento_aceito_admin.html', context)
                send_mail(
                    subject=f"Devis #{orcamento.numero} accepté - LOPES PEINTURE",
                    message=f"Le devis #{orcamento.numero} a été accepté",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    html_message=html_content,
                    fail_silently=False
                )
            except Exception as e:
                print(f"Erro ao enviar email para {admin.email}: {e}")

    @staticmethod
    def enviar_email_orcamento_recusado(orcamento):
        """Enviar email para admins sobre orçamento recusado"""
        admins = User.objects.filter(is_staff=True)

        context = {
            'orcamento': orcamento,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }

        for admin in admins:
            # Criar notificação visual - URL corrigida
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.ORCAMENTO_RECUSADO,
                titulo=f"Devis #{orcamento.numero} refusé",
                mensagem=f"Le devis #{orcamento.numero} a été refusé par {orcamento.solicitacao.nome_solicitante}",
                url_acao=f"/devis/admin/orcamentos/{orcamento.numero}/",
                orcamento=orcamento
            )

            # Enviar email
            try:
                html_content = render_to_string('orcamentos/emails/orcamento_recusado_admin.html', context)
                send_mail(
                    subject=f"Devis #{orcamento.numero} refusé - LOPES PEINTURE",
                    message=f"Le devis #{orcamento.numero} a été refusé",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    html_message=html_content,
                    fail_silently=False
                )
            except Exception as e:
                print(f"Erro ao enviar email para {admin.email}: {e}")

    @staticmethod
    def notificar_projeto_criado(projeto):
        """Notificar sobre novo projeto criado"""
        admins = User.objects.filter(is_staff=True)

        for admin in admins:
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.PROJETO_CRIADO,
                titulo=f"Nouveau projeto: {projeto.titulo}",
                mensagem=f"Un novo projeto a été criado por {projeto.cliente.first_name} {projeto.cliente.last_name}",
                url_acao=f"/devis/admin/projetos/{projeto.uuid}/",
                projeto=projeto
            )

    @staticmethod
    def notificar_orcamentos_vinculados(usuario, quantidade):
        """Notificar usuário sobre orçamentos vinculados após cadastro"""
        try:
            # Montar título e mensagem com pluralização exata esperada nos testes
            plural = quantidade > 1
            titulo = "Demandes retrouvées!"
            # Garantir substring 'X demande' onde X é a quantidade (o teste usa contains)
            mensagem = (
                f"Nous avons trouvé {quantidade} demande{'s' if plural else ''} de devis associée"
                f"{'s' if plural else ''} à votre email. {'Elles sont' if plural else 'Elle est'} maintenant disponible"
                f"{'s' if plural else ''} dans votre tableau de bord."
            )

            # Chamar com argumentos posicionais conforme esperado pelos testes
            NotificationService.criar_notificacao(
                usuario,
                TipoNotificacao.NOVA_SOLICITACAO,
                titulo,
                mensagem,
                "/devis/mes-devis/"
            )

            # Enviar email de boas-vindas com informações sobre os orçamentos
            context = {
                'usuario': usuario,
                'quantidade': quantidade,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
            }

            html_content = render_to_string('orcamentos/emails/orcamentos_vinculados.html', context)

            # Subject deve conter 'Bienvenue' e 'X demande'/'X demandes'
            subject = (
                f"Bienvenue chez LOPES PEINTURE - {quantidade} demande{'s' if plural else ''} retrouvée"
                f"{'s' if plural else ''}!"
            )
            message = (
                f"Bienvenue! Nous avons retrouvée {quantidade} demande{'s' if plural else ''} de devis associée"
                f"{'s' if plural else ''} à votre compte."
            )

            # Passar recipient_list e fail_silently como kwargs para satisfazer asserts dos testes
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                html_message=html_content,
                fail_silently=True
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao notificar orçamentos vinculados para {usuario.email}: {e}")

    @staticmethod
    def verificar_e_processar_orcamentos_orfaos():
        """
        Função utilitária para processar orçamentos órfãos em lote.
        Pode ser executada via comando de management.
        """
        from .models import SolicitacaoOrcamento

        # Buscar todas as solicitações órfãs
        solicitacoes_orfas = SolicitacaoOrcamento.objects.filter(cliente__isnull=True)

        processadas = 0
        for solicitacao in solicitacoes_orfas:
            try:
                # Tentar encontrar usuário com mesmo email
                usuario = User.objects.get(email__iexact=solicitacao.email_solicitante)
                solicitacao.cliente = usuario
                solicitacao.save()
                processadas += 1
            except User.DoesNotExist:
                continue
            except User.MultipleObjectsReturned:
                # Se houver múltiplos usuários com mesmo email, pegar o primeiro
                usuario = User.objects.filter(email__iexact=solicitacao.email_solicitante).first()
                if usuario:
                    solicitacao.cliente = usuario
                    solicitacao.save()
                    processadas += 1

        return processadas
