import streamlit as st
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import random
import os
from datetime import datetime
import pandas as pd
from connector import *
import warnings
import numpy as np
import base64
warnings.filterwarnings("ignore")
from pathlib import Path

def read_pdf(file_path):
    """Read PDF file and return base64 encoded string"""
    try:
        # Read PDF file
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Encode to base64
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        return base64_pdf
    except FileNotFoundError:
        st.error(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# def read_pdf(file_path):
#     """Read PDF content using PyMuPDF."""
#     doc = fitz.open(file_path)
#     text = "\n".join([page.get_text() for page in doc])
#     return text


conn = create_mysql_engine("creds.json")
q_agg = '''SELECT ffa.name "Name",  fa.fid 'FID', fa.farmer_nid 'NID', ffa.phone "Phone Number",ffbr.fathers_name "Father/Husband",
fbi.bank_name "Bank Name" ,fbi.branch_name "Branch" ,fbi.routing_number "Rounting No." ,fbi.account_number "Account No.",
fa.guarantor_name "Guarantors' Name", fa.guarantor_nid "Guarantors' NID", fa.guarantor_phone "Guarantors' Phone",
fa.project_name "Project Name", ffa.project_duration "Project Duration",fa.loan_amt "Fund Requirement", fa.wegro_service "Wegro ROI (%%)", fa.bank_service "Bank ROI (%%)",fa.input_amt "Input Amount",
fhd.district "Area", fhd.name_en "FO Name" from f_aggrement fa 
left join f_bank_info fbi on fbi.nid = fa.farmer_nid 
left join f_farmers_assesment ffa on ffa.fid = fa.fid 
left join fo_hiararchy_details fhd on fhd.id = ffa.fo_id 
left join f_farmers_bank_requirement ffbr on ffbr.id = ffa.id  '''

df = pd.read_sql(q_agg, conn)

# project = 'Maize Harvest -  ভুট্টা'
# fo_name = 'Abdul Karim'
# area = 'Ullapara'

st.title("Sanction Letter Generator")

with st.sidebar:
    project = st.selectbox("Enter Project Name",df['Project Name'].unique())
    area = st.selectbox("Select Area", df['Area'].unique())
    fo_name = st.selectbox("Select FO Name", df['FO Name'].unique())
    farmers_nid = st.multiselect("Select Farmers NID", df[(df['Project Name']==project) & (df['FO Name']==fo_name)]['NID'].unique())
    groupname = st.text_input("Enter Group Name")
    prev = st.button("Preview")



df = df[(df['Project Name']==project) & (df['Area']==area) & (df['FO Name']==fo_name) & (df['NID'].isin(farmers_nid))]
rm_name = pd.read_sql(f"select * from fo_hiararchy_details where district  = '{area}' ", conn)['reporting_rm'].values[0]



df = df.drop_duplicates(subset=['NID','Project Name'])
df['SL'] = range(1, 1+len(df))

summary_table = pd.DataFrame(
    {   
        
        'Project': [project.split('-')[0]],
        'Wegro Center Name': [area],
        'FO Name': [fo_name],
        'Total Farmers': [len(df)],
        'Total Fund Requirement': [format(df['Fund Requirement'].sum(),',')],
    }
)


#### Farmer Details

df_farmer = df[['SL',"Name",'FID','NID','Phone Number',"Father/Husband",]]
df_farmer['Name'] = df_farmer['Name'].str.title()
df_farmer['Father/Husband'] = df_farmer['Father/Husband'].str.title()

df_bank = df[[ 'SL',"Name",'Bank Name','Branch','Rounting No.','Account No.']]
df_bank['Name'] = df_bank['Name'].str.title()
df_bank.columns = ['SL','Account Name','Bank Name','Branch','Routing No.','Account No.']

df_guarantor = df[['SL',"Guarantors' Name","Guarantors' NID","Guarantors' Phone"]]
df_guarantor['Guarantors\' Name'] = df_guarantor["Guarantors' Name"].str.title()
df_guarantor['QTY of Farmer Check'] = 1
df_guarantor['QTY of Guarantor Check'] = 1
df_guarantor.columns = ['SL',"Name","NID","Phone",'QTY of Farmer Check','QTY of Guarantor Check']


df_project = df[['SL','Project Name','Project Duration',"Fund Requirement", 'Input Amount','Wegro ROI (%)','Bank ROI (%)']]
df_project['Project Name'] = df_project['Project Name'].apply(lambda x: x.split(' - ')[0])


def df_to_list_of_lists(df):
    return [df.columns.tolist()] + df.values.tolist()

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
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # Reduced font size
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
        # spaceAfter=20
    )
    
    title = Paragraph("Sanction Letter", title_style)
    
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=1.3*inch)  # Slightly reduced logo size
    else:
        print(f"Warning: Logo file not found at {logo_path}")
        logo = Paragraph("", styles['Normal'])
    
    header_data = [[title, logo]]
    header_table = Table(header_data, colWidths=[5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
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
        spaceAfter=1,
        spaceBefore=1,
        alignment=1
    )
    return Paragraph(title_text, title_style)


def create_signature_section():
    """Create signature boxes section in a single line"""
    # Define signature box content
    signature_boxes = [
        {'designation': 'Checked by RM', 'name': f'{rm_name}'},
        {'designation': 'Reccomended by Coordinator', 'name': ' A K M MAHAMUDUNNOBI'},
        {'designation': 'Reccomended by HOO', 'name': 'Md Abu Helal Mostafa Zaman'},
        # {'designation': 'Technical Lead', 'name': 'Mr. LMN'}
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
            [Paragraph(f"<b>{box['designation']}</b>", normal_style)],
            [Paragraph(f"{box['name']}", normal_style)],
            [Paragraph(f"<b>Date:</b> _________________", normal_style)],
            [Paragraph("<b>Signature:</b> _________________", normal_style)]
        ]
        
        # Create individual signature box
        sign_table = Table(data, colWidths=[2.2*inch])  # Reduced width
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
        colWidths=[2.4*inch] * 3,
        rowHeights=[1.3*inch]  # Reduced height
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


def generate_pdf_report(filename, logo_path='wegrologo.JPG',groupname=groupname):
    """Generate PDF report with header, tables, and signature section"""
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0*inch,leftMargin=0.8*inch,rightMargin=0.8*inch,bottomMargin=0*inch)
    elements = []
    
    # Add header
    header = create_header(logo_path)
    elements.append(header)
    
    # Add space after header
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"<b>Group Name:</b> {groupname}",
        getSampleStyleSheet()['Normal']
    ))
    elements.append(Paragraph(
        f"<b>Sanction Date:</b> {pd.to_datetime('today').strftime('%d-%m-%Y')}",
        getSampleStyleSheet()['Normal']
    ))

    elements.append(Paragraph(
        f"<b>Disbursement Date:</b>________________",
        getSampleStyleSheet()['Normal']
    ))

    elements.append(Paragraph(
        f"Dear Sir,"
    ))

    elements.append(Paragraph(
        f"We are pleased to inform you that the application requesting funding for <b>{format(int(df['Fund Requirement'].sum()),',')} BDT</b> for <b>{len(df)}</b> farmers is hereby submitted to you for approval. The details of the sanctioned investment are as follows."
    ))

    elements.append(Spacer(1, 20))
    
    # Table titles
    table_titles = [
        "Summary",
        "Farmer Details",
        "Farmer Account Details",
        "Gurantor Details",
        "Project Details",
        # "Loan Details",
    ]

    coll_widths = [
        [1.6*inch, 1.4*inch, 1.5*inch, 1.5*inch, 1.5*inch],
        [0.2*inch, 1.5*inch, 1.5*inch, 1.6*inch, 1*inch, 1.7*inch],
        [0.2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch, 1.8*inch],
        [0.2*inch, 1.5*inch, 1.6*inch, 1*inch, 1.5*inch, 1.7*inch],
        [0.2*inch, 1.6*inch, 1.1*inch, 1.4*inch, 1.1*inch, 1*inch, 1.1*inch],
    ]
    
    # Create 4 tables with different row counts
    tabs  = [summary_table, df_farmer, df_bank, df_guarantor, df_project]
    
    for i, (num_rows, title,cwd) in enumerate(zip(tabs, table_titles,coll_widths), 1):
        elements.append(create_table_title(title))
        data = num_rows
        table = Table(df_to_list_of_lists(data), colWidths=cwd)
        table.setStyle(create_table_style())
        elements.append(table)
        elements.append(Spacer(1, 10))
    
    # Add space before signature section
    elements.append(Spacer(1, 30))
    
    # Add signature section
    signature_section = create_signature_section()
    elements.append(signature_section)

    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            "<b>Acceptance:</b> I, Faiyaz Safir, hereby accept the terms and conditions and approve fund disbursement for the project mentioned in this sanction letter.",
            getSampleStyleSheet()['Normal']
        )
    )
    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            "<b>Siganture with Date and Seal</b>",
            getSampleStyleSheet()['Normal']
        )
    )
    elements.append(
        Paragraph(
            "----------------------------------------",
            getSampleStyleSheet()['Normal']
        )
    )

    elements.append(
        Paragraph(
            "Faiyaz Safir",
            getSampleStyleSheet()['Normal']
        )
    )
    elements.append(
        Paragraph(
            "Chief Operating Officer",
            getSampleStyleSheet()['Normal']
        )
    )
    elements.append(
        Paragraph(
            "WeGro Technologies Limited",
            getSampleStyleSheet()['Normal']
        )
    )
    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            "<b>Siganture</b>: ___________________________",
            getSampleStyleSheet()['Normal']
        )
    )

    elements.append(
        Paragraph(
            "<b>Date</b>: ___________________________",
            getSampleStyleSheet()['Normal']
        )
    )
    
    # Build PDF
    doc.build(elements)

