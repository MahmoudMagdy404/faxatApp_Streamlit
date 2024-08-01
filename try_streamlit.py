from datetime import datetime, timezone
import os
import tempfile
import time
import pandas as pd
from urllib.parse import urlencode, quote_plus
import requests
from PyPDF2 import PdfMerger, PdfReader
import re
import base64
from google.oauth2 import service_account
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import io
import json
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth
from faxplus import ApiClient, OutboxApi, OutboxComment, RetryOptions, OutboxOptions, OutboxCoverPage, PayloadOutbox , FilesApi 
from faxplus.configuration import Configuration
from faxplus.rest import ApiException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import logging
import html
from google.auth.transport.requests import Request


style = """
<style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 30px;
                font-size: 16px;
                max-width: 210mm; /* A4 width */
                min-height: 297mm; /* A4 height */
            }
            h1 {
                font-size: 48px;
                font-weight: bold;
                margin-bottom: 30px;
            }
            .grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            .full-width {
                grid-column: 1 / -1;
            }
            .section {
                margin-bottom: 20px;
            }
            .label {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 5px;
            }
            .content {
                font-size: 16px;
            }
            .checkbox-group {
                margin: 30px 0;
                border-top: 2px solid #000;
                border-bottom: 2px solid #000;
                padding: 15px 0;
                font-size: 18px;
            }
            .checkbox-label {
                margin-right: 30px;
            }
            .message-label {
                font-weight: bold;
                font-size: 20px;
                margin-bottom: 10px;
            }
            .message-content {
                font-size: 16px;
            }
        </style>
"""


def generate_cover_page_html(chaser_name, to_name, fax_subject, fax_message, date, sender_email, receiver_number ):
    html_body = f"""9
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fax Cover Sheet</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.8; margin: 0; padding: 40px; font-size: 18px; max-width: 210mm; min-height: 297mm; position: relative;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px;">
        <h1 style="font-size: 60px; font-weight: bold;">FAX</h1>
        <div style="text-align: right;">
            <div style="font-weight: bold; font-size: 22px;">InCall Medical Supplies</div>
            <div>Fax1: (510) 890-3073</div>
            <div>Fax2: (888) 851-6047</div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px;">
        <div style="margin-bottom: 30px;">
            <div style="font-weight: bold; font-size: 22px; margin-bottom: 10px;">To</div>
            <div style="font-size: 18px;">
                Name: {to_name}<br>
                Fax number: {receiver_number}
            </div>
        </div>
        <div style="margin-bottom: 30px;">
            <div style="font-weight: bold; font-size: 22px; margin-bottom: 10px;">From</div>
            <div style="font-size: 18px;">
                Name: {chaser_name}<br>
                Fax number: 737 241 2558
            </div>
        </div>
    </div>
    <div style="margin-bottom: 30px;">
        <div style="font-weight: bold; font-size: 22px; margin-bottom: 10px;">Number of pages: 2</div>
        <div style="font-size: 18px;"></div>
    </div>
    <div style="margin-bottom: 30px;">
        <div style="font-weight: bold; font-size: 22px; margin-bottom: 10px;">Subject: </div>
        <div style="font-size: 18px;">{fax_subject}</div>
    </div>
    <div style="margin-bottom: 30px;">
        <div style="font-weight: bold; font-size: 22px; margin-bottom: 10px;">Date:</div>
        <div style="font-size: 18px;">{date}</div>
    </div>
    <div style="margin: 40px 0; border-top: 2px solid #000; border-bottom: 2px solid #000; padding: 20px 0; font-size: 22px;">
        <span style="margin-right: 40px; font-weight: bold;">☐ Urgent</span>
        <span style="margin-right: 40px; font-weight: bold;">☐ For Review</span>
        <span style="margin-right: 40px; font-weight: bold;">☐ Please Reply</span>
        <span style="font-weight: bold;">☑ Confidential</span>
    </div>
    <div style="margin-bottom: 30px;">
        <div style="font-weight: bold; font-size: 24px; margin-bottom: 15px;">Message:</div>
        <div style="font-size: 18px;">{fax_message}</div>
    </div>
</body>
</html> 
    """
    return html_body


# Define the braces and their forms
Braces = ["Back", "Knees", "Elbow", "Shoulder", "Ankle", "Wrists" , "Neck"]
BracesForms = {
    "Back": {
        'L0637': 'https://docs.google.com/forms/d/e/1FAIpQLSfB7423u2nFC_boKiOq8w-8E6ClY9iY2QLW_-_-SLQwJfbdZg/formResponse',
        'L0457-G': 'https://docs.google.com/forms/d/e/1FAIpQLSe-XTJycYlVMnS7PU6YeIeDXugcBMLuJ1YGr7Y8KEsO3iXRlQ/formResponse'
    },
    "Knees": {
        'L1843': 'https://docs.google.com/forms/d/e/1FAIpQLScf00eJOF1u_60swPRguOZEJTtU7mx6lxIfNUWEJzndiDPD5A/formResponse',
        'L1852-G': 'https://docs.google.com/forms/d/e/1FAIpQLSec52MiutxlJmayam2l0FiQSorT9gyG9efhx7bG7D3K2nPagg/formResponse',
        'L1845': 'https://docs.google.com/forms/d/e/1FAIpQLSfav9S2KJRjyqYClJgZrSuHibaaxSy5gsxvDpqLVrCTyM_8sA/formResponse'
    },
    "Elbow": {
        'L3761': 'https://docs.google.com/forms/d/e/1FAIpQLSfYFk34nTDrm5D22WbVpg5uuASxRoAcc-eaUvJ_rkCNGNLXzw/formResponse'
    },
    "Shoulder": {
        'L3960': 'https://docs.google.com/forms/d/e/1FAIpQLSexO54gwNijfOMjcSp9ZC_9LhXsE0lKpkzzqBQy0_ddBzg1_Q/formResponse'
    },
    "Ankle": {
        'L1971': 'https://docs.google.com/forms/d/e/1FAIpQLSdyRf99metRszBuQ8zHwzQSYvxf-Pb5qJDzJj073-Vu6sfZEA/formResponse',
        "L1906":"https://docs.google.com/forms/d/e/1FAIpQLSfFeFQTiW3-0Z6pLC4w7aki6g15KD9B-bWfj4MKUN-hcbnQ3w/formResponse"
    },
    "Wrists": {
        'L3916': 'https://docs.google.com/forms/d/e/1FAIpQLSd4XQox2yt3wsild0InVMgagrcQ9Aors4PjExoOILHiT9grew/formResponse'
    },
    "Neck":{
        "L0174" : "https://docs.google.com/forms/d/e/1FAIpQLSf0_yOLpX_JGSEJ1CUixkXlkDwi7kl2gwrsunb2IdbtQjPAvg/formResponse"
    }
}

