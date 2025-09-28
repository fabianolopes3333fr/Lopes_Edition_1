from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import EmailValidator, RegexValidator
import uuid
from decimal import Decimal

User = get_user_model()

class StatusOrcamento(models.TextChoices):
    PENDENTE = "pendente", "En attente"
    EM_ELABORACAO = "em_elaboracao", "En cours d'élaboration"
    ENVIADO = "enviado", "Envoyé au client"
    ACEITO = "aceito", "Accepté"
    RECUSADO = "recusado", "Refusé"
    EXPIRADO = "expirado", "Expiré"

class StatusProjeto(models.TextChoices):
    PLANEJANDO = "planejando", "En planification"
    EM_ANDAMENTO = "em_andamento", "En cours"
    CONCLUIDO = "concluido", "Terminé"
    PAUSADO = "pausado", "En pause"
    CANCELADO = "cancelado", "Annulé"

class TipoServico(models.TextChoices):
    PINTURA_INTERIOR = "pintura_interior", "Peinture intérieure"
    PINTURA_EXTERIOR = "pintura_exterior", "Peinture extérieure"
    RENOVACAO_COMPLETA = "renovacao_completa", "Rénovation complète"
    PREPARACAO_SUPERFICIES = "preparacao_superficies", "Préparation des surfaces"
    DECORACAO = "decoracao", "Décoration"
    REPAROS = "reparos", "Réparations"
    OUTRO = "outro", "Autre"

class UrgenciaProjeto(models.TextChoices):
    BAIXA = "baixa", "Pas pressé"
    MEDIA = "media", "Normal"
    ALTA = "alta", "Urgent"
    CRITICA = "critica", "Très urgent"

# Model para projetos criados por clientes logados
class Projeto(models.Model):
    # Identificação
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos')

    # Informações básicas do projeto
    titulo = models.CharField(max_length=200, verbose_name="Titre du projet")
    descricao = models.TextField(verbose_name="Description détaillée")
    tipo_servico = models.CharField(
        max_length=50,
        choices=TipoServico.choices,
        verbose_name="Type de service"
    )
    urgencia = models.CharField(
        max_length=20,
        choices=UrgenciaProjeto.choices,
        default=UrgenciaProjeto.MEDIA,
        verbose_name="Urgence"
    )

    # Localização do projeto
    endereco_projeto = models.CharField(max_length=255, verbose_name="Adresse du projet")
    cidade_projeto = models.CharField(max_length=100, verbose_name="Ville")
    cep_projeto = models.CharField(max_length=10, verbose_name="Code postal")

    # Detalhes técnicos
    area_aproximada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Surface approximative (m²)"
    )
    numero_comodos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de pièces"
    )
    altura_teto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Hauteur du plafond (m)"
    )

    # Preferências
    orcamento_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Budget estimé (€)"
    )
    data_inicio_desejada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de début souhaitée"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observations particulières"
    )

    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusProjeto.choices,
        default=StatusProjeto.PLANEJANDO,
        verbose_name="Statut"
    )

    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} - {self.cliente.first_name} {self.cliente.last_name}"

# Model para solicitações de orçamento (público e de projetos)
class SolicitacaoOrcamento(models.Model):
    # Identificação
    numero = models.CharField(max_length=20, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Relacionamentos
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='solicitacoes_orcamento'
    )
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='solicitacoes_orcamento'
    )

    # Dados do solicitante (para solicitações anônimas)
    nome_solicitante = models.CharField(max_length=100, verbose_name="Nom")
    email_solicitante = models.EmailField(verbose_name="Email")
    telefone_solicitante = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^[\+]?[0-9\s\-\(\)]+$')],
        verbose_name="Téléphone"
    )

    # Localização
    endereco = models.CharField(max_length=255, verbose_name="Adresse")
    cidade = models.CharField(max_length=100, verbose_name="Ville")
    cep = models.CharField(max_length=10, verbose_name="Code postal")

    # Detalhes do serviço solicitado
    tipo_servico = models.CharField(
        max_length=50,
        choices=TipoServico.choices,
        verbose_name="Type de service"
    )
    descricao_servico = models.TextField(verbose_name="Description du service")

    # Informações técnicas
    area_aproximada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Surface approximative (m²)"
    )
    urgencia = models.CharField(
        max_length=20,
        choices=UrgenciaProjeto.choices,
        default=UrgenciaProjeto.MEDIA,
        verbose_name="Urgence"
    )
    data_inicio_desejada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de début souhaitée"
    )
    orcamento_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Budget maximum (€)"
    )

    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name="Informations complémentaires"
    )

    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusOrcamento.choices,
        default=StatusOrcamento.PENDENTE,
        verbose_name="Statut"
    )

    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de devis"
        verbose_name_plural = "Demandes de devis"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.gerar_numero()
        super().save(*args, **kwargs)

    def gerar_numero(self):
        import random
        import string
        while True:
            numero = f"DEV{timezone.now().year}{random.randint(1000, 9999)}"
            if not SolicitacaoOrcamento.objects.filter(numero=numero).exists():
                return numero

    def __str__(self):
        if self.projeto:
            return f"Devis {self.numero} - Projet: {self.projeto.titulo}"
        return f"Devis {self.numero} - {self.nome_solicitante}"

