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


# Define the braces and their forms
Braces = ["Back", "Knees", "Elbow", "Shoulder", "Ankle", "Wrists"]
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
# Function for handling FaxPlus
def handle_faxplus(uploaded_file, receiver_number, fax_message, fax_subject, to_name, chaser_name , uploaded_cover_sheet):
    try:
        sender_email = st.secrets["gmail_creds"]["address"]
        email_password = st.secrets["gmail_creds"]["pass"]
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
                .checkbox-group {{
                    margin-top: 15px;
                }}
                .checkbox-label {{
                    margin-right: 20px;
                }}
                input[type="checkbox"] {{
                    margin-right: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>FAX</h1>
            <div class="section">
                <div class="label">To:</div>
                Name: {to_name}<br>
                Fax number: {receiver_number}
            </div>
            <div class="section">
                <div class="label">From:</div>
                Name: {chaser_name}<br>
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
            <div class="checkbox-group">
                <label class="checkbox-label"><input type="checkbox"> Urgent</label>
                <label class="checkbox-label"><input type="checkbox"> For Review</label>
                <label class="checkbox-label"><input type="checkbox"> Please Reply</label>
                <label class="checkbox-label"><input type="checkbox" checked> Confidential</label>
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
        
        # Attach the cover sheet if provided
        if uploaded_cover_sheet:
            cover_sheet = MIMEApplication(uploaded_cover_sheet.getvalue())
            cover_sheet.add_header('Content-Disposition', 'attachment; filename="cover_sheet.pdf"')
            msg.attach(cover_sheet)

        # Attach the main document
        main_document = MIMEApplication(uploaded_file.getvalue())
        main_document.add_header('Content-Disposition', 'attachment; filename="fax_document.pdf"')
        msg.attach(main_document)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(msg)
        
        st.success(f"Fax sent successfully to {receiver_number}")
    
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
def get_humble_outbox():
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

    
def resend_srfax(fax_id):
    access_id = st.secrets["sr_access_id"]["access_id"]
    access_pwd = st.secrets["sr_access_pwd"]["access_pwd"]
    
    url = "https://www.srfax.com/SRF_SecWebSvc.php"
    payload = {
        "action": "Resend_Fax",
        "access_id": access_id,
        "access_pwd": access_pwd,
        "sFaxDetailsID": fax_id
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None
#TODO
def resend_humble(fax_id):
    return
def resend_hallo(fax_id):
    return
def resend_faxplus(fax_id):
    return

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
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Load credentials from secrets
credentials_json = st.secrets["google_credentials"]["credentials_json"]

# Function to update st.secrets
def update_secrets(key, value):
    st.secrets[key] = value

def get_drive_service(creds):
    return build('drive', 'v3', credentials=creds)

def generate_and_upload_token():
    try:
        # Generate credentials and token
        flow = InstalledAppFlow.from_client_config(
            json.loads(credentials_json), SCOPES
        )
        creds = flow.run_console()  # Change from run_local_server to run_console
        
        # Save token to Streamlit secrets
        token_json = creds.to_json()
        update_secrets("google_credentials.token_json", token_json)
        
        print('Token generated and saved to Streamlit secrets successfully!')
        return creds
    except Exception as e:
        print(f'Error generating token: {e}')
        return None

def get_credentials():
    token_data = st.secrets["google_credentials"].get("token_json")
    
    if token_data:
        creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
    else:
        creds = generate_and_upload_token()
        if not creds:
            return None
    
    return creds

def combine_pdfs(fname):
    creds = get_credentials()
    if not creds:
        return None, "Failed to obtain valid credentials. Please try authenticating again."

    try:
        service = get_drive_service(creds)
        folder_id = "15I95Loh35xI2PcGa36xz7SgMtclo-9DC"
        query = f"'{folder_id}' in parents"

        print("Querying Google Drive...")
        results = service.files().list(q=query, pageSize=20, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get("files", [])

        if not items:
            return None, "No files found in the specified folder."

        fname = fname.strip().lower()
        target_files = [file for file in items if fname in file["name"].lower()]

        print(f"Searching for files with name containing: {fname}")
        for file in items:
            print(f"Found file: {file['name']}")

        if not target_files:
            return None, "No matching files found."

        print(f"Found {len(target_files)} matching files. Combining PDFs...")

        merger = PdfMerger()
        for target_file in target_files:
            mime_type = target_file.get("mimeType")
            file_id = target_file.get("id")

            print(f"Processing file: {target_file['name']}")

            if mime_type.startswith("application/vnd.google-apps."):
                request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
            else:
                request = service.files().get_media(fileId=file_id)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")
            fh.seek(0)

            pdf_reader = PdfReader(fh)
            merger.append(pdf_reader)

        print("Finalizing PDF...")
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        print("PDF combination complete!")

        return output, None
    except Exception as error:
        print(f"An error occurred: {str(error)}")
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

        for idx, brace in enumerate(Braces):
            if brace not in st.session_state:
                st.session_state[brace] = "None"

            with brace_columns[idx]:
                st.subheader(f"{brace} Brace")
                brace_options = ["None"] + list(BracesForms[brace].keys())
                selected_forms[brace] = st.radio(
                    f"Select {brace} Brace Type",
                    brace_options,
                    key=brace,
                    index=brace_options.index(st.session_state[brace])
                )

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
                outbox = get_srfax_outbox()
                if outbox and outbox['Status'] == 'Success':
                    faxes = outbox['Result']
                    for fax in faxes:
                        fax['Service'] = 'SRFax'
                    all_faxes.extend(faxes)

            elif fax_service == 'HumbleFax':
                outbox = get_humble_outbox()
                if outbox and outbox['Status'] == 'Success':
                    faxes = outbox['Result']
                    for fax in faxes:
                        fax['Service'] = 'HumbleFax'
                    all_faxes.extend(faxes)

            elif fax_service == 'HalloFax':
                outbox = get_hallo_outbox()
                if outbox and outbox['Status'] == 'Success':
                    faxes = outbox['Result']
                    for fax in faxes:
                        fax['Service'] = 'HalloFax'
                    all_faxes.extend(faxes)

            elif fax_service == 'FaxPlus':
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
                        st.error("Failed to resend fax. Please try again.")

if __name__ == "__main__":
    main()