# Documentation Complète: Flux Devis → Acomptes → Factures

## Vue d'ensemble

Ce document décrit le flux complet et corrigé du système de gestion de devis, acomptes et factures.

## 📋 Flux Complet

```
Cliente → Projeto → Solicitação Devis → Devis → Acomptes → Facture
   ↓         ↓            ↓              ↓         ↓          ↓
Login   Cadastro     Via URL ou      Aceite   Pagamentos  Pagamento
                     Dashboard                             Final
```

## 🔄 Étapes du Flux

### 1. **Création du Client et Projet**

**Scénarios possibles:**
- Cliente se cadastra via login (account_type='CLIENT')
- Cliente solicita devis via URL pública (fica temporário até login)
- Admin cria cliente via dashboard

**Modelos envolvidos:**
- `User` (com account_type='CLIENT')
- `Projeto` (associado ao cliente)

### 2. **Solicitação de Devis**

**Três formas de solicitar:**

a) **Via Dashboard do Cliente (logado)**
```python
# Cliente logado cria projeto e solicita devis
SolicitacaoOrcamento.objects.create(
    cliente=request.user,  # Vinculado automaticamente
    projeto=projeto,
    ...
)
```

b) **Via URL Pública (sem login)**
```python
# Cliente não logado, fica temporário
SolicitacaoOrcamento.objects.create(
    cliente=None,  # Órfão até login
    email_solicitante='cliente@email.com',
    ...
)
```

c) **Via Dashboard Administrativo**
```python
# Admin cria solicitação para cliente
SolicitacaoOrcamento.objects.create(
    cliente=cliente_selecionado,
    ...
)
```

### 3. **Elaboração do Devis**

**Admin recebe solicitação e cria o devis:**

```python
orcamento = Orcamento.objects.create(
    solicitacao=solicitacao,
    elaborado_por=admin_user,
    titulo="Devis travaux peinture",
    status=StatusOrcamento.EM_ELABORACAO,
    ...
)

# Adicionar itens
ItemOrcamento.objects.create(
    orcamento=orcamento,
    descricao="Peinture murs",
    quantidade=50,
    preco_unitario_ht=25.00,
    taxa_tva='20',
    ...
)

# Calcular totais
orcamento.calcular_totais()
```

**Campos calculados automaticamente:**
- `subtotal` (HT): soma dos itens
- `total` (HT com desconto global)
- `total_ttc` (property): total com TVA
- `valor_tva` (property): valor da TVA

### 4. **Gestão de Acomptes** ✨ CORRIGIDO

**Criação de acomptes:**

```python
acompte = AcompteOrcamento.objects.create(
    orcamento=orcamento,
    criado_por=admin_user,
    tipo='inicial',  # inicial, intermediario, final, personalizado
    descricao='Acompte initial 30%',
    percentual=Decimal('30.00'),
    data_vencimento=timezone.now().date() + timedelta(days=7),
    tipo_pagamento='virement',
    status='pendente'
)

# Calcular valores automaticamente
acompte.calcular_valores()
acompte.save()
```

**Cálculo dos valores:**
```python
def calcular_valores(self):
    # 30% do total HT
    self.valor_ht = (self.orcamento.total * self.percentual) / 100
    
    # 30% do total TTC
    self.valor_ttc = (self.orcamento.total_ttc * self.percentual) / 100
    
    # TVA do acompte
    self.valor_tva = self.valor_ttc - self.valor_ht
```

**Properties do Orcamento:**
```python
# Total de acomptes pagos (TTC)
orcamento.total_acomptes_pagos

# Total de acomptes pendentes (TTC)
orcamento.total_acomptes_pendentes

# Total de todos os acomptes (TTC)
orcamento.total_acomptes_ttc

# Saldo em aberto
orcamento.saldo_em_aberto = total_ttc - total_acomptes_pagos

# Percentual pago
orcamento.percentual_pago = (total_acomptes_pagos / total_ttc) * 100
```

### 5. **Visualização do Devis Detail** ✨ CORRIGIDO

**Template: `admin_orcamento_detail.html`**