chasers_dict = {
    "Olivia Smith":"(941) 293-1794" , "Mia Martin":"(352) 718-1524",
    "Lexi Thomas":"(607) 383-2941" , "Mark Wilson":"(754) 250-1426",
    "Kendrick Adams":"(941) 293-1462" , "Ken Adams":"(352) 718-1436",
    "Anne Mathew":"(727) 910-2808" , "Linda Williams":"(620) 203-2088",
    "Tom miles":"(786) 891-7322" , "Rose Johnson":"(904) 515-1558",
    "Emma Winslet":"(386) 487-2910" , "Hannah Adams":"(904) 515-1565",
}

def handle_srfax(combined_pdf, receiver_number, fax_message, fax_subject, to_name, chaser_name, uploaded_cover_sheet):
    # API credentials
    access_id = st.secrets["sr_access_id"]["access_id"]
    access_pwd = st.secrets["sr_access_pwd"]["access_pwd"]

    # Fax details
    caller_id = "8888516047"
    sender_email = "Alvin.freeman.italk@gmail.com"

    # Cover page details
    cp_from_name = chaser_name
    cp_to_name = to_name
    cp_subject = fax_subject
    cp_comments = fax_message
    cp_organization = "InCall Medical Supplies"
    cp_from_header = "From InCall Medical Supplies"

    # Encode the main PDF file
    encoded_file = base64.b64encode(combined_pdf.getvalue()).decode()

    # API endpoint
    url = "https://www.srfax.com/SRF_SecWebSvc.php"

    # Base payload
    payload = {
        "action": "Queue_Fax",
        "access_id": access_id,
        "access_pwd": access_pwd,
        "sCallerID": caller_id,
        "sSenderEmail": sender_email,
        "sFaxType": "SINGLE",
        "sToFaxNumber": receiver_number,
        "sFileName_1": "combined.pdf",
        "sFileContent_1": encoded_file,
    }

    if uploaded_cover_sheet is not None:
        # If a cover sheet is uploaded, use it as a separate file
        encoded_cover_page = base64.b64encode(uploaded_cover_sheet.read()).decode()
        payload.update({
            "sFileName_2": "cover_page.pdf",
            "sFileContent_2": encoded_cover_page,
        })
    else:
        # If no cover sheet is uploaded, use the text fields to generate a cover page
        payload.update({
            "sCoverPage": "Company",
            "sCPFromName": cp_from_name,
            "sCPToName": cp_to_name,
            "sCPOrganization": cp_organization,
            "sCPSubject": cp_subject,
            "sCPComments": cp_comments,
            "sFaxFromHeader": cp_from_header,
        })

    response = requests.post(url, data=payload)
    time.sleep(5)
    if response.status_code == 200:
        try:
            response_data = response.json()
            if response_data.get("Status") == "Success":
                return True
            else:
                return False
        except ValueError:
            return False
    else:
        return False

def handle_humblefax(combined_pdf, receiver, fax_message, fax_subject, to_name, chaser_name, uploaded_cover_sheet):

    access_key = st.secrets["humble_access_key"]["access_key"]
    secret_key = st.secrets["humble_secret_key"]["secret_key"]
    # Step 1: Create a temporary fax
    create_tmp_fax_url = "https://api.humblefax.com/tmpFax"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    create_tmp_fax_payload = {
        "toName": to_name,
        "recipients": [receiver],
        "fromName": chaser_name,
        "subject": fax_subject,
        "message": fax_message,
        "includeCoversheet": uploaded_cover_sheet is None,
        "companyInfo": (
            "InCall Medical Supplies\n"
            "Fax 1: +1 (888) 851-6047\n"
            "Fax 2: +1 (510) 890-3073\n"
            "Phone: +1 (352) 718-1524"
        ),
        "pageSize": "A4",
        "resolution": "Fine",
        "fromNumber": "12139056868"
    }

    create_tmp_fax_response = requests.post(create_tmp_fax_url, headers=headers, json=create_tmp_fax_payload)
    if create_tmp_fax_response.status_code == 200:
        tmp_fax_data = create_tmp_fax_response.json().get("data", {}).get("tmpFax", {})
        tmp_fax_id = tmp_fax_data.get("id")
        print(f"tmpFaxId obtained: {tmp_fax_id}")
    else:
        print(f"Failed to create temporary fax: {create_tmp_fax_response.text}")
        return False

    # Step 2: Upload the main PDF file
    files = {'file': ('combined.pdf', combined_pdf.getvalue(), 'application/pdf')}
    upload_response = requests.post(f'https://api.humblefax.com/attachment/{tmp_fax_id}', headers=headers, files=files)
    if upload_response.status_code == 200:
        main_file_data = upload_response.json().get("data", {})
        main_file_id = main_file_data.get("id")
        print(f"Main file uploaded successfully. File ID: {main_file_id}")
    else:
        print(f"Failed to upload main file: {upload_response.text}")
        return False

    # Step 3: Upload the cover page PDF file if it was uploaded
    if uploaded_cover_sheet is not None:
        cover_page_files = {'file': ('cover_page.pdf', uploaded_cover_sheet.read(), 'application/pdf')}
        cover_page_upload_response = requests.post(f'https://api.humblefax.com/attachment/{tmp_fax_id}', headers=headers, files=cover_page_files)
        if cover_page_upload_response.status_code == 200:
            cover_page_data = cover_page_upload_response.json().get("data", {})
            cover_page_id = cover_page_data.get("id")
            print(f"Cover page uploaded successfully. File ID: {cover_page_id}")
        else:
            print(f"Failed to upload cover page file: {cover_page_upload_response.text}")
            return False

    # Step 4: Send the temporary fax
    send_fax_url = f"https://api.humblefax.com/tmpFax/{tmp_fax_id}/send"
    send_response = requests.post(send_fax_url, headers=headers)

    # Check the response
    if send_response.status_code == 200:
        response_data = send_response.json()
        if response_data.get("result") == "success":
            fax_id = response_data.get("data", {}).get("id")
            print(f"Fax sent successfully. Fax ID: {fax_id}")
            return True
        else:
            print(f"Failed to send fax: {response_data.get('message')}")
            return False
    else:
        print(f"HTTP Error: {send_response.status_code} - {send_response.text}")
        return False
