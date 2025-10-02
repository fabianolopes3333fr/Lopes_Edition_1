from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from decimal import Decimal
from orcamentos.models import TipoTVA

class Cliente(models.Model):
    CIVILITE_CHOICES = [
        ('M', 'Monsieur'),
        ('MME', 'Madame'),
        ('MLLE', 'Mademoiselle'),
        ('DR', 'Docteur'),
        ('PROF', 'Professeur'),
    ]

    STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('client', 'Client'),
    ]

    CONDITIONS_PAIEMENT_CHOICES = [
        ('30_acompte_solde_fin', '30% d\'acompte à la commande, le solde fin du chantier'),
        ('paiement_fin_mois', 'Paiement la fin du mois'),
        ('paiement_30j_fin_mois', 'Paiement 30 jours fin du mois'),
    ]

    ORIGEM_CHOICES = [
        ('dashboard', 'Criado via Dashboard'),
        ('auto_registro', 'Auto-registro (Login)'),
        ('devis_publico', 'Solicitação de Devis Público'),
    ]

    TVA_INTRA_CHOICES = [
        ('', 'Non applicable'),
        ('FR', 'France - FR'),
        ('BE', 'Belgique - BE'),
        ('DE', 'Allemagne - DE'),
        ('ES', 'Espagne - ES'),
        ('IT', 'Italie - IT'),
        ('LU', 'Luxembourg - LU'),
        ('NL', 'Pays-Bas - NL'),
        ('PT', 'Portugal - PT'),
        ('AT', 'Autriche - AT'),
        ('CH', 'Suisse - CH'),
        ('GB', 'Royaume-Uni - GB'),
        ('IE', 'Irlande - IE'),
        ('DK', 'Danemark - DK'),
        ('SE', 'Suède - SE'),
        ('FI', 'Finlande - FI'),
        ('NO', 'Norvège - NO'),
        ('PL', 'Pologne - PL'),
        ('CZ', 'République tchèque - CZ'),
        ('HU', 'Hongrie - HU'),
        ('autre', 'Autre (saisie libre)'),
    ]

    # Informations principales
    code = models.CharField(max_length=20, unique=True, verbose_name="Code Client")
    civilite = models.CharField(max_length=10, choices=CIVILITE_CHOICES, blank=True, verbose_name="Civilité")
    raison_sociale = models.CharField(max_length=200, blank=True, verbose_name="Raison Sociale")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, blank=True, verbose_name="Prénom")

    # Adresse principale
    adresse = models.TextField(verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, verbose_name="Code Postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=100, default="France", verbose_name="Pays")

    # Contacts
    telephone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(regex=r'^[+]?[0-9\s\-\(\)\.]{8,20}$')],
        verbose_name="Téléphone"
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(regex=r'^[+]?[0-9\s\-\(\)\.]{8,20}$')],
        verbose_name="Mobile"
    )
    email = models.EmailField(blank=True, verbose_name="Email")
    url = models.URLField(blank=True, verbose_name="Site Web")

    # Informations entreprise
    activite = models.CharField(max_length=200, blank=True, verbose_name="Activité")
    siret = models.CharField(
        max_length=14,
        blank=True,
        validators=[RegexValidator(regex=r'^\d{14}$', message="Le SIRET doit contenir 14 chiffres")],
        verbose_name="SIRET"
    )
    code_ape = models.CharField(max_length=10, blank=True, verbose_name="Code APE")
    tva_intra = models.CharField(
        max_length=20,
        choices=TVA_INTRA_CHOICES,
        blank=True,
        verbose_name="TVA Intracommunautaire"
    )
    tva_intra_custom = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="TVA Intracommunautaire (saisie libre)",
        help_text="Utilisé quand 'Autre' est sélectionné"
    )

    # Status e origem
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect', verbose_name="Statut")
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='dashboard', verbose_name="Origem")

    # Conditions commerciales
    taux_tva_defaut = models.CharField(
        max_length=10,
        choices=TipoTVA.choices,
        default=TipoTVA.TVA_20,
        verbose_name="Taux TVA par défaut (%)"
    )
    remise_globale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Remise globale (%)"
    )
    conditions_paiement = models.CharField(
        max_length=50,
        choices=CONDITIONS_PAIEMENT_CHOICES,
        default='30_acompte_solde_fin',
        verbose_name="Conditions de paiement"
    )

    # Ligação com usuário (para clientes que se registraram)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Usuário Associado"
    )

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['origem', 'nom', 'prenom']

    def __str__(self):
        if self.raison_sociale:
            return f"{self.code} - {self.raison_sociale}"
        return f"{self.code} - {self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        if self.raison_sociale:
            return self.raison_sociale
        return f"{self.nom} {self.prenom}".strip()

    @property
    def adresse_complete(self):
        return f"{self.adresse}\n{self.code_postal} {self.ville}\n{self.pays}"

    @property
    def origem_display_icon(self):
        """Retorna ícone para exibir na lista baseado na origem"""
        icons = {
            'dashboard': 'fas fa-user-plus',
            'auto_registro': 'fas fa-user-check',
            'devis_publico': 'fas fa-file-invoice',
        }
        return icons.get(self.origem, 'fas fa-user')

    @classmethod
    def criar_de_usuario(cls, user):
        """Criar cliente automaticamente a partir de um usuário registrado"""
        if hasattr(user, 'cliente'):
            return user.cliente

        # Gerar código único
        last_client = cls.objects.order_by('id').last()
        if last_client:
            try:
                last_number = int(last_client.code.replace('CLI', ''))
                new_number = last_number + 1
            except:
                new_number = 1
        else:
            new_number = 1

        code = f'CLI{new_number:03d}'

        # Criar cliente básico
        cliente = cls.objects.create(
            code=code,
            nom=user.last_name or 'Nome',
            prenom=user.first_name or '',
            email=user.email,
            adresse='Endereço a ser preenchido',
            code_postal='00000',
            ville='Cidade a ser preenchida',
            pays='France',
            status='prospect',
            origem='auto_registro',
            user=user
        )

        return cliente

