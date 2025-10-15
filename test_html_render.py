"""
Teste de renderização HTML dos campos
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from system_config.forms import CompanySettingsForm

print("=" * 80)
print("TESTE DE RENDERIZAÇÃO HTML")
print("=" * 80)

form = CompanySettingsForm()

# Testar renderização de um campo
print("\nCampo 'raison_sociale':")
print("-" * 80)
print(form['raison_sociale'])

print("\n\nCampo 'forme_juridique' (select):")
print("-" * 80)
print(form['forme_juridique'])

print("\n" + "=" * 80)

