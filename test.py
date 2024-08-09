# from xhtml2pdf import pisa

# def generate_prescription_request_html(date, fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip, ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress, drCity, drState, drZip, drPhone, drFax, drNpi):
#     html_body = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Prior Authorization Prescription Request Form</title>
# </head>
# <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; font-size: 12px; max-width: 210mm; min-height: 297mm;">
#     <div style="text-align: center; margin-bottom: 20px;">
#         <h2 style="font-size: 18px;">PRIOR AUTHORIZATION PRESCRIPTION REQUEST FORM</h2>
#         <p>PLEASE SEND THIS FORM BACK IN 3 BUSINESS DAYS</p>
#         <p>WITH THE PT CHART NOTES ( RECENT MEDICAL RECORDS ) AND THE FAX COVER SHEET</p>
#     </div>
    
#     <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
#         <div style="border: 1px solid #000; padding: 10px;">
#             <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>Date: {date}</div>
#                 <div>First: {fname}</div>
#                 <div>Last: {lname}</div>
#             </div>
#             <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>DOB: {ptDob}</div>
#                 <div>Gender: {ptGender}</div>
#             </div>
#             <div style="margin-bottom: 5px;">Address: {ptAddress}</div>
#             <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>City: {ptCity}</div>
#                 <div>State: {ptState}</div>
#                 <div>Postal Code: {ptZip}</div>
#             </div>
#             <div style="margin-bottom: 5px;">Patient Phone Number: {ptPhone}</div>
#             <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>Primary Insurance: Medicare</div>
#                 <div>ID/HICN/MBI: {medID}</div>
#             </div>
#                      <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>Private Ins: </div>
#                 <div>Policy #:{medID}</div>
#             </div>
#             <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>Height: {ptHeight}</div>
#                 <div>Weight: {ptWeight}</div>
#             </div>
#         </div>
        
#         <div style="border: 1px solid #000; padding: 10px;">
#             <div style="margin-bottom: 5px;">Physician Name: {drName}</div>
#             <div style="margin-bottom: 5px;">NPI: {drNpi}</div>
#             <div style="margin-bottom: 5px;">Address: {drAddress}</div>
#             <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#                 <div>City: {drCity}</div>
#                 <div>State: {drState}</div>
#                 <div>Postal code: {drZip}</div>
#             </div>
#             <div style="margin-bottom: 5px;">Phone Number: {drPhone}</div>
#             <div style="margin-bottom: 5px;">Fax Number: {drFax}</div>
#         </div>
#     </div>
    
#     <div style="margin-top: 20px;">
#         <h3 style="font-size: 14px;">DIAGNOSIS: Provider can specify all of the diagnosis which they feel is appropriate</h3>
#         <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag1" name="diag1">
#             <label for="diag1">Primary osteoarthritis, right ankle and foot (M19.071)</label>
#         </div>
#         <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#         <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#         <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#                 <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#                 <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#                 <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#                 <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#                 <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
#         </div>
#                 <div style="margin-bottom: 5px;">
#             <input type="checkbox" id="diag2" name="diag2">
#             <label for="diag2">Sprain of unspecified ligament of right ankle (S93.401)</label>
#         </div>
        
#     </div>
    
#     <div style="border: 1px solid #000; padding: 10px; margin-top: 20px;">
#         <h3 style="font-size: 14px;">AFFECTED AREA</h3>
#         <div style="display: flex; justify-content: ;">
#             <div>
#                 <input type="checkbox" id="leftAnkle" name="leftAnkle">
#                 <label for="leftAnkle">Left ankle</label>
#             </div>
#             <div>
#                 <input type="checkbox" id="rightAnkle" name="rightAnkle">
#                 <label for="rightAnkle">Right Ankle</label>
#             </div>
#         </div>
#     </div>
    
#     <div style="border: 1px solid #000; padding: 10px; margin-top: 20px;">
#         <h3 style="font-size: 14px;">DISPENSE</h3>
#         <p>L1971: Ankle foot orthosis, plastic or other material with ankle joint, prefabricated, includes fitting and adjustment</p>
#         <p>Length of need is 99 months unless otherwise specified: _____ 99-99 (LIFETIME)</p>
#     </div>
    
#     <div style="border: 1px solid #000; padding: 10px; margin-top: 20px;">
#         <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
#             <div>Physician Signature: _________________________</div>
#             <div>Date signed: _________________________</div>
#         </div>
#         <div style="display: flex; justify-content: space-between;">
#             <div>Physician Name: {drName}</div>
#             <div>NPI: {drNpi}</div>
#         </div>
#     </div>
# </body>
# </html>
#     """
#     return html_body

# def convert_html_to_pdf(source_html, output_filename):
#     result_file = open(output_filename, "w+b")
#     pisa_status = pisa.CreatePDF(source_html, dest=result_file)
#     result_file.close()
#     return pisa_status.err

# # Example usage
# date = "08/01/2024"
# fname = "Leonard"
# lname = "Hoskins"
# ptPhone = "(502) 592-8750"
# ptAddress = "2215 Pikes Peak Blvd"
# ptCity = "Louisville"
# ptState = "KY"
# ptZip = "40214"
# ptDob = "11/14/1952"
# medID = "Med123456789"
# ptHeight = "5'1\""
# ptWeight = "168 lbs"
# ptGender = "Male"
# drName = "Dr. John Doe"
# drAddress = "123 Main Street"
# drCity = "Cityville"
# drState = "ST"
# drZip = "12345"
# drPhone = "(123) 456-7890"
# drFax = "(123) 456-7891"
# drNpi = "1234567890"

