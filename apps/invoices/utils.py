from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from django.conf import settings
import os


def generate_invoice_pdf(invoice):
    """Generate PDF for invoice with company branding"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Build content
    content = []
    
    # Company Header
    content.append(Paragraph("INVOICE", title_style))
    content.append(Spacer(1, 20))
    
    # Invoice Info Table
    invoice_info_data = [
        ['Invoice Number:', invoice.invoice_number],
        ['Invoice Date:', invoice.invoice_date.strftime('%B %d, %Y')],
        ['Due Date:', invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'No Due Date'],
        ['Status:', invoice.get_status_display()],
    ]
    
    invoice_info_table = Table(invoice_info_data, colWidths=[2*inch, 2*inch])
    invoice_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(invoice_info_table)
    content.append(Spacer(1, 20))
    
    # Bill To Section
    content.append(Paragraph("Bill To:", header_style))
    bill_to_parts = [f"<b>{invoice.client_name}</b>"]
    if invoice.client_phone:
        bill_to_parts.append(invoice.client_phone)
    if invoice.client_email:
        bill_to_parts.append(invoice.client_email)
    if invoice.client_address:
        bill_to_parts.append(invoice.client_address)
    
    bill_to_text = "<br/>".join(bill_to_parts)
    content.append(Paragraph(bill_to_text, normal_style))
    content.append(Spacer(1, 20))
    
    # Items Table
    items_data = [['Product/Service', 'Description', 'Qty', 'Unit Price', 'Total']]
    
    for item in invoice.items.all():
        items_data.append([
            item.product_service or '[No Product/Service]',
            item.description or '[No Description]',
            str(item.quantity),
            f"₦{item.unit_price:,.2f}",
            f"₦{item.line_total:,.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[1.5*inch, 1.5*inch, 0.7*inch, 1.15*inch, 1.15*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Right align quantity, price, total
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),   # Left align product/service and description
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    content.append(items_table)
    content.append(Spacer(1, 20))
    
    # Totals Table
    totals_data = [
        ['Subtotal:', f"₦{invoice.subtotal:,.2f}"],
        ['Tax:', f"₦{invoice.total_tax:,.2f}"],
        ['Discount:', f"-₦{invoice.total_discount:,.2f}"],
        ['Shipping:', f"₦{invoice.shipping_fee:,.2f}"],
        ['Other Charges:', f"₦{invoice.other_charges:,.2f}"],
        ['', ''],  # Separator
        ['Grand Total:', f"₦{invoice.grand_total:,.2f}"],
        ['Amount Paid:', f"₦{invoice.amount_paid:,.2f}"],
        ['Balance Due:', f"₦{invoice.balance_due:,.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[2*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        
        # Grand Total row
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 6), (-1, 6), 12),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 6), (-1, 6), colors.whitesmoke),
        
        # Balance Due row
        ('FONTNAME', (0, 8), (-1, 8), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 8), (-1, 8), 12),
        ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 8), (-1, 8), colors.whitesmoke),
        
        # Grid for important rows
        ('GRID', (0, 6), (-1, 6), 1, colors.black),
        ('GRID', (0, 8), (-1, 8), 1, colors.black),
    ]))
    
    content.append(totals_table)
    
    # Notes section
    if invoice.notes:
        content.append(Spacer(1, 20))
        content.append(Paragraph("Notes:", header_style))
        content.append(Paragraph(invoice.notes, normal_style))
    
    # Footer
    content.append(Spacer(1, 30))
    footer_text = "Thank you for your business!"
    content.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d')
    )))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()
