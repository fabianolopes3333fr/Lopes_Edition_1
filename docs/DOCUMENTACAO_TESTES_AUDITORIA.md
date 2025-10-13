# Sistema de Testes e Auditoria para Orçamentos - LopesPeinture

## 📋 Visão Geral

Este documento descreve o sistema completo de testes e auditoria criado para o app de orçamentos. O sistema inclui:

- **Testes de fluxo completo** do processo de orçamentos
- **Sistema de auditoria** para rastrear todas as alterações
- **Monitoramento automático** de atividades
- **Relatórios detalhados** de atividades e alterações
- **Scripts de execução** para automação

## 🚀 Arquivos Criados

### 1. Testes de Fluxo
- `orcamentos/tests/test_fluxo_orcamentos.py` - Testes completos do fluxo de orçamentos
- `orcamentos/tests/test_auditoria.py` - Testes específicos do sistema de auditoria

### 2. Sistema de Auditoria
- `orcamentos/auditoria.py` - Manager e models para auditoria
- `orcamentos/middleware.py` - Middleware para integração automática
- `orcamentos/migrations/0002_add_auditoria.py` - Migração para tabelas de auditoria

### 3. Monitoramento e Relatórios
- `orcamentos/monitor_auditoria.py` - Sistema de monitoramento e relatórios
- `orcamentos/config_auditoria.py` - Configurações do sistema

### 4. Scripts de Execução
- `run_orcamentos_tests.py` - Script principal para executar testes e relatórios

## 🔧 Como Usar

### 1. Configurar o Sistema

Adicione ao seu `settings.py`:

```python
# Importar configurações de auditoria
from orcamentos.config_auditoria import AUDITORIA_MIDDLEWARE, LOGGING_AUDITORIA, AUDITORIA_CONFIG

# Adicionar middleware
MIDDLEWARE = [
    # ... seus middlewares existentes ...
    'orcamentos.middleware.AuditoriaMiddleware',
]

# Configurações de auditoria
AUDITORIA = AUDITORIA_CONFIG

# Configurar logging
LOGGING = LOGGING_AUDITORIA
```

### 2. Executar Migrações

```bash
python manage.py makemigrations orcamentos
python manage.py migrate
```

### 3. Executar Testes

#### Execução Completa (Recomendado)
```bash
python run_orcamentos_tests.py --completo
```

#### Execução Específica
```bash
# Apenas testes de fluxo
python run_orcamentos_tests.py --fluxo

# Apenas testes unitários
python run_orcamentos_tests.py --unitarios

# Apenas relatórios de auditoria
python run_orcamentos_tests.py --auditoria

# Apenas verificação de integridade
python run_orcamentos_tests.py --integridade
```

### 4. Gerar Relatórios Manuais

```bash
# Relatório diário
python orcamentos/monitor_auditoria.py relatorio --tipo diario

# Relatório semanal
python orcamentos/monitor_auditoria.py relatorio --tipo semanal

# Salvar em arquivo específico
python orcamentos/monitor_auditoria.py relatorio --tipo diario --arquivo meu_relatorio.json
```

## 📊 Funcionalidades dos Testes

### Testes de Fluxo Completo

1. **Solicitação Pública de Orçamento**
   - Criação de solicitação por usuário não logado
   - Validação de dados obrigatórios
   - Envio de notificações

2. **Projetos de Cliente**
   - Criação de projeto por cliente logado
   - Solicitação de orçamento para projeto
   - Validação de permissões

3. **Elaboração de Orçamento (Admin)**
   - Criação de orçamento pelo admin
   - Adição de itens e cálculos automáticos
   - Envio para cliente

4. **Resposta do Cliente**
   - Aceitação de orçamento
   - Recusa com motivo
   - Atualização de status

5. **Validações e Segurança**
   - Controle de acesso
   - Validação de dados
   - Tratamento de erros

### Sistema de Auditoria

#### Registros Automáticos
- **Criação** de objetos (projetos, solicitações, orçamentos)
- **Edição** com comparação de campos alterados
- **Exclusão** com preservação dos dados
- **Visualização** de páginas importantes
- **Ações específicas** (envio, aprovação, rejeição)

#### Metadados Capturados
- Usuário que realizou a ação
- Timestamp preciso
- IP do cliente
- User agent do navegador
- ID da sessão
- Dados antes e depois da alteração

#### Relatórios Disponíveis
- **Diário**: Atividades das últimas 24h
- **Semanal**: Resumo da semana
- **Por usuário**: Atividades de um usuário específico
- **Por objeto**: Histórico completo de um objeto
- **Estatísticas**: Análises por período

## 🔍 Exemplos de Uso da Auditoria

### Registrar Ação Manualmente
```python
from orcamentos.auditoria import AuditoriaManager, TipoAcao

# Registrar visualização
AuditoriaManager.registrar_visualizacao(
    usuario=request.user,
    objeto=projeto,
    request=request
)

# Registrar envio de orçamento
AuditoriaManager.registrar_envio_orcamento(
    usuario=request.user,
    orcamento=orcamento,
    request=request
)
```

### Obter Histórico de um Objeto
```python
# Histórico de um projeto
historico = AuditoriaManager.obter_historico_objeto(projeto)

for log in historico:
    print(f"{log.timestamp} - {log.usuario} - {log.get_acao_display()}")
    if log.campos_alterados:
        print(f"Alterações: {log.resumo_alteracao}")
```

