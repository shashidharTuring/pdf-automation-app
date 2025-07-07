import streamlit as st
import os
import pandas as pd
import time
import gdown
import json
from analyzer.pdf_processor import analyze_pdf
from analyzer.drive_uploader import download_file_from_drive
from googleapiclient.discovery import build
from google.oauth2 import service_account


import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json, os

import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests


import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

# # ---- Google OAuth login gate ----
# def google_login():
#     if "user_email" in st.session_state:
#         return  # Already authenticated

#     client_cfg = {
#         "web": {
#             "client_id": st.secrets["GOOGLE_CLIENT_ID"],
#             "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
#             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "redirect_uris": [st.secrets["REDIRECT_URI"]],
#         }
#     }

#     flow = Flow.from_client_config(
#         client_cfg,
#         scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
#         redirect_uri=client_cfg["web"]["redirect_uris"][0],
#     )

#     # Step 1: Redirect to Google Login
#     if "code" not in st.query_params:
#         auth_url, _ = flow.authorization_url(prompt="consent")

#         col1, col2, col3 = st.columns([1, 2, 1])
#         with col2:
#             st.image("https://assets-global.website-files.com/64ad6c926d3c2e8d7dd31f6e/64ba7b20ceee5412f306b777_logo_full_dark.svg", width=220)

#             html = f"""
#             <div style="text-align: center; margin-top: 2rem;">
#                 <h2>🔐 Turing Internal Access</h2>
#                 <p style="font-size: 1.1rem;">Please sign in with your <strong>@turing.com</strong> Google account to continue.</p>
#                 <a href="{auth_url}" target="_self" style="
#                     background-color: #0366d6;
#                     color: white;
#                     padding: 0.75rem 1.5rem;
#                     font-size: 1rem;
#                     border-radius: 6px;
#                     text-decoration: none;
#                     display: inline-block;
#                     margin-top: 1rem;
#                 ">
#                     👉 Sign in with Google
#                 </a>
#             </div>
#             """
#             st.markdown(html, unsafe_allow_html=True)
#         st.stop()

#     # Step 2: Handle callback from Google
#     try:
#         code = st.query_params["code"]
#         flow.fetch_token(code=code)
#         creds = flow.credentials
#         idinfo = id_token.verify_oauth2_token(
#             creds._id_token,
#             requests.Request(),
#             client_cfg["web"]["client_id"]
#         )
#         email = idinfo.get("email", "")
#     except Exception as e:
#         st.error(f"❌ OAuth failed: {e}")
#         st.stop()

#     # Step 3: Check email domain
#     if email.endswith(f"@{st.secrets['ALLOWED_DOMAIN']}"):
#         st.session_state["user_email"] = email
#         st.query_params.clear()  # ✅ Clear ?code=... from the URL
#         st.rerun()
#     else:
#         st.error("Access denied. Only @turing.com accounts are allowed.")
#         st.stop()

# # ✅ Call this at the very top of your streamlit_app.py
# google_login()










































# --- Page setup ---
st.set_page_config(page_title="📄 PDF Visual Analyzer", layout="wide")
st.title("📄 GPT-4o PDF Visual Analyzer")

# --- Session state initialization ---
if "stop_analysis" not in st.session_state:
    st.session_state.stop_analysis = False
if "start_analysis" not in st.session_state:
    st.session_state.start_analysis = False
if "status_log" not in st.session_state:
    st.session_state.status_log = []

# --- Utility for logging status ---
def log_status(msg):
    st.session_state.status_log.append(msg)
    with st.sidebar:
        st.markdown("### 🚧 Status")
        for entry in st.session_state.status_log[-8:]:
            st.markdown(f"- {entry}")

# --- Load catalog ---
catalog_df = pd.read_csv("pdf_catalog.csv")

# --- Constants ---
DRIVE_FOLDER_ID = "1zRSbrOpugIJBPpw2aTsjYGRJcPIEZMJh"

# --- Authenticate Google Credentials ---
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in st.secrets:
    creds_dict = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
else:
    credentials = service_account.Credentials.from_service_account_file("turing-genai-ws-58339643dd3f.json")

# --- PDF input field ---
pdf_name = st.text_input("Enter PDF name (e.g., TSX_OGD_2012):")

# --- UI Buttons ---
col1, col2 = st.columns([3, 1])

with col1:
    if st.button("🔍 Fetch and Analyze PDF"):
        if not pdf_name:
            st.error("❌ Please enter a PDF name.")
        elif pdf_name not in catalog_df["pdf_name"].values:
            st.error("❌ PDF name not found in catalog.")
        else:
            st.session_state.stop_analysis = False
            st.session_state.start_analysis = True
            st.session_state.status_log = ["🚀 Analysis triggered..."]
            st.rerun()

