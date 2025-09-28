from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm as DjangoPasswordResetForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import User, AccountType
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(UserCreationForm):
    """✅ CORRIGIDO: Formulário de registro com username automático"""

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("votre.email@exemple.com"),
                "autocomplete": "email",
            }
        ),
        help_text=_("Votre adresse email sera utilisée pour vous connecter."),
    )

    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre prénom"),
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre nom"),
                "autocomplete": "family-name",
            }
        ),
    )

    account_type = forms.ChoiceField(
        choices=[
            (AccountType.CLIENT, "Client"),
            (AccountType.COLLABORATOR, "Collaborateur"),
        ],
        required=True,
        widget=forms.RadioSelect(
            attrs={"class": "text-blue-600 form-radio focus:ring-blue-500"}
        ),
        label=_("Type de compte"),
        help_text=_("Sélectionnez le type de compte aproprié."),
    )

    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre mot de passe"),
                "autocomplete": "new-password",
            }
        ),
    )

    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Confirmez votre mot de passe"),
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "account_type",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"].strip().title()
        user.last_name = self.cleaned_data["last_name"].strip().title()
        user.account_type = self.cleaned_data["account_type"]

        if commit:
            user.save()
        return user


class EmailLoginForm(AuthenticationForm):
    """✅ CORRIGIDO: Formulário de login por email compatível com template"""

    # ✅ IMPORTANTE: Manter o campo username mas renomeá-lo para email no template
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 text-gray-900 bg-white border-2 border-gray-300 rounded-xl shadow-sm placeholder-gray-500 focus:outline-none focus:ring-0 focus:border-blue-600 transition-all duration-200",
                "placeholder": "votre.email@exemple.com",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 text-gray-900 bg-white border-2 border-gray-300 rounded-xl shadow-sm placeholder-gray-500 focus:outline-none focus:ring-0 focus:border-blue-600 transition-all duration-200",
                "placeholder": "••••••••",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Customizar o campo username para aceitar email
        self.fields["username"].help_text = "Entrez votre adresse email"

    def clean_username(self):
        """Normalizar email (que vem como username)"""
        username = self.cleaned_data.get("username")
        if username:
            return username.lower().strip()
        return username

    def clean(self):
        """✅ CORRIGIDO: Validação customizada para login por email"""
        username = self.cleaned_data.get("username")  # Na verdade é o email
        password = self.cleaned_data.get("password")

        if username is not None and password:
            # ✅ CORRIGIDO: Usar username=email (nosso backend espera isso)
            self.user_cache = authenticate(
                self.request,
                username=username,  # Nosso backend vai processar isso como email
                password=password,
            )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


# ✅ Para compatibilidade
UserLoginForm = EmailLoginForm


class PasswordResetForm(DjangoPasswordResetForm):
    """
    Formulário para solicitar redefinição de senha através do email.
    """

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": _("Entrez votre email"),
                "autocomplete": "email",
            }
        ),
        help_text=_("Entrez l'adresse email associée à votre compte."),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if not User.objects.filter(email=email, is_active=True).exists():
                raise ValidationError(
                    _("Aucun compte actif n'a été trouvé avec cette adresse email.")
                )
        return email

    def get_users(self, email):
        return User.objects.filter(
            email__iexact=email,
            is_active=True,
        )


class PasswordChangeForm(DjangoPasswordChangeForm):
    """
    Formulário personalizado para alteração de senha do usuário logado.
    """

    old_password = forms.CharField(
        label=_("Mot de passe actuel"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": _("Entrez votre mot de passe actuel"),
                "autocomplete": "current-password",
            }
        ),
        help_text=_(
            "Entrez votre mot de passe actuel pour confirmer les modifications."
        ),
    )

    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": _("Entrez votre nouveau mot de passe"),
                "autocomplete": "new-password",
            }
        ),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères."),
    )

    new_password2 = forms.CharField(
        label=_("Confirmation du nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": _("Confirmez votre nouveau mot de passe"),
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if old_password and not self.user.check_password(old_password):
            raise ValidationError(
                _("Votre mot de passe actuel est incorrect."),
                code="password_incorrect",
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    _("Les deux nouveaux mots de passe ne correspondent pas."),
                    code="password_mismatch",
                )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordResetConfirmForm(forms.Form):
    """
    Formulário para definir nova senha durante o reset.
    """

    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": _("Entrez votre nouveau mot de passe"),
                "autocomplete": "new-password",
            }
        ),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères."),
    )

    new_password2 = forms.CharField(
        label=_("Confirmation du nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": _("Confirmez votre nouveau mot de passe"),
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    _("Les deux mots de passe ne correspondent pas."),
                    code="password_mismatch",
                )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
