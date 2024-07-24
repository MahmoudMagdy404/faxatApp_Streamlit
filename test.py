import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

def handle_faxplus(uploaded_file, receiver_number, fax_message, fax_subject, to_name, chaser_name, sender_email, sender_password):
    try:
        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = f"{receiver_number}@fax.plus"
        msg['Subject'] = fax_subject
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fax Cover Sheet</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                }}
                h1 {{
                    font-size: 24px;
                    margin-bottom: 20px;
                }}
                .section {{
                    margin-bottom: 15px;
                }}
                .label {{
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h1>FAX</h1>
            <div class="section">
                <div class="label">To:</div>
                Name: {to_name},<br>
                Fax number: {receiver_number}
            </div>
            <div class="section">
                <div class="label">From:</div>
                Name: {chaser_name},<br>
                Fax number: {sender_email}
            </div>
            <div class="section">
                <div class="label">Number of pages:</div>
                2
            </div>
            <div class="section">
                <div class="label">Subject:</div>
                {fax_subject}
            </div>
            <div class="section">
                <div class="label">Date:</div>
                {datetime.now().strftime('%Y-%m-%d')}
            </div>
            <div class="section">
                <div class="label">Message:</div>
                <p>{fax_message}</p>
            </div>
        </body>
        </html>
        """
        
        # Add the HTML body as the cover sheet
        body = MIMEText(html_body, 'html')
        msg.attach(body)
        
        # # Attach the cover sheet if provided
        # if uploaded_cover_sheet:
        #     cover_sheet = MIMEApplication(uploaded_cover_sheet.getvalue())
        #     cover_sheet.add_header('Content-Disposition', 'attachment; filename="cover_sheet.pdf"')
        #     msg.attach(cover_sheet)

        # Attach the main document
        main_document = MIMEApplication(uploaded_file.getvalue())
        main_document.add_header('Content-Disposition', 'attachment; filename="fax_document.pdf"')
        msg.attach(main_document)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        st.success(f"Fax sent successfully to {receiver_number}")
    
    except Exception as e:
        st.error(f"Failed to send fax: {e}")

# Streamlit UI
st.title("Send Fax using Fax.Plus Email")

uploaded_file = st.file_uploader("Upload Fax Document", type=["pdf", "docx", "png", "jpg"])
# uploaded_cover_sheet = st.file_uploader("Upload Cover Sheet (Optional)", type=["pdf", "docx", "png", "jpg"])
receiver_number = st.text_input("Receiver Number")
fax_message = st.text_area("Fax Message")
fax_subject = st.text_input("Fax Subject")
to_name = st.text_input("To Name")
chaser_name = st.text_input("Chaser Name")
sender_email = "jimmyross.incall@gmail.com"
sender_password = "ydta stxc yqkq nbdm"

if st.button("Send Fax"):
    if uploaded_file and receiver_number and sender_email and sender_password:
        handle_faxplus(uploaded_file, receiver_number, fax_message, fax_subject, to_name, chaser_name, sender_email, sender_password)
    else:
        st.error("Please upload a fax document, provide the receiver number, and enter your email credentials.")
