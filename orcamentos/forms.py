from django import forms
from django.core.validators import EmailValidator
from .models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    AnexoProjeto, StatusOrcamento, StatusProjeto, Produto, Fornecedor,
    TipoUnidade, TipoAtividade, TipoTVA, Facture, ItemFacture
)
from django.forms import inlineformset_factory

class SolicitacaoOrcamentoPublicoForm(forms.ModelForm):
    """Formulário público para solicitação de orçamento (sem login)"""

    class Meta:
        model = SolicitacaoOrcamento
        fields = [
            'nome_solicitante', 'email_solicitante', 'telefone_solicitante',
            'endereco', 'cidade', 'cep', 'tipo_servico', 'descricao_servico',
            'area_aproximada', 'urgencia', 'data_inicio_desejada',
            'orcamento_maximo', 'observacoes'
        ]
        widgets = {
            'nome_solicitante': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Votre nom complet'
            }),
            'email_solicitante': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'votre@email.com'
            }),
            'telefone_solicitante': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '+33 1 23 45 67 89'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Adresse complète du projet'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ville'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '75001'
            }),
            'tipo_servico': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descricao_servico': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Décrivez en détail les travaux souhaités...'
            }),
            'urgencia': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'area_aproximada': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Surface en m²',
                'step': '0.01'
            }),
            'data_inicio_desejada': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'orcamento_maximo': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Budget maximum en €',
                'step': '0.01'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Informations complémentaires...'
            })
        }

class ProjetoForm(forms.ModelForm):
    """Formulário para criação/edição de projetos por clientes logados"""

    class Meta:
        model = Projeto
        fields = [
            'titulo', 'descricao', 'tipo_servico', 'urgencia',
            'endereco_projeto', 'cidade_projeto', 'cep_projeto',
            'area_aproximada', 'numero_comodos', 'altura_teto',
            'orcamento_estimado', 'data_inicio_desejada', 'observacoes'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nom de votre projet'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Description détaillée de votre projet...'
            }),
            'tipo_servico': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'urgencia': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'endereco_projeto': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Adresse du projet'
            }),
            'cidade_projeto': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ville'
            }),
            'cep_projeto': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Code postal'
            }),
            'area_aproximada': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Surface en m²',
                'step': '0.01'
            }),
            'numero_comodos': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nombre de pièces'
            }),
            'altura_teto': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Hauteur en mètres',
                'step': '0.01'
            }),
            'orcamento_estimado': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Budget estimé en €',
                'step': '0.01'
            }),
            'data_inicio_desejada': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observations particulières...'
            })
        }

class SolicitacaoOrcamentoProjetoForm(forms.ModelForm):
    """Formulário para solicitar orçamento de um projeto específico"""

    class Meta:
        model = SolicitacaoOrcamento
        fields = [
            'tipo_servico', 'descricao_servico', 'area_aproximada',
            'urgencia', 'data_inicio_desejada', 'orcamento_maximo',
            'observacoes'
        ]
        widgets = {
            'tipo_servico': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descricao_servico': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Décrivez en détail les travaux souhaités...'
            }),
            'area_aproximada': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Surface en m²',
                'step': '0.01'
            }),
            'urgencia': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'data_inicio_desejada': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'orcamento_maximo': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Budget maximum en €',
                'step': '0.01'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observations particulières...'
            })
        }