#TODO
def handle_hallofax(combined_pdf, receiver_number, fax_message, fax_subject, to_name, chaser_name, uploaded_cover_sheet):
    # Implement HalloFax logic here
    print(f"Sending fax to {receiver_number} using HalloFax")
    # Use the provided parameters to send the fax
    # Return True if successful, False otherwise
    return True
#TODO -> Try to fix it


def handle_faxplus(uploaded_file, receiver_number, fax_message, fax_subject, to_name, chaser_name, uploaded_cover_sheet):
    try:
        sender_email = st.secrets["gmail_creds"]["address"]
        email_password = st.secrets["gmail_creds"]["pass"]
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = f"{receiver_number}@fax.plus"
        msg['Subject'] = fax_subject
        
        # Generate cover page HTML
        cover_page_html = generate_cover_page_html(chaser_name, to_name, fax_subject, fax_message, datetime.now().strftime('%b %d, %Y'), sender_email , receiver_number)
        
        # Add the HTML body as the cover sheet
        body = MIMEText(cover_page_html, 'html')
        msg.attach(body)
        
        # Attach the cover sheet if provided
        if uploaded_cover_sheet:
            cover_sheet = MIMEApplication(uploaded_cover_sheet.getvalue())
            cover_sheet.add_header('Content-Disposition', 'attachment; filename="cover_sheet.pdf"')
            msg.attach(cover_sheet)
        
        # Attach the main file
        if uploaded_file:
            main_attachment = MIMEApplication(uploaded_file.getvalue())
            main_attachment.add_header('Content-Disposition', f'attachment; filename="Main File"')
            msg.attach(main_attachment)
        
        # Send the email (SMTP configuration required)
        import smtplib
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, email_password)
        server.sendmail(sender_email, f"{receiver_number}@fax.plus", msg.as_string())
        server.quit()
        
        st.success("Fax sent successfully")
    except Exception as e:
        st.error(f"Failed to send fax: {e}")

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)

