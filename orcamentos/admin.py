from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import (
    Projeto, SolicitacaoOrcamento, Orcamento, ItemOrcamento, AnexoProjeto,
    StatusOrcamento, StatusProjeto, Produto, Fornecedor, Notificacao
)

class AnexoProjetoInline(admin.TabularInline):
    model = AnexoProjeto
    extra = 0
    fields = ['arquivo', 'descricao']
    readonly_fields = ['created_at']

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'cliente', 'tipo_servico', 'status', 'urgencia',
        'cidade_projeto', 'created_at'
    ]
    list_filter = [
        'status', 'tipo_servico', 'urgencia', 'created_at'
    ]
    search_fields = [
        'titulo', 'cliente__first_name', 'cliente__last_name',
        'cliente__email', 'endereco_projeto', 'cidade_projeto'
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at']

    fieldsets = (
        ('Informações Gerais', {
            'fields': ('titulo', 'cliente', 'descricao', 'tipo_servico', 'urgencia', 'status')
        }),
        ('Localização', {
            'fields': ('endereco_projeto', 'cidade_projeto', 'cep_projeto')
        }),
        ('Detalhes Técnicos', {
            'fields': ('area_aproximada', 'numero_comodos', 'altura_teto')
        }),
        ('Planning e Orçamento', {
            'fields': ('orcamento_estimado', 'data_inicio_desejada', 'observacoes')
        }),
        ('Sistema', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [AnexoProjetoInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente')

class ItemOrcamentoInline(admin.TabularInline):
    model = ItemOrcamento
    extra = 1
    fields = ['referencia', 'descricao', 'quantidade', 'unidade', 'preco_unitario_ht', 'total_ht']
    readonly_fields = ['total_ht']

@admin.register(SolicitacaoOrcamento)
class SolicitacaoOrcamentoAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'nome_solicitante', 'email_solicitante', 'tipo_servico',
        'status', 'created_at', 'tem_orcamento'
    ]
    list_filter = [
        'status', 'tipo_servico', 'urgencia', 'created_at'
    ]
    search_fields = [
        'numero', 'nome_solicitante', 'email_solicitante',
        'telefone_solicitante', 'endereco', 'cidade'
    ]
    readonly_fields = ['numero', 'uuid', 'created_at', 'updated_at']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'status', 'cliente', 'projeto')
        }),
        ('Dados do Solicitante', {
            'fields': ('nome_solicitante', 'email_solicitante', 'telefone_solicitante')
        }),
        ('Localização', {
            'fields': ('endereco', 'cidade', 'cep')
        }),
        ('Detalhes do Serviço', {
            'fields': ('tipo_servico', 'descricao_servico', 'area_aproximada', 'urgencia')
        }),
        ('Preferências', {
            'fields': ('data_inicio_desejada', 'orcamento_maximo', 'observacoes')
        }),
        ('Sistema', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['criar_orcamento_action']

    def tem_orcamento(self, obj):
        if hasattr(obj, 'orcamento'):
            return format_html(
                '<span style="color: green;">✓ Sim</span>'
            )
        return format_html('<span style="color: red;">✗ Não</span>')
    tem_orcamento.short_description = 'Tem Orçamento'

    def criar_orcamento_action(self, request, queryset):
        """Action para criar orçamentos em massa"""
        created = 0
        for solicitacao in queryset:
            if not hasattr(solicitacao, 'orcamento'):
                Orcamento.objects.create(
                    solicitacao=solicitacao,
                    elaborado_por=request.user,
                    titulo=f"Orçamento para {solicitacao.tipo_servico}",
                    descricao=solicitacao.descricao_servico,
                    prazo_execucao=30,
                    validade_orcamento=timezone.now().date() + timezone.timedelta(days=30),
                    condicoes_pagamento="30% à la commande, 70% à la livraison"
                )
                created += 1

        if created > 0:
            self.message_user(
                request,
                f"{created} orçamento(s) criado(s) com sucesso!",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "Nenhum orçamento foi criado (já existiam orçamentos para todas as solicitações selecionadas).",
                messages.WARNING
            )

    criar_orcamento_action.short_description = "Criar orçamentos para solicitações selecionadas"

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'solicitacao_numero', 'cliente_nome', 'total',
        'status', 'data_elaboracao', 'data_envio'
    ]
    list_filter = [
        'status', 'data_elaboracao', 'data_envio', 'validade_orcamento'
    ]
    search_fields = [
        'numero', 'solicitacao__numero', 'solicitacao__nome_solicitante',
        'solicitacao__email_solicitante', 'titulo'
    ]
    readonly_fields = [
        'numero', 'uuid', 'subtotal', 'valor_desconto', 'total',
        'data_elaboracao', 'data_envio', 'data_resposta_cliente'
    ]

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'solicitacao', 'elaborado_por', 'status')
        }),
        ('Conteúdo do Orçamento', {
            'fields': ('titulo', 'descricao')
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'valor_desconto', 'total'),
            'classes': ('collapse',)
        }),
        ('Condições', {
            'fields': ('prazo_execucao', 'validade_orcamento', 'condicoes_pagamento')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('data_elaboracao', 'data_envio', 'data_resposta_cliente'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('uuid',),
            'classes': ('collapse',)
        })
    )

    inlines = [ItemOrcamentoInline]

    actions = ['enviar_orcamento_action', 'gerar_pdf_action']

    def solicitacao_numero(self, obj):
        return obj.solicitacao.numero
    solicitacao_numero.short_description = 'Nº Solicitação'

    def cliente_nome(self, obj):
        return obj.solicitacao.nome_solicitante
    cliente_nome.short_description = 'Cliente'

    def enviar_orcamento_action(self, request, queryset):
        """Action para enviar orçamentos"""
        enviados = 0
        for orcamento in queryset:
            if orcamento.status != StatusOrcamento.ENVIADO:
                orcamento.status = StatusOrcamento.ENVIADO
                orcamento.data_envio = timezone.now()
                orcamento.save()

                # Atualizar status da solicitação
                orcamento.solicitacao.status = StatusOrcamento.ENVIADO
                orcamento.solicitacao.save()

                enviados += 1

        if enviados > 0:
            self.message_user(
                request,
                f"{enviados} orçamento(s) marcado(s) como enviado(s)!",
                messages.SUCCESS
            )

    enviar_orcamento_action.short_description = "Marcar como enviados"

    def gerar_pdf_action(self, request, queryset):
        """Action para gerar PDFs dos orçamentos"""
        # Esta funcionalidade pode ser implementada posteriormente
        self.message_user(
            request,
            "Funcionalidade de geração de PDF será implementada em breve.",
            messages.INFO
        )

    gerar_pdf_action.short_description = "Gerar PDFs"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitacao', 'elaborado_por')

