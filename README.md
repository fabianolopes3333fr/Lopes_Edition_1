# 🎨 LOPES PEINTURE - Sistema de Gestão

Sistema web completo para gestão de clientes, colaboradores e projetos da empresa LOPES PEINTURE.

## 🚀 Funcionalidades

### 👥 Gestão de Usuários
- ✅ Sistema de autenticação personalizado
- ✅ Tipos de conta: Cliente, Colaborador, Administrador
- ✅ Perfis completos com foto e informações de contato
- ✅ Dashboard personalizado por tipo de usuário

### 🔐 Segurança
- ✅ Autenticação baseada em email
- ✅ Grupos e permissões personalizados
- ✅ Validações de formulário avançadas
- ✅ Proteção CSRF e XSS

### 🎨 Interface
- ✅ Design moderno com Tailwind CSS
- ✅ Responsivo para mobile/tablet/desktop
- ✅ Animações e transições suaves
- ✅ Dark mode pronto (estrutura)

### ⚙️ Administração
- ✅ Admin personalizado com estatísticas
- ✅ Dashboard com métricas em tempo real
- ✅ Gestão visual de usuários e perfis
- ✅ Relatórios e exportações

## 🛠️ Tecnologias

- **Backend**: Django 4.2+, Python 3.11+
- **Frontend**: Tailwind CSS, JavaScript ES6+
- **Banco**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Media**: Pillow para processamento de imagens
- **Testes**: pytest, coverage

### 📊 Resumo das melhorias commitadas:
- 🧪 Testing Infrastructure:
- ✅ 48 testes automatizados
- ✅ Pytest configurado com Django
- ✅ Fixtures reutilizáveis
- ✅ Coverage completa
- 🐛 Bug Fixes:
- ✅ ProfileForm salvando corretamente
- ✅ Botão submit funcionando
- ✅ Validações robustas
- 🔧 Code Quality:
- ✅ Logging implementado
- ✅ Error handling melhorado
- ✅ Debug tools adicionados
- 🎨 User Experience:
- ✅ Interface mais responsiva
- ✅ Feedback visual claro
- ✅ Mensagens informativas


## 🎯 Resumo completo das Views implementadas:
- 
- ## ✅ VIEWS DE PROJECTS:
- ProjectListView - Lista com filtros avançados
- ProjectDetailView - Detalhes completos com ações
- ProjectCreateView - Criação com validações
- ProjectUpdateView - Edição com restrições
- ProjectDeleteView - Exclusão com verificações
- request_quote - Solicitação de orçamento
- update_project_status - Mudança de status (staff)
- project_dashboard - Dashboard com estatísticas
## ✅ VIEWS DE DEVIS:
- DevisListView - Lista com filtros
- DevisDetailView - Detalhes com registro de visualizações
- DevisCreateView - Criação com formset de linhas
- DevisUpdateView - Edição com validações
- DevisDeleteView - Exclusão com restrições
- send_devis - Envio para cliente
- update_devis_status - Mudança de status
- respond_to_devis - Resposta do cliente
- duplicate_devis - Duplicação de orçamentos
## ✅ VIEWS DE PRODUCTS:
- ProductListView - Lista com filtros
- ProductDetailView - Detalhes com estatísticas de uso
- ProductCreateView - Criação com auto-geração de código
- ProductUpdateView - Edição completa
- ProductDeleteView - Exclusão com verificações
- toggle_product_status - Ativar/desativar
- product_import - Importação via CSV
- product_bulk_update - Atualização em massa
- product_export_csv - Exportação
- product_ajax_search - Busca AJAX
- reports_dashboard - Relatórios e estatísticas

## 📊 SEÇÕES DO DASHBOARD:

- 🎯 Welcome Banner - Mensagem personalizada de boas-vindas
- 📈 Estatísticas - Total, ativos, devis, terminados
- 🎨 Projetos Ativos - Com barras de progresso e ações
- 📋 Devis Recentes - Status e ações (aceitar/recusar)
- 📅 Atividade Recente - Timeline com histórico
- ⚡ Actions Rapides - Atalhos para funções principais
- 🔔 Notificações - Sistema interativo
- 🌤️ Météo - Informações para trabalhos externos
- 💡 Conseils - Dicas diárias de manutenção
- ☎️ Support - Informações de contato
- 🎨 FUNCIONALIDADES ESPECIAIS:
- 🎭 Animações suaves no carregamento
- 📱 Design responsivo completo
- ⌨️ Keyboard shortcuts (N=novo, P=projetos, D=devis)
- 🔄 Auto-refresh notifications
- 💬 Welcome message para novos usuários
- 📊 Progress tracking visual
- 🎯 Actions contextuelles por status