def get_srfax_outbox():
    access_id = st.secrets["sr_access_id"]["access_id"]
    access_pwd = st.secrets["sr_access_pwd"]["access_pwd"]
    
    url = "https://www.srfax.com/SRF_SecWebSvc.php"
    payload = {
        "action": "Get_Fax_Outbox",
        "access_id": access_id,
        "access_pwd": access_pwd,
        "sResponseFormat": "JSON",
        "sPeriod": "ALL",
        "sIncludeSubUsers": "Y"
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None
#TODO
    return
def get_hallo_outbox():
    return
# Function to get outbox faxes from FaxPlus
def get_faxplus_outbox():
    # Your Personal Access Token
    access_token = st.secrets["faxplus_secret_key"]["secret_key"]
    user_id = st.secrets["faxplus_uid"]["user_id"]

    # Base URL for the API
    base_url = 'https://restapi.fax.plus/v3'
    # Endpoint for listing outbox faxes
    endpoint = f'/accounts/{user_id}/outbox'

    # Full URL
    url = base_url + endpoint

    # Headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        outbox_faxes = response.json()
        print("Outbox faxes:", outbox_faxes)
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def retrieve_srfax(fax_file_name, direction):
    access_id = st.secrets["sr_access_id"]["access_id"]
    access_pwd = st.secrets["sr_access_pwd"]["access_pwd"]
    
    url = "https://www.srfax.com/SRF_SecWebSvc.php"
    payload = {
        "action": "Retrieve_Fax",
        "access_id": access_id,
        "access_pwd": access_pwd,
        "sFaxFileName": fax_file_name,
        "sDirection": direction,
        "sResponseFormat": "JSON",
        "sFaxFormat": "PDF"
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def send_srfax(to_fax_number, file_content, sender_email, caller_id):
    access_id = st.secrets["sr_access_id"]["access_id"]
    access_pwd = st.secrets["sr_access_pwd"]["access_pwd"]
    
    url = "https://www.srfax.com/SRF_SecWebSvc.php"
    
    # The file_content is already base64 encoded, so we don't need to encode it again
    payload = {
        "action": "Queue_Fax",
        "access_id": access_id,
        "access_pwd": access_pwd,
        "sToFaxNumber": to_fax_number,
        "sResponseFormat": "JSON",
        "sFaxType": "SINGLE",
        "sFileName_1": "combined.pdf",
        "sFileContent_1": file_content,  # Already base64 encoded
        "sSenderEmail": sender_email,
        "sCallerID": caller_id
    }
    
    logger.debug(f"Attempting to send fax with type: SINGLE")
    logger.debug(f"Sending fax to: {to_fax_number}")
    logger.debug(f"Sender email: {sender_email}")
    logger.debug(f"Caller ID: {caller_id}")
    logger.debug(f"Fax content type: {type(file_content)}")
    logger.debug(f"Fax content preview: {file_content[:100]}")
    
    response = requests.post(url, data=payload)
    logger.debug(f"SRFax API response status code: {response.status_code}")
    logger.debug(f"SRFax API response content: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result['Status'] == 'Success':
            return result
        else:
            logger.error(f"Failed to send fax. Error: {result['Result']}")
    else:
        logger.error(f"HTTP error when sending fax. Status code: {response.status_code}")
    
    return {"Status": "Failed", "Result": "Failed to send fax"}
def resend_srfax(fax_id):
    logger.debug(f"Attempting to resend fax with ID: {fax_id}")
    
    outbox = get_srfax_outbox()
    if not outbox or outbox['Status'] != 'Success':
        logger.error("Failed to get outbox")
        return {"Status": "Failed", "Result": "Failed to get outbox"}
    
    fax_to_resend = next((fax for fax in outbox['Result'] if fax['FileName'] == fax_id), None)
    
    if not fax_to_resend:
        logger.error(f"Fax with ID {fax_id} not found in outbox")
        return {"Status": "Failed", "Result": "Fax not found in outbox"}
    
    logger.debug(f"Fax to resend details: {fax_to_resend}")
    
    retrieved_fax = retrieve_srfax(fax_to_resend['FileName'], "OUT")
    if not retrieved_fax or retrieved_fax['Status'] != 'Success':
        logger.error("Failed to retrieve fax content")
        return {"Status": "Failed", "Result": "Failed to retrieve fax content"}
    
    fax_content = retrieved_fax['Result']
    logger.debug(f"Retrieved fax content type: {type(fax_content)}")
    logger.debug(f"Retrieved fax content preview: {fax_content[:100]}")
    
    # Check if the content is valid base64
    try:
        base64.b64decode(fax_content)
    except:
        logger.error("Retrieved fax content is not valid base64")
        return {"Status": "Failed", "Result": "Invalid fax content"}
    
    sender_email = "Alvin.freeman.italk@gmail.com"
    caller_id = "8888516047"
    
    result = send_srfax(fax_to_resend['ToFaxNumber'], fax_content, sender_email, caller_id)
    
    logger.debug(f"Resend result: {result}")
    return result



#TODO
    return

def resend_hallo(fax_id):
    return
def resend_faxplus(fax_id):
    return


# Streamlit secrets
HUMBLEFAX_API_BASE_URL = "https://api.humblefax.com"
access_key = st.secrets["humble_access_key"]["access_key"]
secret_key = st.secrets["humble_secret_key"]["secret_key"]
def get_humblefax_details(fax_id):
    url = f"{HUMBLEFAX_API_BASE_URL}/sentFax/{fax_id}"
    auth = (access_key, secret_key)
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        fax_data = response.json().get("data", {}).get("sentFax", {})
        
        # Extract relevant details and return them in a structured format
        recipient = fax_data.get("recipients", [{}])[0]  # Get the first recipient's details
        
        fax_details = {
            'ToFaxNumber': recipient.get('toNumber', ''),
            'DateSent': datetime.utcfromtimestamp(int(fax_data.get('timestamp', 0))).strftime('%Y-%m-%d %H:%M:%S'),
            'SentStatus': fax_data.get('status', ''),
            'FileName': fax_data.get('subject', ''),  # Assuming subject as file name as there's no file name in response
            'Service': 'HumbleFax'
        }
        
        return fax_details

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve fax details for fax_id {fax_id}: {e}")
        return None
def get_humble_outbox():
    url = "https://api.humblefax.com/sentFaxes"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to get HumbleFax outbox: {response.text}")
        return None

def retrieve_humble_fax(fax_id):
    url = f"https://api.humblefax.com/fax/{fax_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to retrieve HumbleFax: {response.text}")
        return None

def create_humble_tmp_fax(payload):
    url = "https://api.humblefax.com/tmpFax"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to create temporary fax: {response.text}")
        return None

def get_humble_attachment(fax_id, attachment_id):
    url = f"https://api.humblefax.com/fax/{fax_id}/attachment/{attachment_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        logger.error(f"Failed to get attachment: {response.text}")
        return None

def upload_humble_attachment(tmp_fax_id, file_content, file_name):
    url = f"https://api.humblefax.com/attachment/{tmp_fax_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    files = {'file': (file_name, file_content, 'application/pdf')}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to upload attachment: {response.text}")
        return None

def send_humble_tmp_fax(tmp_fax_id):
    url = f"https://api.humblefax.com/tmpFax/{tmp_fax_id}/send"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("result") == "success":
            return result.get("data", {}).get("id")
    logger.error(f"Failed to send temporary fax: {response.text}")
    return None

def resend_humble(fax_id):
    logger.debug(f"Attempting to resend HumbleFax with ID: {fax_id}")
    
    # Retrieve the original fax details
    fax_details = retrieve_humble_fax(fax_id)
    if not fax_details or fax_details.get("result") != "success":
        logger.error(f"Failed to retrieve fax details for ID: {fax_id}")
        return {"Status": "Failed", "Result": "Failed to retrieve fax details"}
    
    fax_data = fax_details.get("data", {})
    
    # Prepare the payload for creating a new temporary fax
    create_tmp_fax_payload = {
        "toName": fax_data.get("toName"),
        "recipients": fax_data.get("recipients"),
        "fromName": fax_data.get("fromName"),
        "subject": fax_data.get("subject"),
        "message": fax_data.get("message"),
        "includeCoversheet": fax_data.get("includeCoversheet", True),
        "companyInfo": fax_data.get("companyInfo"),
        "pageSize": fax_data.get("pageSize", "A4"),
        "resolution": fax_data.get("resolution", "Fine"),
        "fromNumber": fax_data.get("fromNumber")
    }
    
    # Create a new temporary fax
    tmp_fax = create_humble_tmp_fax(create_tmp_fax_payload)
    if not tmp_fax or tmp_fax.get("result") != "success":
        logger.error("Failed to create temporary fax")
        return {"Status": "Failed", "Result": "Failed to create temporary fax"}
    
    tmp_fax_id = tmp_fax.get("data", {}).get("tmpFax", {}).get("id")
    
    # Upload the original attachments to the new temporary fax
    for attachment in fax_data.get("attachments", []):
        attachment_id = attachment.get("id")
        attachment_content = get_humble_attachment(fax_id, attachment_id)
        if attachment_content:
            upload_result = upload_humble_attachment(tmp_fax_id, attachment_content, attachment.get("name"))
            if not upload_result:
                logger.error(f"Failed to upload attachment: {attachment.get('name')}")
                return {"Status": "Failed", "Result": "Failed to upload attachment"}
    
    # Send the new fax
    send_result = send_humble_tmp_fax(tmp_fax_id)
    if send_result:
        logger.debug(f"HumbleFax resent successfully. New Fax ID: {send_result}")
        return {"Status": "Success", "Result": send_result}
    else:
        logger.error("Failed to send HumbleFax")
        return {"Status": "Failed", "Result": "Failed to send fax"}



# Constants and secrets
HUMBLEFAX_API_BASE_URL = "https://api.humblefax.com"
access_key = st.secrets["humble_access_key"]["access_key"]
secret_key = st.secrets["humble_secret_key"]["secret_key"]
CSV_URL = "https://raw.githubusercontent.com/MahmoudMagdy404/files_holder/main/humble_outbox.csv?token=GHSAT0AAAAAACU33HXMATERVLTKMIHDCDSEZVHWI5Q"

def get_humblefax_details(fax_id):
    url = f"{HUMBLEFAX_API_BASE_URL}/sentFax/{fax_id}"
    auth = (access_key, secret_key)
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()

        fax_data = response.json().get("data", {}).get("sentFax", {})
        recipient = fax_data.get("recipients", [{}])[0]

        fax_details = {
            'FaxID': fax_id,
            'ToFaxNumber': recipient.get('toNumber', ''),
            'DateSent': datetime.datetime.utcfromtimestamp(int(fax_data.get('timestamp', 0))).strftime('%Y-%m-%d %H:%M:%S'),
            'SentStatus': fax_data.get('status', ''),
            'FileName': fax_data.get('subject', ''),  # Assuming subject as file name
            'Service': 'HumbleFax'
        }
        return fax_details

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve fax details for fax_id {fax_id}: {e}")
        return None

def list_sent_faxes():
    url = f"{HUMBLEFAX_API_BASE_URL}/sentFaxes"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{access_key}:{secret_key}'.encode()).decode()}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get HumbleFax outbox: {response.text}")
        return None

def check_and_save_fax_details(fax_details):
    try:
        # Read the existing CSV file
        df = pd.read_csv(CSV_URL)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=['FaxID', 'ToFaxNumber', 'DateSent', 'SentStatus', 'FileName', 'Service'])
    
    # Check if the fax ID already exists
    if fax_details['FaxID'] in df['FaxID'].values:
        print("Fax ID already exists. No new faxes sent.")
        return df

    # Append new fax details
    df = df.append(fax_details, ignore_index=True)

    # Save back to CSV
    df.to_csv(CSV_URL, index=False)
    
    return df

