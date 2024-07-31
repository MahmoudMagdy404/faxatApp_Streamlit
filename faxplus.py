'''
FAXPLUS API is working now with OAuth2.0 , Just try to implement fax Listing and Refax option 
Nothing more
'''


import json
import streamlit as st
import requests
import base64
from datetime import datetime, timedelta
import pytz

# OAuth configuration
AUTH_URL = "https://accounts.fax.plus/login"
TOKEN_URL = "https://accounts.fax.plus/token"
REDIRECT_URI = "http://192.168.168.183:8503/"  # Update this to your Streamlit app's URL
API_BASE_URL = "https://restapi.fax.plus/v3"




# Load secrets
client_id = st.secrets["faxplus_auth"]["client_id"]
client_secret = st.secrets["faxplus_auth"]["client_secret"]
user_id = st.secrets["faxplus_secret_key"]["user_id"]

# Function to get authorization URL
def get_auth_url():
    return f"{AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={REDIRECT_URI}&scope=all"

def exchange_code_for_tokens(code):
    url = f"{TOKEN_URL}?grant_type=authorization_code&client_id={client_id}&code={code}&redirect_uri={REDIRECT_URI}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'access_token' not in data:
            raise Exception(f"Access token not found in response. Response: {json.dumps(data, indent=2)}")
        return data
    else:
        raise Exception(f"Failed to exchange code for tokens. Status code: {response.status_code}, Response: {response.text}")


# Function to refresh access token
def refresh_access_token(refresh_token):
    url = f"{TOKEN_URL}?grant_type=refresh_token&refresh_token={refresh_token}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to refresh access token: {response.text}")


def upload_file(file, access_token):
    url = f"{API_BASE_URL}/accounts/self/files?format=pdf"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-fax-clientid": client_id
    }
    files = {"fax_file": file}
    
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()["path"]
    else:
        raise Exception(f"File upload failed: {response.text}")


def send_fax(to_numbers, file_paths, message, access_token):
    url = f"{API_BASE_URL}/accounts/self/outbox"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-fax-clientid": client_id,
        "Content-Type": "application/json"
    }
    
    current_time = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S +0000")

    payload = {
        "to": to_numbers,
        "files": file_paths,
        "comment": {
            "text": message
        },
        "send_time": current_time
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Fax sending failed. Status code: {response.status_code}, Response: {response.text}")

# Streamlit app
st.title("FaxPlus OAuth and Fax Sender")

if 'access_token' not in st.session_state:
    # OAuth flow
    if 'code' in st.query_params:
        code = st.query_params['code']
        try:
            tokens = exchange_code_for_tokens(code)
            st.session_state.access_token = tokens['access_token']
            st.session_state.refresh_token = tokens.get('refresh_token')
            expires_in = tokens.get('expires_in', 3600)
            st.session_state.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            st.success("Authorization successful!")
            st.query_params.clear()
            st.experimental_rerun()  # Rerun the app to show fax sending fields
        except Exception as e:
            st.error(f"Authorization failed: {str(e)}")
    else:
        st.write("Please authorize the app to access your FaxPlus account.")
        auth_url = get_auth_url()
        st.markdown(f"[Click here to authorize]({auth_url})")
else:
    # Check if the access token is expired and refresh if necessary
    if datetime.now() >= st.session_state.token_expiry:
        try:
            new_tokens = refresh_access_token(st.session_state.refresh_token)
            st.session_state.access_token = new_tokens['access_token']
            st.session_state.token_expiry = datetime.now() + timedelta(seconds=new_tokens.get('expires_in', 3600))
        except Exception as e:
            st.error(f"Failed to refresh token: {str(e)}")
            st.session_state.pop('access_token', None)
            st.session_state.pop('refresh_token', None)
            st.experimental_rerun()

    # Fax sending interface
    st.write("Send a fax:")
    to_numbers = st.text_input("Enter fax numbers (comma-separated)", "+12345688,+12345699")
    uploaded_files = st.file_uploader("Upload files to fax", accept_multiple_files=True)
    message = st.text_area("Enter fax message", "This is a test fax sent from Streamlit.")

    # In the Streamlit app:
    if st.button("Send Fax"):
        if not uploaded_files:
            st.error("Please upload at least one file.")
        else:
            try:
                # Upload files
                uploaded_file_paths = []
                for file in uploaded_files:
                    file_path = upload_file(file, st.session_state.access_token)
                    uploaded_file_paths.append(file_path['path'])
                
                st.write(f"Files uploaded successfully. Paths: {uploaded_file_paths}")
                
                # Send fax
                to_numbers_list = [num.strip() for num in to_numbers.split(',')]
                result = send_fax(to_numbers_list, uploaded_file_paths, message, st.session_state.access_token)
                st.success("Fax sent successfully!")
                st.json(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.button("Logout"):
        st.session_state.pop('access_token', None)
        st.session_state.pop('refresh_token', None)
        st.experimental_rerun()