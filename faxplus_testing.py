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
from faxplus import ApiClient, Configuration
from faxplus.api.faxes_api import FaxesApi
# OAuth configuration
AUTH_URL = "https://accounts.fax.plus/login"
TOKEN_URL = "https://accounts.fax.plus/token"
REDIRECT_URI = "http://192.168.168.183:8501/"  # Update this to your Streamlit app's URL
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
    
def list_faxes(access_token, category, after, before, limit):
    conf = Configuration()
    conf.access_token = access_token
    api_client = ApiClient(header_name='x-fax-clientid', header_value=client_id, configuration=conf)
    api = FaxesApi(api_client)
    
    try:
        st.write(f"Calling list_faxes with parameters:")
        st.write(f"user_id: {user_id}")
        st.write(f"category: {category}")
        st.write(f"after: {after}")
        st.write(f"before: {before}")
        st.write(f"limit: {limit}")
        
        resp = api.list_faxes(
            user_id=user_id,
            category=category,
            after=after,
            before=before,
            limit=int(limit)
        )
        return resp.data.records
    except Exception as e:
        st.write(f"Exception details: {str(e)}")
        if hasattr(e, 'body'):
            st.write(f"Response body: {e.body}")
        if hasattr(e, 'headers'):
            st.write(f"Response headers: {e.headers}")
        raise Exception(f"Failed to list faxes: {str(e)}")

# Streamlit app
st.title("FaxPlus OAuth and Fax Listing")

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
            st.experimental_rerun()  # Rerun the app to show fax listing fields
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

    # After successful authentication
    st.write(f"Access Token: {st.session_state.access_token[:10]}...")  # Show first 10 characters
    st.write(f"User ID: {user_id}")
    st.write(f"Client ID: {client_id}")

    # Fax listing interface
    st.write("List Faxes:")
    category = st.selectbox("Select category", ["inbox", "sent", "spam"])
    after = st.date_input("Start date", datetime.now(pytz.utc) - timedelta(days=30))
    before = st.date_input("End date", datetime.now(pytz.utc))
    limit = st.number_input("Limit", min_value=1, max_value=100, value=50)

    if st.button("List Faxes"):
        try:
            after_str = after.strftime("%Y-%m-%d 00:00:00")
            before_str = before.strftime("%Y-%m-%d 23:59:59")
            faxes = list_faxes(st.session_state.access_token, category, after_str, before_str, limit)
            
            if faxes:
                st.success(f"Retrieved {len(faxes)} faxes.")
                for fax in faxes:
                    st.write(f"Fax ID: {fax.id}")
                    st.write(f"From: {fax.from_number}")
                    st.write(f"To: {fax.to}")
                    st.write(f"Status: {fax.status}")
                    st.write(f"Date: {fax.start_time}")
                    st.write("---")
            else:
                st.info("No faxes found for the given criteria.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            
            
            
            
            
def generate_prescription_request_html(date, fname, lname, ptPhone, ptAddress, ptCity, ptState, ptZip, ptDob, medID, ptHeight, ptWeight, ptGender, drName, drAddress, drCity, drState, drZip, drPhone, drFax, drNpi):
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prior Authorization Prescription Request Form</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; font-size: 12px; max-width: 210mm; min-height: 297mm;">
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="font-size: 18px;">PRIOR AUTHORIZATION PRESCRIPTION REQUEST FORM</h2>
        <p>PLEASE SEND THIS FORM BACK IN 3 BUSINESS DAYS</p>
        <p>WITH THE PT CHART NOTES ( RECENT MEDICAL RECORDS ) AND THE FAX COVER SHEET</p>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="border: 1px solid #000; padding: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>Date: {date}</div>
                <div>First: {fname}</div>
                <div>Last: {lname}</div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>DOB: {ptDob}</div>
                <div>Gender: {ptGender}</div>
            </div>
            <div style="margin-bottom: 5px;">Address: {ptAddress}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>City: {ptCity}</div>
                <div>State: {ptState}</div>
                <div>Postal Code: {ptZip}</div>
            </div>
            <div style="margin-bottom: 5px;">Patient Phone Number: {ptPhone}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>Primary Insurance: Medicare</div>
                <div>ID/HICN/MBI: {medID}</div>
            </div>
                     <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>Private Ins: </div>
                <div>Policy #:{medID}</div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>Height: {ptHeight}</div>
                <div>Weight: {ptWeight}</div>
            </div>
        </div>
        
        <div style="border: 1px solid #000; padding: 10px;">
            <div style="margin-bottom: 5px;">Physician Name: {drName}</div>
            <div style="margin-bottom: 5px;">NPI: {drNpi}</div>
            <div style="margin-bottom: 5px;">Address: {drAddress}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div>City: {drCity}</div>
                <div>State: {drState}</div>
                <div>Postal code: {drZip}</div>
            </div>
            <div style="margin-bottom: 5px;">Phone Number: {drPhone}</div>
            <div style="margin-bottom: 5px;">Fax Number: {drFax}</div>
        </div>
    </div>
    
    <div style="margin-top: 20px;">
        <h3 style="font-size: 14px;">DIAGNOSIS: Provider can specify all of the diagnosis which they feel is appropriate</h3>
        <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag1" name="diag1">
            <label for="diag1">Primary osteoarthritis, right ankle and foot (M19.071)</label>
        </div>
        <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
        <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
        <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
                <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
                <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
                <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
                <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
                <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Primary osteoarthritis, left ankle and foot (M19.072)</label>
        </div>
                <div style="margin-bottom: 5px;">
            <input type="checkbox" id="diag2" name="diag2">
            <label for="diag2">Sprain of unspecified ligament of right ankle (S93.401)</label>
        </div>
        
    </div>
    
    <div style="border: 1px solid #000; padding: 10px; margin-top: 20px;">
        <h3 style="font-size: 14px;">AFFECTED AREA</h3>
        <div style="display: flex; justify-content: ;">
            <div>
                <input type="checkbox" id="leftAnkle" name="leftAnkle">
                <label for="leftAnkle">Left ankle</label>
            </div>
            <div>
                <input type="checkbox" id="rightAnkle" name="rightAnkle">
                <label for="rightAnkle">Right Ankle</label>
            </div>
        </div>
    </div>
    
    <div style="border: 1px solid #000; padding: 10px; margin-top: 20px;">
        <h3 style="font-size: 14px;">DISPENSE</h3>
        <p>L1971: Ankle foot orthosis, plastic or other material with ankle joint, prefabricated, includes fitting and adjustment</p>
        <p>Length of need is 99 months unless otherwise specified: _____ 99-99 (LIFETIME)</p>
    </div>
    
    <div style="border: 1px solid #000; padding: 10px; margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <div>Physician Signature: _________________________</div>
            <div>Date signed: _________________________</div>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>Physician Name: {drName}</div>
            <div>NPI: {drNpi}</div>
        </div>
    </div>
</body>
</html>
    """
    return html_body