def on_row_select():
    if 'selected_fax_index' in st.session_state and st.session_state['selected_fax_index'] is not None:
        selected_fax = st.session_state['faxes_df'].iloc[st.session_state['selected_fax_index']]
        st.session_state['selected_fax_info'] = f"Selected fax: To {selected_fax['To']} sent on {selected_fax['Date']}"
    else:
        st.session_state['selected_fax_info'] = "No fax selected"

# # Dropbox settings
# DROPBOX_ACCESS_TOKEN = st.secrets["dropbox"]["access_token"]
# TOKEN_FOLDER_PATH = '/Apps/faxat app' 
# TOKEN_FILE_NAME = 'token.json'

# SCOPES = ["https://www.googleapis.com/auth/drive"]

# def get_dropbox_client():
#     """Create and return a Dropbox client."""
#     try:
#         client = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
#         client.users_get_current_account()
#         return client
#     except dropbox.exceptions.AuthError:
#         st.error("Dropbox authentication error. Please check your access token.")
#         return None

# def download_token_from_dropbox():
#     """Download the token file from Dropbox."""
#     client = get_dropbox_client()
#     if client is None:
#         st.error("Cannot download token because Dropbox client is not authenticated.")
#         return False

#     try:
#         metadata, response = client.files_download(f'{TOKEN_FOLDER_PATH}/{TOKEN_FILE_NAME}')
#         with open(TOKEN_FILE_NAME, 'wb') as f:
#             f.write(response.content)
#         st.success('Token downloaded from Dropbox successfully!')
#         return True
#     except AuthError as e:
#         st.error(f'Error downloading token: {e}')
#         return False
#     except dropbox.exceptions.ApiError as e:
#         st.error(f'File not found: {e}')
#         return False

# def upload_token_to_dropbox():
#     """Upload the token file to Dropbox."""
#     client = get_dropbox_client()
#     if client is None:
#         st.error("Cannot upload token because Dropbox client is not authenticated.")
#         return False

#     try:
#         with open(TOKEN_FILE_NAME, 'rb') as f:
#             token_data = f.read()
#         client.files_upload(token_data, f'{TOKEN_FOLDER_PATH}/{TOKEN_FILE_NAME}', mode=dropbox.files.WriteMode('overwrite'))
#         st.success('Token uploaded to Dropbox successfully!')
#         return True
#     except AuthError as e:
#         st.error(f'Error uploading token: {e}')
#         return False

# def get_credentials():
#     """Get Google Drive credentials, refreshing or creating them as necessary."""
#     creds = None

#     # Download token from Dropbox if it exists
#     if download_token_from_dropbox() and os.path.exists(TOKEN_FILE_NAME):
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE_NAME, SCOPES)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             credentials_json = st.secrets["google_credentials"]["credentials_json"]
#             with open('credentials.json', 'w') as f:
#                 f.write(credentials_json)
                
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
            
#             with open(TOKEN_FILE_NAME, 'w') as token:
#                 token.write(creds.to_json())
            
#             if not upload_token_to_dropbox():
#                 st.warning("Failed to upload token to Dropbox. Using local token only.")
    
#     return creds
# def get_drive_service(creds):
#     return build("drive", "v3", credentials=creds)

# def combine_pdfs(fname):
#     creds = get_credentials()
#     if not creds:
#         return None, "Failed to obtain valid credentials. Please try authenticating again."

#     try:
#         service = get_drive_service(creds)
#         folder_id = "15I95Loh35xI2PcGa36xz7SgMtclo-9DC"
#         query = f"'{folder_id}' in parents"
        
#         st.write("Querying Google Drive...")
#         results = service.files().list(q=query, pageSize=20, fields="nextPageToken, files(id, name, mimeType)").execute()
#         items = results.get("files", [])
        
#         if not items:
#             return None, "No files found in the specified folder."
        
#         fname = fname.strip()
#         target_files = [file for file in items if fname in file["name"]]
        
#         if not target_files:
#             return None, "No matching files found."
        
#         st.write(f"Found {len(target_files)} matching files. Combining PDFs...")
        
#         merger = PdfMerger()
#         for target_file in target_files:
#             mime_type = target_file.get("mimeType")
#             file_id = target_file.get("id")
            
#             st.write(f"Processing file: {target_file['name']}")
            
#             if mime_type.startswith("application/vnd.google-apps."):
#                 request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
#             else:
#                 request = service.files().get_media(fileId=file_id)
            
#             fh = io.BytesIO()
#             downloader = MediaIoBaseDownload(fh, request)
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 st.write(f"Download {int(status.progress() * 100)}%")
#             fh.seek(0)
            
#             pdf_reader = PdfReader(fh)
#             merger.append(pdf_reader)
        
#         st.write("Finalizing PDF...")
#         output = io.BytesIO()
#         merger.write(output)
#         merger.close()
#         output.seek(0)
#         st.write("PDF combination complete!")
#         return output, None
#     except Exception as error:
#         st.error(f"An error occurred: {str(error)}")
#         return None, str(error)


TOKEN_FOLDER_ID = '1HDwNvgFv_DSEH2WKNfLNheKXxKT_hDM9'
CREDENTIALS_FILE_NAME = 'credentials.json'
TOKEN_FILE_NAME = 'token.json'
SCOPES = ["https://www.googleapis.com/auth/drive"]
# credentials_json = st.secrets["google_credentials"]["credentials_json"]

