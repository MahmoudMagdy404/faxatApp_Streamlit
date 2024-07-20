import streamlit as st
import requests
import dropbox
from dropbox.oauth import DropboxOAuth2Flow
from datetime import datetime, timedelta

# Dropbox credentials from Streamlit secrets
app_key = st.secrets["dropbox"]["app_key"]
app_secret = st.secrets["dropbox"]["app_secret"]
redirect_uri = "https://your-streamlit-app-url"
auth_flow = DropboxOAuth2Flow(app_key, app_secret, redirect_uri)

# Initialize session state
if 'dropbox_access_token' not in st.session_state:
    st.session_state['dropbox_access_token'] = None
if 'dropbox_refresh_token' not in st.session_state:
    st.session_state['dropbox_refresh_token'] = None
if 'dropbox_token_expiry' not in st.session_state:
    st.session_state['dropbox_token_expiry'] = datetime.now()

# Function to get Dropbox authorization URL
def get_authorization_url():
    return auth_flow.start()

# Function to handle OAuth2 code exchange
def handle_oauth_code(code):
    try:
        oauth_result = auth_flow.finish(code)
        st.session_state.dropbox_access_token = oauth_result.access_token
        st.session_state.dropbox_refresh_token = oauth_result.refresh_token
        st.session_state.dropbox_token_expiry = datetime.now() + timedelta(seconds=oauth_result.expires_in)
        st.success("Authorization successful!")
    except Exception as e:
        st.error(f"Failed to complete OAuth2 flow: {e}")

# Function to refresh access token
def refresh_access_token():
    if 'dropbox_refresh_token' not in st.session_state or not st.session_state.dropbox_refresh_token:
        st.error("No refresh token available.")
        return False

    try:
        url = "https://api.dropboxapi.com/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": st.session_state.dropbox_refresh_token,
            "client_id": app_key,
            "client_secret": app_secret
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        st.session_state.dropbox_access_token = token_data["access_token"]
        st.session_state.dropbox_token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])
        st.success("Access token refreshed successfully!")
        return True
    except Exception as e:
        st.error(f"Failed to refresh access token: {e}")
        return False

# Main function
def main():
    st.title("Dropbox OAuth2 Integration")

    if st.session_state.dropbox_access_token is None:
        # Generate Dropbox authorization URL
        auth_url = get_authorization_url()
        st.write(f"Please [authorize the app]({auth_url}) and then paste the authorization code here.")

        # Input for the authorization code
        auth_code = st.text_input("Authorization Code")

        if auth_code:
            handle_oauth_code(auth_code)
    else:
        st.write("You are already authenticated with Dropbox.")
        st.write("You can now use the Dropbox API.")

        # Add functionality to interact with Dropbox
        if not is_token_valid():
            if not refresh_access_token():
                st.error("Unable to refresh access token.")
                return

        # Example Dropbox API interaction
        client = dropbox.Dropbox(st.session_state.dropbox_access_token)
        try:
            account_info = client.users_get_current_account()
            st.write(f"Dropbox Account: {account_info.name.display_name}")
        except Exception as e:
            st.error(f"Error interacting with Dropbox: {e}")

if __name__ == "__main__":
    main()
