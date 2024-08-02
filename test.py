

import json
import io
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyPDF2 import PdfMerger, PdfReader

# # Define SCOPES
# SCOPES = ["https://www.googleapis.com/auth/drive"]

# # Load credentials from secrets
# credentials_json = st.secrets["google_credentials"]["credentials_json"]

# # Function to update st.secrets
# def update_secrets(key, value):
#     st.secrets[key] = value

# def get_drive_service(creds):
#     return build('drive', 'v3', credentials=creds)

# def generate_and_upload_token():
#     try:
#         # Generate credentials and token
#         flow = InstalledAppFlow.from_client_config(
#             json.loads(credentials_json), SCOPES
#         )
#         creds = flow.run_local_server(port=0)
        
#         # Save token to Streamlit secrets
#         token_json = creds.to_json()
#         update_secrets("google_credentials.token_json", token_json)
        
#         print('Token generated and saved to Streamlit secrets successfully!')
#         return creds
#     except Exception as e:
#         print(f'Error generating token: {e}')
#         return None

# def get_credentials():
#     token_data = st.secrets["google_credentials"].get("token_json")
    
#     if token_data:
#         creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
#     else:
#         creds = generate_and_upload_token()
#         if not creds:
#             return None
    
#     return creds

# def combine_pdfs(fname):
#     creds = get_credentials()
#     if not creds:
#         return None, "Failed to obtain valid credentials. Please try authenticating again."

#     try:
#         service = get_drive_service(creds)
#         folder_id = "15I95Loh35xI2PcGa36xz7SgMtclo-9DC"
#         query = f"'{folder_id}' in parents"

#         print("Querying Google Drive...")
#         results = service.files().list(q=query, pageSize=20, fields="nextPageToken, files(id, name, mimeType)").execute()
#         items = results.get("files", [])

#         if not items:
#             return None, "No files found in the specified folder."

#         fname = fname.strip().lower()
#         target_files = [file for file in items if fname in file["name"].lower()]

#         print(f"Searching for files with name containing: {fname}")
#         for file in items:
#             print(f"Found file: {file['name']}")

#         if not target_files:
#             return None, "No matching files found."

#         print(f"Found {len(target_files)} matching files. Combining PDFs...")

#         merger = PdfMerger()
#         for target_file in target_files:
#             mime_type = target_file.get("mimeType")
#             file_id = target_file.get("id")

#             print(f"Processing file: {target_file['name']}")

#             if mime_type.startswith("application/vnd.google-apps."):
#                 request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
#             else:
#                 request = service.files().get_media(fileId=file_id)

#             fh = io.BytesIO()
#             downloader = MediaIoBaseDownload(fh, request)
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 print(f"Download {int(status.progress() * 100)}%")
#             fh.seek(0)

#             pdf_reader = PdfReader(fh)
#             merger.append(pdf_reader)

#         print("Finalizing PDF...")
#         output = io.BytesIO()
#         merger.write(output)
#         merger.close()
#         output.seek(0)
#         print("PDF combination complete!")

#         return output, None
#     except Exception as error:
#         print(f"An error occurred: {str(error)}")
#         return None, str(error)

# # Streamlit UI
# st.header("Combine PDFs")

# doctor_name = st.text_input("Enter Doctor Name for PDF combination")
# if st.button("Combine PDFs"):
#     if doctor_name:
#         with st.spinner("Combining PDFs..."):
#             combined_pdf, error = combine_pdfs(doctor_name)
#             if error:
#                 st.error(f"Error combining PDFs: {error}")
#             elif combined_pdf:
#                 st.success(f"Combined PDF for {doctor_name} created successfully.")
#                 st.session_state['combined_pdf'] = combined_pdf
#                 st.session_state['doctor_name'] = doctor_name
#                 st.experimental_rerun()
#             else:
#                 st.error("Failed to create combined PDF. Please try again.")
#     else:
#         st.warning("Please enter a doctor name for PDF combination.")

# if 'combined_pdf' in st.session_state:
#     st.download_button(
#         label="Download Combined PDF",
#         data=st.session_state['combined_pdf'].getvalue(),
#         file_name=f"{st.session_state['doctor_name']}_combined.pdf",
#         mime="application/pdf"
#     )
#     st.success("Combined PDF is ready for further processing (e.g., sending faxes).")




# import streamlit as st
# import pdfkit
# from datetime import datetime
# from pdfkit import configuration, from_string

# config = configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
# # Define the list of braces
# Braces = ["Ankle", "Knee", "Back", "Wrist", "Shoulder", "Elbow", "Hips"]

# # Initialize selected_forms dictionary
# selected_forms = {}

# def display_brace(brace, column):
#     if brace not in st.session_state:
#         st.session_state[brace] = "None"