# def get_drive_service():
#     try:
#         # Use service account credentials to access Google Drive
#         creds = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
#     except Exception as e:
#         print(f"Error loading service account credentials: {e}")
#         return None
#     return build('drive', 'v3', credentials=creds)

# def download_file_from_drive(service, file_name, folder_id):
#     try:
#         query = f"'{folder_id}' in parents and name='{file_name}'"
#         results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
#         items = results.get('files', [])

#         if not items:
#             print(f'No {file_name} file found in Google Drive folder: {folder_id}')
#             return None

#         file_id = items[0]['id']
#         request = service.files().get_media(fileId=file_id)
#         fh = io.BytesIO()
#         downloader = MediaIoBaseDownload(fh, request)
#         done = False
#         while not done:
#             status, done = downloader.next_chunk()
#             print(f"Download {int(status.progress() * 100)}%")
#         fh.seek(0)
#         return fh.read()

#     except Exception as e:
#         print(f'Error downloading {file_name}: {e}')
#         return None

# def upload_token_to_drive(service, creds):
#     try:
#         file_metadata = {
#             'name': TOKEN_FILE_NAME,
#             'parents': [TOKEN_FOLDER_ID]
#         }
#         media = MediaIoBaseUpload(io.BytesIO(creds.to_json().encode()), mimetype='application/json')

#         query = f"'{TOKEN_FOLDER_ID}' in parents and name='{TOKEN_FILE_NAME}'"
#         results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
#         items = results.get('files', [])

#         if items:
#             file_id = items[0]['id']
#             service.files().update(fileId=file_id, body=file_metadata, media_body=media).execute()
#         else:
#             service.files().create(body=file_metadata, media_body=media).execute()

#         print('Token uploaded to Google Drive successfully!')
#         return True
#     except Exception as e:
#         print(f'Error uploading token: {e}')
#         return False

# def get_credentials():
#     creds = None
#     service = get_drive_service()
#     if service is None:
#         return None
    
#     credentials_data = download_file_from_drive(service, CREDENTIALS_FILE_NAME, TOKEN_FOLDER_ID)
#     if credentials_data:
#         credentials_json = json.loads(credentials_data)
#         flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
    
#         token_data = download_file_from_drive(service, TOKEN_FILE_NAME, TOKEN_FOLDER_ID)
#         if token_data:
#             creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
    
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 creds = flow.run_local_server(port=0)
            
#             upload_token_to_drive(service, creds)
    
#     return creds
# Define SCOPES

# Constants
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "15I95Loh35xI2PcGa36xz7SgMtclo-9DC"
GITHUB_USER = 'MahmoudMagdy404'
GITHUB_PAO = st.secrets["github_token"]["token"]
TOKEN_FILE_URL = "https://api.github.com/repos/MahmoudMagdy404/files_holder/contents/token.json"

def read_token_from_github():
    """Read the token from GitHub repository."""
    github_session = requests.Session()
    github_session.auth = (GITHUB_USER, GITHUB_PAO)
    try:
        response = github_session.get(TOKEN_FILE_URL)
        response.raise_for_status()
        content = response.json()['content']
        decoded_content = base64.b64decode(content).decode('utf-8')
        return json.loads(decoded_content)
    except Exception as e:
        st.error(f"Failed to read token from GitHub: {e}")
        return None

def write_token_to_github(token_data):
    """Write the token to GitHub repository."""
    github_session = requests.Session()
    github_session.auth = (GITHUB_USER, GITHUB_PAO)
    try:
        response = github_session.get(TOKEN_FILE_URL)
        response.raise_for_status()
        current_file = response.json()
        
        content = base64.b64encode(json.dumps(token_data).encode()).decode()
        
        data = {
            "message": "Update token.json",
            "content": content,
            "sha": current_file['sha']
        }
        
        response = github_session.put(TOKEN_FILE_URL, json=data)
        response.raise_for_status()
        st.success("Token updated successfully in GitHub.")
    except Exception as e:
        st.error(f"Failed to write token to GitHub: {e}")

def get_drive_service(creds):
    """Get Google Drive service."""
    return build('drive', 'v3', credentials=creds)