# Model para orçamentos elaborados pelos admins
class Orcamento(models.Model):
    # Identificação
    numero = models.CharField(max_length=20, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Relacionamentos
    solicitacao = models.OneToOneField(
        SolicitacaoOrcamento,
        on_delete=models.CASCADE,
        related_name='orcamento'
    )
    elaborado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orcamentos_elaborados'
    )

    # Dados do orçamento
    titulo = models.CharField(max_length=200, verbose_name="Titre du devis")
    descricao = models.TextField(verbose_name="Description")

    # Valores
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Sous-total"
    )
    desconto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Remise (%)"
    )
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant de la remise"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total"
    )

    # Prazos
    prazo_execucao = models.PositiveIntegerField(
        verbose_name="Délai d'exécution (jours)"
    )
    validade_orcamento = models.DateField(
        verbose_name="Validité du devis"
    )

    # Condições
    condicoes_pagamento = models.TextField(
        verbose_name="Conditions de paiement"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observations"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusOrcamento.choices,
        default=StatusOrcamento.EM_ELABORACAO,
        verbose_name="Statut"
    )

    # Metadados
    data_elaboracao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_resposta_cliente = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
        ordering = ['-data_elaboracao']

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.gerar_numero()
        super().save(*args, **kwargs)

    def gerar_numero(self):
        import random
        while True:
            numero = f"OR{timezone.now().year}{random.randint(10000, 99999)}"
            if not Orcamento.objects.filter(numero=numero).exists():
                return numero

    def calcular_totais(self):
        """Calcula os totais do orçamento"""
        # Recalcular subtotal baseado nos itens
        self.subtotal = sum(item.total_item for item in self.itens.all())
        self.valor_desconto = (self.subtotal * self.desconto) / 100
        self.total = self.subtotal - self.valor_desconto
        self.save(update_fields=['subtotal', 'valor_desconto', 'total'])

    @property
    def total_ttc(self):
        """Retorna o total TTC (com TVA 20%)"""
        # Garante que sempre tenha um valor válido para cálculo
        total_ht = self.total if self.total is not None else Decimal('0.00')
        tva_rate = Decimal('1.20')  # 20% de TVA
        return total_ht * tva_rate

    @property
    def valor_tva(self):
        """Retorna o valor da TVA (20%)"""
        total_ht = self.total if self.total is not None else Decimal('0.00')
        tva_rate = Decimal('0.20')  # 20% de TVA
        return total_ht * tva_rate

    @property
    def tem_itens(self):
        """Verifica se o orçamento tem itens"""
        return self.itens.exists()

    def __str__(self):
        return f"Devis {self.numero}"

# Model para itens do orçamento
class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    # Dados do item
    descricao = models.CharField(max_length=255, verbose_name="Description")
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantité"
    )
    unidade = models.CharField(
        max_length=20,
        default="m²",
        verbose_name="Unité"
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix unitaire"
    )
    total_item = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total"
    )

    # Metadados
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Item do devis"
        verbose_name_plural = "Itens do devis"
        ordering = ['ordem', 'id']

    def save(self, *args, **kwargs):
        self.total_item = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

        # Recalcular total do orçamento
        self.orcamento.subtotal = sum(item.total_item for item in self.orcamento.itens.all())
        self.orcamento.calcular_totais()

    def __str__(self):
        return f"{self.descricao} - {self.quantidade} {self.unidade}"

# Model para fotos/anexos dos projetos
class AnexoProjeto(models.Model):
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='anexos'
    )

    arquivo = models.FileField(
        upload_to='projetos/anexos/%Y/%m/',
        verbose_name="Arquivo"
    )
    descricao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Description"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anexo do projeto"
        verbose_name_plural = "Anexos do projeto"
        ordering = ['-created_at']

    def __str__(self):
        return f"Anexo - {self.projeto.titulo}"
