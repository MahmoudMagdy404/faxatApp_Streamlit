import json
import io
import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests
import os

# # Set up the necessary variables
# TOKEN_FOLDER_ID = '1HDwNvgFv_DSEH2WKNfLNheKXxKT_hDM9'
# SCOPES = ["https://www.googleapis.com/auth/drive"]

# # Fetch credentials from Streamlit secrets
# credentials_json = st.secrets["google_credentials"]["credentials_json"]

# def get_drive_service():
#     creds = Credentials.from_authorized_user_info(json.loads(credentials_json), SCOPES)
#     return build('drive', 'v3', credentials=creds)

# def generate_and_upload_token():
#     try:
#         st.write("Starting token generation...")
#         flow = InstalledAppFlow.from_client_config(
#             json.loads(credentials_json), SCOPES
#         )
#         creds = flow.run_local_server(port=0)
#         st.write("Authentication flow completed.")
        
#         service = get_drive_service()
#         token_json = creds.to_json()
#         st.write("Token JSON created.")
        
#         # Store token locally
#         try:
#             with open('token.json', 'w') as token_file:
#                 token_file.write(token_json)
#             st.success('Token stored locally.')
#         except Exception as local_error:
#             st.error(f"Error storing token locally: {local_error}")
        
#         # Debug: Print token contents (redact sensitive info)
#         debug_token = json.loads(token_json)
#         debug_token['client_id'] = 'REDACTED'
#         debug_token['client_secret'] = 'REDACTED'
#         debug_token['refresh_token'] = 'REDACTED'
#         st.write("Debug - Token contents:", json.dumps(debug_token, indent=2))
        
#         # ... (rest of the function remains the same)
        
#     except Exception as e:
#         st.error(f'Error generating or uploading token: {e}')
#         return False
# def download_token_from_drive():
#     try:
#         service = get_drive_service()
#         query = f"'{TOKEN_FOLDER_ID}' in parents and name='token.json'"
#         results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
#         items = results.get('files', [])
        
#         if not items:
#             st.warning(f'No token file found in Google Drive folder: {TOKEN_FOLDER_ID}')
#             return None
        
#         file_id = items[0]['id']
#         request = service.files().get_media(fileId=file_id)
#         fh = io.BytesIO()
#         downloader = MediaIoBaseDownload(fh, request)
#         done = False
#         while not done:
#             status, done = downloader.next_chunk()
#             st.info(f"Download {int(status.progress() * 100)}%")
#         fh.seek(0)
        
#         return fh.getvalue().decode('utf-8')
#     except Exception as e:
#         st.error(f'Error downloading token: {e}')
#         return None
# def get_credentials():
#     token_data = download_token_from_drive()
    
#     if not token_data:
#         st.warning("Couldn't download token from Drive. Checking for local token.")
#         if os.path.exists('token.json'):
#             with open('token.json', 'r') as token_file:
#                 token_data = token_file.read()
#         else:
#             st.warning("No local token found.")
    
#     if token_data:
#         creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
#     else:
#         # If no token found, generate and upload it
#         if not generate_and_upload_token():
#             return None
#         token_data = download_token_from_drive()
#         if not token_data and os.path.exists('token.json'):
#             with open('token.json', 'r') as token_file:
#                 token_data = token_file.read()
#         creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(google.auth.transport.requests.Request())
#             # Save updated token to Google Drive and locally
#             token_json = creds.to_json()
#             with open('token.json', 'w') as token_file:
#                 token_file.write(token_json)
#             generate_and_upload_token()
#         else:
#             if not generate_and_upload_token():
#                 return None
#             token_data = download_token_from_drive()
#             if not token_data and os.path.exists('token.json'):
#                 with open('token.json', 'r') as token_file:
#                     token_data = token_file.read()
#             creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
    
#     return creds

# # Example usage in your main application
# def main():
#     st.title('Google Drive Token Management')

#     if st.button('Get Credentials'):
#         credentials = get_credentials()
#         if credentials:
#             st.success('Credentials obtained successfully!')
#         else:
#             st.error('Failed to obtain credentials.')

# if __name__ == "__main__":
#     main()


from datetime import datetime, timezone
import os
import tempfile
import time
import pandas as pd
import streamlit as st
from urllib.parse import urlencode, quote_plus
import requests
from PyPDF2 import PdfMerger, PdfReader
import re
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import base64
from google.oauth2 import service_account
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from PyPDF2 import PdfMerger, PdfReader
import io
import json
from google.auth.transport.requests import Request
import dropbox
from dropbox.exceptions import AuthError
from dropbox.files import WriteMode
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth
from faxplus import ApiClient, OutboxApi, OutboxComment, RetryOptions, OutboxOptions, OutboxCoverPage, PayloadOutbox , FilesApi 
from faxplus.configuration import Configuration
from datetime import datetime
from faxplus.rest import ApiException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

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
        creds = flow.run_local_server(port=0)
        
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

        fname = fname.strip()
        target_files = [file for file in items if fname in file["name"]]

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


combine_pdfs("Katrina Glover, MD")
