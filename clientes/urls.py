from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('criar/', views.criar_cliente, name='criar_cliente'),
    path('<int:pk>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:pk>/deletar/', views.deletar_cliente, name='deletar_cliente'),
    path('<int:pk>/converter/', views.converter_prospect_cliente, name='converter_prospect_cliente'),
    path('ajax/copiar-endereco/', views.copiar_endereco_principal, name='copiar_endereco_principal'),
]
