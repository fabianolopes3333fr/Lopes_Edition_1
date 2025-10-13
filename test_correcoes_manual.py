"""
Script de teste simplificado para verificar as correções
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Agora importar os modelos
from django.test import Client
from django.contrib.auth import get_user_model
from orcamentos.models import Orcamento, ItemOrcamento, AcompteOrcamento, SolicitacaoOrcamento, Projeto
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=" * 80)
print("TESTE DE CORREÇÕES - ACOMPTES")
print("=" * 80)

# Limpar dados de teste anteriores
print("\n1. Limpando dados de teste anteriores...")
User.objects.filter(username__in=['admin_test_manual', 'cliente_test_manual']).delete()

# Criar usuários
print("\n2. Criando usuários de teste...")
admin = User.objects.create_user(
    username='admin_test_manual',
    email='admin@test.com',
    password='senha123',
    first_name='Admin',
    last_name='Teste',
    is_staff=True,
    is_superuser=True,
    account_type='ADMIN'
)
print(f"   Admin criado: {admin.username}, is_staff={admin.is_staff}, is_authenticated={admin.is_authenticated}")

cliente = User.objects.create_user(
    username='cliente_test_manual',
    email='cliente@test.com',
    password='senha123',
    first_name='Cliente',
    last_name='Teste',
    account_type='CLIENT'
)
print(f"   Cliente criado: {cliente.username}")

# Criar projeto e solicitação
print("\n3. Criando projeto e solicitação...")
projeto = Projeto.objects.create(
    cliente=cliente,
    titulo='Projeto Teste Manual',
    tipo_servico='pintura_interior',
    urgencia='media'
)

solicitacao = SolicitacaoOrcamento.objects.create(
    cliente=cliente,
    projeto=projeto,
    tipo_servico='pintura_interior',
    urgencia='media',
    nome_solicitante='Cliente Teste',
    email_solicitante='cliente@test.com',
    telefone_solicitante='+33123456789',
    descricao_servico='Teste'
)
print(f"   Solicitação criada: {solicitacao.numero}")

# Criar orçamento
print("\n4. Criando orçamento com itens...")
orc = Orcamento.objects.create(
    solicitacao=solicitacao,
    elaborado_por=admin,
    titulo='Devis Teste',
    prazo_execucao=30,
    validade_orcamento=timezone.now().date() + timedelta(days=30),
    status='aceito'
)

ItemOrcamento.objects.create(
    orcamento=orc,
    referencia='PINT001',
    descricao='Peinture murs',
    unidade='m2',
    atividade='service',
    quantidade=Decimal('50.00'),
    preco_unitario_ht=Decimal('25.00'),
    taxa_tva='20',
    remise_percentual=Decimal('0.00')
)

ItemOrcamento.objects.create(
    orcamento=orc,
    referencia='PINT002',
    descricao='Peinture plafond',
    unidade='m2',
    atividade='service',
    quantidade=Decimal('30.00'),
    preco_unitario_ht=Decimal('30.00'),
    taxa_tva='20',
    remise_percentual=Decimal('0.00')
)

orc.calcular_totais()
orc.refresh_from_db()

print(f"   Orçamento criado: {orc.numero}")
print(f"   Total HT: {orc.total}")
print(f"   Total TTC: {orc.total_ttc}")
print(f"   TVA: {orc.valor_tva}")

# Criar acompte
print("\n5. Criando acompte de 30%...")
acompte = AcompteOrcamento.objects.create(
    orcamento=orc,
    criado_por=admin,
    tipo='inicial',
    descricao='Acompte 30%',
    percentual=Decimal('30.00'),
    data_vencimento=timezone.now().date(),
    status='pago'
)
acompte.calcular_valores()
acompte.save()

print(f"   Acompte criado: {acompte.numero}")
print(f"   Valor HT: {acompte.valor_ht}")
print(f"   Valor TTC: {acompte.valor_ttc}")
print(f"   Status: {acompte.status}")

orc.refresh_from_db()
print(f"\n6. Verificando totais do orçamento:")
print(f"   Total acomptes pagos: {orc.total_acomptes_pagos}")
print(f"   Saldo em aberto: {orc.saldo_em_aberto}")

# Testar acesso às URLs
print("\n7. Testando acesso às URLs com client autenticado...")
client = Client()
client.force_login(admin)

# Teste 1: admin_orcamento_detail
url1 = f'/orcamentos/admin/orcamentos/{orc.numero}/'
print(f"\n   Testando URL: {url1}")
response1 = client.get(url1)
print(f"   Status code: {response1.status_code}")
if response1.status_code == 302:
    print(f"   Redirecionado para: {response1.url}")
    response1 = client.get(response1.url, follow=True)
    print(f"   Status após seguir: {response1.status_code}")

# Teste 2: admin_criar_fatura_from_orcamento
url2 = f'/orcamentos/admin/faturas/nova/orcamento/{orc.numero}/'
print(f"\n   Testando URL: {url2}")
response2 = client.get(url2)
print(f"   Status code: {response2.status_code}")
if response2.status_code == 302:
    print(f"   Redirecionado para: {response2.url}")
    response2 = client.get(response2.url, follow=True)
    print(f"   Status após seguir: {response2.status_code}")

# Teste 3: admin_orcamento_pdf
url3 = f'/orcamentos/admin/orcamentos/{orc.numero}/pdf/'
print(f"\n   Testando URL: {url3}")
response3 = client.get(url3)
print(f"   Status code: {response3.status_code}")
if response3.status_code == 302:
    print(f"   Redirecionado para: {response3.url}")

print("\n" + "=" * 80)
print("TESTE CONCLUÍDO")
print("=" * 80)

# Limpar
print("\nLimpando dados de teste...")
orc.delete()
solicitacao.delete()
projeto.delete()
admin.delete()
cliente.delete()
print("Dados limpos com sucesso!")

