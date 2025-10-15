# 🎨 LOPES PEINTURE - Sistema de Gestão

Sistema web completo para gestão de clientes, colaboradores, projetos e orçamentos da empresa LOPES PEINTURE.

## 🚀 Funcionalidades

### 👥 Gestão de Usuários
- ✅ Sistema de autenticação personalizado
- ✅ Tipos de conta: Cliente, Colaborador, Administrador
- ✅ Perfis completos com foto e informações de contato
- ✅ Dashboard personalizado por tipo de usuário

### 📊 Gestão de Projetos
- ✅ Lista de projetos com filtros avançados
- ✅ Criação e edição com validações robustas
- ✅ Controle de status (pendente, em andamento, concluído)
- ✅ Dashboard com estatísticas em tempo real

### 💰 Gestão de Orçamentos (Devis)
- ✅ Criação de orçamentos com linhas detalhadas
- ✅ Envio automático para clientes
- ✅ Sistema de aceitação/recusa pelo cliente
- ✅ Duplicação de orçamentos existentes
- ✅ Relatórios e estatísticas completas

### 📦 Gestão de Produtos
- ✅ Cadastro com código auto-gerado
- ✅ Controle de estoque e preços
- ✅ Importação/exportação via CSV
- ✅ Busca AJAX em tempo real
- ✅ Atualização em massa

### 🏢 Gestão de Clientes
- ✅ Cadastro completo de empresas e particulares
- ✅ Múltiplos endereços (entrega, canteiro, transportador)
- ✅ Histórico de projetos e orçamentos
- ✅ Notas e observações
- ✅ Controle de status (ativo, inativo, suspenso)

### ⚙️ Configuração do Sistema (System Config)
- ✅ **Informações da Empresa**:
  - Coordonnées complètes (SIRET, APE, RCS, TVA)
  - Responsable/Gérant da empresa
  - Expert-Comptable e dados do cabinet
  
- ✅ **Parâmetros Auto-Entrepreneur**:
  - Configuração de charges (cotisations sociales, impôts, formation, CCI)
  - Separação Biens/Services
  - Cálculo automático de totais
  
- ✅ **Interface do Sistema**:
  - Upload de logo da empresa
  - Imagem de fundo personalizada
  - Preview visual em tempo real
  
- ✅ **Configuração de Email (SMTP)**:
  - Servidor SMTP configurável
  - Suporte TLS/SSL
  - Exemplos de configuração (Gmail, Outlook, Yahoo, OVH)
  - Teste de conexão
  
- ✅ **Listas de Referência**:
  - Civilités (M., Mme, Mlle, etc.)
  - Formes Juridiques (SARL, SAS, EI, Auto-Entrepreneur)
  - Modes de Règlement (Chèque, Virement, Carte, Espèces)
  - Taux de Taxes (TVA 5.5%, 10%, 20%)
  - Conditions de Paiement (Immédiat, 30j, 45j)

### 🔐 Segurança
- ✅ Autenticação baseada em email
- ✅ Grupos e permissões personalizados
- ✅ Validações de formulário avançadas
- ✅ Proteção CSRF e XSS
- ✅ Sistema de auditoria (logs)

### 🎨 Interface
- ✅ Design moderno com Tailwind CSS (via CDN)
- ✅ Responsivo para mobile/tablet/desktop
- ✅ Animações e transições suaves
- ✅ Ícones Font Awesome
- ✅ Paleta de cores consistente
- ✅ Componentes reutilizáveis

### 📊 Dashboards
- ✅ Dashboard principal com estatísticas
- ✅ Projetos ativos com barras de progresso
- ✅ Devis recentes com ações rápidas
- ✅ Timeline de atividades
- ✅ Sistema de notificações
- ✅ Ações rápidas contextuais

## 🛠️ Tecnologias

- **Backend**: Django 4.2+, Python 3.12
- **Frontend**: Tailwind CSS (CDN), JavaScript ES6+
- **Banco**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Media**: Pillow para processamento de imagens
- **Testes**: pytest, pytest-django, coverage

