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

# Classes para gestão de produtos e serviços - MOVIDAS PARA CIMA
class TipoUnidade(models.TextChoices):
    UNITE = "unite", "Unité"
    PIECE = "piece", "Pièce"
    M2 = "m2", "M²"
    ML = "ml", "ML"
    LONGUEUR = "longueur", "Longueur"
    KG = "kg", "Kg"
    HEURE = "heure", "Heure"
    FORFAIT = "forfait", "Forfait"

class TipoAtividade(models.TextChoices):
    MARCHANDISE = "marchandise", "Marchandise"
    SERVICE = "service", "Service"

class TipoTVA(models.TextChoices):
    TVA_20 = "20", "TVA 20%"
    TVA_10 = "10", "TVA 10%"
    TVA_5_5 = "5.5", "TVA 5,5%"
    EXONEREE = "0", "Exonérée"

class TipoPagamento(models.TextChoices):
    VIREMENT = "virement", "Virement bancaire"
    CHEQUE = "cheque", "Chèque"
    ESPECE = "espece", "Espèce"
    CARTE_BANCAIRE = "carte_bancaire", "Carte bancaire"

class CondicoesPagamento(models.TextChoices):
    COMPTANT = "comptant", "Comptant"
    ACOMPTE_30 = "acompte_30", "30% d'acompte, solde à la fin"
    ACOMPTE_50 = "acompte_50", "50% d'acompte, solde à la fin"
    ECHEANCE_30 = "echeance_30", "Paiement à 30 jours"
    ECHEANCE_60 = "echeance_60", "Paiement à 60 jours"
    PERSONNALISE = "personnalise", "Conditions personnalisées"

class StatusFacture(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    ENVOYEE = "envoyee", "Envoyée"
    PAYEE = "payee", "Payée"
    ANNULEE = "annulee", "Annulée"
    EN_RETARD = "en_retard", "En retard"

class TipoNotificacao(models.TextChoices):
    NOVA_SOLICITACAO = "nova_solicitacao", "Nouvelle demande de devis"
    ORCAMENTO_ELABORADO = "orcamento_elaborado", "Devis élaboré"
    ORCAMENTO_ENVIADO = "orcamento_enviado", "Devis envoyé"
    ORCAMENTO_ACEITO = "orcamento_aceito", "Devis accepté"
    ORCAMENTO_RECUSADO = "orcamento_recusado", "Devis refusé"
    PROJETO_CRIADO = "projeto_criado", "Nouveau projet créé"

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
    condicoes_pagamento = models.CharField(
        max_length=20,
        choices=CondicoesPagamento.choices,
        default=CondicoesPagamento.COMPTANT,
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

    # Tipo de pagamento
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TipoPagamento.choices,
        default=TipoPagamento.VIREMENT,
        verbose_name="Type de paiement"
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
        """Calcula os totais do orçamento com base nos itens"""
        # Somar todos os valores dos itens
        total_ht_itens = Decimal('0.00')
        total_ttc_itens = Decimal('0.00')

        for item in self.itens.all():
            total_ht_itens += item.total_ht
            total_ttc_itens += item.total_ttc

        # Calcular subtotal (HT)
        self.subtotal = total_ht_itens

        # Aplicar desconto global sobre HT
        self.valor_desconto = (self.subtotal * self.desconto) / 100
        total_ht_com_desconto = self.subtotal - self.valor_desconto

        # O total final deve ser HT com desconto
        self.total = total_ht_com_desconto

        self.save(update_fields=['subtotal', 'valor_desconto', 'total'])

    @property
    def total_ttc(self):
        """Retorna o total TTC calculado baseado nos itens com desconto aplicado"""
        # Somar TTC de todos os itens
        total_ttc_itens = sum(item.total_ttc for item in self.itens.all())

        # Aplicar desconto proporcional no TTC também
        if self.desconto > 0 and total_ttc_itens > 0:
            valor_desconto_ttc = (total_ttc_itens * self.desconto) / 100
            return total_ttc_itens - valor_desconto_ttc

        return total_ttc_itens

    @property
    def valor_tva(self):
        """Retorna o valor total da TVA com desconto aplicado"""
        return self.total_ttc - self.total

    @property
    def total_compras(self):
        """Retorna o total de compras (custo dos produtos)"""
        total = Decimal('0.00')
        for item in self.itens.all():
            total += item.quantidade * item.preco_compra_unitario
        return total

    def __str__(self):
        return f"Devis {self.numero}"

# Model para itens do orçamento
class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    # Referência ao produto (opcional)
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto de referência"
    )

    # Dados do item
    referencia = models.CharField(max_length=50, blank=True, verbose_name="Référence")
    descricao = models.CharField(max_length=255, verbose_name="Désignation")
    unidade = models.CharField(
        max_length=20,
        choices=TipoUnidade.choices,
        default=TipoUnidade.UNITE,
        verbose_name="Unité"
    )
    atividade = models.CharField(
        max_length=20,
        choices=TipoAtividade.choices,
        default=TipoAtividade.MARCHANDISE,
        verbose_name="Activité"
    )

    # Quantidades e preços
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantité"
    )
    preco_unitario_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="P.U HT"
    )
    preco_unitario_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="P.U TTC"
    )
    preco_compra_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Prix d'achat unitaire"
    )

    # Remise e totais
    remise_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Remise (%)"
    )
    total_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total HT"
    )
    total_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total TTC"
    )

    # Taxa
    taxa_tva = models.CharField(
        max_length=5,
        choices=TipoTVA.choices,
        default=TipoTVA.TVA_20,
        verbose_name="Taxe TVA"
    )

    # Metadados
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Item du devis"
        verbose_name_plural = "Itens du devis"
        ordering = ['ordem', 'id']

    def save(self, *args, **kwargs):
        # Calcular preço unitário TTC
        taxa_decimal = Decimal(self.taxa_tva) / 100
        self.preco_unitario_ttc = self.preco_unitario_ht * (1 + taxa_decimal)

        # Calcular total bruto
        total_bruto_ht = self.quantidade * self.preco_unitario_ht

        # Aplicar remise
        valor_remise = (total_bruto_ht * self.remise_percentual) / 100
        self.total_ht = total_bruto_ht - valor_remise

        # Calcular total TTC
        valor_tva = self.total_ht * taxa_decimal
        self.total_ttc = self.total_ht + valor_tva

        super().save(*args, **kwargs)

        # Recalcular total do orçamento
        if hasattr(self, 'orcamento'):
            self.orcamento.calcular_totais()

    @property
    def valor_tva(self):
        """Retorna o valor da TVA para este item"""
        return self.total_ttc - self.total_ht

    def __str__(self):
        return f"{self.referencia} - {self.descricao}"