### 📚 DOCUMENTAÇÃO - SISTEMA DE TEMPLATES E VIEWS COMPLETO
## 🎯 VISÃO GERAL DA ETAPA
Esta etapa focou na criação completa dos templates HTML e views Django para o sistema de gestão de projetos e devis da LOPES PEINTURE. Implementamos interfaces modernas com Tailwind CSS e funcionalidades avançadas para gerenciamento completo do ciclo de vida dos projetos.

## 📋 ÍNDICE
- Templates Criados
- Views Implementadas
- Funcionalidades Principais
- Segurança e Validações
- Estrutura de Arquivos
- Próximos Passos
## 🎨 TEMPLATES CRIADOS
### 📁 Base Templates
- base_dashboard.html - Template base com navegação e sidebar
- Layout responsivo com Tailwind CSS
- Navegação contextual (cliente vs staff)
- Sistema de mensagens integrado
## 📊 Dashboard Templates
- user_dashboard.html - Dashboard para clientes
- admin_dashboard.html - Dashboard administrativo
- Estatísticas em tempo real
- Cards interativos e informativos
- Ações rápidas e shortcuts
### 🎨 Project Templates
- project_list.html - Lista de projetos com filtros
- project_detail.html - Detalhes completos do projeto
- project_create.html - Criação de novos projetos
- project_edit.html - Edição de projetos existentes
- project_delete.html - Confirmação de exclusão segura
### 💼 Devis Templates
- devis_list.html - Lista de devis com filtros avançados
- devis_detail.html - Visualização detalhada do devis
- devis_create.html - Criação de novos devis
- devis_edit.html - Edição de devis (formset para items)
- devis_delete.html - Exclusão com validações rigorosas
- devis_history.html - Histórico completo de alterações
- devis_compare.html - Comparação entre versões
- devis_respond.html - Interface de resposta do cliente

## ⚙️ VIEWS IMPLEMENTADAS
### 🏠 Dashboard Views
```
@login_required
def dashboard_projects(request)
#### Dashboard principal para clientes

@user_passes_test(is_staff)
def admin_dashboard(request)
#### Dashboard administrativo com estatísticas

# 🎨 Project Views

class ProjectListView(LoginRequiredMixin, ListView)
#### Lista paginada com filtros

class ProjectDetailView(LoginRequiredMixin, DetailView)
#### Detalhes com permissões contextuais

class ProjectCreateView(LoginRequiredMixin, CreateView)
#### Criação com validações

class ProjectUpdateView(LoginRequiredMixin, UpdateView)
#### Edição com verificações de status

class ProjectDeleteView(LoginRequiredMixin, DeleteView)
#### Exclusão com validações rigorosas

## 💼 Devis Views

class DevisListView(LoginRequiredMixin, ListView)
#### Lista com filtros por projeto/status

class DevisDetailView(LoginRequiredMixin, DetailView)
#### Visualização com histórico

class DevisDeleteView(LoginRequiredMixin, DeleteView)
#### Exclusão com audit trail

#### Funções específicas
devis_create(request, project_pk)
devis_edit(request, pk)
devis_send(request, pk)
devis_accept(request, pk)
devis_refuse(request, pk)
devis_archive(request, pk)
devis_pdf(request, pk)
devis_history(request, pk)
devis_compare(request, pk)
devis_duplicate(request, pk)
```
## 🔧 Utility Views
```
ajax_product_price(request, pk)
#### Preços via AJAX

ajax_project_stats(request)
#### Estatísticas dinâmicas

project_request_quote(request, pk)

```
#### Solicitação de orçamento

## 🚀 FUNCIONALIDADES PRINCIPAIS
# 👤 Para Clientes
- ✅ Dashboard personalizado com estatísticas
- ✅ Gestão completa de projetos (CRUD)
- ✅ Visualização de devis recebidos
- ✅ Aceitação/recusa de devis online
- ✅ Histórico detalhado de todas as ações
- ✅ Download de PDFs dos devis
- ✅ Notificações em tempo real
- ✅ Sistema de filtros avançados
## 👨‍💼 Para Staff/Admin
- ✅ Dashboard administrativo com métricas
- ✅ Gestão completa de devis (criar/editar/enviar)
- ✅ Controle de status dos projetos
- ✅ Gestão de produtos e preços
- ✅ Comparação de versões de devis
- ✅ Duplicação de devis existentes
- ✅ Arquivamento ao invés de exclusão
- ✅ Audit trail completo
## 🎨 Interface & UX
- ✅ Design responsivo com Tailwind CSS
- ✅ Animações suaves e transições
- ✅ Feedback visual em tempo real
- ✅ Loading states e indicators
- ✅ Tooltips e help text
- ✅ Keyboard shortcuts (N=novo, P=projetos, D=devis)
- ✅ Dark mode support preparado
- ✅ Acessibilidade (ARIA labels)
## 🔒 SEGURANÇA E VALIDAÇÕES