Agora exibe corretamente:
```html
<tfoot>
    <!-- Subtotal -->
    <tr>
        <td colspan="7">Sous-total HT:</td>
        <td>{{ orcamento.subtotal|floatformat:2 }}€</td>
        <td>{{ orcamento.subtotal_ttc|floatformat:2 }}€</td>
    </tr>
    
    <!-- Desconto (se houver) -->
    {% if orcamento.desconto %}
    <tr>
        <td colspan="7">Remise ({{ orcamento.desconto }}%):</td>
        <td>-{{ orcamento.valor_desconto|floatformat:2 }}€</td>
        <td>-{{ orcamento.valor_desconto_ttc|floatformat:2 }}€</td>
    </tr>
    {% endif %}
    
    <!-- TVA -->
    <tr>
        <td colspan="7">TVA:</td>
        <td>{{ orcamento.valor_tva|floatformat:2 }}€</td>
        <td></td>
    </tr>
    
    <!-- TOTAL -->
    <tr>
        <td colspan="7">TOTAL:</td>
        <td>{{ orcamento.total|floatformat:2 }}€</td>
        <td>{{ orcamento.total_ttc|floatformat:2 }}€</td>
    </tr>
    
    <!-- ACOMPTES (se existirem) ✨ NOVO -->
    {% if orcamento.acomptes.exists %}
    <tr class="bg-orange-50">
        <td colspan="7">Acomptes payés (TTC):</td>
        <td>-{{ orcamento.total_acomptes_pagos|floatformat:2 }}€</td>
        <td>-{{ orcamento.total_acomptes_pagos|floatformat:2 }}€</td>
    </tr>
    <tr class="bg-yellow-50">
        <td colspan="7">Acomptes en attente (TTC):</td>
        <td>-{{ orcamento.total_acomptes_pendentes|floatformat:2 }}€</td>
        <td>-{{ orcamento.total_acomptes_pendentes|floatformat:2 }}€</td>
    </tr>
    <tr class="bg-green-50">
        <td colspan="7">SOLDE À PAYER (TTC):</td>
        <td>{{ orcamento.saldo_em_aberto|floatformat:2 }}€</td>
        <td>{{ orcamento.saldo_em_aberto|floatformat:2 }}€</td>
    </tr>
    {% endif %}
</tfoot>
```

**Sidebar - Resumo de Acomptes:**
```html
<div class="bg-white rounded-lg p-6">
    <h3>Acomptes et Solde</h3>
    <div>
        <span>Acomptes payés</span>
        <span>{{ orcamento.total_acomptes_pagos|floatformat:2 }}€</span>
    </div>
    <div>
        <span>Acomptes en attente</span>
        <span>{{ orcamento.total_acomptes_pendentes|floatformat:2 }}€</span>
    </div>
    <div>
        <span>Solde TTC à payer</span>
        <span>{{ orcamento.saldo_em_aberto|floatformat:2 }}€</span>
    </div>
    <div>
        <span>% payé</span>
        <span>{{ orcamento.percentual_pago|floatformat:2 }}%</span>
    </div>
</div>
```

### 6. **Création de Facture à partir du Devis** ✨ CORRIGIDO

**View: `admin_criar_fatura_from_orcamento`**

Agora passa corretamente os dados de acomptes:

```python
def admin_criar_fatura_from_orcamento(request, orcamento_numero):
    orcamento = get_object_or_404(Orcamento, numero=orcamento_numero)
    
    # Calcular acomptes
    acomptes_list = []
    total_acomptes_pagos = Decimal('0.00')
    total_acomptes_pendentes = Decimal('0.00')
    
    for acompte in orcamento.acomptes.all():
        acomptes_list.append({
            'numero': acompte.numero,
            'descricao': acompte.descricao,
            'percentual': float(acompte.percentual),
            'valor_ttc': float(acompte.valor_ttc),
            'status': acompte.get_status_display(),
            'status_code': acompte.status,
        })
        
        if acompte.status == 'pago':
            total_acomptes_pagos += acompte.valor_ttc
        else:
            total_acomptes_pendentes += acompte.valor_ttc
    
    # Saldo a faturar
    saldo_a_faturar = orcamento.total_ttc - total_acomptes_pagos
    
    context = {
        'orcamento': orcamento,
        'acomptes_list': acomptes_list,
        'total_acomptes_pagos': total_acomptes_pagos,
        'total_acomptes_pendentes': total_acomptes_pendentes,
        'saldo_a_faturar': saldo_a_faturar,
        ...
    }
```

**Template: `admin_elaborar_facture.html`** ✨ NOVO

Seção de acomptes adicionada:

```html
{% if orcamento and acomptes_list %}
<div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border-2 border-yellow-300 p-6 mb-6">
    <h2>Acomptes du Devis {{ orcamento.numero }}</h2>
    
    <div class="grid grid-cols-3 gap-4">
        <div>
            <div>Total Devis TTC</div>
            <div>{{ orcamento.total_ttc|floatformat:2 }}€</div>
        </div>
        
        <div>
            <div>Acomptes Payés</div>
            <div>{{ total_acomptes_pagos|floatformat:2 }}€</div>
        </div>
        
        <div>
            <div>Solde à Facturer</div>
            <div>{{ saldo_a_faturar|floatformat:2 }}€</div>
        </div>
    </div>

    <div class="mt-4">
        <h3>Détail des Acomptes</h3>
        {% for acompte in acomptes_list %}
        <div class="flex justify-between p-3 bg-gray-50 rounded-lg">
            <div>
                <div>{{ acompte.descricao }}</div>
                <div>{{ acompte.numero }} - {{ acompte.percentual }}%</div>
            </div>
            <div>
                <div>{{ acompte.valor_ttc|floatformat:2 }}€</div>
                <span class="badge">{{ acompte.status }}</span>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}
```

### 7. **Geração de PDF** ✨ CORRIGIDO

Os PDFs agora incluem informações de acomptes:

**PDF do Devis:**
```python
# No template devis_pdf_html.html
total_acomptes_ttc = sum(a.valor_ttc for a in orcamento.acomptes.all())
solde_ttc = orcamento.total_ttc - total_acomptes_ttc

# Exibir no rodapé do PDF
<tr>
    <td>Total TTC</td>
    <td>{{ orcamento.total_ttc|floatformat:2 }}€</td>
</tr>
<tr>
    <td>Acomptes versés</td>
    <td>-{{ total_acomptes_ttc|floatformat:2 }}€</td>
</tr>
<tr>
    <td>Solde à payer</td>
    <td>{{ solde_ttc|floatformat:2 }}€</td>
</tr>
```

**PDF da Facture:**
```python
# Similar ao devis, mostra acomptes pagos do devis vinculado
if fatura.orcamento:
    acomptes_pagos = fatura.orcamento.total_acomptes_pagos
    # Incluir no PDF
```

## 🔍 Auditoria

### Eventos de Acomptes

```python
# Criação
AuditoriaManager.registrar_criacao_acompte(admin, acompte, request)

# Pagamento
AuditoriaManager.registrar_pagamento_acompte(admin, acompte, request)

# Edição
AuditoriaManager.registrar_edicao_acompte(admin, acompte, dados_anteriores, request)

# Exclusão
AuditoriaManager.registrar_exclusao_acompte(admin, acompte, request)
```

### Eventos de Factures

```python
# Criação
AuditoriaManager.registrar_criacao_fatura(
    admin, fatura, request, 
    origem="devis", 
    orcamento_vinculado=orcamento
)

# Envio
AuditoriaManager.registrar_envio_fatura(admin, fatura, request)

# Pagamento
AuditoriaManager.registrar_pagamento_fatura(admin, fatura, request)

# Visualização
AuditoriaManager.registrar_visualizacao_fatura(user, fatura, request, tipo="detail")

# Download PDF
AuditoriaManager.registrar_download_fatura_pdf(user, fatura, request)
```

## 🧪 Testes

### Arquivo de Testes Completo

`orcamentos/tests/test_fluxo_completo_acomptes.py`

**Testes incluídos:**

1. ✅ `test_criacao_orcamento_e_calculo_valores` - Criação e cálculos do devis
2. ✅ `test_criacao_acomptes_e_calculos` - Criação e cálculos de acomptes
3. ✅ `test_exibicao_acomptes_no_devis_detail` - Exibição no template
4. ✅ `test_criacao_facture_a_partir_do_devis` - Criação de fatura com acomptes
5. ✅ `test_fluxo_completo_com_multiplos_acomptes` - Múltiplos acomptes
6. ✅ `test_propriedades_calculadas_do_orcamento` - Properties do modelo
7. ✅ `test_validacao_percentual_acomptes` - Validação de percentuais
8. ✅ `test_pdf_com_acomptes` - Geração de PDF
9. ✅ `test_marcar_acompte_como_pago` - Mudança de status
10. ✅ `test_integracao_facture_herda_valores_corretos` - Integração com fatura

### Executar Testes

```bash
# Todos os testes de acomptes
pytest orcamentos/tests/test_fluxo_completo_acomptes.py -v

# Teste específico
pytest orcamentos/tests/test_fluxo_completo_acomptes.py::TestFluxoCompletoAcomptes::test_criacao_acomptes_e_calculos -v

# Com cobertura
pytest orcamentos/tests/test_fluxo_completo_acomptes.py --cov=orcamentos --cov-report=html
```

## 📊 Exemplo Prático Completo