def get_credentials():
    """Get or refresh Google credentials."""
    token_data = read_token_from_github()
    
    if not token_data:
        st.warning("No token found in GitHub. Initiating new authentication flow.")
        flow = InstalledAppFlow.from_client_config(
            json.loads(st.secrets["google_credentials"]["credentials_json"]),
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        write_token_to_github(json.loads(creds.to_json()))
        return creds
    
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            write_token_to_github(json.loads(creds.to_json()))
        else:
            flow = InstalledAppFlow.from_client_config(
                json.loads(st.secrets["google_credentials"]["credentials_json"]),
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            write_token_to_github(json.loads(creds.to_json()))
    
    return creds

def combine_pdfs(fname):
    """Combine PDFs from Google Drive folder."""
    creds = get_credentials()
    if not creds:
        return None, "Failed to obtain valid credentials. Please try authenticating again."

    try:
        service = get_drive_service(creds)
        query = f"'{FOLDER_ID}' in parents"

        st.info("Querying Google Drive...")
        results = service.files().list(q=query, pageSize=20, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get("files", [])

        if not items:
            return None, "No files found in the specified folder."

        fname = fname.strip().lower()
        target_files = [file for file in items if fname in file["name"].lower()]

        st.info(f"Searching for files with name containing: {fname}")
        for file in items:
            st.info(f"Found file: {file['name']}")

        if not target_files:
            return None, "No matching files found."

        st.info(f"Found {len(target_files)} matching files. Combining PDFs...")

        merger = PdfMerger()
        for target_file in target_files:
            mime_type = target_file.get("mimeType")
            file_id = target_file.get("id")

            st.info(f"Processing file: {target_file['name']}")

            if mime_type.startswith("application/vnd.google-apps."):
                request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
            else:
                request = service.files().get_media(fileId=file_id)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                st.info(f"Download {int(status.progress() * 100)}%")
            fh.seek(0)

            pdf_reader = PdfReader(fh)
            merger.append(pdf_reader)

        st.info("Finalizing PDF...")
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        st.info("PDF combination complete!")

        return output, None
    except Exception as error:
        st.error(f"An error occurred: {str(error)}")
        return None, str(error)
    
def main():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Form Submission", "Send Fax", "Sent Faxes List"])
    # Adding a note in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Ankle States → L1906")
    st.sidebar.markdown("- AR")
    st.sidebar.markdown("- TN")
    st.sidebar.markdown("- MN")
    st.sidebar.markdown("- IL")
    st.sidebar.markdown("- NJ")
    st.sidebar.markdown("- OH")
    st.sidebar.markdown("- KY")
    if page == "Form Submission":
        st.title("Brace Form Submission")
        
        st.header("Patient and Doctor Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Patient Information")
            date = st.date_input("Date")
            fname = st.text_input("First Name")
            lname = st.text_input("Last Name")
            ptPhone = st.text_input("Patient Phone Number")
            ptAddress = st.text_input("Patient Address")
            ptCity = st.text_input("Patient City")
            ptState = st.text_input("Patient State")
            ptZip = st.text_input("Patient Zip Code")
            ptDob = st.text_input("Date of Birth")
            medID = st.text_input("MBI")
            ptHeight = st.text_input("Height")
            ptWeight = st.text_input("Weight")
            ptGender = st.selectbox("Gender", ["Male", "Female"])

        with col2:
            st.subheader("Doctor Information")
            drName = st.text_input("Doctor Name")
            drAddress = st.text_input("Doctor Address")
            drCity = st.text_input("Doctor City")
            drState = st.text_input("Doctor State")
            drZip = st.text_input("Doctor Zip Code")
            drPhone = st.text_input("Doctor Phone Number")
            drFax = st.text_input("Doctor Fax Number")
            drNpi = st.text_input("Doctor NPI")

        st.header("Select Braces")
        brace_columns = st.columns(len(Braces))
        selected_forms = {}
        # Create two rows of columns: 3 columns in the first row, 4 columns in the second row
        col1, col2, col3 = st.columns(3)
        col4, col5, col6, col7 = st.columns(4)

        # Function to handle displaying the braces and their forms
        def display_brace(brace, column):
            if brace not in st.session_state:
                st.session_state[brace] = "None"

            with column:
                st.subheader(f"{brace} Brace")
                brace_options = ["None"] + list(BracesForms[brace].keys())
                selected_forms[brace] = st.radio(
                    f"Select {brace} Brace",
                    brace_options,
                    key=brace,
                    index=brace_options.index(st.session_state[brace])
                )

        # Display the first 3 braces in the first row
        for idx, brace in enumerate(Braces[:3]):
            display_brace(brace, [col1, col2, col3][idx])

        # Display the remaining 4 braces in the second row
        for idx, brace in enumerate(Braces[3:]):
            display_brace(brace, [col4, col5, col6, col7][idx])

        def validate_all_fields():
            required_fields = [
                fname, lname, ptPhone, ptAddress,
                ptCity, ptState, ptZip, ptDob, medID,
                ptHeight, ptWeight, drName,
                drAddress, drCity, drState, drZip,
                drPhone, drFax, drNpi
            ]
            for field in required_fields:
                if not field:
                    st.warning(f"{field} is required.")
                    return False
            return True

        if st.button("Submit"):
            if not validate_all_fields():
                st.warning("Please fill out all required fields.")
            else:
                selected_urls = []
                for brace_type, brace_code in selected_forms.items():
                    if brace_code != "None":
                        url = BracesForms[brace_type][brace_code]
                        selected_urls.append((brace_type, url))

                if not selected_urls:
                    st.warning("Please select at least one brace form.")
                else:
                    for brace_type, url in selected_urls:
                        form_data = {
                            "entry.1545087922": date.strftime("%m/%d/%Y"),
                            "entry.1992907553": fname,
                            "entry.1517085063": lname,
                            "entry.1178853697": ptPhone,
                            "entry.478400313": ptAddress,
                            "entry.1687085318": ptCity,
                            "entry.1395966108": ptState,
                            "entry.1319952523": ptZip,
                            "entry.1553550428": ptDob,
                            "entry.1122949100": medID,
                            "entry.2102408689": ptHeight,
                            "entry.1278616009": ptWeight,
                            "entry.1322384700": ptGender,
                            "entry.2090908898": drName,
                            "entry.198263517": drAddress,
                            "entry.1349410133": drCity,
                            "entry.847367280": drState,
                            "entry.1652935364": drZip,
                            "entry.756850883": drPhone,
                            "entry.1725680069": drFax,
                            "entry.314880762": drNpi
                        }

                        encoded_data = urlencode(form_data, quote_via=quote_plus)
                        full_url = f"{url}?{encoded_data}"
                        
                        # Test the URL
                        try:
                            response = requests.get(full_url)
                            if response.status_code == 200:
                                # webbrowser.open(full_url)

                                st.write(f"[Click here to open the form for {brace_type} brace](<{full_url}>)")
                            else:
                                st.error(f"Failed to access the form for {brace_type} brace. Status Code: {response.status_code}")
                        except Exception as e:
                            st.error(f"Error accessing the form for {brace_type} brace: {e}")

                    st.success(f"{len(selected_urls)} form(s) are ready for submission. Please click the links above to submit.")



    elif page == "Send Fax":
        st.title("Send Fax")

        st.header("Combine PDFs")
        # uploaded_cover_sheet = st.file_uploader("Upload Cover Sheet PDF (Optional)", type="pdf")

        doctor_name = st.text_input("Enter Doctor Name for PDF combination")
        if st.button("Combine PDFs"):
            if doctor_name:
                with st.spinner("Combining PDFs..."):
                    combined_pdf, error = combine_pdfs(doctor_name)
                    if error:
                        st.error(f"Error combining PDFs: {error}")
                    elif combined_pdf:
                        st.success(f"Combined PDF for {doctor_name} created successfully.")
                        st.session_state['combined_pdf'] = combined_pdf
                        st.session_state['doctor_name'] = doctor_name
                        st.experimental_rerun()
                    else:
                        st.error("Failed to create combined PDF. Please try again.")
            else:
                st.warning("Please enter a doctor name for PDF combination.")

        if 'combined_pdf' in st.session_state:
            st.download_button(
                label="Download Combined PDF",
                data=st.session_state['combined_pdf'].getvalue(),
                file_name=f"{st.session_state['doctor_name']}_combined.pdf",
                mime="application/pdf"
            )
            st.success("Combined PDF is ready for further processing (e.g., sending faxes).")


        st.subheader("Select Fax Service")
        fax_service = st.radio(
            "Choose a fax service:",
            ["SRFax", "HumbleFax", "HalloFax", "FaxPlus"],
            horizontal=True
        )
        # # Receiver number input
        # receiver_number = st.text_input("Receiver Fax Number")

        # # Common fax inputs
        # fax_message = st.text_area("Fax Message")
        # fax_subject = st.text_input("Fax Subject")
        # to_name = st.text_input("To (Recipient Name)")
        # chaser_name = st.selectbox("From (Sender Name)", list(chasers_dict.keys()))
        
        uploaded_cover_sheet = st.file_uploader("Upload Cover Sheet (Optional)", type="pdf")

        if not uploaded_cover_sheet:
            # Fields required if no cover sheet is uploaded
            receiver_number = st.text_input("Receiver Fax Number")
            fax_message = st.text_area("Fax Message")
            fax_subject = st.text_input("Fax Subject")
            to_name = st.text_input("To (Recipient Name)")
            chaser_name = st.selectbox("From (Sender Name)", list(chasers_dict.keys()))

        else:
            # If a cover sheet is uploaded, skip additional input fields
            receiver_number = None
            fax_message = None
            fax_subject = None
            to_name = None
            chaser_name = None

        if st.button("Send Fax"):
            if not uploaded_cover_sheet and (not receiver_number or not fax_message or not fax_subject or not to_name or not chaser_name):
                st.error("Please provide all required fields to generate a cover sheet.")
            elif 'combined_pdf' not in st.session_state:
                st.error("Please combine PDFs before sending a fax.")
            else:
                combined_pdf = st.session_state.get('combined_pdf')
                chaser_number = chasers_dict.get(chaser_name, "")
                fax_message_with_number = f"{fax_message}<br><br><b>From: {chaser_name} {chaser_number}</b>" if fax_message else ""

                if fax_service == "SRFax":
                    result = handle_srfax(combined_pdf, receiver_number, fax_message_with_number, fax_subject, to_name, chaser_name, uploaded_cover_sheet)
                elif fax_service == "HumbleFax":
                    result = handle_humblefax(combined_pdf, receiver_number, fax_message_with_number, fax_subject, to_name, chaser_name, uploaded_cover_sheet)
                elif fax_service == "HalloFax":
                    result = handle_hallofax(combined_pdf, receiver_number, fax_message_with_number, fax_subject, to_name, chaser_name, uploaded_cover_sheet)
                elif fax_service == "FaxPlus":
                    result = handle_faxplus(combined_pdf, receiver_number, fax_message_with_number, fax_subject, to_name, chaser_name, uploaded_cover_sheet)

                if result:
                    st.success(f"Fax sent successfully using {fax_service}.")
                else:
                    st.error(f"Failed to send fax using {fax_service}. Please check the logs for more information.")

    elif page == "Sent Faxes List":
        st.title("Sent Faxes List")
        st.header("Refax Option")

        # Fax service selection using radio buttons
        st.subheader("Select Fax Service")
        fax_service = st.radio(
            "Choose a fax service:",
            ["SRFax", "HumbleFax", "HalloFax", "FaxPlus"],
            horizontal=True
        )

        if st.button("List Sent Faxes"):
            all_faxes = []

            if fax_service == 'SRFax':
                all_faxes = []
                outbox = get_srfax_outbox()
                if outbox and outbox['Status'] == 'Success':
                    faxes = outbox['Result']
                    for fax in faxes:
                        fax['Service'] = 'SRFax'
                    all_faxes.extend(faxes)

            elif fax_service == 'HumbleFax':
                all_faxes = []
                outbox = get_humble_outbox()
                if outbox:
                    faxes = outbox["data"].get("sentFaxIds", [])
                    print(faxes)
                    for fax_id in faxes[:10]:
                        # Assuming you have a way to get details for each fax_id
                        print(fax_id)
                        fax_details = get_humblefax_details(fax_id)  # You need to implement this function
                        print(fax_details)
                        if fax_details:
                            fax_details['Service'] = 'HumbleFax'
                            all_faxes.append(fax_details)

            elif fax_service == 'HalloFax':
                all_faxes = []
                outbox = get_hallo_outbox()
                if outbox and outbox['Status'] == 'Success':
                    faxes = outbox['Result']
                    for fax in faxes:
                        fax['Service'] = 'HalloFax'
                    all_faxes.extend(faxes)

            elif fax_service == 'FaxPlus':
                all_faxes = []
                outbox = get_faxplus_outbox()
                if outbox:
                    for fax in outbox:
                        fax['Service'] = 'FaxPlus'
                    all_faxes.extend(outbox)

            if all_faxes:
                # Create a DataFrame from the faxes data
                df = pd.DataFrame(all_faxes)
                df = df[['ToFaxNumber', 'DateSent', 'SentStatus', 'FileName', 'Service']]  # Include FileName for resending
                df.columns = ['To', 'Date', 'Status', 'FileName', 'Service']  # Rename columns for display

                # Store the DataFrame in session state for later use
                st.session_state['faxes_df'] = df
                st.session_state['selected_fax_index'] = None
                st.session_state['selected_fax_info'] = "No fax selected"

        if 'faxes_df' in st.session_state:
            # Display the DataFrame
            st.dataframe(
                st.session_state['faxes_df'].drop(columns=['FileName']),
                height=300
            )

            # Add a number input for row selection
            selected_index = st.number_input("Select a row number", min_value=1, max_value=len(st.session_state['faxes_df']), value=1, step=1) - 1

            if st.button("Confirm Selection"):
                st.session_state['selected_fax_index'] = selected_index
                on_row_select()

            # Display the selected fax information
            st.write(st.session_state.get('selected_fax_info', "No fax selected"))
            
            # Check if any row is selected
            if st.session_state.get('selected_fax_index') is not None:
                if st.button("Resend Selected Fax"):
                    selected_fax = st.session_state['faxes_df'].iloc[st.session_state['selected_fax_index']]
                    service = selected_fax['Service']
                    if service == 'SRFax':
                        result = resend_srfax(selected_fax['FileName'])
                    elif service == 'HumbleFax':
                        result = resend_humble(selected_fax['FileName'])
                    elif service == 'HalloFax':
                        result = resend_hallo(selected_fax['FileName'])
                    elif service == 'FaxPlus':
                        result = resend_faxplus(selected_fax['FileName'])
                    else:
                        st.error("Unknown fax service.")
                        return
                    
                    if result and result['Status'] == 'Success':
                        st.success("Fax resent successfully!")
                    else:
                        st.error(f"Failed to resend fax. Reason: {result.get('Result', 'Unknown error')}")

if __name__ == "__main__":
    main()