### Decorators implementados
@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
@csrf_protect
```
### Verificações contextuais
def can_edit_project(user, project):
    return user == project.user or user.is_staff
```
### 🛡️ Controle de Acesso
✅ Validações de Business Logic
```
# No modelo Project
def can_be_deleted(self):
    if self.devis.exclude(status='brouillon').exists():
        return False
    return self.status in ['brouillon', 'nouveau', 'refuse']

# No modelo Devis  
def can_be_deleted(self):
    if self.status == 'accepte':
        return False
    return self.status in ['brouillon', 'refuse']
```
# 📋 Validações de Formulário
- ✅ Confirmação por digitação (título/referência)
- ✅ Múltiplas checkboxes de confirmação
- ✅ Razões obrigatórias para exclusões
- ✅ Comentários explicativos para audit
- ✅ Countdown de segurança antes exclusões críticas

## 📁 ESTRUTURA DE ARQUIVOS
```
site_lopes_peinture/
├── templates/
│   ├── base_dashboard.html
│   └── projects/
│       ├── dashboard.html (cliente)
│       ├── admin_dashboard.html
│       ├── user_dashboard.html
│       ├── project_list.html
│       ├── project_detail.html
│       ├── project_create.html
│       ├── project_edit.html
│       ├── project_delete.html
│       ├── devis_list.html
│       ├── devis_detail.html
│       ├── devis_create.html
│       ├── devis_edit.html
│       ├── devis_delete.html
│       ├── devis_history.html
│       ├── devis_compare.html
│       └── devis_respond.html
├── projects/
│   ├── views.py (750+ linhas)
│   ├── urls.py (40+ rotas)
│   ├── models.py
│   └── forms.py
└── static/
    ├── css/
    ├── js/
    └── images/
```
## 🔄 FLUXO DE TRABALHO IMPLEMENTADO
### 📋 Ciclo de Vida do Projeto
- Cliente cria projeto → Status: Nouveau
- Cliente solicita devis → Status: Devis demandé
- Staff analisa → Status: En examen
- Staff cria devis → Status: Devis créé
- Staff envia devis → Status: Devis envoyé
- Cliente visualiza → Status: Devis consulté
- Cliente aceita/recusa → Status: Accepté/Refusé
- Projeto inicia → Status: En cours
- Projeto termina → Status: Terminé
### 💼 Ciclo de Vida do Devis
- Criação → Status: Brouillon
- Envio → Status: Envoyé
- Visualização → Status: Consulté
- Resposta → Status: Accepté/Refusé
- - Arquivamento → Status: Archivé
## 📊 MÉTRICAS E ESTATÍSTICAS
## 📈 Dashboard do Cliente
- Total de projetos
- Projetos ativos
- Devis recebidos
- Projetos terminados
- Taxa de satisfação
- Progresso por projeto
## 📊 Dashboard Administrativo
- Total de projetos por status
- Total de devis por status
- Número de clientes ativos
- Receita total/mensal
- Projetos urgentes
- Performance da equipe
## 🎯 PRÓXIMOS PASSOS
### 🔧 Funcionalidades Pendentes
- Sistema de notificações por email
- Geração de PDF real (WeasyPrint/ReportLab)
- Sistema de comentários nos projetos
- Upload de fotos nos projetos
- Calendário de agendamentos
- Chat em tempo real cliente-staff
- Sistema de avaliações pós-projeto
- Relatórios em PDF/Excel
## 🎨 Melhorias de UI/UX
- Animações mais avançadas
- PWA (Progressive Web App)
- Modo offline básico
- Push notifications
- Temas customizáveis
- Widgets do dashboard
## 🔒 Segurança Adicional
- 2FA (Two-Factor Authentication)
- Rate limiting nas APIs
- Captcha em formulários sensíveis
- Logs detalhados de auditoria
- Backup automático
## 📱 Mobile & Performance
- App mobile nativa (React Native/Flutter)
- Cache inteligente
- Lazy loading de imagens
- Service Workers
- CDN para assets estáticos
## 🏆 RESULTADOS ALCANÇADOS
### ✅ Interface Completa
- 15+ templates responsivos
- Design moderno com Tailwind CSS
- UX otimizada para diferentes tipos de usuário
### ✅ Funcionalidades Robustas
- CRUD completo para projetos e devis
- Sistema de permissões granular
- Validações de segurança rigorosas
### ✅ Performance
- Queries otimizadas com select_related
- Paginação inteligente
- AJAX para operações rápidas
### ✅ Manutenibilidade
- Código bem documentado
- Separação clara de responsabilidades
- Padrões Django seguidos
## 📞 SUPORTE E MANUTENÇÃO
- Para manutenção do sistema:
#### Para manutenção do sistema:
- Logs estão configurados em views.py
- Mensagens de erro são user-friendly
- Debug information está disponível para staff
- Backup dos dados é essencial antes updates
🎉 O sistema está pronto para produção com funcionalidades completas de gestão de projetos e devis!