if prev:
    # file_no = np.random.randint(1,999999999)
    st.header("Summary")
    st.write(summary_table)
    st.header("Farmer Details")
    st.write(df_farmer)
    st.header("Bank Details")
    st.write(df_bank)
    st.header("Guarantor Details")
    st.write(df_guarantor)
    st.header("Project Details")
    st.write(df_project)
    file_no = np.random.randint(1,999999999)
    generate_pdf_report(f"temp/{rm_name}_{file_no}.pdf", 'logo.png')
    pdf_data = read_pdf(f"temp/{rm_name}_{file_no}.pdf")
    # generate_pdf_report(f"temp/{rm_name}_{file_no}.pdf", 'logo.png')
    

    st.download_button(
                label="Download PDF",
                data=base64.b64decode(pdf_data),
                file_name="sanction_letter.pdf",
                mime="application/pdf"
            )




# pdf_text = read_pdf(f"temp/{rm_name}_{file_no}")
# st.text_area("Extracted Text", pdf_text, height=300)
# download = st.button("Download Sanction Letter")

# with open(f"temp/{rm_name}_{file_no}", "rb") as f:
#     pdf_bytes = f.read()

# st.download_button(
#     label="Download PDF",
#     data=pdf_bytes,
#     file_name="downloaded.pdf",
#     mime="application/pdf"
# )