@admin.register(ItemOrcamento)
class ItemOrcamentoAdmin(admin.ModelAdmin):
    list_display = [
        'orcamento', 'referencia', 'descricao', 'quantidade', 'preco_unitario_ht', 'total_ht'
    ]
    list_filter = ['unidade', 'atividade', 'taxa_tva']
    search_fields = ['referencia', 'descricao', 'orcamento__numero']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('orcamento')

@admin.register(AnexoProjeto)
class AnexoProjetoAdmin(admin.ModelAdmin):
    list_display = ['projeto', 'descricao', 'arquivo', 'created_at']
    list_filter = ['created_at', 'projeto__status']
    search_fields = ['descricao', 'projeto__titulo']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('projeto')

# Administração para Produtos e Fornecedores
@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'email', 'telefone', 'cidade', 'ativo',
        'produtos_count', 'created_at'
    ]
    list_filter = ['ativo', 'cidade', 'created_at']
    search_fields = ['nome', 'email', 'telefone', 'endereco', 'cidade']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'email', 'telefone', 'ativo')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'cep')
        }),
        ('Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def produtos_count(self, obj):
        count = obj.produtos.count()
        if count > 0:
            return format_html(
                '<a href="{}?fornecedor__id__exact={}">{} produto(s)</a>',
                reverse('admin:orcamentos_produto_changelist'),
                obj.id,
                count
            )
        return "0 produtos"
    produtos_count.short_description = 'Produtos'

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = [
        'referencia', 'descricao', 'unidade', 'atividade', 'fornecedor',
        'preco_compra', 'preco_venda_ht', 'preco_venda_ttc', 'margem_percentual',
        'ativo', 'created_at'
    ]
    list_filter = [
        'ativo', 'unidade', 'atividade', 'taxa_tva', 'fornecedor', 'created_at'
    ]
    search_fields = ['referencia', 'descricao', 'fornecedor__nome']
    readonly_fields = [
        'preco_venda_ht', 'preco_venda_ttc', 'margem_ht',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('referencia', 'descricao', 'unidade', 'atividade', 'ativo')
        }),
        ('Fornecedor', {
            'fields': ('fornecedor',)
        }),
        ('Preços e Margens', {
            'fields': (
                'preco_compra', 'margem_percentual', 'margem_ht',
                'preco_venda_ht', 'taxa_tva', 'preco_venda_ttc'
            )
        }),
        ('Foto', {
            'fields': ('foto',)
        }),
        ('Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        """Override para garantir que os cálculos sejam feitos"""
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('fornecedor')

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'tipo', 'titulo', 'lida', 'created_at'
    ]
    list_filter = ['lida', 'tipo', 'created_at']
    search_fields = ['titulo', 'mensagem', 'usuario__email']
    readonly_fields = ['created_at', 'read_at']

    fieldsets = (
        ('Notificação', {
            'fields': ('usuario', 'tipo', 'titulo', 'mensagem', 'url_acao')
        }),
        ('Status', {
            'fields': ('lida', 'created_at', 'read_at')
        }),
        ('Relacionamentos', {
            'fields': ('solicitacao', 'orcamento', 'projeto'),
            'classes': ('collapse',)
        })
    )

    actions = ['marcar_como_lida', 'marcar_como_nao_lida']

    def marcar_como_lida(self, request, queryset):
        updated = queryset.filter(lida=False).update(
            lida=True,
            read_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} notificação(ões) marcada(s) como lida(s).',
            messages.SUCCESS
        )
    marcar_como_lida.short_description = "Marcar como lidas"

    def marcar_como_nao_lida(self, request, queryset):
        updated = queryset.filter(lida=True).update(
            lida=False,
            read_at=None
        )
        self.message_user(
            request,
            f'{updated} notificação(ões) marcada(s) como não lidas.',
            messages.SUCCESS
        )
    marcar_como_nao_lida.short_description = "Marcar como não lidas"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

# Customização do Admin Site
admin.site.site_header = "LOPES PEINTURE - Administration"
admin.site.site_title = "LOPES PEINTURE Admin"
admin.site.index_title = "Gestion des Orçamentos et Projets"
