"""
Script para diagnosticar problema com URLs retornando 404
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.urls import resolve, reverse, Resolver404
from django.test import Client
from django.contrib.auth import get_user_model
from orcamentos.models import Orcamento, ItemOrcamento, SolicitacaoOrcamento, Projeto
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=" * 80)
print("DIAGNÓSTICO DE URLS - TESTE 404")
print("=" * 80)

# Limpar dados anteriores
User.objects.filter(username__in=['test_url_admin', 'test_url_cliente']).delete()

# Criar usuários
admin = User.objects.create_user(
    username='test_url_admin',
    email='admin@test.com',
    password='senha123',
    is_staff=True,
    is_superuser=True,
    account_type='ADMIN'
)

cliente = User.objects.create_user(
    username='test_url_cliente',
    email='cliente@test.com',
    password='senha123',
    account_type='CLIENT'
)

# Criar projeto e solicitação
projeto = Projeto.objects.create(
    cliente=cliente,
    titulo='Projeto Debug',
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

# Criar orçamento
orc = Orcamento.objects.create(
    solicitacao=solicitacao,
    elaborado_por=admin,
    titulo='Devis Debug',
    prazo_execucao=30,
    validade_orcamento=timezone.now().date() + timedelta(days=30),
    status='aceito'
)

ItemOrcamento.objects.create(
    orcamento=orc,
    descricao='Item teste',
    quantidade=Decimal('10.00'),
    preco_unitario_ht=Decimal('100.00'),
    taxa_tva='20'
)

orc.calcular_totais()

print(f"\n✓ Orçamento criado: {orc.numero}")
print(f"  - ID: {orc.id}")
print(f"  - Tipo do numero: {type(orc.numero)}")

# Testar resolução de URLs
print("\n" + "=" * 80)
print("TESTANDO RESOLUÇÃO DE URLS")
print("=" * 80)

urls_to_test = [
    ('admin_orcamento_detail', {'numero': orc.numero}),
    ('admin_criar_fatura_from_orcamento', {'orcamento_numero': orc.numero}),
    ('admin_orcamento_pdf', {'numero': orc.numero}),
]

for url_name, kwargs in urls_to_test:
    print(f"\n{url_name}:")
    try:
        url = reverse(f'orcamentos:{url_name}', kwargs=kwargs)
        print(f"  ✓ Reverse OK: {url}")
        
        # Tentar resolver de volta
        try:
            match = resolve(url)
            print(f"  ✓ Resolve OK: view={match.view_name}")
        except Resolver404 as e:
            print(f"  ✗ Resolve FALHOU: {e}")
            
    except Exception as e:
        print(f"  ✗ Reverse FALHOU: {e}")

# Testar acesso com Client
print("\n" + "=" * 80)
print("TESTANDO ACESSO COM CLIENT")
print("=" * 80)

client = Client()

# Teste SEM login
print(f"\n1. Testando SEM login:")
url = f'/orcamentos/admin/orcamentos/{orc.numero}/'
print(f"   URL: {url}")
response = client.get(url)
print(f"   Status: {response.status_code}")
if response.status_code == 302:
    print(f"   Redireciona para: {response.url}")

# Teste COM login (sem força)
print(f"\n2. Testando COM login (login normal):")
logged_in = client.login(username='test_url_admin', password='senha123')
print(f"   Login sucesso: {logged_in}")
response = client.get(url)
print(f"   Status: {response.status_code}")
if response.status_code == 302:
    print(f"   Redireciona para: {response.url}")

# Teste COM force_login
print(f"\n3. Testando COM force_login:")
client = Client()
client.force_login(admin)
print(f"   Force login executado")
print(f"   Admin.is_staff: {admin.is_staff}")
print(f"   Admin.is_superuser: {admin.is_superuser}")
print(f"   Admin.is_authenticated: {admin.is_authenticated}")

response = client.get(url)
print(f"   Status: {response.status_code}")
if response.status_code == 302:
    print(f"   Redireciona para: {response.url}")
elif response.status_code == 404:
    print(f"   ✗ 404 - Não encontrado!")
    print(f"   Tentando URL alternativa sem barra final:")
    url_sem_barra = url.rstrip('/')
    response2 = client.get(url_sem_barra)
    print(f"   Status sem barra: {response2.status_code}")

# Testar URL de fatura
print(f"\n4. Testando URL de criação de fatura:")
url_fatura = f'/orcamentos/admin/faturas/nova/orcamento/{orc.numero}/'
print(f"   URL: {url_fatura}")
response = client.get(url_fatura)
print(f"   Status: {response.status_code}")
if response.status_code == 404:
    print(f"   ✗ 404 - Verificando variações:")
    # Testar sem barra final
    response2 = client.get(url_fatura.rstrip('/'))
    print(f"   Sem barra final: {response2.status_code}")

# Verificar se a view existe
print("\n" + "=" * 80)
print("VERIFICANDO VIEWS")
print("=" * 80)

from orcamentos import views, views_faturas

print(f"\n✓ views.admin_orcamento_detail existe: {hasattr(views, 'admin_orcamento_detail')}")
print(f"✓ views_faturas.admin_criar_fatura_from_orcamento existe: {hasattr(views_faturas, 'admin_criar_fatura_from_orcamento')}")
print(f"✓ views.admin_orcamento_pdf existe: {hasattr(views, 'admin_orcamento_pdf')}")

# Listar todas as URLs do app orcamentos
print("\n" + "=" * 80)
print("URLS REGISTRADAS NO APP ORCAMENTOS")
print("=" * 80)

from django.urls import get_resolver
resolver = get_resolver()

print("\nBuscando padrões 'orcamentos:'...")
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'namespace') and pattern.namespace == 'orcamentos':
        print(f"\nNamespace: {pattern.namespace}")
        for p in pattern.url_patterns:
            if hasattr(p, 'name'):
                print(f"  - {p.name}: {p.pattern}")

# Limpar
print("\n" + "=" * 80)
print("LIMPANDO DADOS DE TESTE")
print("=" * 80)
orc.delete()
solicitacao.delete()
projeto.delete()
admin.delete()
cliente.delete()
print("✓ Dados limpos")

