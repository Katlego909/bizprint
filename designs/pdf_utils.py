"""
PDF generation utilities for quotes and invoices using ReportLab
"""
from io import BytesIO
from decimal import Decimal
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from django.conf import settings
import os


def generate_design_quote_pdf(design_request):
    """
    Generate a professional PDF quote for a design request
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1d3557'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1d3557'),
        spaceAfter=12,
    )
    
    normal_style = styles['Normal']
    
    # Add logo if exists
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'bp-logo-1.png')
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=1.5*inch, height=0.6*inch)
            elements.append(img)
            elements.append(Spacer(1, 12))
        except:
            pass
    
    # Title
    elements.append(Paragraph("QUOTATION", title_style))
    elements.append(Spacer(1, 12))
    
    # Quote details
    quote_info = [
        ['Quote #:', str(design_request.id)],
        ['Date:', design_request.created_at.strftime('%d %B %Y')],
        ['Status:', design_request.get_status_display()],
    ]
    
    quote_table = Table(quote_info, colWidths=[1.5*inch, 4*inch])
    quote_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1d3557')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(quote_table)
    elements.append(Spacer(1, 20))
    
    # Client information
    elements.append(Paragraph("Prepared For:", heading_style))
    
    if design_request.user:
        client_name = design_request.user.get_full_name()
        client_email = design_request.user.email
        client_phone = design_request.phone or (design_request.user.profile.phone if hasattr(design_request.user, 'profile') else '')
    else:
        client_name = design_request.full_name or "Guest"
        client_email = design_request.email
        client_phone = design_request.phone or ''
    
    client_info = [
        ['Name:', client_name],
        ['Email:', client_email],
    ]
    
    if client_phone:
        client_info.append(['Phone:', client_phone])
    
    client_table = Table(client_info, colWidths=[1.5*inch, 4*inch])
    client_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 20))
    
    # Estimated turnaround time
    turnaround_days = design_request.get_estimated_turnaround_days()
    timeline_text = f"Estimated Turnaround Time: {turnaround_days} business days"
    if design_request.timeline_preference:
        timeline_text += f" ({design_request.get_timeline_preference_display()} timeline)"
    
    turnaround_style = ParagraphStyle(
        'Turnaround',
        parent=normal_style,
        fontSize=10,
        textColor=colors.HexColor('#1d3557'),
        backColor=colors.HexColor('#f0f7ff'),
        borderPadding=10,
        borderColor=colors.HexColor('#1d3557'),
        borderWidth=1,
        borderRadius=4,
        leftIndent=10,
    )
    elements.append(Paragraph(f"<b>⏱ {timeline_text}</b>", turnaround_style))
    elements.append(Spacer(1, 30))
    
    # Selected packages
    elements.append(Paragraph("Selected Packages", heading_style))
    
    # Package table data
    package_data = [['Package', 'Price (R)']]
    for pkg in design_request.packages.all():
        package_data.append([pkg.title, f"{pkg.price:.2f}"])
    
    package_table = Table(package_data, colWidths=[4*inch, 1.5*inch])
    package_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d3557')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1d3557')),
    ]))
    elements.append(package_table)
    elements.append(Spacer(1, 20))
    
    # Totals
    subtotal = design_request.total_price
    rush_fee = design_request.get_rush_fee()
    subtotal_with_rush = design_request.get_subtotal_with_rush()
    vat = subtotal_with_rush * Decimal('0.15')
    total = subtotal_with_rush + vat
    
    # Build totals data with rush fee if applicable
    totals_data = [
        ['Subtotal:', f"R {subtotal:.2f}"],
    ]
    
    if rush_fee > 0:
        totals_data.append(['Rush Fee (50%):', f"R {rush_fee:.2f}"])
        totals_data.append(['Subtotal with Rush:', f"R {subtotal_with_rush:.2f}"])
    
    totals_data.extend([
        ['VAT (15%):', f"R {vat:.2f}"],
        ['', ''],  # Spacer row
        ['Total:', f"R {total:.2f}"],
    ])
    
    totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 2), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 2), 'Helvetica'),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 2), 10),
        ('FONTSIZE', (0, 3), (-1, 3), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#e63946')),
        ('LINEABOVE', (0, 3), (-1, 3), 1, colors.HexColor('#1d3557')),
        ('TOPPADDING', (0, 3), (-1, 3), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # Banking details
    elements.append(Paragraph("Banking Details", heading_style))
    
    banking_data = [
        ['Account Name:', 'BizPrint (Pty) Ltd'],
        ['Bank:', 'ABSA Bank'],
        ['Account Number:', '1234567890'],
        ['Branch Code:', '632005'],
        ['Reference:', f'Quote {design_request.id}'],
    ]
    
    banking_table = Table(banking_data, colWidths=[1.5*inch, 4*inch])
    banking_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3cd')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ffc107')),
    ]))
    elements.append(banking_table)
    elements.append(Spacer(1, 20))
    
    # Footer note
    footer_text = """
    <para align=center>
    <font size=8 color="#666666">
    © 2025 BizPrint. A Subsidiary of Ardent SA (Pty) Ltd.<br/>
    Terms of Service | Privacy Policy
    </font>
    </para>
    """
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
