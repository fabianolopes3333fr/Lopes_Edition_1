from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Cliente, AdresseLivraison, AdresseTransporteur, AdresseChantier, TarifTVAClient


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'code', 'civilite', 'raison_sociale', 'nom', 'prenom',
            'adresse', 'code_postal', 'ville', 'pays',
            'telephone', 'mobile', 'email', 'url',
            'activite', 'siret', 'code_ape', 'tva_intra', 'tva_intra_custom',
            'status', 'origem', 'taux_tva_defaut', 'remise_globale',
            'conditions_paiement', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: CLI001'
            }),
            'civilite': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'raison_sociale': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'activite': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'siret': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'code_ape': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tva_intra': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'onchange': 'toggleTvaIntraCustom(this)'
            }),
            'tva_intra_custom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: ES12345678901',
                'style': 'display: none;'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'origem': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            # Removendo step dos campos numéricos para melhor aparência
            'taux_tva_defaut': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '20.00',
                'onchange': 'toggleTvaIntraCustom(this)'
            }),
            'remise_globale': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '0.00'
            }),
            'conditions_paiement': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Gerar automaticamente o código se é um novo cliente
        if not self.instance.pk:
            last_client = Cliente.objects.order_by('id').last()
            if last_client:
                try:
                    last_number = int(last_client.code.replace('CLI', ''))
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            self.fields['code'].initial = f'CLI{new_number:03d}'

    def clean_taux_tva_defaut(self):
        """Validação corrigida para taxa TVA"""
        value = self.cleaned_data.get('taux_tva_defaut')
        # Este campo é uma choice do TipoTVA, não precisa validação numérica
        return value

    def clean_remise_globale(self):
        """Validação customizada para desconto global"""
        value = self.cleaned_data.get('remise_globale')
        if value is not None:
            if value < 0 or value > 100:
                raise ValidationError("O desconto deve estar entre 0 e 100%")
        return value

    def clean_code(self):
        """Validação para código único"""
        code = self.cleaned_data.get('code')
        if code:
            # Verificar se o código já existe (exceto para o próprio objeto)
            existing = Cliente.objects.filter(code=code)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError("Este código já está em uso.")
        return code

    def clean_siret(self):
        """Validação customizada para SIRET"""
        siret = self.cleaned_data.get('siret')
        if siret and len(siret) != 14:
            raise ValidationError("O SIRET deve conter exatamente 14 dígitos.")
        return siret

    def clean(self):
        """Validação customizada do formulário inteiro"""
        cleaned_data = super().clean()

        # Verificar se pelo menos nome ou razão social está preenchido
        nom = cleaned_data.get('nom')
        raison_sociale = cleaned_data.get('raison_sociale')

        if not nom and not raison_sociale:
            raise ValidationError("Pelo menos o nome ou a razão social deve ser preenchido.")

        # Validação de TVA intracommunautaire
        tva_intra = cleaned_data.get('tva_intra')
        tva_intra_custom = cleaned_data.get('tva_intra_custom')

        if tva_intra == 'autre' and not tva_intra_custom:
            self.add_error('tva_intra_custom', 'Campo obrigatório quando "Autre" é selecionado.')

        return cleaned_data


class AdresseLivraisonForm(forms.ModelForm):
    class Meta:
        model = AdresseLivraison
        fields = [
            'nom', 'copier_adresse_principale', 'adresse', 'code_postal',
            'ville', 'pays', 'contact_nom', 'contact_telephone', 'instructions'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'copier_adresse_principale': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'contact_nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'contact_telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
        }


class AdresseTransporteurForm(forms.ModelForm):
    class Meta:
        model = AdresseTransporteur
        fields = [
            'nom', 'copier_adresse_principale', 'adresse', 'code_postal',
            'ville', 'pays', 'contact_nom', 'contact_telephone', 'contact_email'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'copier_adresse_principale': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'contact_nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'contact_telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }


class AdresseChantierForm(forms.ModelForm):
    class Meta:
        model = AdresseChantier
        fields = [
            'nom', 'copier_adresse_principale', 'adresse', 'code_postal',
            'ville', 'pays', 'responsable_nom', 'responsable_telephone', 'instructions_acces'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'copier_adresse_principale': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'responsable_nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'responsable_telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'instructions_acces': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
        }


class TarifTVAClientForm(forms.ModelForm):
    class Meta:
        model = TarifTVAClient
        fields = ['taux_tva', 'description', 'actif']
        widgets = {
            'taux_tva': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }

    def clean_taux_tva(self):
        """Validação customizada para taxa TVA"""
        value = self.cleaned_data.get('taux_tva')
        if value is not None:
            if value < 0 or value > 100:
                raise forms.ValidationError("A taxa TVA deve estar entre 0 e 100%")
        return value


# Formsets corrigidos com configuração adequada para campos opcionais
AdresseLivraisonFormSet = inlineformset_factory(
    Cliente, AdresseLivraison,
    form=AdresseLivraisonForm,
    extra=0,  # Mudado de 1 para 0 para evitar campos obrigatórios vazios
    can_delete=True,
    min_num=0,  # Mínimo de 0 forms
    validate_min=False  # Não validar mínimo
)

AdresseTransporteurFormSet = inlineformset_factory(
    Cliente, AdresseTransporteur,
    form=AdresseTransporteurForm,
    extra=0,  # Mudado de 1 para 0
    can_delete=True,
    min_num=0,
    validate_min=False
)

AdresseChantierFormSet = inlineformset_factory(
    Cliente, AdresseChantier,
    form=AdresseChantierForm,
    extra=0,  # Mudado de 1 para 0
    can_delete=True,
    min_num=0,
    validate_min=False
)

TarifTVAClientFormSet = inlineformset_factory(
    Cliente, TarifTVAClient,
    form=TarifTVAClientForm,
    extra=0,  # Mudado de 1 para 0
    can_delete=True,
    min_num=0,
    validate_min=False
)