#     with column:
#         st.subheader(f"{brace} Brace")
#         brace_options = ["None", "Selected"]
#         selected_forms[brace] = st.radio(
#             f"Select {brace} Brace",
#             brace_options,
#             key=brace,
#             index=brace_options.index(st.session_state[brace])
#         )

# def validate_all_fields():
#     required_fields = [
#         fname, lname, ptPhone, ptAddress,
#         ptCity, ptState, ptZip, ptDob, medID,
#         ptHeight, ptWeight, drName,
#         drAddress, drCity, drState, drZip,
#         drPhone, drFax, drNpi
#     ]
#     for field in required_fields:
#         if not field:
#             st.warning(f"{field} is required.")
#             return False
#     return True

# def generate_prescription_request_html(date, fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip, ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress, drCity, drState, drZip, drPhone, drFax, drNpi, selected_braces):
#     html_body = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Prior Authorization Prescription Request Form</title>
# </head>
# <body style="font-family: Arial, sans-serif; line-height: 1.4; padding: 10px; font-size: 10px; width: 210mm; height: 297mm;">

#     <div style="text-align: center; margin-bottom: 15px;">
#         <h2 style="font-size: 16px; margin: 0;">PRIOR AUTHORIZATION PRESCRIPTION REQUEST FORM</h2>
#         <p style="margin: 0;">PLEASE SEND THIS FORM BACK IN 3 BUSINESS DAYS</p>
#         <p style="margin: 0;">WITH THE PT CHART NOTES (RECENT MEDICAL RECORDS) AND THE FAX COVER SHEET</p>
#     </div>

#     <div style="border: 1px solid #000; padding: 5px; display: flex; justify-content: space-between; font-size: 10px; width: 100%; box-sizing: border-box;">
#         <div style="width: 32%;">Date: {date}</div>
#         <div style="width: 32%;">First: {fname}</div>
#         <div style="width: 32%;">Last: {lname}</div>
#     </div>

#     <div style="display: flex; justify-content: space-between; margin-top: 10px;">
#         <div style="width: 48%; border: 1px solid #000; padding: 5px;">
#             <div>DOB: {ptDob}</div>
#             <div>Gender: {ptGender}</div>
#             <div>Address: {ptAddress}</div>
#             <div>City: {ptCity}</div>
#             <div>State: {ptState}</div>
#             <div>Postal Code: {ptZip}</div>
#             <div>Patient Phone Number: {ptPhone}</div>
#             <div>Primary Insurance: Medicare</div>
#             <div>ID/HICN/MBI: {medID}</div>
#             <div>Private Ins:</div>
#             <div>Policy #: {medID}</div>
#             <div>Height: {ptHeight}</div>
#             <div>Weight: {ptWeight}</div>
#         </div>

#         <div style="width: 48%; border: 1px solid #000; padding: 5px;">
#             <div>Physician Name: {drName}</div>
#             <div>NPI: {drNpi}</div>
#             <div>Address: {drAddress}</div>
#             <div>City: {drCity}</div>
#             <div>State: {drState}</div>
#             <div>Postal Code: {drZip}</div>
#             <div>Phone Number: {drPhone}</div>
#             <div>Fax Number: {drFax}</div>
#         </div>
#     </div>

#     <h3 style="font-size: 12px; margin-top: 15px;">DIAGNOSIS: Provider can specify all of the diagnoses they feel are appropriate</h3>
#     <div style="display: flex; flex-wrap: wrap;">
#         <div style="width: 48%; margin-bottom: 5px;">
#             <input type="checkbox" id="diag1" name="diag1">
#             <label for="diag1">Primary osteoarthritis, right ankle and foot (M19.071)</label>
#         </div>
#         <div style="width: 48%; margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#         <div style="width: 48%; margin-bottom: 5px;">
#             <input type="checkbox" id="diag3" name="diag3">
#             <label for="diag3">Sprain of unspecified ligament of right ankle (S93.401)</label>
#         </div>
#         <!-- Add more diagnosis options as needed -->
#     </div>

#     <div style="border: 1px solid #000; padding: 5px; margin-top: 15px;">
#         <h3 style="font-size: 12px;">AFFECTED AREA</h3>
#         <div style="display: flex; justify-content: space-between;">
#             <div>
#                 <input type="checkbox" id="leftAnkle" name="leftAnkle">
#                 <label for="leftAnkle">Left ankle</label>
#             </div>
#             <div>
#                 <input type="checkbox" id="rightAnkle" name="rightAnkle">
#                 <label for="rightAnkle">Right ankle</label>
#             </div>
#         </div>
#     </div>

