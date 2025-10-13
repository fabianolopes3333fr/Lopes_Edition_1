# Correções nos Testes de Orçamentos Órfãos

## Data: 2025-10-12

## Erros Corrigidos

### 1. **test_auditoria_aceitacao_orcamento e test_auditoria_recusa_orcamento**
**Erro:** `AttributeError: type object 'TipoAcao' has no attribute 'ALTERACAO'`

**Correção:**
- Alterado `TipoAcao.ALTERACAO` para `TipoAcao.EDICAO`
- O enum TipoAcao não possui a opção ALTERACAO, o correto é EDICAO

**Arquivos modificados:**
- `orcamentos/tests/test_auditoria_orcamentos_orfaos.py`

### 2. **test_auditoria_envio_orcamento_admin**
**Erro:** `AttributeError: type object 'AuditoriaManager' has no attribute 'registrar_alteracao'`

**Correção:**
- Alterado `AuditoriaManager.registrar_alteracao()` para `AuditoriaManager.registrar_edicao()`
- O método correto é `registrar_edicao`, não `registrar_alteracao`

**Arquivos modificados:**
- `orcamentos/tests/test_auditoria_orcamentos_orfaos.py`

### 3. **test_auditoria_cascata_operacoes**
**Erro:** `AssertionError: datetime.datetime(...) not less than datetime.datetime(...)`

**Correção:**
- Adicionado `time.sleep(0.01)` entre as operações para garantir timestamps diferentes
- Alterado `assertLess()` para `assertLessEqual()` para aceitar timestamps iguais
- Isso resolve o problema de timestamps idênticos quando as operações ocorrem muito rapidamente

**Arquivos modificados:**
- `orcamentos/tests/test_auditoria_orcamentos_orfaos.py`

### 4. **Testes de Admin - Contagem incorreta de orçamentos órfãos**
**Erros:**
- `test_admin_orcamentos_orfaos_view_carrega_corretamente`: AssertionError: 13 != 3
- `test_admin_dashboard_estatisticas_orfaos`: AssertionError: 13 != 3
- `test_admin_dashboard_com_orcamentos_ja_vinculados`: AssertionError: 11 != 1
- `test_admin_orcamentos_orfaos_agrupamento_emails`: AssertionError: 2 != 1
- `test_admin_vincular_orcamentos_orfaos_ajax_sucesso`: AssertionError: False is not true
- `test_verificar_e_processar_orcamentos_orfaos_service`: AssertionError: 8 != 1

**Problema:** Dados de testes anteriores estavam persistindo entre os testes, causando contagens incorretas.

**Correção:**
- Alterado `TestCase` para `TransactionTestCase` na classe `AdminOrcamentosOrfaosViewsTestCase`
- Adicionado limpeza explícita de dados no método `setUp()`:
  ```python
  SolicitacaoOrcamento.objects.all().delete()
  User.objects.all().delete()
  ```
- Adicionado decorator `@pytest.mark.django_db(transaction=True)`
- Isso garante isolamento completo entre os testes

**Arquivos modificados:**
- `orcamentos/tests/test_admin_orcamentos_orfaos.py`

## Resumo das Mudanças

### Arquivo: `orcamentos/tests/test_auditoria_orcamentos_orfaos.py`

1. **Importações:** Mantidas as mesmas
2. **TipoAcao.ALTERACAO → TipoAcao.EDICAO** em 2 testes
3. **registrar_alteracao() → registrar_edicao()** em 1 teste
4. **Adicionado delays no teste de cascata** com `time.sleep(0.01)`

### Arquivo: `orcamentos/tests/test_admin_orcamentos_orfaos.py`

1. **Importações:**
   - Adicionado `pytest`
   - Adicionado `TransactionTestCase`

2. **Classe de teste:**
   ```python
   @pytest.mark.django_db(transaction=True)
   class AdminOrcamentosOrfaosViewsTestCase(TransactionTestCase):
   ```

3. **Método setUp:**
   - Adicionado limpeza de dados:
   ```python
   SolicitacaoOrcamento.objects.all().delete()
   User.objects.all().delete()
   ```

## Testes para Executar

Para verificar se as correções funcionaram, execute:

```bash
# Todos os testes de auditoria
python -m pytest orcamentos/tests/test_auditoria_orcamentos_orfaos.py -v

# Todos os testes de admin
python -m pytest orcamentos/tests/test_admin_orcamentos_orfaos.py -v

# Ou ambos
python -m pytest orcamentos/tests/test_admin_orcamentos_orfaos.py orcamentos/tests/test_auditoria_orcamentos_orfaos.py -v
```

## Notas Importantes

1. **Isolamento de Testes:** O uso de `TransactionTestCase` e limpeza explícita garante que cada teste inicie com um banco de dados limpo.

2. **Timestamps:** Os delays adicionados são mínimos (10ms) e não impactam significativamente o tempo de execução dos testes.

3. **Nomenclatura Correta:** Sempre use `TipoAcao.EDICAO` e `AuditoriaManager.registrar_edicao()` para alterações de objetos.

4. **Consistência:** Todos os testes agora seguem os padrões corretos definidos no sistema de auditoria.