## 📁 Estrutura do Projeto

```
LopesPeinture/
│
├── 📁 accounts/                    # Sistema de Autenticação e Usuários
│   ├── management/                 # Comandos personalizados do Django
│   ├── migrations/                 # Migrações do banco de dados
│   ├── tests/                      # Testes unitários e integração
│   ├── adapters.py                 # Adaptadores de autenticação social
│   ├── admin.py                    # Configuração do Django Admin
│   ├── admin_dashboard.py          # Dashboard administrativo
│   ├── admin_groups.py             # Gestão de grupos e permissões
│   ├── backends.py                 # Backends de autenticação customizados
│   ├── decorators.py               # Decoradores de permissão
│   ├── forms.py                    # Formulários de registro/login
│   ├── models.py                   # Models de usuário customizado
│   ├── permissions.py              # Sistema de permissões
│   ├── settings_views.py           # Views de configurações
│   ├── signals.py                  # Signals do Django
│   ├── social_views.py             # Views para login social
│   ├── urls.py                     # Rotas de autenticação
│   ├── utils.py                    # Funções utilitárias
│   └── views.py                    # Views principais
│
├── 📁 blog/                        # Sistema de Blog (opcional)
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── 📁 clientes/                    # ⭐ Gestão de Clientes
│   ├── migrations/
│   ├── admin.py                    # Admin customizado para clientes
│   ├── forms.py                    # Formulários de cliente e endereços
│   ├── models.py                   # Cliente, AdresseLivraison, AdresseChantier
│   ├── signals.py                  # Signals de auditoria
│   ├── urls.py                     # Rotas CRUD de clientes
│   └── views.py                    # Views de listagem, criação, edição
│
├── 📁 contato/                     # Formulário de Contato
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── 📁 core/                        # ⚙️ Configurações Django
│   ├── __pycache__/
│   ├── asgi.py                     # Configuração ASGI
│   ├── settings.py                 # Settings principal do Django
│   ├── urls.py                     # URLs raiz do projeto
│   └── wsgi.py                     # Configuração WSGI
│
├── 📁 docs/                        # 📚 Documentação
│   ├── COMANDOS_ORFAOS.md
│   ├── COMO_LIMPAR_MIGRACOES.md
│   ├── CORRECAO_FINAL_TESTE_ORCAMENTO.md
│   ├── CORRECOES_FINAIS_TESTES.md
│   ├── CORRECOES_TESTES_FINAIS.md
│   ├── CORRECOES_TESTES_ORCAMENTOS_ORFAOS.md
│   ├── CORRECOES_WARNINGS.md
│   ├── DOCUMENTACAO_FLUXO_ACOMPTES_DEVIS_FACTURES.md
│   ├── DOCUMENTACAO_TESTES_AUDITORIA.md
│   ├── RELATORIO_MELHORIAS_CLIENTES.md
│   ├── SOCIAL_LOGIN_GUIDE.md
│   └── STATUS_FINAL_TESTES_ORCAMENTOS.md
│
├── 📁 home/                        # Página Inicial
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── 📁 logs/                        # 📋 Logs do Sistema
│   ├── testes/
│   ├── accounts.log
│   └── auditoria_orcamentos.log
│
├── 📁 media/                       # 📸 Arquivos de Mídia (uploads)
│   ├── avatars/                    # Fotos de perfil
│   ├── produtos/                   # Imagens de produtos
│   └── projetos/                   # Documentos de projetos
│
├── 📁 orcamentos/                  # 💰 Sistema de Orçamentos (Devis)
│   ├── migrations/
│   ├── acompte_views.py            # Views de acomptes (pagamentos)
│   ├── admin.py                    # Admin de devis
│   ├── auditoria.py                # Sistema de auditoria
│   ├── config_auditoria.py         # Configuração de logs
│   ├── forms.py                    # Formulários de devis e linhas
│   ├── middleware.py               # Middleware de auditoria
│   ├── models.py                   # Devis, LigneDevis, Acompte
│   ├── urls.py                     # Rotas de orçamentos
│   └── views.py                    # Views CRUD de devis
│
├── 📁 profiles/                    # 👤 Perfis de Usuários
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py                    # Formulário de edição de perfil
│   ├── models.py                   # Profile com foto e contatos
│   ├── urls.py
│   └── views.py                    # Views de perfil (detail, edit)
│
├── 📁 projetos/                    # 🏗️ Gestão de Projetos
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py                    # Formulários de projeto
│   ├── models.py                   # Projeto, Status, Timeline
│   ├── urls.py
│   └── views.py                    # Views CRUD e dashboard
│
├── 📁 scripts/                     # 🔧 Scripts Utilitários
│   └── (scripts de manutenção)
│
├── 📁 static/                      # 🎨 Arquivos Estáticos
│   ├── admin/                      # CSS/JS do Django Admin
│   ├── config/                     # Configurações frontend
│   ├── css/
│   │   ├── input.css               # CSS de entrada do Tailwind
│   │   ├── output.css              # CSS compilado do Tailwind
│   │   └── dashboard.css           # CSS customizado
│   ├── img/                        # Imagens estáticas
│   └── js/                         # JavaScript customizado
│
├── 📁 system_config/               # ⭐ Configuração do Sistema (NOVO)
│   ├── migrations/
│   ├── __pycache__/
│   ├── admin.py                    # Admin de configurações
│   ├── apps.py                     # Config da app
│   ├── forms.py                    # Forms estilizados (Company, Auto, Email)
│   ├── models.py                   # Models de configuração
│   │                               # - CompanySettings
│   │                               # - AutoEntrepreneurParameters
│   │                               # - InterfaceSettings
│   │                               # - EmailSettings
│   │                               # - Civilite, LegalForm, PaymentMode
│   │                               # - TaxRate, PaymentCondition
│   ├── urls.py                     # Rotas de configuração
│   └── views.py                    # Views (4 páginas + CRUD)
│
├── 📁 templates/                   # 🎨 Templates HTML
│   ├── accounts/                   # Templates de autenticação
│   ├── admin/                      # Templates do Django Admin
│   ├── clientes/                   # Templates de clientes
│   │   ├── form_cliente.html
│   │   └── lista_clientes.html
│   ├── components/                 # Componentes reutilizáveis
│   ├── contato/                    # Template de contato
│   ├── dashboard/                  # Dashboard principal
│   ├── emails/                     # Templates de email
│   ├── orcamentos/                 # Templates de devis
│   ├── pages/                      # Páginas estáticas
│   ├── partials_dashboard/         # Partials do dashboard
│   ├── profiles/                   # Templates de perfil
│   ├── socialaccount/              # Login social
│   ├── system_config/              # ⭐ Templates de configuração
│   │   ├── configuration_home.html # Dashboard de config
│   │   ├── company_settings.html   # Info da empresa (4 abas)
│   │   ├── parameters.html         # Parâmetros sistema (3 abas)
│   │   └── list_generic.html       # CRUD de listas
│   ├── base.html                   # Template base público
│   └── base_dashboard.html         # Template base do dashboard
│
├── 📁 utils/                       # 🛠️ Utilitários Globais
│   └── (funções auxiliares)
│
├── 📁 .venv/                       # Ambiente virtual Python
├── 📁 node_modules/                # Dependências Node.js
│
├── 📄 .env                         # Variáveis de ambiente (não versionado)
├── 📄 .env.example                 # Exemplo de configuração
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
├── 📄 conftest.py                  # Configuração de testes Pytest
├── 📄 db.sqlite3                   # Banco de dados (desenvolvimento)
├── 📄 manage.py                    # CLI do Django
├── 📄 package.json                 # Dependências Node.js (Tailwind)
├── 📄 pytest.ini                   # Configuração Pytest
├── 📄 README.md                    # Este arquivo
├── 📄 requirements.txt             # Dependências Python
└── 📄 tailwind.config.js           # Configuração Tailwind CSS
```