class OrcamentoForm(forms.ModelForm):
    """Formulário para elaboração de orçamentos pelos administradores"""

    class Meta:
        model = Orcamento
        fields = [
            'titulo', 'descricao', 'prazo_execucao', 'validade_orcamento',
            'desconto', 'condicoes_pagamento', 'tipo_pagamento', 'observacoes'
        ]

        labels = {
            'titulo': 'Titre du devis',
            'descricao': 'Description',
            'prazo_execucao': 'Délai d\'exécution (jours)',
            'validade_orcamento': 'Validité du devis',
            'desconto': 'Remise globale (%)',
            'condicoes_pagamento': 'Conditions de paiement',
            'tipo_pagamento': 'Type de paiement',
            'observacoes': 'Observations'
        }

        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Saisissez le titre du devis...',
                'id': 'titulo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'Décrivez le projet ou les travaux à réaliser...',
                'id': 'descricao'
            }),
            'prazo_execucao': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 365,
                'placeholder': '30',
                'id': 'prazo'
            }),
            'validade_orcamento': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'id': 'validade'
            }),
            'desconto': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': 0,
                'max': 100,
                'placeholder': '0.00',
                'id': 'desconto-global'
            }),
            'condicoes_pagamento': forms.Select(attrs={
                'class': 'form-input',
                'id': 'condicoes'
            }),
            'tipo_pagamento': forms.Select(attrs={
                'class': 'form-input',
                'id': 'tipo_pagamento'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'Ajoutez des observations, notes ou conditions particulières...',
                'id': 'observacoes'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Definir valores padrão
        if not self.instance.pk:  # Apenas para novos orçamentos
            from datetime import date, timedelta
            self.fields['prazo_execucao'].initial = 30
            self.fields['validade_orcamento'].initial = date.today() + timedelta(days=30)
            self.fields['desconto'].initial = 0.00

        # Tornar todos os campos obrigatórios exceto observações
        for field_name, field in self.fields.items():
            if field_name != 'observacoes':
                field.required = True

            # Adicionar classe de erro se o campo tem erros
            if field_name in self.errors:
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_classes} border-red-500 focus:border-red-500 focus:ring-red-500"

class ItemOrcamentoForm(forms.ModelForm):
    """Formulário para itens do orçamento"""

    class Meta:
        model = ItemOrcamento
        fields = [
            'produto', 'referencia', 'descricao', 'unidade', 'atividade',
            'quantidade', 'preco_unitario_ttc', 'remise_percentual', 'taxa_tva'
        ]

        widgets = {
            'produto': forms.HiddenInput(),
            'referencia': forms.TextInput(attrs={
                'class': 'excel-input referencia',
                'readonly': True
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'excel-input descricao',
                'placeholder': 'Description...'
            }),
            'unidade': forms.Select(attrs={
                'class': 'excel-select unidade'
            }),
            'atividade': forms.Select(attrs={
                'class': 'excel-select atividade'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'excel-input quantidade',
                'step': '0.01',
                'min': 0,
                'value': 1
            }),
            'preco_unitario_ttc': forms.NumberInput(attrs={
                'class': 'excel-input preco-ht',
                'step': '0.01',
                'min': 0,
                'value': 0
            }),
            'remise_percentual': forms.NumberInput(attrs={
                'class': 'excel-input remise',
                'step': '0.01',
                'min': 0,
                'max': 100,
                'value': 0
            }),
            'taxa_tva': forms.Select(attrs={
                'class': 'excel-select taxa-tva'
            })
        }

# Formset para múltiplos itens do orçamento
ItemOrcamentoFormSet = inlineformset_factory(
    Orcamento,
    ItemOrcamento,
    form=ItemOrcamentoForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)

class ProdutoForm(forms.ModelForm):
    """Formulário para cadastro/edição de produtos"""

    class Meta:
        model = Produto
        fields = [
            'referencia', 'descricao', 'unidade', 'atividade',
            'preco_compra', 'margem_percentual', 'margem_ht',
            'preco_venda_ht', 'taxa_tva', 'preco_venda_ttc',
            'fornecedor', 'foto', 'ativo'
        ]

        labels = {
            'referencia': 'Référence',
            'descricao': 'Description',
            'unidade': 'Unité',
            'atividade': 'Activité',
            'preco_compra': 'Prix d\'achat',
            'margem_percentual': 'Marge %',
            'margem_ht': 'Marge HT',
            'preco_venda_ht': 'Prix de vente HT',
            'taxa_tva': 'Taux TVA',
            'preco_venda_ttc': 'Prix de vente TTC',
            'fornecedor': 'Fournisseur',
            'foto': 'Photo',
            'ativo': 'Actif'
        }

        widgets = {
            'referencia': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Référence du produit'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description détaillée du produit'
            }),
            'unidade': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'atividade': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'preco_compra': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': 0,
                'placeholder': '0.00',
                'id': 'id_preco_compra'
            }),
            'margem_percentual': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': 0,
                'placeholder': '0.00',
                'id': 'id_margem_percentual'
            }),
            'margem_ht': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-100',
                'step': '0.01',
                'min': 0,
                'placeholder': '0.00',
                'readonly': True,
                'id': 'id_margem_ht'
            }),
            'preco_venda_ht': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-100',
                'step': '0.01',
                'min': 0,
                'placeholder': '0.00',
                'readonly': True,
                'id': 'id_preco_venda_ht'
            }),
            'taxa_tva': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_taxa_tva'
            }),
            'preco_venda_ttc': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-100',
                'step': '0.01',
                'min': 0,
                'placeholder': '0.00',
                'readonly': True,
                'id': 'id_preco_venda_ttc'
            }),
            'fornecedor': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*',
                'id': 'id_foto'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }

