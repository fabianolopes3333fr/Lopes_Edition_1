from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os


class OrcamentoPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Configurar estilos customizados"""
        # Título principal
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#2c5aa0"),
                fontName="Helvetica-Bold",
            )
        )

        # Subtítulo
        self.styles.add(
            ParagraphStyle(
                name="CustomSubtitle",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor("#666666"),
                alignment=TA_CENTER,
            )
        )

        # Cabeçalho de seção
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading3"],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor("#2c5aa0"),
                fontName="Helvetica-Bold",
            )
        )

        # Texto normal
        self.styles.add(
            ParagraphStyle(
                name="CustomNormal",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceAfter=6,
                fontName="Helvetica",
            )
        )

        # Texto pequeno
        self.styles.add(
            ParagraphStyle(
                name="CustomSmall",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.grey,
                fontName="Helvetica",
            )
        )

    def generate_pdf(self, orcamento):
        """Gerar PDF do orçamento usando ReportLab"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm,
        )

        # Construir o conteúdo
        story = []

        # Cabeçalho
        story.extend(self._build_header(orcamento))

        # Informações da empresa e cliente
        story.extend(self._build_company_client_info(orcamento))

        # Informações do projeto
        story.extend(self._build_project_info(orcamento))

        # Tabela de itens
        story.extend(self._build_items_table(orcamento))

        # Totais
        story.extend(self._build_totals(orcamento))

        # Condições
        story.extend(self._build_conditions(orcamento))

        # Rodapé
        story.extend(self._build_footer(orcamento))

        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_header(self, orcamento):
        """Construir cabeçalho"""
        elements = []

        # Linha decorativa superior
        elements.append(Spacer(1, 10))

        # Título
        title = Paragraph("DEVIS", self.styles["CustomTitle"])
        elements.append(title)

        # Número do orçamento
        numero = Paragraph(f"N° {orcamento.numero}", self.styles["CustomSubtitle"])
        elements.append(numero)

        # Linha decorativa
        elements.append(Spacer(1, 20))

        return elements

    def _build_company_client_info(self, orcamento):
        """Construir informações da empresa e cliente"""
        elements = []

        # Dados da empresa e cliente lado a lado
        cliente_nome = orcamento.solicitacao.nome_solicitante
        cliente_email = orcamento.solicitacao.email_solicitante
        cliente_telefone = orcamento.solicitacao.telefone_solicitante or "N/A"
        cliente_endereco = f"{orcamento.solicitacao.endereco}"
        cliente_cidade = f"{orcamento.solicitacao.cidade} {orcamento.solicitacao.cep}"

        data = [
            [
                Paragraph("<b>LOPES PEINTURE</b>", self.styles["SectionHeader"]),
                Paragraph(
                    f"<b>{cliente_nome}</b>",
                    self.styles["SectionHeader"],
                ),
            ],
            [
                Paragraph(
                    "261 Chemin de la Castellane<br/>31790 ST SAUVEUR",
                    self.styles["CustomNormal"],
                ),
                Paragraph(
                    f'Email: {cliente_email}<br/>Tél: {cliente_telefone}',
                    self.styles["CustomNormal"],
                ),
            ],
            [
                Paragraph(
                    "Tél: +33 07 69 27 37 76<br/>contact@lopespeinture.fr",
                    self.styles["CustomNormal"],
                ),
                Paragraph(
                    f'{cliente_endereco}<br/>{cliente_cidade}',
                    self.styles["CustomNormal"],
                ),
            ],
            [
                Paragraph("www.lopespeinture.fr", self.styles["CustomNormal"]),
                Paragraph("", self.styles["CustomNormal"]),
            ],
        ]

        table = Table(data, colWidths=[9.5 * cm, 8.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 30))

        return elements

    def _build_project_info(self, orcamento):
        """Construir informações do projeto"""
        elements = []

        # Título da seção
        project_title = Paragraph(
            "INFORMATIONS DU PROJET", self.styles["SectionHeader"]
        )
        elements.append(project_title)

        # Dados do projeto
        project_data = []

        if orcamento.titulo:
            project_data.append(
                [
                    Paragraph("<b>Projet:</b>", self.styles["CustomNormal"]),
                    Paragraph(orcamento.titulo, self.styles["CustomNormal"]),
                ]
            )

        if orcamento.descricao:
            project_data.append(
                [
                    Paragraph("<b>Description:</b>", self.styles["CustomNormal"]),
                    Paragraph(orcamento.descricao, self.styles["CustomNormal"]),
                ]
            )

        # Usar dados da solicitação para endereço
        if orcamento.solicitacao.endereco:
            adresse_complete = f"{orcamento.solicitacao.endereco}"
            if orcamento.solicitacao.cidade:
                adresse_complete += f", {orcamento.solicitacao.cidade}"

            project_data.append(
                [
                    Paragraph("<b>Adresse:</b>", self.styles["CustomNormal"]),
                    Paragraph(adresse_complete, self.styles["CustomNormal"]),
                ]
            )

        # Datas
        if orcamento.data_elaboracao:
            project_data.append(
                [
                    Paragraph("<b>Date de création:</b>", self.styles["CustomNormal"]),
                    Paragraph(
                        orcamento.data_elaboracao.strftime("%d/%m/%Y"),
                        self.styles["CustomNormal"],
                    ),
                ]
            )

        if orcamento.validade_orcamento:
            project_data.append(
                [
                    Paragraph("<b>Valable jusqu'au:</b>", self.styles["CustomNormal"]),
                    Paragraph(
                        orcamento.validade_orcamento.strftime("%d/%m/%Y"),
                        self.styles["CustomNormal"],
                    ),
                ]
            )

        if project_data:
            project_table = Table(project_data, colWidths=[4 * cm, 14.5 * cm])
            project_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2c5aa0")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            elements.append(project_table)

        elements.append(Spacer(1, 30))

        return elements

    def _build_items_table(self, orcamento):
        """Construir tabela de itens"""
        elements = []

        # Título da seção
        items_title = Paragraph("DÉTAIL DES PRESTATIONS", self.styles["SectionHeader"])
        elements.append(items_title)
        elements.append(Spacer(1, 10))

        # Cabeçalho da tabela
        data = [
            [
                Paragraph("<b>Référence</b>", self.styles["CustomNormal"]),
                Paragraph("<b>Description</b>", self.styles["CustomNormal"]),
                Paragraph("<b>Qté</b>", self.styles["CustomNormal"]),
                Paragraph("<b>Unité</b>", self.styles["CustomNormal"]),
                Paragraph("<b>Prix Unit. HT</b>", self.styles["CustomNormal"]),
                Paragraph("<b>Total HT</b>", self.styles["CustomNormal"]),
            ]
        ]

        # Itens
        for item in orcamento.itens.all():
            ref_text = item.referencia if item.referencia else "N/A"
            description = Paragraph(item.descricao, self.styles["CustomNormal"])

            data.append(
                [
                    Paragraph(ref_text, self.styles["CustomNormal"]),
                    description,
                    Paragraph(str(item.quantidade), self.styles["CustomNormal"]),
                    Paragraph(item.unidade, self.styles["CustomNormal"]),
                    Paragraph(
                        f"{item.preco_unitario_ht:.2f} €", self.styles["CustomNormal"]
                    ),
                    Paragraph(
                        f"<b>{item.total_ht:.2f} €</b>", self.styles["CustomNormal"]
                    ),
                ]
            )

        # Se não há itens
        if len(data) == 1:
            data.append(
                [
                    Paragraph(
                        "<i>Aucun item ajouté à ce devis</i>",
                        self.styles["CustomNormal"],
                    ),
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )

        # Criar tabela
        table = Table(
            data, colWidths=[3 * cm, 7.2 * cm, 1.8 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm]
        )
        table.setStyle(
            TableStyle(
                [
                    # Cabeçalho
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    # Dados
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    (
                        "ALIGN",
                        (2, 1),
                        (-1, -1),
                        "CENTER",
                    ),  # Quantidade, unidade, preços centralizados
                    (
                        "ALIGN",
                        (0, 1),
                        (1, -1),
                        "LEFT",
                    ),  # Referência e descrição à esquerda
                    # Bordas
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # Cores alternadas nas linhas
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8f9fa")],
                    ),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_totals(self, orcamento):
        """Construir seção de totais com acomptes e saldo"""
        elements = []

        # Calcular totais baseando-se no modelo
        try:
            subtotal_ht = orcamento.subtotal
        except Exception:
            subtotal_ht = orcamento.total

        total_ht = orcamento.total
        total_ttc = getattr(orcamento, 'total_ttc', total_ht)
        valor_tva = getattr(orcamento, 'valor_tva', total_ttc - total_ht)

        # Acomptes
        try:
            from decimal import Decimal
            total_acomptes_ttc = sum((a.valor_ttc for a in orcamento.acomptes.all()), Decimal('0.00'))
        except Exception:
            total_acomptes_ttc = 0
        solde_ttc = max(0, float(total_ttc) - float(total_acomptes_ttc))

        # Tabela de totais
        data = [
            [
                Paragraph("<b>Sous-total HT:</b>", self.styles["CustomNormal"]),
                Paragraph(f"<b>{float(subtotal_ht):.2f} €</b>", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("<b>TVA:</b>", self.styles["CustomNormal"]),
                Paragraph(f"<b>{float(valor_tva):.2f} €</b>", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("<b>TOTAL TTC:</b>", self.styles["CustomNormal"]),
                Paragraph(f"<b>{float(total_ttc):.2f} €</b>", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("<b>Acomptes:</b>", self.styles["CustomNormal"]),
                Paragraph(f"<b>-{float(total_acomptes_ttc):.2f} €</b>", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("<b>Solde TTC à payer:</b>", self.styles["CustomNormal"]),
                Paragraph(f"<b>{float(solde_ttc):.2f} €</b>", self.styles["CustomNormal"]),
            ],
        ]

        table = Table(data, colWidths=[12 * cm, 6.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, 1), 10),
                    ("FONTSIZE", (0, 2), (-1, 4), 12),
                    ("FONTNAME", (0, 2), (-1, 4), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#2c5aa0")),
                    ("TEXTCOLOR", (0, 4), (-1, 4), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 30))

        return elements

    def _build_conditions(self, orcamento):
        """Construir condições"""
        elements = []

        # Título
        title = Paragraph("CONDITIONS GÉNÉRALES", self.styles["SectionHeader"])
        elements.append(title)

        # Condições de pagamento
        if orcamento.condicoes_pagamento:
            payment = Paragraph(
                f"<b>Conditions de paiement:</b> {orcamento.condicoes_pagamento}",
                self.styles["CustomNormal"],
            )
            elements.append(payment)
            elements.append(Spacer(1, 6))

        if orcamento.total:
            from decimal import Decimal
            acompte = Paragraph(
                f"<b>Acompte (30%):</b> {orcamento.total * Decimal('0.3'):.2f} €",
                self.styles["CustomNormal"],
            )
            elements.append(acompte)
            elements.append(Spacer(1, 6))

        # Validade
        if orcamento.validade_orcamento:
            validity = Paragraph(
                f"<b>Validité du devis:</b> {orcamento.validade_orcamento.strftime('%d/%m/%Y')}",
                self.styles["CustomNormal"],
            )
            elements.append(validity)
            elements.append(Spacer(1, 6))

        # Condições gerais
        conditions_text = """
        <b>Conditions générales:</b><br/>
        • Les prix sont exprimés en euros TTC<br/>
        • Devis valable 30 jours à compter de la date d'émission<br/>
        • Acompte de 30% à la commande<br/>
        • Solde à la livraison<br/>
        • Matériaux et main d'œuvre garantis selon les normes en vigueur<br/>
        • Délais d'exécution donnés à titre indicatif<br/>
        • Travaux réalisés selon les règles de l'art<br/>
        • Assurance décennale et responsabilité civile professionnelle
        """

        conditions = Paragraph(conditions_text, self.styles["CustomNormal"])
        elements.append(conditions)

        elements.append(Spacer(1, 30))

        return elements

    def _build_footer(self, orcamento):
        """Construir rodapé"""
        elements = []

        # Assinatura
        signature_data = [
            [
                Paragraph("<b>Bon pour accord:</b>", self.styles["CustomNormal"]),
                Paragraph("<b>LOPES PEINTURE</b>", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("Date: ________________", self.styles["CustomNormal"]),
                Paragraph("Date: ________________", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("Signature du client:", self.styles["CustomNormal"]),
                Paragraph("Signature de l'entreprise:", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("", self.styles["CustomNormal"]),
                Paragraph("", self.styles["CustomNormal"]),
            ],
            [
                Paragraph("", self.styles["CustomNormal"]),
                Paragraph("", self.styles["CustomNormal"]),
            ],
        ]

        signature_table = Table(signature_data, colWidths=[8 * cm, 5 * cm])
        signature_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    # alignement des cellules en haut et à gauche de la table

                ]
            )
        )

        elements.append(signature_table)
        elements.append(Spacer(1, 20))

        # Informações da empresa no rodapé
        elements.append(Spacer(1, 10))
        footer = Paragraph(
            "<i>LOPES PEINTURE - 261 Chemin de la Castellane - 31790 ST SAUVEUR - France<br/>Tél: +33 07 69 27 37 76 - contact@lopespeinture.fr - www.lopespeinture.fr <br/> PAIEMENT PAR VIREMENT BANCAIRE LOPES DE SOUZA FABIANO (EI) IBAN FR76 1027 8022 3400 0206 6300 131</i>",
            ParagraphStyle(
                name="Footer",
                parent=self.styles["CustomNormal"],
                fontSize=9,
                alignment=TA_CENTER,
                # textColor=colors.HexColor("#2c5aa0"),
            ),
        )

        elements.append(footer)
        elements.append(Spacer(1, 20))

        # Mensagem de agradecimento
        elements.append(Spacer(1, 10))
        thank_you = Paragraph(
            "<i>Merci de votre confiance !</i>",
            ParagraphStyle(
                name="ThankYou",
                parent=self.styles["CustomNormal"],
                fontSize=10,
                textColor=colors.HexColor("#2c5aa0"),
                alignment=TA_CENTER,
                fontName="Helvetica-Oblique",
            ),
        )
        elements.append(thank_you)

        return elements


def gerar_pdf_orcamento(orcamento):
    """
    Função wrapper para gerar PDF do orçamento
    Retorna um buffer BytesIO com o PDF gerado
    """
    generator = OrcamentoPDFGenerator()
    return generator.generate_pdf(orcamento)
