from .pdf_generator import OrcamentoPDFGenerator


def gerar_pdf_orcamento(orcamento):
    """Função utilitária para gerar PDF do orçamento usando ReportLab"""
    generator = OrcamentoPDFGenerator()
    return generator.generate_pdf(orcamento)
