from django import forms
from django.core.exceptions import ValidationError
from .models import Profile
import re
import logging

logger = logging.getLogger(__name__)


class ProfileForm(forms.ModelForm):
    """✅ CORRIGIDO: Formulário de perfil com validações e styling correto"""

    class Meta:
        model = Profile
        fields = [
            "phone",
            "address",
            "city",
            "postal_code",
            "country",
            "avatar",
            "receive_newsletters",
            "receive_notifications",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ LOG para debug
        logger.info(
            f"Inicializando ProfileForm para: {self.instance.user.email if self.instance.pk else 'novo'}"
        )

        # ✅ CONFIGURAR WIDGETS
        self.fields["phone"].widget = forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "+33 1 23 45 67 89",
                "autocomplete": "tel",
            }
        )

        self.fields["address"].widget = forms.Textarea(
            attrs={
                "class": "form-input",
                "placeholder": "123 Rue de la Paix",
                "rows": 3,
                "autocomplete": "street-address",
            }
        )

        self.fields["city"].widget = forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Paris",
                "autocomplete": "address-level2",
            }
        )

        self.fields["postal_code"].widget = forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "75001",
                "autocomplete": "postal-code",
                "maxlength": "5",
                "pattern": "[0-9]{5}",
            }
        )

        self.fields["country"].widget = forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "France",
                "autocomplete": "country-name",
            }
        )

        self.fields["avatar"].widget = forms.FileInput(
            attrs={
                "class": "hidden",
                "accept": "image/jpeg,image/jpg,image/png,image/gif",
            }
        )

        self.fields["receive_newsletters"].widget = forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            }
        )

        self.fields["receive_notifications"].widget = forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            }
        )

        # ✅ LABELS E HELP TEXT
        self.fields["phone"].label = "Téléphone"
        self.fields["phone"].help_text = "Format: +33 1 23 45 67 89"
        self.fields["phone"].required = False

        self.fields["address"].label = "Adresse"
        self.fields["address"].help_text = "Votre adresse complète"
        self.fields["address"].required = False

        self.fields["city"].label = "Ville"
        self.fields["city"].required = False

        self.fields["postal_code"].label = "Code postal"
        self.fields["postal_code"].help_text = "Code postal français (5 chiffres)"
        self.fields["postal_code"].required = False

        self.fields["country"].label = "Pays"
        self.fields["country"].required = False

        self.fields["avatar"].label = "Photo de profil"
        self.fields["avatar"].help_text = "JPG, PNG ou GIF. Taille maximum 2MB."
        self.fields["avatar"].required = False

        self.fields["receive_newsletters"].label = "Recevoir la newsletter"
        self.fields["receive_newsletters"].help_text = (
            "Actualités, promotions et conseils"
        )
        self.fields["receive_newsletters"].required = False

        self.fields["receive_notifications"].label = "Recevoir les notifications"
        self.fields["receive_notifications"].help_text = (
            "Notifications importantes par email"
        )
        self.fields["receive_notifications"].required = False

        # ✅ VALORES INICIAIS
        if not self.instance.pk:
            self.fields["country"].initial = "France"
            self.fields["receive_newsletters"].initial = True
            self.fields["receive_notifications"].initial = True

        # ✅ LOG valores atuais
        if self.instance.pk:
            logger.info(
                f"Valores atuais - phone: {self.instance.phone}, city: {self.instance.city}"
            )

    def clean_phone(self):
        """✅ MELHORADO: Validação de telefone"""
        phone = self.cleaned_data.get("phone")

        logger.info(f"Validando telefone: '{phone}'")

        if not phone:
            return phone

        # Remover espaços e caracteres especiais para validação
        phone_clean = re.sub(r"[^\d+]", "", phone)

        # Validações
        if phone_clean:
            # Deve ter pelo menos 10 dígitos
            digits_only = re.sub(r"[^\d]", "", phone_clean)
            if len(digits_only) < 10:
                logger.error(f"Telefone muito curto: {phone}")
                raise ValidationError(
                    "Le numéro de téléphone doit contenir au moins 10 chiffres."
                )

        logger.info(f"Telefone validado: '{phone}'")
        return phone

    def clean_postal_code(self):
        """✅ MELHORADO: Validação de código postal"""
        postal_code = self.cleaned_data.get("postal_code")
        country = self.cleaned_data.get("country", "France")

        logger.info(f"Validando código postal: '{postal_code}' para país: '{country}'")

        if not postal_code:
            return postal_code

        # Remover espaços
        postal_code = postal_code.replace(" ", "")

        # Validação para França
        if country.lower() in ["france", "frança"]:
            if not postal_code.isdigit() or len(postal_code) != 5:
                logger.error(f"Código postal inválido: {postal_code}")
                raise ValidationError(
                    "Code postal français invalide. 5 chiffres requis (ex: 75001)."
                )

        logger.info(f"Código postal validado: '{postal_code}'")
        return postal_code

    def clean_avatar(self):
        """✅ CORRIGIDO: Validação de avatar com debug"""
        avatar = self.cleaned_data.get("avatar")

        logger.info(f"Validando avatar: {avatar}")

        if not avatar:
            logger.info("Nenhum avatar fornecido")
            return avatar

        logger.info(
            f"Avatar details - name: {avatar.name}, size: {avatar.size}, type: {getattr(avatar, 'content_type', 'unknown')}"
        )

        # Verificar tamanho (2MB)
        if avatar.size > 2097152:  # 2MB em bytes
            logger.error(f"Avatar muito grande: {avatar.size} bytes")
            raise ValidationError("La taille du fichier ne doit pas dépasser 2MB.")

        # Verificar tipo de arquivo
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]

        # Tentar obter content_type
        content_type = getattr(avatar, "content_type", None)

        if content_type and content_type not in allowed_types:
            logger.error(f"Tipo de arquivo não permitido: {content_type}")
            raise ValidationError(
                "Type de fichier non autorisé. Utilisez JPG, PNG ou GIF."
            )

        # Verificar extensão como fallback
        if avatar.name:
            extension = avatar.name.lower().split(".")[-1]
            allowed_extensions = ["jpg", "jpeg", "png", "gif"]
            if extension not in allowed_extensions:
                logger.error(f"Extensão não permitida: {extension}")
                raise ValidationError(
                    "Extension de fichier non autorisée. Utilisez .jpg, .png ou .gif."
                )

        logger.info(f"Avatar validado com sucesso: {avatar.name}")
        return avatar

    def clean(self):
        """✅ CORRIGIDO: Validação geral do formulário"""
        cleaned_data = super().clean()

        logger.info(f"Validação geral - dados limpos: {cleaned_data}")

        return cleaned_data

    def save(self, commit=True):
        """✅ CORRIGIDO: Save com debug detalhado"""
        profile = super().save(commit=False)

        logger.info(f"Salvando perfil para {profile.user.email}")
        logger.info(
            f"Dados a salvar - phone: '{profile.phone}', city: '{profile.city}'"
        )

        # Se há um novo avatar e já existia um anterior, deletar o antigo
        if commit and self.cleaned_data.get("avatar") and self.instance.pk:
            try:
                old_profile = Profile.objects.get(pk=self.instance.pk)
                if old_profile.avatar and old_profile.avatar != profile.avatar:
                    logger.info(f"Deletando avatar antigo: {old_profile.avatar.name}")
                    old_profile.delete_old_avatar()
            except Profile.DoesNotExist:
                logger.warning("Profile antigo não encontrado para deletar avatar")

        if commit:
            profile.save()
            logger.info(f"Perfil salvo com sucesso para {profile.user.email}")

            # Verificar se foi realmente salvo
            profile.refresh_from_db()
            logger.info(
                f"Verificação pós-save - phone: '{profile.phone}', city: '{profile.city}'"
            )

        return profile
