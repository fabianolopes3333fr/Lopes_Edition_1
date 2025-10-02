from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
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
            # Criar notificação visual
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.NOVA_SOLICITACAO,
                titulo=f"Nouvelle demande de devis #{solicitacao.numero}",
                mensagem=f"Une nouvelle demande de devis a été reçue de {solicitacao.nome_solicitante}",
                url_acao=f"/orcamentos/admin/solicitacao/{solicitacao.numero}/",
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
        """Enviar email para cliente sobre orçamento enviado"""
        cliente = orcamento.solicitacao.cliente

        context = {
            'orcamento': orcamento,
            'cliente': cliente,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }

        if cliente:
            # Criar notificação visual para cliente logado
            NotificationService.criar_notificacao(
                usuario=cliente,
                tipo=TipoNotificacao.ORCAMENTO_ENVIADO,
                titulo=f"Votre devis #{orcamento.numero} est prêt",
                mensagem=f"Votre devis pour le projet '{orcamento.solicitacao.descricao_servico[:50]}...' est maintenant disponible",
                url_acao=f"/orcamentos/devis/{orcamento.numero}/",
                orcamento=orcamento
            )

        # Enviar email
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
            # Criar notificação visual
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.ORCAMENTO_ACEITO,
                titulo=f"Devis #{orcamento.numero} accepté!",
                mensagem=f"Le devis #{orcamento.numero} a été accepté par {orcamento.solicitacao.nome_solicitante}",
                url_acao=f"/orcamentos/admin/orcamento/{orcamento.numero}/",
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
            # Criar notificação visual
            NotificationService.criar_notificacao(
                usuario=admin,
                tipo=TipoNotificacao.ORCAMENTO_RECUSADO,
                titulo=f"Devis #{orcamento.numero} refusé",
                mensagem=f"Le devis #{orcamento.numero} a été refusé par {orcamento.solicitacao.nome_solicitante}",
                url_acao=f"/orcamentos/admin/orcamento/{orcamento.numero}/",
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
                titulo=f"Nouveau projet: {projeto.titulo}",
                mensagem=f"Un nouveau projet a été créé par {projeto.cliente.first_name} {projeto.cliente.last_name}",
                url_acao=f"/orcamentos/admin/projetos/{projeto.uuid}/",
                projeto=projeto
            )