# Model para faturas elaboradas pelos admins
class Facture(models.Model):
    # Identificação
    numero = models.CharField(max_length=20, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Relacionamentos
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='faturas',
        verbose_name="Devis de référence"
    )
    cliente = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='faturas_cliente',
        verbose_name="Client"
    )
    elaborado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='faturas_elaboradas'
    )

    # Dados da fatura
    titulo = models.CharField(max_length=200, verbose_name="Titre de la facture")
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

    # Datas importantes
    data_emissao = models.DateField(
        default=timezone.now,
        verbose_name="Date d'émission"
    )
    data_vencimento = models.DateField(
        verbose_name="Date d'échéance"
    )
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de paiement"
    )

    # Condições de pagamento
    condicoes_pagamento = models.CharField(
        max_length=20,
        choices=CondicoesPagamento.choices,
        default=CondicoesPagamento.COMPTANT,
        verbose_name="Conditions de paiement"
    )
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TipoPagamento.choices,
        default=TipoPagamento.VIREMENT,
        verbose_name="Type de paiement"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=StatusFacture.choices,
        default=StatusFacture.BROUILLON,
        verbose_name="Statut"
    )

    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observations"
    )

    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-data_criacao']

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.gerar_numero()
        super().save(*args, **kwargs)

    def gerar_numero(self):
        import random
        while True:
            numero = f"FA{timezone.now().year}{random.randint(10000, 99999)}"
            if not Facture.objects.filter(numero=numero).exists():
                return numero

    def calcular_totais(self):
        """Calcula os totais da fatura com base nos itens"""
        total_ht_itens = Decimal('0.00')
        total_ttc_itens = Decimal('0.00')

        for item in self.itens.all():
            total_ht_itens += item.total_ht
            total_ttc_itens += item.total_ttc

        self.subtotal = total_ht_itens
        self.valor_desconto = (self.subtotal * self.desconto) / 100
        total_ht_com_desconto = self.subtotal - self.valor_desconto
        self.total = total_ht_com_desconto

        self.save(update_fields=['subtotal', 'valor_desconto', 'total'])

    @property
    def total_ttc(self):
        """Retorna o total TTC calculado baseado nos itens com desconto aplicado"""
        total_ttc_itens = sum(item.total_ttc for item in self.itens.all())
        if self.desconto > 0 and total_ttc_itens > 0:
            valor_desconto_ttc = (total_ttc_itens * self.desconto) / 100
            return total_ttc_itens - valor_desconto_ttc
        return total_ttc_itens

    @property
    def valor_tva(self):
        """Retorna o valor total da TVA com desconto aplicado"""
        return self.total_ttc - self.total

    @property
    def is_em_atraso(self):
        """Verifica se a fatura está em atraso"""
        if self.status == StatusFacture.ENVOYEE and self.data_vencimento < timezone.now().date():
            return True
        return False

    def marcar_como_paga(self, data_pagamento=None):
        """Marca a fatura como paga"""
        self.status = StatusFacture.PAYEE
        self.data_pagamento = data_pagamento or timezone.now().date()
        self.save()

    def __str__(self):
        return f"Facture {self.numero}"