#     <div style="border: 1px solid #000; padding: 5px; margin-top: 15px;">
#         <h3 style="font-size: 12px;">DISPENSE</h3>
#         <p>L1971: Ankle foot orthosis, plastic or other material with ankle joint, prefabricated, includes fitting and adjustment</p>
#         <p>Length of need is 99 months unless otherwise specified: _____ 99-99 (LIFETIME)</p>
#     </div>

#     <div style="border: 1px solid #000; padding: 5px; margin-top: 15px; display: flex; justify-content: space-between;">
#         <div>Physician Signature: _________________________</div>
#         <div>Date signed: _________________________</div>
#     </div>
#     <div style="border: 1px solid #000; padding: 5px; display: flex; justify-content: space-between;">
#         <div>Physician Name: {drName}</div>
#         <div>NPI: {drNpi}</div>
#     </div>

#     <div style="border: 1px solid #000; padding: 5px; margin-top: 15px;">
#         <h3 style="font-size: 12px;">Selected Braces</h3>
#         <ul>
#     """
    
#     for brace in selected_braces:
#         html_body += f"<li>{brace} Brace</li>"
    
#     html_body += """
#         </ul>
#     </div>
# </body>
# </html>
#     """
    
#     return html_body


# # Streamlit app
# st.title("Brace Form Submission")

# st.header("Patient and Doctor Information")
# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("Patient Information")
#     date = st.date_input("Date")
#     fname = st.text_input("First Name")
#     lname = st.text_input("Last Name")
#     ptPhone = st.text_input("Patient Phone Number")
#     ptAddress = st.text_input("Patient Address")
#     ptCity = st.text_input("Patient City")
#     ptState = st.text_input("Patient State")
#     ptZip = st.text_input("Patient Zip Code")
#     ptDob = st.text_input("Date of Birth")
#     medID = st.text_input("MBI")
#     ptHeight = st.text_input("Height")
#     ptWeight = st.text_input("Weight")
#     ptGender = st.selectbox("Gender", ["Male", "Female"])

# with col2:
#     st.subheader("Doctor Information")
#     drName = st.text_input("Doctor Name")
#     drAddress = st.text_input("Doctor Address")
#     drCity = st.text_input("Doctor City")
#     drState = st.text_input("Doctor State")
#     drZip = st.text_input("Doctor Zip Code")
#     drPhone = st.text_input("Doctor Phone Number")
#     drFax = st.text_input("Doctor Fax Number")
#     drNpi = st.text_input("Doctor NPI")

# st.header("Select Braces")
# col1, col2, col3, col4 = st.columns(4)
# col5, col6, col7 = st.columns(3)

# # Display the first 4 braces in the first row
# for idx, brace in enumerate(Braces[:4]):
#     display_brace(brace, [col1, col2, col3, col4][idx])

# # Display the remaining 3 braces in the second row
# for idx, brace in enumerate(Braces[4:]):
#     display_brace(brace, [col5, col6, col7][idx])

# if st.button("Submit"):
#     if not validate_all_fields():
#         st.warning("Please fill out all required fields.")
#     else:
#         selected_braces = [brace for brace, selection in selected_forms.items() if selection == "Selected"]

#         if not selected_braces:
#             st.warning("Please select at least one brace.")
#         else:
#             # Generate HTML content
#             html_content = generate_prescription_request_html(
#                 date.strftime("%m/%d/%Y"), fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip,
#                 ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress, drCity, drState,
#                 drZip, drPhone, drFax, drNpi, selected_braces
#             )

#             # Convert HTML to PDF
#             options = {
#     'page-size': 'A4',
#     'margin-top': '0.75in',
#     'margin-right': '0.75in',
#     'margin-bottom': '0.75in',
#     'margin-left': '0.75in',
#     'encoding': "UTF-8",
#     'no-outline': None
# }
#             pdf_filename = f"prescription_request_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
#             from_string(html_content, pdf_filename, configuration=config , options=options)

#             # Provide download link for the generated PDF
#             with open(pdf_filename, "rb") as pdf_file:
#                 pdf_bytes = pdf_file.read()
#                 st.download_button(
#                     label="Download Prescription Request PDF",
#                     data=pdf_bytes,
#                     file_name=pdf_filename,
#                     mime="application/pdf"
#                 )

#             st.success(f"Prescription request for {', '.join(selected_braces)} brace(s) has been generated. Click the button above to download the PDF.")