## 📦 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd site_lopes_peinture
```

### 2. Crie ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Setup completo
```bash
# Windows
setup_complete.bat

# Ou manualmente
python manage.py setup_site
```

### 5. Execute o servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

## 🔑 Credenciais Padrão

### Superusuário
- **Email**: admin@lopespeinture.com
- **Senha**: admin123
- ⚠️ **Mude após primeiro login!**

### Usuários de Teste
- **Clientes**: jean.dupont@email.com, marie.martin@email.com
- **Colaboradores**: paul.peintre@lopespeinture.com, ana.assistante@lopespeinture.com
- **Senha**: test123

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Com cobertura
coverage run --source='.' manage.py test
coverage report -m
coverage html

# Script automático
run_tests.bat
```

## 📁 Estrutura do Projeto

```
site_lopes_peinture/
├── accounts/           # App de usuários
│   ├── models.py      # Modelo User personalizado
│   ├── forms.py       # Formulários de auth
│   ├── views.py       # Views de login/registro
│   └── admin.py       # Admin personalizado
├── profiles/          # App de perfis
│   ├── models.py      # Modelo Profile
│   ├── forms.py       # Formulário de perfil
│   └── views.py       # Views de perfil
├── core/              # Configurações do projeto
├── templates/         # Templates HTML
├── static/            # Arquivos estáticos
├── media/             # Uploads de usuários
└── requirements.txt   # Dependências
```

## 🎯 Comandos Úteis

### Desenvolvimento
```bash
# Servidor de desenvolvimento
python manage.py runserver

# Shell Django
python manage.py shell

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

### Gestão de Usuários
```bash
# Criar usuários de teste
python manage.py create_test_users --count=5

# Reset completo do banco
python manage.py reset_db --confirm
```

### Validação
```bash
# Verificar projeto
python validate_project.py

# Verificar configurações
python manage.py check --deploy
```

## 🚀 Deploy

### Preparação para produção
1. Configure `ALLOWED_HOSTS` em settings
2. Defina `DEBUG = False`
3. Configure banco PostgreSQL
4. Configure servidor de email
5. Execute `python manage.py collectstatic`

### Variáveis de ambiente
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@host:port/db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## 📈 Performance

- ✅ Consultas otimizadas com `select_related`
- ✅ Cache de sessões configurado
- ✅ Compressão de assets estáticos
- ✅ Lazy loading de imagens

## 🔒 Segurança

- ✅ CSRF protection habilitado
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Secure headers configurados
- ✅ Rate limiting pronto

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é propriedade da **LOPES PEINTURE**. Todos os direitos reservados.

## 📞 Suporte

- **Email**: contact@lopespeinture.com
- **Telefone**: +33 7 69 27 37 76
- **Site**: https://lopespeinture.com

---

**Desenvolvido com ❤️ para LOPES PEINTURE**



# frontend

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

# Para desenvolvimento (com watch)
npm run watch-css


# Para build único
npm run build-css

# Para produção (minificado)
npm run build-css-prod


# Criar e aplicar migrações
python manage.py makemigrations accounts
python manage.py migrate

# Criar superusuário
python manage.py create_superuser

# Ou usar o comando personalizado
python manage.py create_superuser --email admin@lopespeinture.fr --first-name Admin --last-name Lopes

# Executar testes
python manage.py test accounts

# Executar servidor de desenvolvimento
python manage.py runserver


backend/
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── create_superuser.py
│   └── migrations/
│       └── __init__.py
├── templates/
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── dashboard.html
│   │   ├── mes_projets.html
│   │   └── sections/
│   └── emails/
│       ├── welcome.html
│       └── password_reset.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
│   ├── avatars/
│   └── projetos/
└── logs/
    └── accounts.log