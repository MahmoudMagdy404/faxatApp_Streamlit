import streamlit as st
from urllib.parse import urlencode , quote_plus
import webbrowser
import requests

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
                            webbrowser.open(full_url)

                            st.write(f"[Click here to open the form for {brace_type} brace](<{full_url}>)")
                        else:
                            st.error(f"Failed to access the form for {brace_type} brace. Status Code: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error accessing the form for {brace_type} brace: {e}")

                st.success(f"{len(selected_urls)} form(s) are ready for submission. Please click the links above to submit.")


if __name__ == "__main__":
    main()