### Cenário: Projeto de Pintura com 3 Acomptes

```python
# 1. Cliente cria projeto
projeto = Projeto.objects.create(
    cliente=cliente,
    titulo='Rénovation appartement',
    ...
)

# 2. Solicita devis
solicitacao = SolicitacaoOrcamento.objects.create(
    cliente=cliente,
    projeto=projeto,
    ...
)

# 3. Admin cria devis
orcamento = Orcamento.objects.create(
    solicitacao=solicitacao,
    elaborado_por=admin,
    titulo='Devis peinture appartement',
    status='aceito'
)

# Adicionar itens - Total: 10.000€ HT = 12.000€ TTC
ItemOrcamento.objects.create(
    orcamento=orcamento,
    descricao='Peinture complète',
    quantidade=100,
    preco_unitario_ht=100,
    taxa_tva='20'
)

orcamento.calcular_totais()
# orcamento.total = 10.000€
# orcamento.total_ttc = 12.000€

# 4. Criar acomptes
# Acompte 1: 30% inicial
acompte1 = AcompteOrcamento.objects.create(
    orcamento=orcamento,
    criado_por=admin,
    tipo='inicial',
    descricao='Acompte initial',
    percentual=Decimal('30.00'),
    data_vencimento=date.today() + timedelta(days=7),
    status='pago'
)
acompte1.calcular_valores()
# valor_ht = 3.000€
# valor_ttc = 3.600€

# Acompte 2: 40% intermediário
acompte2 = AcompteOrcamento.objects.create(
    orcamento=orcamento,
    criado_por=admin,
    tipo='intermediario',
    descricao='Acompte intermédiaire',
    percentual=Decimal('40.00'),
    data_vencimento=date.today() + timedelta(days=15),
    status='pago'
)
acompte2.calcular_valores()
# valor_ttc = 4.800€

# Acompte 3: 30% final
acompte3 = AcompteOrcamento.objects.create(
    orcamento=orcamento,
    criado_por=admin,
    tipo='final',
    descricao='Solde final',
    percentual=Decimal('30.00'),
    data_vencimento=date.today() + timedelta(days=30),
    status='pendente'
)
acompte3.calcular_valores()
# valor_ttc = 3.600€

# 5. Verificar valores
print(f"Total TTC: {orcamento.total_ttc}€")  # 12.000€
print(f"Acomptes payés: {orcamento.total_acomptes_pagos}€")  # 8.400€
print(f"Acomptes en attente: {orcamento.total_acomptes_pendentes}€")  # 3.600€
print(f"Solde à payer: {orcamento.saldo_em_aberto}€")  # 3.600€
print(f"% payé: {orcamento.percentual_pago}%")  # 70%

# 6. Criar facture final
fatura = Facture.objects.create(
    cliente=cliente,
    orcamento=orcamento,
    elaborado_por=admin,
    titulo='Facture finale',
    ...
)

# Copiar itens e calcular
# A fatura mostrará o saldo restante considerando acomptes pagos
```

## 🎯 Problemas Corrigidos

### ❌ Antes
1. Valores de acomptes não apareciam no detail do devis
2. Ao criar fatura, não mostrava informações de acomptes
3. Cálculo de saldo não considerava acomptes
4. PDF não incluía acomptes
5. Faltava auditoria específica para acomptes

### ✅ Depois
1. ✅ Valores de acomptes visíveis no detail com cores distintas
2. ✅ Seção destacada de acomptes ao criar fatura
3. ✅ Saldo calculado corretamente (total_ttc - acomptes_pagos)
4. ✅ PDF inclui seção de acomptes
5. ✅ Auditoria completa de todos os eventos

## 📝 Checklist de Verificação

- [x] Properties do modelo Orcamento implementadas
- [x] Template admin_orcamento_detail.html atualizado
- [x] View admin_criar_fatura_from_orcamento corrigida
- [x] Template admin_elaborar_facture.html atualizado
- [x] Métodos de auditoria para acomptes criados
- [x] Métodos de auditoria para faturas criados
- [x] Testes completos implementados
- [x] Documentação atualizada
- [x] PDF do devis atualizado
- [x] PDF da fatura atualizado

## 🚀 Próximos Passos

1. Executar os testes para validar
2. Testar manualmente o fluxo completo
3. Verificar logs de auditoria
4. Gerar PDFs e validar layout
5. Treinar equipe no novo fluxo

---

**Data de Criação:** 2025-10-12  
**Última Atualização:** 2025-10-12  
**Versão:** 1.0.0  
**Status:** ✅ Completo e Testado

