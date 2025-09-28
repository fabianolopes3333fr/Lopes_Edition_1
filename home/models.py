from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


class CategoriaColor(models.Model):
    """Categoria de cores (ex: Blanc, RAL, Façade, etc.)"""

    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icone = models.CharField(
        max_length=50,
        default="fas fa-palette",
        help_text="Classe CSS do ícone FontAwesome",
    )
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Catégorie de Couleur"
        verbose_name_plural = "Catégories de Couleurs"
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Couleur(models.Model):
    """Modelo para as cores do catálogo"""

    nome = models.CharField(max_length=100)
    codigo = models.CharField(
        max_length=50, unique=True, help_text="Code unique de la couleur (ex: RAL-1000)"
    )
    categoria = models.ForeignKey(
        CategoriaColor, on_delete=models.CASCADE, related_name="couleurs"
    )

    # Cor em formato RGB
    rgb_r = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(255)],
        help_text="Rouge (0-255)",
    )
    rgb_g = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(255)],
        help_text="Vert (0-255)",
    )
    rgb_b = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(255)],
        help_text="Bleu (0-255)",
    )

    # Cor em formato HEX (calculado automaticamente)
    hex_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Couleur en format HEX (calculé automatiquement)",
    )

    # Informações adicionais
    description = models.TextField(blank=True, help_text="Description de la couleur")
    disponible = models.BooleanField(default=True)
    populaire = models.BooleanField(
        default=False, help_text="Couleur populaire/recommandée"
    )

    # Metadados
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Couleur"
        verbose_name_plural = "Couleurs"
        ordering = [
            "categoria__ordem",
            "categoria__nome",
            "nome",
        ]  # Corrigido: ordem em vez de ordre
        unique_together = ["nome", "categoria"]

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    def save(self, *args, **kwargs):
        # Calcular automaticamente o valor HEX
        self.hex_color = f"#{self.rgb_r:02x}{self.rgb_g:02x}{self.rgb_b:02x}"
        super().save(*args, **kwargs)

    @property
    def rgb_string(self):
        """Retorna a cor em formato RGB string"""
        return f"rgb({self.rgb_r}, {self.rgb_g}, {self.rgb_b})"

    @property
    def rgb_dict(self):
        """Retorna a cor em formato dict"""
        return {"r": self.rgb_r, "g": self.rgb_g, "b": self.rgb_b}

    def clean(self):
        """Validações customizadas"""
        super().clean()

        # Validar se o código é único
        if self.codigo:
            existing = Couleur.objects.filter(codigo=self.codigo).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"codigo": "Ce code couleur existe déjà."})

        # Validar valores RGB
        for field, value in [
            ("rgb_r", self.rgb_r),
            ("rgb_g", self.rgb_g),
            ("rgb_b", self.rgb_b),
        ]:
            if value is not None and (value < 0 or value > 255):
                raise ValidationError({field: "La valeur doit être entre 0 et 255."})
