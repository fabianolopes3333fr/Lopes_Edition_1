from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.conf import settings

# ========================= LISTAS BÁSICAS =========================
class Civilite(models.Model):
    label = models.CharField(max_length=20, unique=True)
    abreviation = models.CharField(max_length=10, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Civilité"
        verbose_name_plural = "Civilités"
        ordering = ["label"]

    def __str__(self):
        return self.label


class LegalForm(models.Model):
    name = models.CharField("Forme juridique", max_length=80, unique=True)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Forme juridique"
        verbose_name_plural = "Formes juridiques"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PaymentMode(models.Model):
    name = models.CharField("Mode de règlement", max_length=50, unique=True)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Mode de règlement"
        verbose_name_plural = "Modes de règlement"
        ordering = ["ordre", "name"]

    def __str__(self):
        return self.name


class PaymentCondition(models.Model):
    code = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Condition de paiement"
        verbose_name_plural = "Conditions de paiement"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.description}" if self.code else self.description


class TaxRate(models.Model):
    TAX_TYPES = (
        ("tva", "TVA"),
        ("autre", "Autre"),
    )
    name = models.CharField(max_length=50, unique=True)  # ex: TVA 20%
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    tax_type = models.CharField(max_length=10, choices=TAX_TYPES, default="tva")
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Taux de taxe"
        verbose_name_plural = "Taux de taxes"
        ordering = ["tax_type", "rate"]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


# ========================= PARAMÈTRES AUTO-ENTREPRENEUR =========================
class AutoEntrepreneurParameters(models.Model):
    PERIODICITE = (("mois", "Mois"), ("trimestre", "Trimestre"))
    PRODUCT_TYPES = (("marchandise", "Fourniture / Marchandise"), ("service", "Service"))

    default_product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default="service")
    declaration_periodicite = models.CharField(max_length=15, choices=PERIODICITE, default="trimestre")

    # Vente de biens
    biens_taux_cotisation_sociale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    biens_taux_imposition = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    biens_taux_formation_pro = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    biens_taux_chambre_consulaire = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Vente de services
    services_taux_cotisation_sociale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    services_taux_imposition = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    services_taux_formation_pro = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    services_taux_chambre_consulaire = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres Auto-Entrepreneur"
        verbose_name_plural = "Paramètres Auto-Entrepreneur"

    def __str__(self):
        return "Paramètres Auto-Entrepreneur"


# ========================= PARAMÈTRES INTERFACE =========================
class InterfaceSettings(models.Model):
    logo = models.ImageField(upload_to="interface/logo/", blank=True, null=True)
    background_image = models.ImageField(upload_to="interface/background/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres d'interface"
        verbose_name_plural = "Paramètres d'interface"

    def __str__(self):
        return "Interface Logiciel"


# ========================= PARAMÈTRES EMAIL =========================
class EmailSettings(models.Model):
    host = models.CharField(max_length=100, blank=True)
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    username = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=150, blank=True)
    from_email = models.EmailField(blank=True)
    actif = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres Email"
        verbose_name_plural = "Paramètres Email"

    def __str__(self):
        return f"Serveur SMTP ({self.host or 'non configuré'})"


# ========================= SOCIÉTÉ =========================
class CompanySettings(models.Model):
    # Coordonnées
    raison_sociale = models.CharField(max_length=150, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    code_postal = models.CharField(max_length=10, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=80, default="France", blank=True)
    siret = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r"^[0-9 ]*$", "SIRET invalide")])
    code_ape = models.CharField(max_length=10, blank=True)
    code_rcs = models.CharField(max_length=50, blank=True)
    tva_intra = models.CharField(max_length=30, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Informations complémentaires
    site_internet = models.URLField(blank=True)
    activite = models.CharField(max_length=150, blank=True)
    forme_juridique = models.ForeignKey(LegalForm, null=True, blank=True, on_delete=models.SET_NULL)
    type_entreprise = models.CharField(max_length=40, blank=True, help_text="Auto entrepreneur / micro entreprise / autre")
    capital = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Responsable
    responsable_civilite = models.ForeignKey(Civilite, null=True, blank=True, on_delete=models.SET_NULL, related_name='responsables')
    responsable_nom = models.CharField(max_length=80, blank=True)
    responsable_prenom = models.CharField(max_length=80, blank=True)

    # Expert comptable
    expert_raison_sociale = models.CharField(max_length=150, blank=True)
    expert_adresse = models.CharField(max_length=255, blank=True)
    expert_code_postal = models.CharField(max_length=10, blank=True)
    expert_ville = models.CharField(max_length=100, blank=True)
    expert_nom_prenom = models.CharField(max_length=150, blank=True)
    expert_tel = models.CharField(max_length=20, blank=True)
    expert_mobile = models.CharField(max_length=20, blank=True)
    expert_fax = models.CharField(max_length=20, blank=True)
    expert_email = models.EmailField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres Société"
        verbose_name_plural = "Paramètres Société"

    def __str__(self):
        return self.raison_sociale or "Société (non configurée)"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