### 📊 Estatísticas do Projeto

- **Apps Django**: 10 apps principais
- **Models**: ~30 models implementados
- **Views**: ~80+ views (CBV + FBV)
- **Templates**: ~60+ templates HTML
- **Testes**: 48 testes automatizados
- **Linhas de Código**: ~15.000+ LOC

### 🎯 Apps Principais

| App | Descrição | Status |
|-----|-----------|--------|
| `accounts` | Autenticação e usuários | ✅ Completo |
| `clientes` | Gestão de clientes | ✅ Completo |
| `projetos` | Gestão de projetos | ✅ Completo |
| `orcamentos` | Devis e orçamentos | ✅ Completo |
| `profiles` | Perfis de usuários | ✅ Completo |
| `system_config` | Configuração do sistema | ⭐ Novo (v2.0) |
| `home` | Página inicial | ✅ Completo |
| `contato` | Formulário de contato | ✅ Completo |
| `blog` | Sistema de blog | 🚧 Opcional |
| `core` | Configurações Django | ✅ Completo |

## 🧪 Testes

- ✅ **48 testes automatizados**
- ✅ Pytest configurado com Django
- ✅ Fixtures reutilizáveis
- ✅ Coverage completa
- ✅ Testes de integração

## 🚀 Como Executar

### Pré-requisitos
```bash
Python 3.12+
pip
virtualenv
```

### Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd LopesPeinture
```

2. Crie o ambiente virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Execute o servidor:
```bash
python manage.py runserver
```

7. Acesse: `http://localhost:8000`

## 📝 Configuração Inicial

Após a primeira instalação, acesse:

1. **Admin Django**: `/admin/` - Configure dados iniciais
2. **System Config**: `/config/` - Configure sua empresa
   - Preencha informações da empresa
   - Configure parâmetros Auto-Entrepreneur
   - Faça upload do logo
   - Configure email SMTP
   - Crie listas de referência (civilités, formes juridiques, etc.)

## 🎨 Padrões de Design

### Forms
- Widgets com classes CSS aplicadas diretamente no `Meta.widgets`
- Constantes para classes reutilizáveis (`INPUT_CLASSES`, `SELECT_CLASSES`, etc.)
- Validações personalizadas nos clean methods

### Templates
- Extensão de `base_dashboard.html`
- Uso de `{{ form.field }}` ao invés de `render_field`
- Ícones Font Awesome contextuais
- Boxes informativos coloridos
- Labels com ícones e textos de ajuda

### JavaScript
- Vanilla JS (sem jQuery)
- Event listeners modernos
- Scroll suave
- Cálculos em tempo real
- Preview dinâmico

## 📊 Melhorias Recentes

### v2.0 - System Config Module (Janeiro 2025)
- ✅ Módulo completo de configuração do sistema
- ✅ 4 templates profissionais redesenhados
- ✅ Interface CRUD moderna para listas de referência
- ✅ Formulários totalmente estilizados com Tailwind
- ✅ JavaScript interativo (cálculos, previews, highlights)
- ✅ Validações robustas em todos os formulários
- ✅ Documentação completa inline

### v1.5 - Testing & Bug Fixes
- ✅ 48 testes automatizados implementados
- ✅ ProfileForm corrigido e funcionando
- ✅ Validações melhoradas
- ✅ Logging implementado
- ✅ Error handling robusto

## 📄 Licença

Projeto proprietário - LOPES PEINTURE © 2024-2025

## 👨‍💻 Desenvolvedor

Sistema desenvolvido para LOPES PEINTURE
- Gestão completa de projetos de pintura
- Interface moderna e intuitiva
- Performance otimizada
- Código limpo e documentado

---

**Status**: 🟢 Em Produção  
**Versão**: 2.0  
**Última Atualização**: Janeiro 2025
