from django.urls import path
from . import views

app_name = 'orcamentos'

urlpatterns = [
    # URLs Públicas (sem login)
    path('solicitar/', views.solicitar_orcamento_publico, name='solicitar_publico'),
    path('sucesso/<str:numero>/', views.sucesso_solicitacao, name='sucesso_solicitacao'),

    # URLs para Clientes
    path('meus-projetos/', views.cliente_projetos, name='cliente_projetos'),
    path('projeto/criar/', views.cliente_criar_projeto, name='cliente_criar_projeto'),
    path('projeto/<uuid:uuid>/', views.cliente_projeto_detail, name='cliente_projeto_detail'),
    path('projeto/<uuid:uuid>/editar/', views.cliente_editar_projeto, name='cliente_editar_projeto'),
    path('projeto/<uuid:uuid>/excluir/', views.cliente_excluir_projeto, name='cliente_excluir_projeto'),
    path('projeto/<uuid:uuid>/solicitar-orcamento/', views.cliente_solicitar_orcamento_projeto, name='cliente_solicitar_orcamento'),
    path('meus-orcamentos/', views.cliente_orcamentos, name='cliente_orcamentos'),

    # URLs para visualizar e responder orçamentos (cliente)
    path('devis/<str:numero>/', views.cliente_devis_detail, name='cliente_devis_detail'),
    path('devis/<str:numero>/accepter/', views.cliente_devis_accepter, name='cliente_devis_accepter'),
    path('devis/<str:numero>/refuser/', views.cliente_devis_refuser, name='cliente_devis_refuser'),
    path('devis/<str:numero>/pdf/', views.cliente_devis_pdf, name='cliente_devis_pdf'),

    # URLs para Administradores
    path('admin/solicitacoes/', views.admin_solicitacoes, name='admin_solicitacoes'),
    path('admin/solicitacao/<str:numero>/', views.admin_solicitacao_detail, name='admin_solicitacao_detail'),
    path('admin/solicitacao/<str:numero>/criar-orcamento/', views.admin_criar_orcamento, name='admin_criar_orcamento'),
    path('admin/orcamento/<str:numero>/', views.admin_orcamento_detail, name='admin_orcamento_detail'),
    path('admin/orcamento/<str:numero>/editar/', views.admin_editar_orcamento, name='admin_editar_orcamento'),
    path('admin/orcamento/<str:numero>/enviar/', views.admin_enviar_orcamento, name='admin_enviar_orcamento'),
    path('admin/orcamento/<str:numero>/pdf/', views.admin_orcamento_pdf, name='admin_orcamento_pdf'),

    # URLs AJAX
    path('projeto/<uuid:uuid>/upload-anexo/', views.upload_anexo_projeto, name='upload_anexo_projeto'),
    path('projeto/<uuid:uuid>/anexo/<int:anexo_id>/excluir/', views.excluir_anexo_projeto, name='excluir_anexo_projeto'),
]
