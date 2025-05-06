from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import random
import os
from datetime import datetime

def generate_sample_data(num_rows):
    """Generate sample data for tables"""
    departments = ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance']
    statuses = ['Active', 'Pending', 'Completed', 'Delayed']
    
    data = [['ID', 'Department', 'Project', 'Status', 'Budget', 'Completion']]
    
    for i in range(num_rows):
        row = [
            f'PRJ{i+1:03d}',
            random.choice(departments),
            f'Project {i+1}',
            random.choice(statuses),
            f'${random.randint(10000, 100000):,}',
            f'{random.randint(0, 100)}%'
        ]
        data.append(row)
    return data

def create_table_style():
    """Create a consistent style for all tables"""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),  # Reduced font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),  # Reduced font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

def create_header(logo_path):
    """Create header with title and logo"""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,  # Reduced font size
        textColor=colors.black,
        spaceAfter=20
    )
    
    title = Paragraph("Sanction Letter", title_style)
    
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2*inch, height=0.8*inch)  # Slightly reduced logo size
    else:
        print(f"Warning: Logo file not found at {logo_path}")
        logo = Paragraph("", styles['Normal'])
    
    header_data = [[title, logo]]
    header_table = Table(header_data, colWidths=[5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    return header_table

def create_table_title(title_text):
    """Create styled table title"""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TableTitle',
        parent=styles['Heading2'],
        fontSize=11,  # Reduced font size
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=12,
        alignment=0
    )
    return Paragraph(title_text, title_style)

def create_signature_section():
    """Create signature boxes section in a single line"""
    # Define signature box content
    signature_boxes = [
        {'designation': 'Project Manager', 'name': 'Mr. XYZ'},
        {'designation': 'Finance Director', 'name': 'Mr. ABC'},
        {'designation': 'HR Manager', 'name': 'Ms. PQR'},
        {'designation': 'Technical Lead', 'name': 'Mr. LMN'}
    ]
    
    # Create a list to hold all signature boxes
    signature_tables = []
    
    for box in signature_boxes:
        # Create signature box data with smaller font
        normal_style = ParagraphStyle(
            'SignatureStyle',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=9,
            leading=12
        )
        
        data = [
            [Paragraph(f"<b>Designation:</b> {box['designation']}", normal_style)],
            [Paragraph(f"<b>Name:</b> {box['name']}", normal_style)],
            [Paragraph(f"<b>Date:</b> _________________", normal_style)],
            [Paragraph("<b>Signature:</b> _________________", normal_style)]
        ]
        
        # Create individual signature box
        sign_table = Table(data, colWidths=[1.8*inch])  # Reduced width
        sign_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        signature_tables.append(sign_table)
    
    # Create a table to hold all signature boxes in a single row
    signature_grid = Table(
        [signature_tables],
        colWidths=[1.8*inch] * 4,
        rowHeights=[1.2*inch]  # Reduced height
    )
    
    signature_grid.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    return signature_grid

def generate_pdf_report(filename, logo_path='company_logo.png'):
    """Generate PDF report with header, tables, and signature section"""
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch)
    elements = []
    
    # Add header
    header = create_header(logo_path)
    elements.append(header)
    
    # Add space after header
    elements.append(Spacer(1, 20))
    
    # Table titles
    table_titles = [
        "Table 1: Project Status Overview",
        "Table 2: Department Performance Summary",
        "Table 3: Budget Allocation Details",
        "Table 4: Project Completion Analysis"
    ]
    
    # Create 4 tables with different row counts
    table_rows = [7, 5, 8, 6]
    
    for i, (num_rows, title) in enumerate(zip(table_rows, table_titles), 1):
        elements.append(create_table_title(title))
        data = generate_sample_data(num_rows)
        table = Table(data, colWidths=[0.8*inch, 1.2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(create_table_style())
        elements.append(table)
    
    # Add space before signature section
    elements.append(Spacer(1, 30))
    
    # Add signature section
    signature_section = create_signature_section()
    elements.append(signature_section)
    
    # Build PDF
    doc.build(elements)

if __name__ == '__main__':
    # Generate the PDF report
    generate_pdf_report('project_report.pdf', 'image.png')