with col2:
    if st.button("🚩 Stop"):
        st.session_state.stop_analysis = True
        st.session_state.start_analysis = False
        st.warning("⛔ Stopping analysis...")

# --- Google Drive Search Utility ---
def get_drive_file_id_by_name(file_name):
    service = build("drive", "v3", credentials=credentials)
    results = service.files().list(
        q=f"name = '{file_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed = false",
        fields="files(id, name)",
        pageSize=1
    ).execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None

# --- Run analysis if triggered ---
if st.session_state.get("start_analysis", False) and not st.session_state.get("stop_analysis", False):
    st.session_state.start_analysis = False

    csv_file_name = f"{pdf_name}_gpt4o_summary.csv"
    local_csv_path = os.path.join("drive_outputs", csv_file_name)
    pdf_file = f"{pdf_name}.pdf"

    log_status("🔍 Checking for existing results on Google Drive...")
    file_id = get_drive_file_id_by_name(csv_file_name)

    if file_id:
        log_status("✅ Found on Drive. Downloading CSV...")
        os.makedirs("drive_outputs", exist_ok=True)
        download_file_from_drive(file_id, local_csv_path)
        log_status("📂 Download complete.")
        st.rerun()
    else:
        drive_link = catalog_df[catalog_df["pdf_name"] == pdf_name]["pdf_link"].values[0]
        file_id = drive_link.split("/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?id={file_id}"

        if not os.path.exists(pdf_file):
            with st.spinner("⬇️ Downloading PDF from Google Drive..."):
                log_status("📁 Downloading PDF from Google Drive...")
                gdown.download(download_url, pdf_file, quiet=False)
                log_status("✅ PDF downloaded successfully.")

        st.warning("⏳ Please wait ~90–120 seconds for full analysis.")
        log_status("🔄 Starting GPT-4o analysis. This may take 1–2 minutes...")
        progress = st.progress(0, text="Starting PDF analysis...")
        start_time = time.time()
        elapsed_display = st.empty()


        def progress_callback(current, total):
            if st.session_state.get("stop_analysis", False):
                raise Exception("⛔ Analysis stopped by user.")
            pct = int((current / total) * 100)
            progress.progress(pct, text=f"Analyzing pages... ({pct}%)")
            elapsed_time = int(time.time() - start_time)
            elapsed_display.markdown(f"⏱️ Elapsed time: `{elapsed_time}` seconds")


        try:
            analyze_pdf(pdf_file, progress_callback=progress_callback)
            end_time = time.time()
            st.success(f"✅ Analysis Complete in {int(end_time - start_time)} seconds.")
            log_status("✅ Analysis complete. Summary + prompts generated.")
        except Exception as e:
            st.error(f"❌ {str(e)}")
            log_status(f"❌ Analysis failed: {str(e)}")

        st.rerun()

# --- Display Results ---
csv_file_path = os.path.join("drive_outputs", f"{pdf_name}_gpt4o_summary.csv")
pdf_file_path = f"{pdf_name}.pdf"

if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)

    tab1, tab2 = st.tabs(["📘 PDF Summary", "🤯 Model-Breaking Prompts"])

    with tab1:
        st.subheader("📘 PDF Summary")
        summary_text = df['pdf_summary'].iloc[0] if 'pdf_summary' in df.columns else "No summary found."
        st.markdown(summary_text)

    with tab2:
        st.subheader("🤯 5 Model-Breaking Prompts")
        if "prompts_suggestions" in df.columns and df["prompts_suggestions"].dropna().any():
            prompt_text = df.loc[df["prompts_suggestions"].str.strip() != "", "prompts_suggestions"].iloc[0]

            st.markdown(prompt_text)

            st.download_button(
                label="📥 Download Prompts",
                data=prompt_text,
                file_name="model_breaking_prompts.txt",
                mime="text/plain"
            )
        else:
            st.info("⚠️ No model-breaking prompts available in this report.")

    if os.path.exists(pdf_file_path):
        with open(pdf_file_path, "rb") as f:
            st.download_button("📄 Download Original PDF", f.read(), file_name=pdf_file_path, mime="application/pdf")

    st.subheader("📄 Page-wise Analysis")
    page_numbers = df["page_no"].tolist()
    selected_page = st.selectbox("Select a page number:", page_numbers)
    selected_row = df[df["page_no"] == selected_page].iloc[0]
    st.markdown(f"**Page {selected_page} Analysis:**")
    st.markdown(selected_row["gpt4o_description"])

    st.subheader("⬇️ Download CSV")
    with open(csv_file_path, "rb") as f:
        st.download_button("📊 Download Results CSV", f.read(), file_name=csv_file_path, mime="text/csv")
