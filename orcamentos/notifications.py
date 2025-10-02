from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class TipoNotificacao(models.TextChoices):
    NOVA_SOLICITACAO = "nova_solicitacao", "Nouvelle demande de devis"
    ORCAMENTO_ELABORADO = "orcamento_elaborado", "Devis élaboré"
    ORCAMENTO_ENVIADO = "orcamento_enviado", "Devis envoyé"
    ORCAMENTO_ACEITO = "orcamento_aceito", "Devis accepté"
    ORCAMENTO_RECUSADO = "orcamento_recusado", "Devis refusé"
    PROJETO_CRIADO = "projeto_criado", "Nouveau projet créé"

class Notificacao(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )
    tipo = models.CharField(
        max_length=30,
        choices=TipoNotificacao.choices
    )
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    url_acao = models.URLField(blank=True, null=True)

    # Relacionamentos opcionais para contexto
    solicitacao = models.ForeignKey(
        'SolicitacaoOrcamento',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    orcamento = models.ForeignKey(
        'Orcamento',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    projeto = models.ForeignKey(
        'Projeto',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def marcar_como_lida(self):
        if not self.lida:
            self.lida = True
            self.read_at = timezone.now()
            self.save(update_fields=['lida', 'read_at'])

    def __str__(self):
        return f"{self.titulo} - {self.usuario.email}"