class FornecedorForm(forms.ModelForm):
    """Formulário para cadastro/edição de fornecedores"""

    class Meta:
        model = Fornecedor
        fields = [
            'nome', 'endereco', 'cidade', 'cep',
            'telefone', 'email', 'ativo'
        ]

        labels = {
            'nome': 'Nom du fournisseur',
            'endereco': 'Adresse',
            'cidade': 'Ville',
            'cep': 'Code postal',
            'telefone': 'Téléphone',
            'email': 'Email',
            'ativo': 'Actif'
        }

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nom de l\'entreprise'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Adresse complète'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ville'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Code postal'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '+33 1 23 45 67 89'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'email@exemple.fr'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50'
            })
        }

class AnexoProjetoForm(forms.ModelForm):
    """Formulário para upload de anexos de projetos"""

    class Meta:
        model = AnexoProjeto
        fields = ['arquivo', 'descricao']

        widgets = {
            'arquivo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Description du fichier'
            })
        }

class FactureForm(forms.ModelForm):
    """Formulário para elaboração de faturas pelos administradores"""

    # Campo personalizado para busca de cliente
    cliente_search = forms.CharField(
        label='Client',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'id': 'cliente-search',
            'placeholder': 'Tapez le nom ou email du client...',
            'autocomplete': 'off'
        }),
        required=False,  # CORREÇÃO: Sempre não obrigatório
        help_text='Recherchez un client par nom ou email'
    )

    # Campo hidden para armazenar o ID do cliente selecionado
    cliente = forms.ModelChoiceField(
        queryset=None,
        widget=forms.HiddenInput(),
        required=True
    )

    class Meta:
        model = Facture
        fields = [
            'cliente', 'titulo', 'descricao', 'data_emissao', 'data_vencimento',
            'desconto', 'condicoes_pagamento', 'tipo_pagamento', 'observacoes'
        ]

        labels = {
            'titulo': 'Titre de la facture',
            'descricao': 'Description',
            'data_emissao': "Date d'émission",
            'data_vencimento': "Date d'échéance",
            'desconto': 'Remise globale (%)',
            'condicoes_pagamento': 'Conditions de paiement',
            'tipo_pagamento': 'Type de paiement',
            'observacoes': 'Observations'
        }

        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Saisissez le titre de la facture...',
                'id': 'titulo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'Décrivez les services facturés...',
                'id': 'descricao'
            }),
            'data_emissao': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'id': 'data_emissao'
            }),
            'data_vencimento': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'id': 'data_vencimento'
            }),
            'desconto': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': 0,
                'max': 100,
                'placeholder': '0.00',
                'id': 'desconto-global'
            }),
            'condicoes_pagamento': forms.Select(attrs={
                'class': 'form-input',
                'id': 'condicoes'
            }),
            'tipo_pagamento': forms.Select(attrs={
                'class': 'form-input',
                'id': 'tipo_pagamento'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'Ajoutez des observations, notes ou conditions particulières...',
                'id': 'observacoes'
            })
        }

    def __init__(self, *args, **kwargs):
        # CORREÇÃO: Extrair cliente antes de chamar super
        cliente_predefinido = kwargs.pop('cliente_predefinido', None)
        super().__init__(*args, **kwargs)

        # Configurar queryset para o campo cliente
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['cliente'].queryset = User.objects.filter(is_active=True, is_staff=False)

        # Guardar referência para uso no clean()
        self._cliente_predefinido = cliente_predefinido

        # CORREÇÃO: Se tem cliente predefinido, configurar automaticamente
        if cliente_predefinido:
            self.fields['cliente'].initial = cliente_predefinido
            # Em POST o hidden pode não vir (ex.: testes); tornar não obrigatório
            self.fields['cliente'].required = False
            nome_cliente = f"{cliente_predefinido.first_name} {cliente_predefinido.last_name}".strip()
            if not nome_cliente:
                nome_cliente = cliente_predefinido.email
            self.fields['cliente_search'].initial = nome_cliente
            # Tornar o campo cliente_search não obrigatório
            self.fields['cliente_search'].required = False

        # Se estamos editando uma fatura existente, preencher o campo de busca
        elif self.instance and self.instance.pk and self.instance.cliente:
            nome_cliente = f"{self.instance.cliente.first_name} {self.instance.cliente.last_name}".strip()
            if not nome_cliente:
                nome_cliente = self.instance.cliente.email
            self.fields['cliente_search'].initial = nome_cliente

        # CORREÇÃO: Definir data de emissão padrão se não fornecida
        if not self.initial.get('data_emissao') and not (self.instance and self.instance.pk):
            from django.utils import timezone
            self.fields['data_emissao'].initial = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()

        # CORREÇÃO: Validação personalizada para o cliente
        cliente = cleaned_data.get('cliente')
        cliente_search = cleaned_data.get('cliente_search', '').strip()

        # Se cliente não veio no POST mas temos predefinido (ex.: fluxo a partir do devis), usar ele
        if not cliente and getattr(self, '_cliente_predefinido', None) is not None:
            cleaned_data['cliente'] = self._cliente_predefinido
            return cleaned_data

        # Se já tem cliente, não precisa validar busca
        if cliente:
            return cleaned_data

        # Se não tem cliente mas tem busca, tentar encontrar
        if cliente_search:
            from django.contrib.auth import get_user_model
            from django.db.models import Q
            User = get_user_model()

            # Buscar por email exato primeiro
            try:
                cliente_encontrado = User.objects.get(
                    email__iexact=cliente_search.strip(),
                    is_active=True,
                    is_staff=False
                )
                cleaned_data['cliente'] = cliente_encontrado
                return cleaned_data
            except User.DoesNotExist:
                # Buscar por nome
                usuarios = User.objects.filter(
                    is_active=True,
                    is_staff=False
                ).filter(
                    Q(first_name__icontains=cliente_search) |
                    Q(last_name__icontains=cliente_search) |
                    Q(email__icontains=cliente_search)
                )

                if usuarios.count() == 1:
                    cleaned_data['cliente'] = usuarios.first()
                    return cleaned_data
                elif usuarios.count() > 1:
                    raise forms.ValidationError("Plusieurs clients correspondent à votre recherche. Soyez plus précis.")
                else:
                    raise forms.ValidationError("Aucun client trouvé avec ce nom ou email.")

        # Se chegou até aqui, não tem cliente
        raise forms.ValidationError("Veuillez sélectionner un client.")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # CORREÇÃO: Garantir que o cliente está definido
        if not instance.cliente and hasattr(self, 'cleaned_data'):
            cliente = self.cleaned_data.get('cliente')
            if cliente:
                instance.cliente = cliente

        if commit:
            instance.save()
        return instance

