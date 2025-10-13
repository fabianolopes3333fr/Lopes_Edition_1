"""
Script para executar os testes de acomptes que falharam
"""
import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Executar pytest
import pytest

if __name__ == '__main__':
    # Executar os testes específicos que falharam
    args = [
        'orcamentos/tests/test_fluxo_completo_acomptes.py::TestFluxoCompletoAcomptes::test_criacao_acomptes_e_calculos',
        'orcamentos/tests/test_fluxo_completo_acomptes.py::TestFluxoCompletoAcomptes::test_exibicao_acomptes_no_devis_detail',
        'orcamentos/tests/test_fluxo_completo_acomptes.py::TestFluxoCompletoAcomptes::test_criacao_facture_a_partir_do_devis',
        'orcamentos/tests/test_fluxo_completo_acomptes.py::TestFluxoCompletoAcomptes::test_pdf_com_acomptes',
        '-v',
        '--tb=short'
    ]
    
    sys.exit(pytest.main(args))