# html_content = generate_prescription_request_html(date, fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip, ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress, drCity, drState, drZip, drPhone, drFax, drNpi)

# pdf_filename = 'prescription_request.pdf'
# if convert_html_to_pdf(html_content, pdf_filename) == 0:
#     print(f"PDF generated successfully: {pdf_filename}")
# else:
#     print("Error generating PDF")



from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def create_pdf(filename, data):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    title = Paragraph("PRIOR AUTHORIZATION PRESCRIPTION REQUEST FORM FOR BACK ORTHOSIS", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    sub_title = Paragraph("PLEASE SEND THIS FORM BACK IN 3 BUSINESS DAYS<br/>"
                          "WITH THE PT CHART NOTES (RECENT MEDICAL RECORDS) AND THE FAX COVER SHEET", styles['Normal'])
    elements.append(sub_title)
    elements.append(Spacer(1, 12))

    # Table data
    table_data = [
        ["Date:", data['date'], "Physician Name:", data['drName']],
        ["First:", data['fName'], "NPI:", data['drNpi']],
        ["Last:", data['lName'], "Address:", data['drAddress']],
        ["DOB:", data['ptDob'], "City:", data['drCity']],
        ["Gender:", data['ptGender'], "State:", data['drState']],
        ["Address:", data['ptAddress'], "Postal Code:", data['drZip']],
        ["City:", data['ptCity'], "Phone Number:", data['drPhone']],
        ["State:", data['ptState'], "Fax Number:", data['drFax']],
        ["Postal Code:", data['ptZip'], "", ""],
        ["Patient Phone:", data['ptPhone'], "", ""],
        ["Primary Ins:", data['medIns'], "", ""],
        ["Policy #:", data['medId'], "", ""],
        ["Height:", data['ptHeight'], "", ""],
        ["Weight:", data['ptWeight'], "", ""]
    ]

    # Create table
    table = Table(table_data, colWidths=[100, 200, 100, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Diagnosis checkboxes (just text in this case)
    diagnosis_title = Paragraph("DIAGNOSIS: Provider can specify all of the diagnoses they feel are appropriate", styles['Normal'])
    elements.append(diagnosis_title)
    elements.append(Spacer(1, 12))

    diagnoses = ['Lumbar Intervertebral Disc Degeneration (M51.36)',
                 'Other intervertebral disc displacement, lumbar region (M51.26)',
                 'Spinal Stenosis, lumbar region (M48.06)',
                 'Spinal instability, lumbosacral region (M53.2X7)',
                 'Other intervertebral disc disorders, lumbosacral region (M51.87)',
                 'Low back pain (M54.5)']

    for diagnosis in diagnoses:
        elements.append(Paragraph(f'<bullet>&#x2610;</bullet> {diagnosis}', styles['Normal']))

    elements.append(Spacer(1, 12))

    # Affected Area
    affected_area_title = Paragraph("AFFECTED AREA", styles['Normal'])
    elements.append(affected_area_title)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph('<bullet>&#x2610;</bullet> Back', styles['Normal']))
    elements.append(Spacer(1, 12))

    # Dispense
    dispense_title = Paragraph("DISPENSE", styles['Normal'])
    elements.append(dispense_title)
    elements.append(Spacer(1, 12))

    dispense_text = ("L0457 - TLSO, flexible, provides trunk support, thoracic region, "
                     "rigid posterior panel and soft anterior apron, extends from the "
                     "sacrococcygeal junction and terminates just inferior to the scapular spine, "
                     "restricts gross trunk motion in the sagittal plane, produces intracavity pressure "
                     "to reduce load on the intervertebral discs, includes straps and closures, "
                     "prefabricated item that has been trimmed, bent, molded, assembled, or otherwise "
                     "customized to fit a specific patient by an individual with expertise.")
    elements.append(Paragraph(dispense_text, styles['Normal']))

    elements.append(Spacer(1, 24))

    # Footer
    elements.append(Paragraph("Length of need is 99 months unless otherwise specified: ____________ 99-99 (LIFETIME)", styles['Normal']))
    elements.append(Spacer(1, 48))

    signature_table = Table([
        ["Physician Name: " + data['drName'], "NPI: " + data['drNpi']],
        ["Physician Signature: ____________________", "Date signed: ____________________"]
    ], colWidths=[300, 300])

    elements.append(signature_table)

    # Build PDF
    doc.build(elements)

# Example usage
data = {
    'date': '08/09/2024',
    'fName': 'John',
    'lName': 'Doe',
    'ptDob': '01/01/1980',
    'ptGender': 'Male',
    'ptAddress': '1234 Elm Street',
    'ptCity': 'Springfield',
    'ptState': 'IL',
    'ptZip': '62701',
    'ptPhone': '555-1234',
    'medIns': 'Medicare',
    'medId': '123456',
    'ptHeight': '6ft',
    'ptWeight': '180lbs',
    'drName': 'Dr. Smith',
    'drNpi': '1234567890',
    'drAddress': '5678 Oak Street',
    'drCity': 'Springfield',
    'drState': 'IL',
    'drZip': '62701',
    'drPhone': '555-5678',
    'drFax': '555-6789'
}

create_pdf('prescription_request.pdf', data)
