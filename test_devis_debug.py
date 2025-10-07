#!/usr/bin/env python
"""
Script de debug para testar a função cliente_devis_pdf diretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from orcamentos.models import Orcamento
from django.template.loader import render_to_string
from decimal import Decimal
from datetime import datetime

def test_cliente_devis_pdf():
    """Testar a função de geração de PDF do cliente"""
    
    # Buscar um orçamento de teste
    try:
        orcamento = Orcamento.objects.filter(
            solicitacao__cliente__isnull=False
        ).first()
        
        if not orcamento:
            print("❌ Nenhum orçamento encontrado com cliente associado")
            return
            
        print(f"✅ Encontrado orçamento: {orcamento.numero}")
        print(f"📝 Cliente: {orcamento.solicitacao.nome_solicitante}")
        print(f"📊 Total: {orcamento.total}")
        print(f"📋 Itens: {orcamento.itens.count()}")
        
        # Testar cálculos
        subtotal_ht = Decimal('0.00')
        total_taxe = Decimal('0.00')
        total_ttc = Decimal('0.00')

        items_data = []
        for i, item in enumerate(orcamento.itens.all(), 1):
            taxa_tva_decimal = Decimal(item.taxa_tva) / 100
            pu_ht = item.preco_unitario_ht
            pu_ttc = pu_ht * (1 + taxa_tva_decimal)
            total_item_ht = item.total_ht
            total_item_ttc = item.total_ttc
            taxe_item = total_item_ttc - total_item_ht

            subtotal_ht += total_item_ht
            total_taxe += taxe_item
            total_ttc += total_item_ttc

            items_data.append({
                'ref': item.referencia or f"REF{i:03d}",
                'designation': item.descricao,
                'unite': item.get_unidade_display(),
                'quantite': item.quantidade,
                'pu_ht': pu_ht,
                'pu_ttc': pu_ttc,
                'remise': (item.quantidade * pu_ht * item.remise_percentual / 100) if item.remise_percentual else Decimal('0.00'),
                'total_ht': total_item_ht,
                'total_ttc': total_item_ttc,
                'taxe': taxe_item,
                'taxa_tva': item.taxa_tva
            })
            
            print(f"  - Item {i}: {item.descricao[:50]}... | {total_item_ht}€")

        # Calcular totais
        remise_global = orcamento.desconto or Decimal('0.00')
        valor_remise_global = (subtotal_ht * remise_global / 100) if remise_global else Decimal('0.00')

        # Calcular taxa média de TVA
        taxa_tva_media = "Variável"
        if total_ttc > 0 and subtotal_ht > 0:
            percentual_tva = ((total_taxe / subtotal_ht) * 100)
            if abs(percentual_tva - 20) < 0.01:
                taxa_tva_media = "20"
            elif abs(percentual_tva - 10) < 0.01:
                taxa_tva_media = "10"
            elif abs(percentual_tva - 5.5) < 0.01:
                taxa_tva_media = "5.5"
            elif abs(percentual_tva - 0) < 0.01:
                taxa_tva_media = "0"
            else:
                taxa_tva_media = f"{percentual_tva:.1f}"

        # Totais finais
        subtotal_final_ht = orcamento.total
        taxe_finale = orcamento.valor_tva
        subtotal_final_ttc = orcamento.total_ttc

        print(f"💰 Subtotal HT: {subtotal_ht}€")
        print(f"💰 Taxa final: {taxe_finale}€")
        print(f"💰 Total TTC: {subtotal_final_ttc}€")

        # Context para o template
        context = {
            'orcamento': orcamento,
            'items_data': items_data,
            'subtotal_ht': subtotal_ht,
            'remise_global': remise_global,
            'valor_remise': valor_remise_global,
            'subtotal_apres_remise_ht': subtotal_final_ht,
            'taxe_finale': taxe_finale,
            'subtotal_apres_remise_ttc': subtotal_final_ttc,
            'taxa_tva_media': taxa_tva_media,
            'date_generation': datetime.now(),
            'company_info': {
                'name': 'LOPES DE SOUZA fabiano',
                'address': '261 Chemin de La Castellane',
                'city': '31790 Saint Sauveur, France',
                'phone': '+33 7 69 27 37 76',
                'email': 'contact@lopespeinture.fr',
                'siret': '978 441 756 00019',
                'ape': '4334Z',
                'tva': 'FR35978441756',
                'site': 'www.lopespeinture.fr'
            }
        }

        print(f"📋 Context criado com {len(context)} elementos")
        
        # Testar template do admin
        try:
            html_content_admin = render_to_string('orcamentos/admin/devis_pdf_html.html', context)
            print(f"✅ Template admin renderizado: {len(html_content_admin)} caracteres")
            
            # Salvar para debug
            with open('debug_admin_template.html', 'w', encoding='utf-8') as f:
                f.write(html_content_admin)
            print("💾 Debug salvo em: debug_admin_template.html")
            
        except Exception as e:
            print(f"❌ Erro no template admin: {e}")
            
        # Testar template simples
        try:
            html_content_simple = render_to_string('orcamentos/devis_pdf_html.html', context)
            print(f"✅ Template simples renderizado: {len(html_content_simple)} caracteres")
            
            # Salvar para debug
            with open('debug_simple_template.html', 'w', encoding='utf-8') as f:
                f.write(html_content_simple)
            print("💾 Debug salvo em: debug_simple_template.html")
            
        except Exception as e:
            print(f"❌ Erro no template simples: {e}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cliente_devis_pdf()
