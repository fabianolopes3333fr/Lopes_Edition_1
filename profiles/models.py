from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
import logging

logger = logging.getLogger(__name__)


def avatar_upload_path(instance, filename):
    """Definir caminho de upload do avatar"""
    # Extrair extensão do arquivo
    ext = filename.split(".")[-1]
    # Gerar nome único: user_id + timestamp + extensão
    filename = f"user_{instance.user.id}_{int(timezone.now().timestamp())}.{ext}"
    return os.path.join("avatars", filename)


class Profile(models.Model):
    """✅ CORRIGIDO: Modelo Profile com todas as funcionalidades"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Utilisateur",
    )

    # ✅ CORRIGIDO: Username para exibição (calculado automaticamente)
    display_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Nom d'utilisateur",
        help_text="Généré automatiquement à partir de l'email",
    )

    # Informações pessoais
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
        help_text="Format: +33 1 23 45 67 89",
    )

    address = models.TextField(
        blank=True, verbose_name="Adresse", help_text="Adresse complète"
    )

    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code postal",
        help_text="Code postal français (5 chiffres)",
    )

    country = models.CharField(max_length=50, default="France", verbose_name="Pays")

    # Avatar com validação
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name="Photo de profil",
        help_text="Image JPG, PNG ou GIF. Taille max: 2MB",
    )

    # Configurações de comunicação
    receive_newsletters = models.BooleanField(
        default=True,
        verbose_name="Recevoir la newsletter",
        help_text="Recevoir les actualités et promotions par email",
    )

    receive_notifications = models.BooleanField(
        default=True,
        verbose_name="Recevoir les notifications",
        help_text="Recevoir les notifications importantes par email",
    )

    # ===== NOVOS CAMPOS PARA PARÂMETROS =====
    # Configurações de notificação
    notifications_email = models.BooleanField(
        default=True,
        verbose_name="Notifications par email",
        help_text="Recevoir les mises à jour importantes par email",
    )

    newsletter = models.BooleanField(
        default=True,
        verbose_name="Newsletter",
        help_text="Recevoir les offres spéciales et actualités",
    )

    project_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications de projets",
        help_text="Recevoir les mises à jour sur vos projets",
    )

    # Configurações de segurança
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name="Authentification à deux facteurs",
        help_text="Activer l'authentification à deux facteurs pour plus de sécurité",
    )

    # Configurações de privacidade
    data_processing_consent = models.BooleanField(
        default=True,
        verbose_name="Consentement de traitement des données",
        help_text="Autoriser le traitement des données personnelles",
    )

    marketing_consent = models.BooleanField(
        default=False,
        verbose_name="Consentement marketing",
        help_text="Autoriser l'utilisation des données à des fins marketing",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        """✅ CORRIGIDO: Atualizar display_username automaticamente"""
        try:
            if self.user:
                if hasattr(self.user, "username") and self.user.username:
                    self.display_username = self.user.username
                elif self.user.email:
                    # Extrair username do email
                    self.display_username = self.user.email.split("@")[0]

            # ✅ LOG para debug
            logger.info(
                f"Salvando perfil para {self.user.email}: phone={self.phone}, city={self.city}"
            )

            super().save(*args, **kwargs)

            # ✅ LOG após save
            logger.info(f"Perfil salvo com sucesso para {self.user.email}")

        except Exception as e:
            logger.error(f"Erro ao salvar perfil para {self.user.email}: {e}")
            raise

    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"

    @property
    def username(self):
        """✅ CORRIGIDO: Propriedade para acessar username facilmente"""
        return self.display_username or (
            self.user.username
            if hasattr(self.user, "username")
            else self.user.email.split("@")[0] if self.user.email else ""
        )

    @property
    def is_complete(self):
        """✅ MELHORADO: Verifica se o perfil está completo"""
        required_fields = [
            self.phone and self.phone.strip(),
            self.address and self.address.strip(),
            self.city and self.city.strip(),
            self.postal_code and self.postal_code.strip(),
        ]
        return all(required_fields)

    @property
    def completion_percentage(self):
        """✅ NOVO: Calcular porcentagem de completude"""
        total_fields = 6
        completed_fields = 0

        # Campos obrigatórios
        if self.phone and self.phone.strip():
            completed_fields += 1
        if self.address and self.address.strip():
            completed_fields += 1
        if self.city and self.city.strip():
            completed_fields += 1
        if self.postal_code and self.postal_code.strip():
            completed_fields += 1
        if self.country and self.country.strip():
            completed_fields += 1
        if self.avatar:
            completed_fields += 1

        return int((completed_fields / total_fields) * 100)

    @property
    def avatar_url(self):
        """✅ NOVO: URL segura do avatar"""
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return None

    @property
    def initials(self):
        """✅ NOVO: Iniciais do usuário para avatar padrão"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        elif self.user.first_name:
            return self.user.first_name[0].upper()
        elif self.user.email:
            return self.user.email[0].upper()
        return "U"

    def clean(self):
        """✅ NOVO: Validação customizada"""
        # Validar telefone
        if self.phone:
            phone_clean = self.phone.replace(" ", "").replace("+", "").replace("-", "")
            if not phone_clean.isdigit() or len(phone_clean) < 10:
                raise ValidationError(
                    {
                        "phone": "Numéro de téléphone invalide. Format attendu: +33 1 23 45 67 89"
                    }
                )

        # Validar código postal francês
        if self.postal_code and self.country.lower() == "france":
            if not self.postal_code.isdigit() or len(self.postal_code) != 5:
                raise ValidationError(
                    {"postal_code": "Code postal français invalide. 5 chiffres requis."}
                )

    def delete_old_avatar(self):
        """✅ NOVO: Deletar avatar antigo ao fazer upload de novo"""
        if self.avatar:
            try:
                if os.path.isfile(self.avatar.path):
                    os.remove(self.avatar.path)
            except (ValueError, OSError):
                pass  # Arquivo não existe ou erro de acesso
