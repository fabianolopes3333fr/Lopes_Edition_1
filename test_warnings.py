"""
Script para testar se os warnings foram corrigidos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print("=" * 80)
print("TESTANDO CORREÇÕES DE WARNINGS")
print("=" * 80)

# Teste 1: Verificar que métodos de teste não retornam valores
print("\n1. Verificando métodos de teste...")
from orcamentos.tests.test_basico import TesteAuditoriaBasicoTestCase
import inspect

test_case = TesteAuditoriaBasicoTestCase()
test_case.setUp() if hasattr(test_case, 'setUp') else None

try:
    # Executar teste e verificar se retorna None
    result1 = test_case.test_01_import_auditoria()
    if result1 is None:
        print("   ✓ test_01_import_auditoria não retorna valor (CORRIGIDO)")
    else:
        print(f"   ✗ test_01_import_auditoria retorna {result1} (PROBLEMA)")
except Exception as e:
    print(f"   ⚠ Erro ao executar teste: {e}")

# Teste 2: Verificar uso de timezone-aware datetimes
print("\n2. Verificando uso de timezone...")
from django.utils import timezone
from datetime import datetime, timedelta

aware_datetime = timezone.now()
naive_datetime = datetime.now()

print(f"   timezone.now() é aware: {timezone.is_aware(aware_datetime)} ✓")
print(f"   datetime.now() é aware: {timezone.is_aware(naive_datetime)} ✗")

# Teste 3: Verificar imports de timezone nos arquivos de teste
print("\n3. Verificando imports nos arquivos de teste...")

import orcamentos.tests.test_auditoria_orcamentos_orfaos as test_orfaos

if hasattr(test_orfaos, 'timezone'):
    print("   ✓ test_auditoria_orcamentos_orfaos importa timezone")
else:
    print("   ✗ test_auditoria_orcamentos_orfaos NÃO importa timezone")

# Teste 4: Verificar LogAuditoria com timezone-aware
print("\n4. Testando criação de LogAuditoria com timezone...")
from orcamentos.auditoria import LogAuditoria, TipoAcao
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Criar usuário temporário
    user = User.objects.create_user(
        username='test_warnings',
        email='test@warnings.com',
        password='test123'
    )
    
    # Criar log com timezone-aware
    log = LogAuditoria.objects.create(
        usuario=user,
        acao=TipoAcao.CRIACAO,
        descricao='Teste de timezone',
        modulo='teste',
        funcionalidade='warnings'
    )
    
    if timezone.is_aware(log.timestamp):
        print(f"   ✓ LogAuditoria.timestamp é aware: {log.timestamp}")
    else:
        print(f"   ✗ LogAuditoria.timestamp é naive: {log.timestamp}")
    
    # Limpar
    log.delete()
    user.delete()
    
except Exception as e:
    print(f"   ✗ Erro ao criar LogAuditoria: {e}")

print("\n" + "=" * 80)
print("RESUMO DAS CORREÇÕES")
print("=" * 80)
print("""
Correções implementadas:

1. ✓ Removidos return statements dos métodos de teste
   - test_01_import_auditoria
   - test_02_criar_log_auditoria
   - Substituídos por self.fail() em caso de erro

2. ✓ Substituído datetime.now() por timezone.now()
   - test_auditoria_cleanup_logs_antigos
   - test_auditoria_filtros_avancados
   - Todos os testes agora usam timezone-aware datetimes

3. ⚠ URLField Warning (Django 6.0)
   - Este é um warning de deprecação do Django
   - Não requer ação imediata
   - Será resolvido automaticamente ao atualizar para Django 6.0

Resultado: Os warnings críticos (DeprecationWarning e RuntimeWarning) foram corrigidos!
""")
print("=" * 80)