# Model para itens da fatura
class ItemFacture(models.Model):
    facture = models.ForeignKey(
        Facture,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    # Referência ao produto (opcional)
    produto = models.ForeignKey(
        'Produto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto de referência"
    )

    # Dados do item
    referencia = models.CharField(max_length=50, blank=True, verbose_name="Référence")
    descricao = models.CharField(max_length=255, verbose_name="Désignation")
    unidade = models.CharField(
        max_length=20,
        choices=TipoUnidade.choices,
        default=TipoUnidade.UNITE,
        verbose_name="Unité"
    )
    atividade = models.CharField(
        max_length=20,
        choices=TipoAtividade.choices,
        default=TipoAtividade.MARCHANDISE,
        verbose_name="Activité"
    )

    # Quantidades e preços
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantité"
    )
    preco_unitario_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="P.U HT"
    )
    preco_unitario_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="P.U TTC"
    )

    # Remise e totais
    remise_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Remise (%)"
    )
    total_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total HT"
    )
    total_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total TTC"
    )

    # Taxa
    taxa_tva = models.CharField(
        max_length=5,
        choices=TipoTVA.choices,
        default=TipoTVA.TVA_20,
        verbose_name="Taxe TVA"
    )

    # Metadados
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Item de la facture"
        verbose_name_plural = "Itens de la facture"
        ordering = ['ordem', 'id']

    def save(self, *args, **kwargs):
        # Calcular preço unitário TTC
        taxa_decimal = Decimal(self.taxa_tva) / 100
        self.preco_unitario_ttc = self.preco_unitario_ht * (1 + taxa_decimal)

        # Calcular total bruto
        total_bruto_ht = self.quantidade * self.preco_unitario_ht

        # Aplicar remise
        valor_remise = (total_bruto_ht * self.remise_percentual) / 100
        self.total_ht = total_bruto_ht - valor_remise

        # Calcular total TTC
        valor_tva = self.total_ht * taxa_decimal
        self.total_ttc = self.total_ht + valor_tva

        super().save(*args, **kwargs)

        # Recalcular total da fatura
        if hasattr(self, 'facture'):
            self.facture.calcular_totais()

    @property
    def valor_tva(self):
        """Retorna o valor da TVA para este item"""
        return self.total_ttc - self.total_ht

    def __str__(self):
        return f"{self.referencia} - {self.descricao}"

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


# Model para notificações do sistema
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
        SolicitacaoOrcamento,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    projeto = models.ForeignKey(
        Projeto,
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

# Model para gestão de produtos e serviços
class Fornecedor(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nom du fournisseur")
    email = models.EmailField(blank=True, verbose_name="Email")
    telefone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^[\+]?[0-9\s\-\(\)]+$')],
        verbose_name="Téléphone"
    )
    endereco = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    cep = models.CharField(max_length=10, blank=True, verbose_name="Code postal")

    ativo = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Produto(models.Model):
    # Campos principais
    referencia = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Référence"
    )
    descricao = models.CharField(max_length=255, verbose_name="Désignation")

    # Tipo de unidade e atividade
    unidade = models.CharField(
        max_length=20,
        choices=TipoUnidade.choices,
        default=TipoUnidade.UNITE,
        verbose_name="Type d'unité"
    )
    atividade = models.CharField(
        max_length=20,
        choices=TipoAtividade.choices,
        default=TipoAtividade.MARCHANDISE,
        verbose_name="Activité"
    )

    # Fornecedor
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name="Fournisseur"
    )

    # Preços e margens
    preco_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Prix d'achat"
    )
    margem_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Marge HT"
    )
    margem_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Marge HT em %"
    )
    preco_venda_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="P.Vente HT"
    )

    # Taxa e preço final
    taxa_tva = models.CharField(
        max_length=5,
        choices=TipoTVA.choices,
        default=TipoTVA.TVA_20,
        verbose_name="Taxe TVA"
    )
    preco_venda_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="P.Vente TTC"
    )

    # Foto do produto
    foto = models.ImageField(
        upload_to='produtos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )

    # Controles
    ativo = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['referencia']

    def save(self, *args, **kwargs):
        # Calcular preço de venda HT baseado na margem
        if self.margem_percentual > 0:
            self.margem_ht = (self.preco_compra * self.margem_percentual) / 100

        self.preco_venda_ht = self.preco_compra + self.margem_ht

        # Calcular preço TTC
        taxa_decimal = Decimal(self.taxa_tva) / 100
        self.preco_venda_ttc = self.preco_venda_ht * (1 + taxa_decimal)

        # Recalcular margem percentual se necessário
        if self.preco_compra > 0 and self.margem_percentual == 0:
            self.margem_percentual = (self.margem_ht / self.preco_compra) * 100

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.referencia} - {self.descricao}"
