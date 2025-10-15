"""
Script de debug para testar a estilização dos formulários
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from system_config.forms import CompanySettingsForm, CiviliteForm, AutoEntrepreneurParametersForm

print("=" * 80)
print("TESTE DE ESTILIZAÇÃO DOS FORMULÁRIOS")
print("=" * 80)

# Teste 1: CompanySettingsForm
print("\n1. CompanySettingsForm")
print("-" * 80)
form1 = CompanySettingsForm()
for field_name, field in form1.fields.items():
    widget_class = field.widget.attrs.get('class', 'SEM CLASSE')
    print(f"  {field_name}: {widget_class[:80]}...")
    if widget_class == 'SEM CLASSE':
        print(f"    ⚠️  PROBLEMA: Campo sem classes CSS!")

# Teste 2: CiviliteForm
print("\n2. CiviliteForm")
print("-" * 80)
form2 = CiviliteForm()
for field_name, field in form2.fields.items():
    widget_class = field.widget.attrs.get('class', 'SEM CLASSE')
    widget_type = type(field.widget).__name__
    print(f"  {field_name} ({widget_type}): {widget_class[:80] if widget_class != 'SEM CLASSE' else 'SEM CLASSE'}")

# Teste 3: AutoEntrepreneurParametersForm
print("\n3. AutoEntrepreneurParametersForm")
print("-" * 80)
form3 = AutoEntrepreneurParametersForm()
count_ok = 0
count_fail = 0
for field_name, field in form3.fields.items():
    widget_class = field.widget.attrs.get('class', '')
    if widget_class and 'w-full' in widget_class:
        count_ok += 1
    else:
        count_fail += 1
        print(f"  ⚠️  {field_name}: {widget_class if widget_class else 'SEM CLASSE'}")

print(f"\n  ✅ OK: {count_ok} campos")
print(f"  ❌ FAIL: {count_fail} campos")

# Teste 4: Verificar um campo específico em detalhes
print("\n4. Análise Detalhada do Campo 'raison_sociale'")
print("-" * 80)
form = CompanySettingsForm()
if 'raison_sociale' in form.fields:
    field = form.fields['raison_sociale']
    print(f"  Widget Type: {type(field.widget).__name__}")
    print(f"  Widget Attrs: {field.widget.attrs}")
    print(f"  Rendered HTML (início):")
    rendered = str(field)
    print(f"    {rendered[:200]}...")
else:
    print("  Campo 'raison_sociale' não encontrado")

print("\n" + "=" * 80)
print("FIM DO TESTE")
print("=" * 80)