### Atividades de um Usuário
```python
# Atividades dos últimos 30 dias
atividades = AuditoriaManager.obter_atividades_usuario(usuario, dias=30)

for atividade in atividades:
    print(f"{atividade.timestamp} - {atividade.descricao}")
```

## 📈 Monitoramento Contínuo

### Script de Monitoramento Diário
```bash
# Adicionar ao crontab para execução diária às 6h
0 6 * * * cd /path/to/project && python orcamentos/monitor_auditoria.py
```

### Alertas e Notificações
O sistema pode ser configurado para enviar notificações:
- Email para admins em caso de problemas
- Webhooks para Slack/Discord
- Relatórios automáticos por email

## 🛡️ Segurança e Performance

### Medidas de Segurança
- Campos sensíveis são filtrados dos logs
- IPs e user agents são registrados para auditoria
- Logs podem ser criptografados (configurável)
- Backup automático dos logs de auditoria

### Otimizações de Performance
- Índices otimizados nas tabelas de auditoria
- Paginação automática em consultas grandes
- Limpeza automática de logs antigos
- Compressão de arquivos de log

### Configurações de Retenção
- Logs mantidos por 365 dias (configurável)
- Compressão automática após 30 dias
- Backup automático antes da exclusão

## 🎯 Casos de Uso Práticos

### 1. Investigar Problema de Orçamento
```python
# Buscar histórico de um orçamento específico
orcamento = Orcamento.objects.get(numero='OR2025xxxxx')
historico = AuditoriaManager.obter_historico_objeto(orcamento)

# Ver todas as alterações
for log in historico:
    print(f"{log.timestamp}: {log.descricao}")
    if log.campos_alterados:
        for campo, dados in log.campos_alterados.items():
            print(f"  {campo}: {dados['anterior']} → {dados['novo']}")
```

### 2. Auditoria de Usuário
```python
# Ver atividades suspeitas de um usuário
usuario = User.objects.get(email='usuario@email.com')
atividades = AuditoriaManager.obter_atividades_usuario(usuario, dias=7)

# Filtrar apenas alterações
alteracoes = [a for a in atividades if a.acao == TipoAcao.EDICAO]
```

### 3. Relatório Gerencial
```python
from datetime import datetime, timedelta

# Estatísticas do mês
inicio_mes = datetime.now().replace(day=1)
fim_mes = datetime.now()

stats = AuditoriaManager.obter_estatisticas_periodo(inicio_mes, fim_mes)
print(f"Total de ações no mês: {stats['total_acoes']}")
print(f"Usuários mais ativos: {stats['usuarios_mais_ativos']}")
```

## 🔄 Fluxo de Testes Automatizados

### 1. Testes de Integração
Os testes simulam um fluxo completo:
1. Cliente cria projeto
2. Solicita orçamento
3. Admin elabora orçamento
4. Adiciona itens e calcula totais
5. Envia para cliente
6. Cliente aceita/recusa

### 2. Testes de Auditoria
Verificam se todas as ações são registradas:
- Criação, edição e exclusão de objetos
- Metadados da requisição
- Detecção de alterações
- Performance das consultas

### 3. Testes de Performance
- Tempo de resposta das páginas
- Eficiência das consultas de banco
- Memory usage durante testes
- Concorrência de usuários

## 📋 Relatórios Gerados

### Relatório Diário
```json
{
  "data": "2025-10-04",
  "total_atividades": 25,
  "atividades_por_tipo": {
    "Création": 8,
    "Modification": 12,
    "Consultation": 5
  },
  "usuarios_ativos": ["João Silva", "Admin Sistema"],
  "modelos_afetados": {
    "projeto": 5,
    "solicitacaoorcamento": 3,
    "orcamento": 2
  }
}
```

### Relatório Semanal
```json
{
  "periodo": "2025-09-28 - 2025-10-04",
  "total_atividades": 156,
  "usuarios_mais_ativos": {
    "Admin Sistema": 89,
    "João Silva": 45,
    "Maria Santos": 22
  },
  "estatisticas_diarias": {
    "2025-10-01": 20,
    "2025-10-02": 35,
    "2025-10-03": 42,
    "2025-10-04": 25
  }
}
```

## 🚨 Solução de Problemas

### Problema: Testes Falhando
1. Verificar se migrações estão aplicadas
2. Verificar configurações no settings.py
3. Executar `python manage.py check`
4. Ver logs em `logs/auditoria_orcamentos.log`

### Problema: Auditoria Não Registrando
1. Verificar se middleware está ativo
2. Verificar permissões da pasta `logs/`
3. Verificar configuração `AUDITORIA_HABILITADA`
4. Testar manualmente com `AuditoriaManager`

### Problema: Performance Lenta
1. Verificar índices na tabela `LogAuditoria`
2. Configurar limpeza automática de logs
3. Ajustar `LIMITE_REGISTROS_CONSULTA`
4. Habilitar cache do Django

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs em `logs/`
2. Executar testes de diagnóstico
3. Verificar documentação técnica
4. Contatar equipe de desenvolvimento

---

**Sistema criado por GitHub Copilot para LopesPeinture**  
*Versão 1.0 - Outubro 2025*
