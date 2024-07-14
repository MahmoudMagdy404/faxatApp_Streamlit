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
import tempfile


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
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_json = json.loads(st.secrets["google_credentials"]["credentials_json"])
                flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
                creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        service = build("drive", "v3", credentials=creds)
        folder_id = "15I95Loh35xI2PcGa36xz7SgMtclo-9DC"
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, pageSize=20, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get("files", [])
        if not items:
            return None, "No files found in the specified folder."

        target_files = [file for file in items if fname in file["name"]]

        if not target_files:
            return None, "No matching files found."

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
            fh.seek(0)
            file_content = fh.read()

            temp_pdf_path = os.path.join(tempfile.gettempdir(), f"temp_{sanitized_file_name}.pdf")
            with open(temp_pdf_path, "wb") as f:
                f.write(file_content)

            with open(temp_pdf_path, "rb") as f:
                merger.append(f)

            os.remove(temp_pdf_path)

        combined_pdf_path = os.path.join(tempfile.gettempdir(), f"{sanitize_filename(fname)}_combined.pdf")
        with open(combined_pdf_path, "wb") as f:
            merger.write(f)

        merger.close()
        return combined_pdf_path, None

    except HttpError as error:
        return None, f"An error occurred: {error}"

def main():
    # st.markdown(
    #     """
    #     <style>
    #     .main {
    #         background-color: #F3F7EC;
    #     }
    #     .css-1v0mbdj {
    #         background-color: #005C78;
    #         color: #FFFFFF;
    #         font-weight: bold;
    #         padding: 0.75em 1.5em;
    #         border-radius: 5px;
    #         text-align: center;
    #     }
    #     .css-1v0mbdj:hover {
    #         background-color: #006989;
    #     }
    #     .css-1f1h61n {
    #         margin: 1em 0;
    #     }
    #     </style>
    #     """, unsafe_allow_html=True
    # )

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
            fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip,
            ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress,
            drCity, drState, drZip, drPhone, drFax, drNpi
        ]
        if not all(required_fields):
            return False, "All fields are required."
        return True, None

    if st.button("Submit"):
        is_valid, validation_message = validate_all_fields()
        if not is_valid:
            st.error(validation_message)
        else:
            patient_params = {
                "entry.1013683290": date,
                "entry.1096785263": fname,
                "entry.1842745765": lname,
                "entry.1436444388": ptPhone,
                "entry.128647103": ptAddress,
                "entry.1838964175": ptCity,
                "entry.1256466694": ptState,
                "entry.76096564": ptZip,
                "entry.947716815": ptDob,
                "entry.1442211744": medID,
                "entry.80565363": ptHeight,
                "entry.1560113764": ptWeight,
                "entry.848469829": ptGender,
                "entry.1557749263": drName,
                "entry.1569206044": drAddress,
                "entry.752895498": drCity,
                "entry.2043453995": drState,
                "entry.146484812": drZip,
                "entry.1998442715": drPhone,
                "entry.1096785263": drFax,
                "entry.1069274004": drNpi,
            }

            submission_results = []

            for brace, form_url in selected_forms.items():
                if form_url != "None":
                    if brace in BracesForms and form_url in BracesForms[brace]:
                        form_url = BracesForms[brace][form_url]
                        brace_params = {
                            f"entry.{field_id}": value
                            for field_id, value in patient_params.items()
                        }
                        form_url = f"{form_url}?{urlencode(brace_params, quote_via=quote_plus)}"
                        response = requests.get(form_url)
                        if response.status_code == 200:
                            submission_results.append(f"{brace} form submitted successfully.")
                        else:
                            submission_results.append(f"Failed to submit {brace} form.")
                    else:
                        submission_results.append(f"No form URL found for {brace}.")
            st.success("\n".join(submission_results))

            combined_pdf_path, error = combine_pdfs(fname)
            if error:
                st.error(error)
            else:
                with open(combined_pdf_path, "rb") as f:
                    combined_pdf_data = f.read()

                st.download_button(
                    label="Download Combined PDF",
                    data=combined_pdf_data,
                    file_name=f"{fname}_combined.pdf",
                    mime="application/pdf"
                )
                st.success(f"Combined PDF for {fname} created successfully.")

if __name__ == "__main__":
    main()
