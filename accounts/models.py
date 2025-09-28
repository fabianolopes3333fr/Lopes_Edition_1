from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re


class AccountType(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    COLLABORATOR = "COLLABORATOR", "Collaborateur"
    ADMINISTRATOR = "ADMINISTRATOR", "Administrateur"


class CustomUserManager(BaseUserManager):
    """✅ CORRIGIDO: Manager personalizado que usa email como identificador principal"""

    def _create_user(self, email, password=None, **extra_fields):
        """Criar usuário com email como identificador principal"""
        if not email:
            raise ValueError("L'adresse email doit être définie")

        # Normalizar email
        email = self.normalize_email(email)

        # Gerar username automaticamente se não fornecido
        if not extra_fields.get("username"):
            extra_fields["username"] = self._generate_username_from_email(email)

        # ✅ CORRIGIDO: Criar usuário sem triggerar signals desnecessários
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # ✅ IMPORTANTE: Usar save com update_fields para controle
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """Criar usuário comum"""
        # Definir valores padrão
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("account_type", AccountType.CLIENT)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """✅ CORRIGIDO: Criar superusuário"""
        # Definir valores obrigatórios para superuser
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("account_type", AccountType.ADMINISTRATOR)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def _generate_username_from_email(self, email):
        """Gerar username baseado no email"""
        if not email:
            return None

        # Extrair parte antes do @
        username_base = email.split("@")[0].lower()

        # Limpar caracteres especiais
        username_base = re.sub(r"[^a-zA-Z0-9._-]", "", username_base)

        # Garantir que é único
        username = username_base
        counter = 1

        while self.model.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        return username


class User(AbstractUser):
    """✅ CORRIGIDO: Modelo de usuário personalizado com email como identificador"""

    # Campo email obrigatório e único
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Adresse email utilisée pour la connexion",
    )

    # Tipo de conta
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CLIENT,
        verbose_name="Type de compte",
        help_text="Type de compte utilisateur",
    )

    # Campos obrigatórios
    first_name = models.CharField(
        max_length=150, verbose_name="Prénom", help_text="Prénom de l'utilisateur"
    )

    last_name = models.CharField(
        max_length=150, verbose_name="Nom", help_text="Nom de famille de l'utilisateur"
    )

    # ✅ IMPORTANTE: Definir email como campo de login
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # ✅ CORRIGIDO: Usar o manager personalizado
    objects = CustomUserManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        db_table = "accounts_user"

    def clean(self):
        """Validação personalizada"""
        super().clean()

        # Validar email
        if self.email:
            self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        """✅ CORRIGIDO: Override do save mais seguro"""
        # Normalizar email
        if self.email:
            self.email = self.email.lower().strip()

        # Gerar username se necessário (apenas na criação)
        if not self.username and self.email:
            self.username = self._generate_username_from_email()

        # Normalizar nomes
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()

        super().save(*args, **kwargs)

    def _generate_username_from_email(self):
        """Gerar username baseado no email"""
        if not self.email:
            return None

        # Usar o método do manager
        return User.objects._generate_username_from_email(self.email)

    def get_full_name(self):
        """Retornar nome completo"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Retornar nome curto"""
        return self.first_name

    def __str__(self):
        """Representação em string"""
        return self.email
