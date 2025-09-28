from django import forms
from django.core.validators import EmailValidator
from .models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento,
    AnexoProjeto, TipoServico, UrgenciaProjeto, StatusProjeto
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
        fields = ['observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Informações adicionais para este orçamento...'
            })
        }

class OrcamentoForm(forms.ModelForm):
    """Formulário para elaboração de orçamentos pelos administradores"""

    class Meta:
        model = Orcamento
        fields = [
            'titulo', 'descricao', 'prazo_execucao', 'validade_orcamento',
            'condicoes_pagamento', 'desconto', 'observacoes'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Titre du devis'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Description détaillée des travaux...'
            }),
            'prazo_execucao': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nombre de jours'
            }),
            'validade_orcamento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'condicoes_pagamento': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Conditions de paiement...'
            }),
            'desconto': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Pourcentage de remise',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observations...'
            })
        }

class ItemOrcamentoForm(forms.ModelForm):
    """Formulário para itens do orçamento"""

    class Meta:
        model = ItemOrcamento
        fields = ['descricao', 'quantidade', 'unidade', 'preco_unitario']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Description de l\'item'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            }),
            'unidade': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'm², ml, unité...'
            }),
            'preco_unitario': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            })
        }

# Formset para itens do orçamento
ItemOrcamentoFormSet = inlineformset_factory(
    Orcamento,
    ItemOrcamento,
    form=ItemOrcamentoForm,
    extra=1,
    can_delete=True,
    can_order=True
)

class AnexoProjetoForm(forms.ModelForm):
    """Formulário para upload de anexos dos projetos"""

    class Meta:
        model = AnexoProjeto
        fields = ['arquivo', 'descricao']
        widgets = {
            'arquivo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*,.pdf,.doc,.docx'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Description de ce fichier...'
            })
        }
