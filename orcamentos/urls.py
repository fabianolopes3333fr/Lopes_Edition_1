from django.urls import path
from . import views
from . import produtos_views


app_name = 'orcamentos'

urlpatterns = [
    # ============ URLs PÚBLICAS (SEM LOGIN) ============
    path('solicitar/', views.solicitar_orcamento_publico, name='solicitar_publico'),
    path('sucesso/<str:numero>/', views.sucesso_solicitacao, name='sucesso_solicitacao'),

    # ============ URLs PARA CLIENTES ============
    path('projets/', views.cliente_projetos, name='cliente_projetos'),
    path('projets/nouveau/', views.cliente_criar_projeto, name='cliente_criar_projeto'),
    path('projets/<uuid:uuid>/', views.cliente_projeto_detail, name='cliente_projeto_detail'),
    path('projets/<uuid:uuid>/editer/', views.cliente_editar_projeto, name='cliente_editar_projeto'),
    path('projets/<uuid:uuid>/supprimer/', views.cliente_excluir_projeto, name='cliente_excluir_projeto'),
    path('projets/<uuid:uuid>/solicitar-orcamento/', views.cliente_solicitar_orcamento_projeto, name='cliente_solicitar_orcamento'),

    # URLs para orçamentos dos clientes
    path('mes-devis/', views.cliente_orcamentos, name='cliente_orcamentos'),
    path('devis/<str:numero>/', views.cliente_devis_detail, name='cliente_devis_detail'),
    path('devis/<str:numero>/accepter/', views.cliente_devis_accepter, name='cliente_aceitar_orcamento'),
    path('devis/<str:numero>/refuser/', views.cliente_devis_refuser, name='cliente_recusar_orcamento'),
    path('devis/<str:numero>/pdf/', views.cliente_devis_pdf, name='cliente_devis_pdf'),

    # URLs para faturas dos clientes
    path('mes-factures/', views.cliente_faturas, name='cliente_faturas'),
    path('factures/<str:numero>/', views.cliente_fatura_detail, name='cliente_fatura_detail'),
    path('factures/<str:numero>/pdf/', views.cliente_fatura_pdf, name='cliente_fatura_pdf'),

    # URLs AJAX para clientes
    path('projets/<uuid:uuid>/upload-anexo/', views.upload_anexo_projeto, name='upload_anexo_projeto'),
    path('projets/<uuid:uuid>/anexos/<int:anexo_id>/delete/', views.excluir_anexo_projeto, name='excluir_anexo_projeto'),

    # ============ URLs ADMINISTRATIVAS ============
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/solicitacoes/', views.admin_solicitacoes, name='admin_solicitacoes'),
    path('admin/solicitacoes/<str:numero>/', views.admin_solicitacao_detail, name='admin_solicitacao_detail'),
    path('admin/solicitacoes/<str:numero>/criar-orcamento/', views.admin_elaborar_orcamento, name='admin_criar_orcamento'),

    # URLs para gestão de orçamentos
    path('admin/orcamentos/', views.admin_orcamentos, name='admin_orcamentos'),
    path('admin/orcamentos/<str:numero>/', views.admin_orcamento_detail, name='admin_orcamento_detail'),
    path('admin/orcamentos/<str:numero>/editar/', views.admin_editar_orcamento, name='admin_editar_orcamento'),
    path('admin/orcamentos/<str:numero>/enviar/', views.admin_enviar_orcamento, name='admin_enviar_orcamento'),
    path('admin/orcamentos/<str:numero>/pdf/', views.admin_orcamento_pdf, name='admin_orcamento_pdf'),
    path('admin/orcamentos/<str:numero>/pdf-html/', views.admin_orcamento_pdf_html, name='admin_orcamento_pdf_html'),

    # URLs para elaboração de orçamentos
    path('admin/elaborar/<str:numero>/', views.admin_elaborar_orcamento, name='admin_elaborar_orcamento'),
    path('admin/solicitacoes/<str:numero>/criar-orcamento/', views.admin_elaborar_orcamento, name='admin_criar_orcamento'),
    path('admin/clientes/<int:cliente_id>/criar-orcamento/', views.admin_criar_orcamento_cliente, name='admin_criar_orcamento_cliente'),

    # URLs para gestão de orçamentos órfãos
    path('admin/orcamentos-orfaos/', views.admin_orcamentos_orfaos, name='admin_orcamentos_orfaos'),
    path('admin/vincular-orcamentos-orfaos/', views.admin_vincular_orcamentos_orfaos, name='admin_vincular_orcamentos_orfaos'),

    # ============ URLs ADMINISTRATIVAS DE PROJETOS ============
    path('admin/projetos/', views.admin_projetos_list, name='admin_projetos_list'),
    path('admin/projetos/<uuid:uuid>/', views.admin_projeto_detail, name='admin_projeto_detail'),
    path('admin/projetos/<uuid:uuid>/change-status/', views.admin_projeto_change_status, name='admin_projeto_change_status'),

    # ============ URLs PARA PRODUTOS ============
    path('admin/produtos/', produtos_views.lista_produtos, name='lista_produtos'),
    path('admin/produtos/criar/', produtos_views.criar_produto, name='criar_produto'),
    path('admin/produtos/<int:produto_id>/editar/', produtos_views.editar_produto, name='editar_produto'),
    path('admin/produtos/<int:produto_id>/excluir/', produtos_views.excluir_produto, name='excluir_produto'),

    # ============ URLs PARA FORNECEDORES ============
    path('admin/fornecedores/', produtos_views.lista_fornecedores, name='lista_fornecedores'),
    path('admin/fornecedores/criar/', produtos_views.criar_fornecedor, name='criar_fornecedor'),
    path('admin/fornecedores/<int:fornecedor_id>/editar/', produtos_views.editar_fornecedor, name='editar_fornecedor'),

    # ============ URLs PARA FATURAS ============
    path('admin/faturas/', views.admin_faturas_list, name='admin_faturas_list'),
    path('admin/faturas/nova/', views.admin_criar_fatura, name='admin_criar_fatura'),
    path('admin/faturas/nova/orcamento/<str:orcamento_numero>/', views.admin_criar_fatura_from_orcamento, name='admin_criar_fatura_from_orcamento'),
    path('admin/faturas/<str:numero>/', views.admin_fatura_detail, name='admin_fatura_detail'),
    path('admin/faturas/<str:numero>/editar/', views.admin_editar_fatura, name='admin_editar_fatura'),
    path('admin/faturas/<str:numero>/deletar/', views.admin_deletar_fatura, name='admin_deletar_fatura'),
    path('admin/faturas/<str:numero>/marcar-paga/', views.admin_marcar_fatura_paga, name='admin_marcar_fatura_paga'),
    path('admin/faturas/<str:numero>/pdf/', views.admin_fatura_pdf, name='admin_fatura_pdf'),

    # ============ URLs AJAX ============
    path('ajax/buscar-clientes/', views.buscar_clientes_ajax, name='buscar_clientes_ajax'),
    path('ajax/buscar-produtos/', views.buscar_produtos_ajax, name='buscar_produtos_ajax'),
    path('ajax/orcamento-items/<str:numero>/', views.ajax_orcamento_items, name='ajax_orcamento_items'),
]