from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_prescription_request_pdf(date, fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip, ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress, drCity, drState, drZip, drPhone, drFax, drNpi):
    pdf_filename = f"prescription_request_{date.replace('/', '')}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle('Header', fontSize=10, leading=12, alignment=1)
    elements.append(Paragraph("PRIOR AUTHORIZATION PRESCRIPTION REQUEST FORM FOR Back orthotic", header_style))
    elements.append(Paragraph("PLEASE SEND THIS FORM BACK IN 3 BUSINESS DAYS", header_style))
    elements.append(Paragraph("Note:- Fax: +1 (888) 831-8047       Phone: +1 (786) 391-3722", header_style))
    elements.append(Paragraph("WITH THE PT CHART NOTES (RECENT MEDICAL RECORDS) AND THE FAX COVER SHEET", header_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Patient and Physician Information
    data = [
        [f"Date: {date}", "", f"Physician Name: {drName}"],
        [f"First: {fname}", f"Last: {lname}", f"NPI: {drNpi}"],
        [f"DOB: {ptDob}", f"Gender: {ptGender}", f"Address: {drAddress}"],
        [f"Address: {ptAddress}", "", f"City: {drCity}"],
        [f"City: {ptCity}", "", f"State: {drState}"],
        [f"State: {ptState}", "", f"Postal code: {drZip}"],
        [f"Postal Code: {ptZip}", "", f"Phone Number: {drPhone}"],
        [f"Patient Phone Number: {ptPhone}", "", f"Fax Number: {drFax}"],
        [f"Primary Ins: Medicare", f"Policy #: {medID}", ""],
        [f"Private Ins:", "Policy #", ""],
        [f"Height: {ptHeight}", f"Weight: {ptWeight}", ""]
    ]
    
    t = Table(data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t)
    
    # Additional text
    elements.append(Spacer(1, 0.1*inch))
    additional_text = """This patient is being treated under a comprehensive plan of care for breast pain.
I, the undersigned, certify that the prescribed orthosis is medically necessary for the patient's overall well-being. In my opinion, the following
medical product are both reasonable and necessary in reference to treatment of the patient's condition and/or illness. All statements contained
has been in care regarding the diagnosis below. This is the treatment I see fit for this patient at this time. I certify that this information is true
and correct."""
    elements.append(Paragraph(additional_text, ParagraphStyle('Small', fontSize=6, leading=8)))
    
    # Diagnosis section
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("DIAGNOSIS:Provider can simply cut off the diagnosis which they don't find appropriate", ParagraphStyle('Small', fontSize=8, leading=10)))
    
    diagnosis_data = [
        ["□ Lumbar/ Lumbosacral Intervertebral Disc Degeneration (M51.36)"],
        ["□ Other intervertebral disc degeneration, lumbosacral region (M51.37)"],
        ["□ Spinal Stenosis, lumbar region(M48.06)"],
        ["□ Spinal stenosis, lumbosacral region (M48.07)"],
        ["□ Other Intervertebral disc disorders, lumbosacral region (M51.87)"],
        ["□ Low back pain (M54.5)"]
    ]
    
    diagnosis_table = Table(diagnosis_data, colWidths=[7*inch])
    diagnosis_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(diagnosis_table)
    
    # Affected Area
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("AFFECTED AREA:", ParagraphStyle('Small', fontSize=8, leading=10)))
    elements.append(Paragraph("☑ Back", ParagraphStyle('Small', fontSize=8, leading=10)))
    
    # Dispensing
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("DISPENSE:", ParagraphStyle('Small', fontSize=8, leading=10)))
    elements.append(Paragraph("L0457 - lumbar-Sacral Orthosis, Sagittal-Coronal Control, With Rigid Anterior And Posterior Frame/Panel(S), Posterior Extends From Sacrococcygeal Junction To T-9 Vertebra, Lateral Strength Provided By Rigid Lateral Frame/Panel(S), Produces Intracavitary Pressure To Reduce Load On Intervertebral Discs, Includes Straps, Closures, May Include Padding, Shoulder Straps, Pendulous Abdomen Design, Prefabricated, Off-The-Shelf", ParagraphStyle('Small', fontSize=8, leading=10)))
    
    # Length of need
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("Length of need is 99 months unless otherwise specified _____________ 6 - 99 (99= LIFETIME)", ParagraphStyle('Small', fontSize=8, leading=10)))
    
    # Signature
    elements.append(Spacer(1, 0.5*inch))
    signature_data = [
        ["Physician Signature: _________________________", "Date signed: _____________"],
        [f"Physician Name: {drName}", f"NPI: {drNpi}"]
    ]
    signature_table = Table(signature_data, colWidths=[3.5*inch, 3.5*inch])
    signature_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(signature_table)
    
    doc.build(elements)
    return pdf_filename

# Example usage
pdf_file = generate_prescription_request_pdf(
    "08/01/2024", "Leonard", "Hoskins", "(502) 592-8750", "2215 Pikes Peak Blvd", "Louisville", "KY", "40214", "11/14/1952", "1DVODN6EG39",
    "5'1", "250", "Male", "Dr. Lal Tanwani, MD", "1900 Bluegrass Ave # 108", "Louisville", "KY", "40215", "(502) 361-2524", "(502) 361-2525", "1336133347"
)
print(f"PDF generated: {pdf_file}")