class AdresseLivraison(models.Model):
    client = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='adresses_livraison')
    nom = models.CharField(max_length=200, verbose_name="Nom de l'adresse")

    # Copie des données de l'adresse principale
    copier_adresse_principale = models.BooleanField(default=False, verbose_name="Copier l'adresse principale")

    # Adresse de livraison
    adresse = models.TextField(verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, verbose_name="Code Postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=100, default="France", verbose_name="Pays")

    # Contact spécifique
    contact_nom = models.CharField(max_length=100, blank=True, verbose_name="Nom du contact")
    contact_telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

    # Instructions spéciales
    instructions = models.TextField(blank=True, verbose_name="Instructions de livraison")

    class Meta:
        verbose_name = "Adresse de livraison"
        verbose_name_plural = "Adresses de livraison"

    def __str__(self):
        return f"{self.client.nom_complet} - {self.nom}"

    def save(self, *args, **kwargs):
        if self.copier_adresse_principale and self.client:
            self.adresse = self.client.adresse
            self.code_postal = self.client.code_postal
            self.ville = self.client.ville
            self.pays = self.client.pays
        super().save(*args, **kwargs)


class AdresseTransporteur(models.Model):
    client = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='adresses_transporteur')
    nom = models.CharField(max_length=200, verbose_name="Nom du transporteur")

    # Copie des données de l'adresse principale
    copier_adresse_principale = models.BooleanField(default=False, verbose_name="Copier l'adresse principale")

    # Adresse du transporteur
    adresse = models.TextField(verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, verbose_name="Code Postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=100, default="France", verbose_name="Pays")

    # Contact
    contact_nom = models.CharField(max_length=100, blank=True, verbose_name="Nom du contact")
    contact_telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    contact_email = models.EmailField(blank=True, verbose_name="Email")

    class Meta:
        verbose_name = "Adresse transporteur"
        verbose_name_plural = "Adresses transporteur"

    def __str__(self):
        return f"{self.client.nom_complet} - {self.nom}"

    def save(self, *args, **kwargs):
        if self.copier_adresse_principale and self.client:
            self.adresse = self.client.adresse
            self.code_postal = self.client.code_postal
            self.ville = self.client.ville
            self.pays = self.client.pays
        super().save(*args, **kwargs)


class AdresseChantier(models.Model):
    client = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='adresses_chantier')
    nom = models.CharField(max_length=200, verbose_name="Nom du chantier")

    # Adresse du chantier
    adresse = models.TextField(verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, verbose_name="Code Postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=100, default="France", verbose_name="Pays")

    # Contact sur site
    contact_nom = models.CharField(max_length=100, blank=True, verbose_name="Nom du contact sur site")
    contact_telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

    # Informations chantier
    date_debut_prevue = models.DateField(blank=True, null=True, verbose_name="Date début prévue")
    date_fin_prevue = models.DateField(blank=True, null=True, verbose_name="Date fin prévue")
    instructions = models.TextField(blank=True, verbose_name="Instructions spéciales")

    class Meta:
        verbose_name = "Adresse de chantier"
        verbose_name_plural = "Adresses de chantier"

    def __str__(self):
        return f"{self.client.nom_complet} - {self.nom}"


class TarifTVAClient(models.Model):
    client = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='tarifs_tva')
    description = models.CharField(max_length=200, verbose_name="Description")
    taux_tva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux TVA (%)"
    )
    par_defaut = models.BooleanField(default=False, verbose_name="Taux par défaut")

    class Meta:
        verbose_name = "Tarif TVA"
        verbose_name_plural = "Tarifs TVA"
        unique_together = ['client', 'description']

    def __str__(self):
        return f"{self.client.nom_complet} - {self.description} ({self.taux_tva}%)"

    def save(self, *args, **kwargs):
        if self.par_defaut:
            # S'assurer qu'il n'y a qu'un seul taux par défaut par client
            TarifTVAClient.objects.filter(client=self.client, par_defaut=True).update(par_defaut=False)
        super().save(*args, **kwargs)
