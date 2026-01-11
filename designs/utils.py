from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_design_quote_pdf(design_request, subtotal, vat, total):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Company Logo (assuming it's in static files)
    # You might need to adjust the path to your logo
    logo_path = 'static/images/bp-logo-1.png'
    try:
        story.append(Paragraph(f'<img src="{logo_path}" width="150" height="auto"/>', styles['Normal']))
    except:
        story.append(Paragraph("BizPrint", styles['h1']))
    story.append(Paragraph("<br/><br/>", styles['Normal']))

    # Header
    story.append(Paragraph("<b>QUOTATION</b>", styles['h1']))
    story.append(Paragraph(f"<b>Quote #:</b> {design_request.id}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {design_request.created_at.strftime('%d %b %Y')}", styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))

    # Prepared For
    prepared_for = design_request.user.get_full_name() if design_request.user else design_request.full_name or "Guest"
    email = design_request.user.email if design_request.user else design_request.email
    phone = design_request.user.profile.phone if design_request.user and design_request.user.profile.phone else design_request.phone

    story.append(Paragraph("<b>Prepared For:</b>", styles['h2']))
    story.append(Paragraph(prepared_for, styles['Normal']))
    story.append(Paragraph(email, styles['Normal']))
    if phone:
        story.append(Paragraph(phone, styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))

    # Line Items
    data = [['Package', 'Price (R)']]
    for pkg in design_request.packages.all():
        data.append([pkg.title, f"R{pkg.price:.2f}"])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'), # Align prices to right
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    table = Table(data)
    table.setStyle(table_style)
    story.append(table)
    story.append(Paragraph("<br/>", styles['Normal']))

    # Totals
    story.append(Paragraph(f"<b>Subtotal:</b> R{subtotal:.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>VAT (15%):</b> R{vat:.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Total:</b> R{total:.2f}", styles['h2']))
    story.append(Paragraph("<br/>", styles['Normal']))

    # Banking Details
    story.append(Paragraph("<b>Banking Details:</b>", styles['h2']))
    story.append(Paragraph("Account Name: BizPrint (Pty) Ltd", styles['Normal']))
    story.append(Paragraph("Bank: ABSA Bank", styles['Normal']))
    story.append(Paragraph("Account Number: 1234567890", styles['Normal']))
    story.append(Paragraph("Branch Code: 632005", styles['Normal']))
    story.append(Paragraph(f"Reference: Quote {design_request.id}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_design_invoice_pdf(design_request, subtotal, vat, total):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Company Logo (assuming it's in static files)
    logo_path = 'static/images/bp-logo-1.png'
    try:
        story.append(Paragraph(f'<img src="{logo_path}" width="150" height="auto"/>', styles['Normal']))
    except:
        story.append(Paragraph("BizPrint", styles['h1']))
    story.append(Paragraph("<br/><br/>", styles['Normal']))

    # Header
    story.append(Paragraph("<b>INVOICE</b>", styles['h1']))
    story.append(Paragraph(f"<b>Invoice #:</b> {design_request.id}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {design_request.created_at.strftime('%d %b %Y')}", styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))

    # Prepared For
    prepared_for = design_request.user.get_full_name() if design_request.user else design_request.full_name or "Guest"
    email = design_request.user.email if design_request.user else design_request.email
    phone = design_request.user.profile.phone if design_request.user and design_request.user.profile.phone else design_request.phone

    story.append(Paragraph("<b>Prepared For:</b>", styles['h2']))
    story.append(Paragraph(prepared_for, styles['Normal']))
    story.append(Paragraph(email, styles['Normal']))
    if phone:
        story.append(Paragraph(phone, styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))

    # Line Items
    data = [['Package', 'Price (R)']]
    for pkg in design_request.packages.all():
        data.append([pkg.title, f"R{pkg.price:.2f}"])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'), # Align prices to right
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    table = Table(data)
    table.setStyle(table_style)
    story.append(table)
    story.append(Paragraph("<br/>", styles['Normal']))

    # Totals
    story.append(Paragraph(f"<b>Subtotal:</b> R{subtotal:.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>VAT (15%):</b> R{vat:.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Total:</b> R{total:.2f}", styles['h2']))
    story.append(Paragraph("<br/>", styles['Normal']))

    # Payment Status
    story.append(Paragraph(f"<b>Payment Status:</b> {design_request.get_status_display()}", styles['h2']))
    story.append(Paragraph("<br/>", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer