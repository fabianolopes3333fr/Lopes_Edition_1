# Como Excluir Todas as Migrações de Uma Vez

## 🎯 Opções Disponíveis

Criei **3 formas diferentes** para você excluir todas as migrações:

---

## ✅ **OPÇÃO 1: Script Python (Recomendado)**

### Vantagens:
- ✓ Multiplataforma (funciona em Windows, Linux, Mac)
- ✓ Interface colorida e clara
- ✓ Pede confirmação antes de deletar
- ✓ Mostra progresso detalhado

### Como usar:
```bash
python limpar_migracoes.py
```

### O que ele faz:
1. Pede confirmação (você precisa digitar "SIM")
2. Deleta todos os arquivos de migração (exceto `__init__.py`)
3. Deleta pastas `__pycache__` das migrações
4. Deleta o banco de dados `db.sqlite3`
5. Mostra os próximos passos

---

## ✅ **OPÇÃO 2: Script Batch Windows (Mais Rápido)**

### Vantagens:
- ✓ Específico para Windows
- ✓ Execução com duplo clique
- ✓ Pode executar os comandos Django automaticamente
- ✓ Interface colorida

### Como usar:

**Forma 1 - Duplo clique:**
1. Dê duplo clique no arquivo `limpar_migracoes.bat`
2. Digite "SIM" para confirmar
3. Escolha se quer executar os comandos Django automaticamente

**Forma 2 - Terminal:**
```cmd
limpar_migracoes.bat
```

---

## ✅ **OPÇÃO 3: Comandos Manuais (Linha por Linha)**

Se preferir fazer manualmente:

### Windows (CMD):
```cmd
REM Deletar migrações de cada app (mantém __init__.py)
for %f in (accounts\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (blog\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (clientes\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (contato\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (home\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (orcamentos\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (profiles\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"
for %f in (projetos\migrations\*.py) do @if not "%~nf"=="__init__" del "%f"

REM Deletar __pycache__
rmdir /s /q accounts\migrations\__pycache__
rmdir /s /q blog\migrations\__pycache__
rmdir /s /q clientes\migrations\__pycache__
rmdir /s /q contato\migrations\__pycache__
rmdir /s /q home\migrations\__pycache__
rmdir /s /q orcamentos\migrations\__pycache__
rmdir /s /q profiles\migrations\__pycache__
rmdir /s /q projetos\migrations\__pycache__

REM Deletar banco de dados
del db.sqlite3
```

### Linux/Mac (Bash):
```bash
# Deletar migrações (mantém __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
find . -path "*/migrations/__pycache__" -type d -exec rm -rf {} +

# Deletar banco de dados
rm db.sqlite3
```

---

## 📋 Depois de Limpar as Migrações

### **Passo 1: Criar novas migrações**
```bash
python manage.py makemigrations
```

### **Passo 2: Aplicar migrações**
```bash
python manage.py migrate
```

### **Passo 3: Criar superusuário**
```bash
python manage.py createsuperuser
```

### **Passo 4 (Opcional): Carregar dados iniciais**
Se você tiver fixtures:
```bash
python manage.py loaddata initial_data.json
```

---

## ⚠️ **IMPORTANTE - LEIA ANTES DE EXECUTAR**

### O que será deletado:
- ✗ **Todos os arquivos de migração** (exceto `__init__.py`)
- ✗ **Banco de dados completo** (`db.sqlite3`)
- ✗ **Todos os dados de usuários, posts, orçamentos, etc.**
- ✗ **Cache Python** das migrações (`__pycache__`)

### O que NÃO será deletado:
- ✓ Arquivos `__init__.py` (necessários para Python reconhecer a pasta)
- ✓ Código fonte dos seus apps
- ✓ Arquivos de configuração
- ✓ Arquivos de media/static

### Quando usar isso:
- ✓ Quando as migrações estão conflitadas
- ✓ Quando você quer começar do zero
- ✓ No ambiente de desenvolvimento (NUNCA em produção!)
- ✓ Quando você tem backup dos dados importantes

### Quando NÃO usar:
- ✗ **NUNCA em produção com dados reais!**
- ✗ Quando você não tem backup dos dados
- ✗ Se outras pessoas estão trabalhando no mesmo banco

---

## 🔄 **Fluxo Completo Recomendado**

```bash
# 1. Fazer backup (se necessário)
python manage.py dumpdata > backup.json

# 2. Limpar migrações (escolha uma opção)
python limpar_migracoes.py
# OU
limpar_migracoes.bat

# 3. Criar novas migrações
python manage.py makemigrations

# 4. Aplicar migrações
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Restaurar dados (se tiver backup)
python manage.py loaddata backup.json
```

---

## 🐛 **Resolução de Problemas**

### Erro: "Arquivo em uso"
**Problema:** Algum processo está usando o banco de dados

**Solução:**
1. Feche o servidor Django (`Ctrl+C`)
2. Feche qualquer programa que esteja acessando o banco (DB Browser, etc.)
3. Execute o script novamente

### Erro: "Permissão negada"
**Problema:** Sem permissão para deletar arquivos

**Solução:**
1. Execute o terminal como administrador
2. Verifique se os arquivos não estão em uso

### Erro: "ModuleNotFoundError" após limpar
**Problema:** Algum `__init__.py` foi deletado acidentalmente

**Solução:**
```bash
# Criar __init__.py em cada pasta migrations
echo. > accounts\migrations\__init__.py
echo. > blog\migrations\__init__.py
echo. > clientes\migrations\__init__.py
echo. > contato\migrations\__init__.py
echo. > home\migrations\__init__.py
echo. > orcamentos\migrations\__init__.py
echo. > profiles\migrations\__init__.py
echo. > projetos\migrations\__init__.py
```

---

## 📊 **Comparação das Opções**

| Característica | Python Script | Batch Script | Manual |
|----------------|---------------|--------------|--------|
| Facilidade | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Segurança | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Multiplataforma | ✅ | ❌ (só Windows) | ✅ |
| Interface | Colorida | Colorida | Nenhuma |
| Automação | Parcial | Total | Nenhuma |
| Controle | Alto | Médio | Total |

---

## 🎯 **Recomendação Final**

Para a maioria dos casos, use:
```bash
python limpar_migracoes.py
```

É seguro, claro, e funciona em qualquer sistema operacional!

---

## 📝 **Checklist Antes de Executar**

- [ ] Estou em ambiente de **desenvolvimento** (não produção)
- [ ] Fiz **backup** dos dados importantes (se houver)
- [ ] Fechei o **servidor Django**
- [ ] Fechei programas que acessam o **banco de dados**
- [ ] Entendo que **todos os dados serão perdidos**
- [ ] Li os **próximos passos** necessários

Se marcou tudo, pode executar! ✅

