from django.db import models
from django.utils import timezone


class TipoContato(models.TextChoices):
    INFORMACAO = "informacao", "Demande d'information"
    DEVIS = "devis", "Demande de devis"
    RECLAMATION = "reclamation", "Réclamation"
    AUTRE = "autre", "Autre"


class StatusContato(models.TextChoices):
    NOUVEAU = "nouveau", "Nouveau"
    EN_COURS = "en_cours", "En cours de traitement"
    TRAITE = "traite", "Traité"
    FERME = "ferme", "Fermé"


class Contato(models.Model):
    # Informações pessoais
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

    # Informações da solicitação
    type_contact = models.CharField(
        max_length=20,
        choices=TipoContato.choices,
        default=TipoContato.INFORMACAO,
        verbose_name="Type de contact",
    )
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")

    # Informações do projeto (opcional)
    adresse_projet = models.CharField(
        max_length=255, blank=True, verbose_name="Adresse du projet"
    )
    ville_projet = models.CharField(
        max_length=100, blank=True, verbose_name="Ville du projet"
    )
    surface_estimee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Surface estimée (m²)",
    )
    budget_estime = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Budget estimé (€)",
    )

    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusContato.choices,
        default=StatusContato.NOUVEAU,
        verbose_name="Statut",
    )

    # Metadados
    date_creation = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    date_traitement = models.DateTimeField(
        null=True, blank=True, verbose_name="Date de traitement"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="Adresse IP"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")

    # Notas internas
    notes_internes = models.TextField(blank=True, verbose_name="Notes internes")

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.sujet}"

    def marquer_comme_traite(self):
        """Marcar contato como tratado"""
        self.status = StatusContato.TRAITE
        self.date_traitement = timezone.now()
        self.save()


class PieceJointe(models.Model):
    contato = models.ForeignKey(
        Contato,
        on_delete=models.CASCADE,
        related_name="pieces_jointes",
        verbose_name="Contact",
    )
    fichier = models.FileField(
        upload_to="contatos/pieces_jointes/", verbose_name="Fichier"
    )
    nom_original = models.CharField(max_length=255, verbose_name="Nom original")
    taille = models.PositiveIntegerField(verbose_name="Taille (bytes)")
    date_upload = models.DateTimeField(
        default=timezone.now, verbose_name="Date d'upload"
    )

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"
        ordering = ["-date_upload"]

    def __str__(self):
        return f"{self.nom_original} - {self.contato}"
