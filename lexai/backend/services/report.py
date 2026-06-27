import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from models.schemas import AnalysisResponse, RiskLevel


# Color scheme
DARK_BLUE = colors.HexColor("#1a237e")
RED = colors.HexColor("#c62828")
ORANGE = colors.HexColor("#ef6c00")
GREEN = colors.HexColor("#2e7d32")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY = colors.HexColor("#e0e0e0")
WHITE = colors.white


def generate_report(analysis: AnalysisResponse, output_path: str) -> str:
    """Generate a PDF risk report from analysis results"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ──────────────────────────────────────────
    header_style = ParagraphStyle(
        "Header",
        fontSize=24,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "Sub",
        fontSize=10,
        fontName="Helvetica",
        textColor=WHITE,
        alignment=TA_CENTER
    )

    header_table = Table(
        [[Paragraph("⚖ LexAI Risk Report", header_style)],
         [Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", sub_style)]],
        colWidths=[6.8 * inch]
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BLUE),
        ("ROWPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.2 * inch))

    # ── Document Info ────────────────────────────────────
    overall_risk = "HIGH" if analysis.high_risk_count > 0 else "MEDIUM" if analysis.medium_risk_count > 0 else "LOW"
    risk_color = RED if overall_risk == "HIGH" else ORANGE if overall_risk == "MEDIUM" else GREEN

    info_data = [
        ["Document Type", analysis.document_type],
        ["Overall Risk", overall_risk],
        ["Total Clauses Found", str(analysis.total_clauses_found)],
        ["High Risk Clauses", str(analysis.high_risk_count)],
        ["Medium Risk Clauses", str(analysis.medium_risk_count)],
        ["Low Risk Clauses", str(analysis.low_risk_count)],
    ]

    info_table = Table(info_data, colWidths=[2.5 * inch, 4.3 * inch])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("TEXTCOLOR", (1, 1), (1, 1), risk_color),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.15 * inch))

    # ── Summary ──────────────────────────────────────────
    story.append(Paragraph("Document Summary", ParagraphStyle(
        "SectionTitle", fontSize=13, fontName="Helvetica-Bold",
        textColor=DARK_BLUE, spaceAfter=6
    )))
    story.append(Paragraph(analysis.summary, ParagraphStyle(
        "Body", fontSize=10, fontName="Helvetica",
        leading=16, alignment=TA_JUSTIFY
    )))
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 0.1 * inch))

    # ── Clauses by Risk Level ────────────────────────────
    risk_groups = [
        (RiskLevel.HIGH, "🔴 HIGH RISK CLAUSES", RED),
        (RiskLevel.MEDIUM, "🟡 MEDIUM RISK CLAUSES", ORANGE),
        (RiskLevel.LOW, "🟢 LOW RISK CLAUSES", GREEN),
    ]

    section_style = ParagraphStyle(
        "SectionTitle", fontSize=12, fontName="Helvetica-Bold", spaceAfter=8
    )
    clause_title_style = ParagraphStyle(
        "ClauseTitle", fontSize=10, fontName="Helvetica-Bold", spaceAfter=3
    )
    clause_body_style = ParagraphStyle(
        "ClauseBody", fontSize=9, fontName="Helvetica", leading=14, spaceAfter=4
    )
    label_style = ParagraphStyle(
        "Label", fontSize=9, fontName="Helvetica-Bold", spaceAfter=2
    )

    for risk_level, section_title, section_color in risk_groups:
        clauses = [c for c in analysis.clauses if c.risk_level == risk_level]
        if not clauses:
            continue

        story.append(Paragraph(f"{section_title} ({len(clauses)})", ParagraphStyle(
            "RiskSection", fontSize=12, fontName="Helvetica-Bold",
            textColor=section_color, spaceAfter=8
        )))

        for i, clause in enumerate(clauses, 1):
            clause_data = [
                [Paragraph(f"{i}. {clause.clause_type}", clause_title_style)],
                [Paragraph(f"<b>Original Text:</b> {clause.original_text[:300]}{'...' if len(clause.original_text) > 300 else ''}", clause_body_style)],
                [Paragraph(f"<b>Explanation:</b> {clause.plain_explanation}", clause_body_style)],
                [Paragraph(f"<b>Recommendation:</b> {clause.recommendation}", clause_body_style)],
            ]
            clause_table = Table(clause_data, colWidths=[6.8 * inch])
            clause_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), section_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
                ("ROWPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
            ]))
            story.append(clause_table)
            story.append(Spacer(1, 0.1 * inch))

        story.append(Spacer(1, 0.1 * inch))

    # ── Disclaimer ───────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(analysis.disclaimer, ParagraphStyle(
        "Disclaimer", fontSize=8, fontName="Helvetica-Oblique",
        textColor=colors.gray, alignment=TA_CENTER
    )))

    doc.build(story)
    return output_path