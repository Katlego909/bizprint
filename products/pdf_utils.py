"""
PDF generation utilities for order invoices using ReportLab
"""
from io import BytesIO
from decimal import Decimal
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from django.conf import settings
import os


def generate_order_invoice_pdf(order):
    """
    Generate a professional PDF invoice for an order
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
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 12))
    
    # Invoice details
    invoice_info = [
        ['Invoice #:', str(order.uuid)[:8].upper()],
        ['Date:', order.created_at.strftime('%d %B %Y')],
        ['Payment Status:', order.get_status_display()],
    ]
    
    invoice_table = Table(invoice_info, colWidths=[1.5*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1d3557')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Client information
    elements.append(Paragraph("Billed To:", heading_style))
    
    client_info = [
        ['Name:', order.full_name],
        ['Email:', order.email],
    ]
    
    if order.phone:
        client_info.append(['Phone:', order.phone])
    if order.address:
        client_info.append(['Address:', order.address])
    
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
    elements.append(Spacer(1, 30))
    
    # Order details
    elements.append(Paragraph("Order Details", heading_style))
    
    # Build order items table
    order_data = [['Item', 'Quantity', 'Price (R)']]
    
    # Product
    order_data.append([
        order.product.name,
        str(order.quantity),
        f"{order.base_price:.2f}"
    ])
    
    # Options
    if order.options:
        for opt_type, opt_value in order.options.items():
            order_data.append([
                f"  • {opt_type}: {opt_value}",
                '',
                ''
            ])
    
    # Services
    if order.services:
        for service in order.services:
            order_data.append([
                f"  • {service}",
                '',
                ''
            ])
    
    order_table = Table(order_data, colWidths=[3.5*inch, 1*inch, 1.5*inch])
    order_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d3557')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        
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
    elements.append(order_table)
    elements.append(Spacer(1, 20))
    
    # Calculate totals
    vat_amount = order.total_price * Decimal("0.15") / Decimal("1.15")
    taxable_total = order.total_price - vat_amount
    product_subtotal = taxable_total - order.shipping_price + order.discount_amount
    
    # Totals
    totals_data = [
        ['Subtotal:', f"R {product_subtotal:.2f}"],
    ]
    
    if order.shipping_price > 0:
        totals_data.append(['Shipping:', f"R {order.shipping_price:.2f}"])
    
    if order.discount_amount > 0:
        totals_data.append(['Discount:', f"-R {order.discount_amount:.2f}"])
    
    totals_data.extend([
        ['VAT (15%):', f"R {vat_amount:.2f}"],
        ['', ''],  # Spacer row
        ['Total:', f"R {order.total_price:.2f}"],
    ])
    
    totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#e63946')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1d3557')),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # Payment status box
    if order.status == 'received':
        status_text = """
        <para align=center>
        <font size=11 color="#856404">
        <b>Payment Pending</b><br/>
        Please make payment via EFT using the details below.
        </font>
        </para>
        """
        elements.append(Paragraph(status_text, normal_style))
        elements.append(Spacer(1, 20))
    
    # Banking details (if payment pending)
    if order.status == 'received':
        elements.append(Paragraph("Banking Details", heading_style))
        
        banking_data = [
            ['Account Name:', 'BizPrint'],
            ['Bank:', 'Capitec Bank'],
            ['Account Number:', '2482418611'],
            ['Branch Code:', '470010'],
            ['Reference:', f'INV{str(order.uuid)[:8].upper()}'],
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
