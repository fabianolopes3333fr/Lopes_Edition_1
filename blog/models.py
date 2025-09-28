from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse


class CategorieBlog(models.Model):
    nom = models.CharField(
        max_length=100, unique=True, verbose_name="Nom de la catégorie"
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    couleur = models.CharField(
        max_length=7, default="#007bff", verbose_name="Couleur (hex)"
    )
    actif = models.BooleanField(default=True, verbose_name="Catégorie active")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Catégorie de blog"
        verbose_name_plural = "Catégories de blog"
        ordering = ["ordre", "nom"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class ArticleBlog(models.Model):
    STATUS_CHOICES = [
        ("brouillon", "Brouillon"),
        ("publie", "Publié"),
        ("archive", "Archivé"),
    ]

    # Contenu principal
    titre = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    resume = models.TextField(max_length=300, verbose_name="Résumé/Extrait")
    contenu = models.TextField(verbose_name="Contenu")

    # Métadonnées
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Mudança aqui
        on_delete=models.CASCADE,
        verbose_name="Auteur",
    )
    categorie = models.ForeignKey(
        CategorieBlog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Séparez les tags par des virgules",
        verbose_name="Tags",
    )

    # Images
    image = models.ImageField(  # Mudança: de image_principale para image
        upload_to="blog/articles/",
        blank=True,
        null=True,
        verbose_name="Image principale",
    )
    text_alt = models.CharField(
        max_length=200, blank=True, verbose_name="Texte alternatif de l'image"
    )
    temps_lecture = models.PositiveIntegerField(
        default=5, verbose_name="Temps de lecture"
    )
    # Statut et dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="brouillon",
        verbose_name="Statut",
    )
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True, verbose_name="Dernière modification"
    )
    date_publication = models.DateTimeField(
        blank=True, null=True, verbose_name="Date de publication"
    )

    # SEO
    meta_description = models.CharField(
        max_length=160, blank=True, verbose_name="Meta description"
    )
    meta_keywords = models.CharField(
        max_length=200, blank=True, verbose_name="Meta keywords"
    )

    # Statistiques
    vues = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    featured = models.BooleanField(default=False, verbose_name="Article en vedette")

    class Meta:
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
        ordering = ["-date_publication", "-date_creation"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)

        if self.contenu:
            word_count = len(self.contenu.split())
            self.temps_lecture = max(1, word_count // 200)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    @property
    def tags_list(self):
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def incrementer_vues(self):
        self.vues += 1
        self.save(update_fields=["vues"])


class CommentaireBlog(models.Model):
    STATUS_CHOICES = [
        ("en_attente", "En attente"),
        ("approuve", "Approuvé"),
        ("rejete", "Rejeté"),
    ]

    article = models.ForeignKey(
        ArticleBlog,
        on_delete=models.CASCADE,
        related_name="commentaires",
        verbose_name="Article",
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web")
    contenu = models.TextField(verbose_name="Commentaire")

    # Modération
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="en_attente",
        verbose_name="Statut",
    )
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="Adresse IP"
    )

    # Dates
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    date_moderation = models.DateTimeField(
        blank=True, null=True, verbose_name="Date de modération"
    )

    # Réponse (pour les commentaires hiérarchiques)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reponses",
        verbose_name="Réponse à",
    )

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Commentaire de {self.nom} sur {self.article.titre}"


# Adicione este bloco no final do seu models.py


class NewsletterList(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Lista")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    active = models.BooleanField(default=True, verbose_name="Lista Ativa")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Lista de Newsletter"
        verbose_name_plural = "Listas de Newsletter"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def subscriber_count(self):
        """Retorna o número de assinantes ativos nesta lista"""
        return self.subscribers.filter(active=True).count()


class NewsletterSubscriber(models.Model):
    INTEREST_CHOICES = [
        ("peinture_interieur", "Peinture Intérieur"),
        ("peinture_exterieur", "Peinture Extérieur"),
        ("decoration", "Décoration"),
        ("conseils", "Conseils"),
    ]

    prenom = models.CharField(max_length=100, blank=True, verbose_name="Prénom")
    email = models.EmailField(unique=True, verbose_name="Adresse Email")
    interests = models.CharField(
        max_length=255, blank=True, verbose_name="Centres d'intérêt"
    )
    rgpd_consent = models.BooleanField(default=False, verbose_name="Consentement RGPD")
    active = models.BooleanField(default=True, verbose_name="Assinante Ativo")
    confirmed = models.BooleanField(default=False, verbose_name="Email Confirmé")
    confirmation_token = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Token de Confirmação"
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Date d'inscription"
    )
    date_confirmed = models.DateTimeField(
        blank=True, null=True, verbose_name="Date de Confirmation"
    )
    last_email_sent = models.DateTimeField(
        blank=True, null=True, verbose_name="Dernier Email Envoyé"
    )
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="Adresse IP"
    )

    # Campo para associar assinantes a listas
    lists = models.ManyToManyField(
        NewsletterList,
        blank=True,
        related_name="subscribers",
        verbose_name="Listas",
    )

    class Meta:
        verbose_name = "Assinante de Newsletter"
        verbose_name_plural = "Assinantes de Newsletter"
        ordering = ["-date_joined"]

    def __str__(self):
        if self.prenom:
            return f"{self.prenom} ({self.email})"
        return self.email

    def save(self, *args, **kwargs):
        # Gerar token de confirmação se não existir
        if not self.confirmation_token:
            import uuid
            self.confirmation_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    @property
    def interests_list(self):
        """Retorna lista de interesses"""
        if self.interests:
            return [interest.strip() for interest in self.interests.split(",") if interest.strip()]
        return []

    @property
    def full_name(self):
        """Retorna nome completo ou email se nome não disponível"""
        return self.prenom if self.prenom else self.email.split('@')[0]

    def confirm_email(self):
        """Confirma o email do assinante"""
        from django.utils import timezone
        self.confirmed = True
        self.date_confirmed = timezone.now()
        self.save(update_fields=['confirmed', 'date_confirmed'])

    def unsubscribe(self):
        """Desinscreve o assinante"""
        self.active = False
        self.save(update_fields=['active'])

    def get_interests_display(self):
        """Retorna os interesses em formato legível"""
        interests_dict = dict(self.INTEREST_CHOICES)
        return [interests_dict.get(interest, interest) for interest in self.interests_list]