class ItemFactureForm(forms.ModelForm):
    """Formulário para itens da fatura"""

    class Meta:
        model = ItemFacture
        fields = [
            'produto', 'referencia', 'descricao', 'unidade', 'atividade',
            'quantidade', 'preco_unitario_ttc', 'remise_percentual', 'taxa_tva'
        ]

        widgets = {
            'produto': forms.HiddenInput(),
            'referencia': forms.TextInput(attrs={
                'class': 'excel-input referencia',
                'readonly': True
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'excel-input descricao',
                'placeholder': 'Description...'
            }),
            'unidade': forms.Select(attrs={
                'class': 'excel-select unidade'
            }),
            'atividade': forms.Select(attrs={
                'class': 'excel-select atividade'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'excel-input quantidade',
                'step': '0.01',
                'min': 0,
                'value': 1
            }),
            'preco_unitario_ttc': forms.NumberInput(attrs={
                'class': 'excel-input preco-ht',
                'step': '0.01',
                'min': 0,
                'value': 0
            }),
            'remise_percentual': forms.NumberInput(attrs={
                'class': 'excel-input remise',
                'step': '0.01',
                'min': 0,
                'max': 100,
                'value': 0
            }),
            'taxa_tva': forms.Select(attrs={
                'class': 'excel-select taxa-tva'
            })
        }

# Formset para múltiplos itens da fatura
ItemFactureFormSet = inlineformset_factory(
    Facture,
    ItemFacture,
    form=ItemFactureForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)
