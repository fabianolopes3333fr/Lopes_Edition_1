# Create your models here.
from django.db import models
from django.utils import timezone


class Projeto(models.Model):
    STATUS_CHOICES = [
        ("nouveau", "Nouveau"),
        ("en_cours", "En cours"),
        ("termine", "Terminé"),
        ("suspendu", "Suspendu"),
    ]

    TIPO_CHOICES = [
        ("interieur", "Peinture Intérieure"),
        ("exterieur", "Peinture Extérieure"),
        ("renovation", "Rénovation"),
        ("decoration", "Décoration"),
    ]

    titre = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    adresse = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    type_projet = models.CharField(
        max_length=20, choices=TIPO_CHOICES, verbose_name="Type de projet"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="nouveau", verbose_name="Statut"
    )
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    surface_m2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Surface (m²)",
    )
    prix_estime = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Prix estimé (€)",
    )
    image_principale = models.ImageField(
        upload_to="projetos/", blank=True, verbose_name="Image principale"
    )
    visible_site = models.BooleanField(default=True, verbose_name="Visible sur le site")
    date_creation = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.titre} - {self.ville}"


class ImageProjeto(models.Model):
    projeto = models.ForeignKey(
        Projeto, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="projetos/galeria/")
    legende = models.CharField(max_length=255, blank=True, verbose_name="Légende")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Image du projet"
        verbose_name_plural = "Images du projet"
        ordering = ["ordre"]

    def __str__(self):
        return f"Image - {self.projeto.titre}"
