from django.urls import path, include
from . import views
from . import notification_views
from . import produtos_views

app_name = 'orcamentos'

urlpatterns = [
    # URLs Públicas (sem login)
    path('demande/', views.solicitar_orcamento_publico, name='solicitar_publico'),
    path('succès/<str:numero>/', views.sucesso_solicitacao, name='sucesso_solicitacao'),

    # URLs para Clientes
    path('mes-projets/', views.cliente_projetos, name='cliente_projetos'),
    path('mes-projets/criar/', views.cliente_criar_projeto, name='cliente_criar_projeto'),
    path('projets/<uuid:uuid>/', views.cliente_projeto_detail, name='cliente_projeto_detail'),
    path('projets/<uuid:uuid>/editar/', views.cliente_editar_projeto, name='cliente_editar_projeto'),
    path('projets/<uuid:uuid>/excluir/', views.cliente_excluir_projeto, name='cliente_excluir_projeto'),
    path('projets/<uuid:uuid>/solicitar-orcamento/', views.cliente_solicitar_orcamento_projeto, name='cliente_solicitar_orcamento'),
    path('mes-devis/', views.cliente_orcamentos, name='cliente_orcamentos'),

    # URLs para visualizar e responder orçamentos (cliente)
    path('devis/<str:numero>/', views.cliente_devis_detail, name='cliente_devis_detail'),
    path('devis/<str:numero>/accepter/', views.cliente_devis_accepter, name='cliente_devis_accepter'),
    path('devis/<str:numero>/refuser/', views.cliente_devis_refuser, name='cliente_devis_refuser'),
    path('devis/<str:numero>/pdf/', views.cliente_devis_pdf, name='cliente_devis_pdf'),

    # URLs para anexos de projetos
    path('projets/<uuid:uuid>/upload-anexo/', views.upload_anexo_projeto, name='upload_anexo_projeto'),
    path('projets/<uuid:uuid>/anexo/<int:anexo_id>/excluir/', views.excluir_anexo_projeto, name='excluir_anexo_projeto'),

    # URLs para Gestão de Produtos
    path('admin/produits/créer/', produtos_views.criar_produto, name='criar_produto'),
    path('admin/produits/<int:produto_id>/editar/', produtos_views.editar_produto, name='editar_produto'),
    path('admin/produits/<int:produto_id>/excluir/', produtos_views.excluir_produto, name='excluir_produto'),
    path('admin/produits/buscar-ajax/', produtos_views.buscar_produtos_ajax, name='buscar_produtos_ajax'),
    path('admin/produits/<int:produto_id>/detalhes-ajax/', produtos_views.detalhes_produto_ajax, name='detalhes_produto_ajax'),
    path('admin/produits/', produtos_views.lista_produtos, name='lista_produtos'),

    # URLs para Gestão de Fornecedores
    path('admin/fournisseurs/', produtos_views.lista_fornecedores, name='lista_fornecedores'),
    path('admin/fournisseurs/créer/', produtos_views.criar_fornecedor, name='criar_fornecedor'),
    path('admin/fournisseurs/<int:fornecedor_id>/editar/', produtos_views.editar_fornecedor, name='editar_fornecedor'),

    # URLs para Administradores (apenas as que existem)
    path('admin/demandes/', views.admin_solicitacoes, name='admin_solicitacoes'),
    path('admin/demandes/<str:numero>/', views.admin_solicitacao_detail, name='admin_solicitacao_detail'),
    path('admin/préparer-le-budget/<str:numero>/', views.admin_elaborar_orcamento, name='admin_elaborar_orcamento'),
    path('admin/criar-devis-cliente/<int:cliente_id>/', views.admin_criar_orcamento_cliente, name='admin_criar_orcamento_cliente'),
    path('admin/mes-devis/', views.admin_orcamentos, name='admin_orcamentos'),
    path('admin/devis/<str:numero>/', views.admin_orcamento_detail, name='admin_orcamento_detail'),
    path('admin/devis/<str:numero>/editar/', views.admin_editar_orcamento, name='admin_editar_orcamento'),
    path('admin/devis/<str:numero>/enviar/', views.admin_enviar_orcamento, name='admin_enviar_orcamento'),
    path('admin/devis/<str:numero>/pdf/', views.admin_orcamento_pdf, name='admin_orcamento_pdf'),

    # URLs para notificações (apenas se existirem)
    # path('notificacoes/', notification_views.lista_notificacoes, name='lista_notificacoes'),

    # AJAX (apenas as que existem)
    # path('ajax/calcular-item/', views.calcular_item_ajax, name='calcular_item_ajax'),
]
