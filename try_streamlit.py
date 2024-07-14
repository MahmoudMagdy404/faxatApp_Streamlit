import streamlit as st
from urllib.parse import urlencode, quote_plus
import requests
from PyPDF2 import PdfMerger
import io
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the braces and their forms
Braces = ["Back", "Knees", "Elbow", "Shoulder", "Ankle", "Wrists"]
BracesForms = {
    "Back": {
        'L0637': 'https://docs.google.com/forms/d/e/1FAIpQLSfB7423u2nFC_boKiOq8w-8E6ClY9iY2QLW_-_-SLQwJfbdZg/formResponse',
        'L0457': 'https://docs.google.com/forms/d/e/1FAIpQLSe-XTJycYlVMnS7PU6YeIeDXugcBMLuJ1YGr7Y8KEsO3iXRlQ/formResponse'
    },
    "Knees": {
        'L1843': 'https://docs.google.com/forms/d/e/1FAIpQLScf00eJOF1u_60swPRguOZEJTtU7mx6lxIfNUWEJzndiDPD5A/formResponse',
        'L1852': 'https://docs.google.com/forms/d/e/1FAIpQLSec52MiutxlJmayam2l0FiQSorT9gyG9efhx7bG7D3K2nPagg/formResponse',
        'L1845': 'https://docs.google.com/forms/d/e/1FAIpQLSfav9S2KJRjyqYClJgZrSuHibaaxSy5gsxvDpqLVrCTyM_8sA/formResponse'
    },
    "Elbow": {
        'L3761': 'https://docs.google.com/forms/d/e/1FAIpQLSfYFk34nTDrm5D22WbVpg5uuASxRoAcc-eaUvJ_rkCNGNLXzw/formResponse'
    },
    "Shoulder": {
        'L3960': 'https://docs.google.com/forms/d/e/1FAIpQLSexO54gwNijfOMjcSp9ZC_9LhXsE0lKpkzzqBQy0_ddBzg1_Q/formResponse'
    },
    "Ankle": {
        'L1971': 'https://docs.google.com/forms/d/e/1FAIpQLSdyRf99metRszBuQ8zHwzQSYvxf-Pb5qJDzJj073-Vu6sfZEA/formResponse'
    },
    "Wrists": {
        'L3916': 'https://docs.google.com/forms/d/e/1FAIpQLSd4XQox2yt3wsild0InVMgagrcQ9Aors4PjExoOILHiT9grew/formResponse'
    }
}
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)

def combine_pdfs(fname):
    try:
        logging.info("Starting PDF combination process.")
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = None
        
        # Check for token in session state
        if 'token' in st.session_state:
            creds = Credentials.from_authorized_user_info(st.session_state['token'], SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_json = json.loads(st.secrets["google_credentials"]["credentials_json"])
                flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials in session state
                st.session_state['token'] = json.loads(creds.to_json())

        logging.info("Building Google Drive service.")
        service = build("drive", "v3", credentials=creds)
        folder_id = "15I95Loh35xI2PcGa36xz7SgMtclo-9DC"
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, pageSize=20, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get("files", [])
        if not items:
            logging.warning("No files found in the specified folder.")
            return None, "No files found in the specified folder."

        target_files = [file for file in items if fname in file["name"]]

        if not target_files:
            logging.warning("No matching files found.")
            return None, "No matching files found."

        logging.info(f"Found {len(target_files)} matching files. Starting PDF merge.")
        merger = PdfMerger()
        for target_file in target_files:
            mime_type = target_file.get("mimeType")
            file_id = target_file.get("id")
            file_name = target_file.get("name")
            sanitized_file_name = sanitize_filename(file_name)

            if mime_type.startswith("application/vnd.google-apps."):
                export_mime_type = "application/pdf"
                request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            else:
                request = service.files().get_media(fileId=file_id)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f"Downloaded {int(status.progress() * 100)}% of {file_name}.")
            fh.seek(0)
            file_content = fh.read()

            temp_pdf_path = os.path.join(os.getcwd(), f"temp_{sanitized_file_name}.pdf")
            with open(temp_pdf_path, "wb") as f:
                f.write(file_content)

            with open(temp_pdf_path, "rb") as f:
                merger.append(f)

            os.remove(temp_pdf_path)

        combined_pdf_path = os.path.join(os.getcwd(), f"{sanitize_filename(fname)}_combined.pdf")
        with open(combined_pdf_path, "wb") as f:
            merger.write(f)

        merger.close()
        logging.info(f"Combined PDF saved to {combined_pdf_path}.")
        return combined_pdf_path, None

    except HttpError as error:
        logging.error(f"An error occurred: {error}")
        return None, f"An error occurred: {error}"

def main():
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
        ptGender = st.selectbox("Gender", ["Male", "Female", "Other"])

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
            st.write(brace)
            options = ["None"] + list(BracesForms[brace].keys())
            choice = st.radio(f"Choose {brace} Form", options, index=options.index(st.session_state[brace]), key=brace)
            if choice != "None":
                selected_forms[brace] = BracesForms[brace][choice]

    submitted = st.button("Submit Forms")

    if submitted:
        logging.info("Form submission started.")
        logging.info(f"Selected forms: {selected_forms}")
        form_data = {
            'entry.1514355731': date.strftime('%Y-%m-%d'),
            'entry.1875681828': fname,
            'entry.1895444545': lname,
            'entry.1665101977': ptPhone,
            'entry.989664536': ptAddress,
            'entry.2040354425': ptCity,
            'entry.314703275': ptState,
            'entry.1606987851': ptZip,
            'entry.427126331': ptDob,
            'entry.1525956683': medID,
            'entry.849807525': ptHeight,
            'entry.2061358987': ptWeight,
            'entry.1805780994': ptGender,
            'entry.520924561': drName,
            'entry.1318794132': drAddress,
            'entry.186314603': drCity,
            'entry.993400837': drState,
            'entry.1239738180': drZip,
            'entry.537430697': drPhone,
            'entry.987445008': drFax,
            'entry.1857894757': drNpi
        }

        encoded_data = urlencode(form_data, quote_via=quote_plus)

        for brace, form_url in selected_forms.items():
            try:
                response = requests.post(form_url, data=encoded_data)
                response.raise_for_status()
                logging.info(f"Submitted {brace} form successfully.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error submitting {brace} form: {e}")
                st.error(f"Error submitting {brace} form: {e}")

        combined_pdf_path, error = combine_pdfs(f"{fname} {lname}")
        if combined_pdf_path:
            with open(combined_pdf_path, "rb") as f:
                st.download_button("Download Combined PDF", f, file_name=f"{fname}_{lname}_combined.pdf")
        else:
            st.error(error)

if __name__ == "__main__":
    main()
