# import streamlit as st
# import os
# import pandas as pd
# import time
# import gdown
# from analyzer.pdf_processor import analyze_pdf
# from analyzer.drive_uploader import download_file_from_drive
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# # --- Page setup ---
# st.set_page_config(page_title="📄 PDF Visual Analyzer", layout="wide")
# st.title("📄 GPT-4o PDF Visual Analyzer")

# # --- Session state initialization ---
# if "stop_analysis" not in st.session_state:
#     st.session_state.stop_analysis = False
# if "start_analysis" not in st.session_state:
#     st.session_state.start_analysis = False

# # --- Load catalog ---
# catalog_df = pd.read_csv("pdf_catalog.csv")

# # --- Constants ---
# DRIVE_FOLDER_ID = "1zRSbrOpugIJBPpw2aTsjYGRJcPIEZMJh"  # Replace with your folder ID
# # SERVICE_ACCOUNT_FILE = "turing-genai-ws-58339643dd3f.json"

# import json
# from google.oauth2 import service_account

# import streamlit as st

# if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in st.secrets:
#     creds_dict = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
#     credentials = service_account.Credentials.from_service_account_info(creds_dict)
# else:
#     credentials = service_account.Credentials.from_service_account_file("turing-genai-ws-58339643dd3f.json")



# # --- PDF input field ---
# pdf_name = st.text_input("Enter PDF name (e.g., TSX_OGD_2012):")

# # --- UI Buttons ---
# col1, col2 = st.columns([3, 1])

# with col1:
#     if st.button("🔍 Fetch and Analyze PDF"):
#         if not pdf_name:
#             st.error("❌ Please enter a PDF name.")
#         elif pdf_name not in catalog_df["pdf_name"].values:
#             st.error("❌ PDF name not found in catalog.")
#         else:
#             st.session_state.stop_analysis = False
#             st.session_state.start_analysis = True
#             st.rerun()

# with col2:
#     if st.button("🛑 Stop"):
#         st.session_state.stop_analysis = True
#         st.session_state.start_analysis = False
#         st.warning("⛔ Stopping analysis...")

# # --- Google Drive Search Utility ---
# def get_drive_file_id_by_name(file_name):
#     # creds = service_account.Credentials.from_service_account_file(
#     #     SERVICE_ACCOUNT_FILE,
#     #     scopes=["https://www.googleapis.com/auth/drive.readonly"]
#     # )
#     # service = build("drive", "v3", credentials=creds)

#     creds = credentials
#     service = build("drive", "v3", credentials=creds)

    
#     results = service.files().list(
#         q=f"name = '{file_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed = false",
#         fields="files(id, name)",
#         pageSize=1
#     ).execute()
#     files = results.get("files", [])
#     return files[0]["id"] if files else None

# # --- Run analysis if triggered ---
# if st.session_state.get("start_analysis", False) and not st.session_state.get("stop_analysis", False):
#     st.session_state.start_analysis = False  # reset trigger

#     # Define paths
#     csv_file_name = f"{pdf_name}_gpt4o_summary.csv"
#     local_csv_path = os.path.join("drive_outputs", csv_file_name)
#     pdf_file = f"{pdf_name}.pdf"

#     # Try to get existing result from Drive
#     st.info("🔎 Checking if already processed...")
#     file_id = get_drive_file_id_by_name(csv_file_name)

#     if file_id:
#         st.success("✅ Found existing results on Google Drive. Downloading...")
#         os.makedirs("drive_outputs", exist_ok=True)
#         # download_file_from_drive(SERVICE_ACCOUNT_FILE, file_id, local_csv_path)
#         download_file_from_drive(file_id, local_csv_path)

#         st.rerun()
#     else:
#         # Get Drive link for PDF
#         drive_link = catalog_df[catalog_df["pdf_name"] == pdf_name]["pdf_link"].values[0]
#         file_id = drive_link.split("/d/")[1].split("/")[0]
#         download_url = f"https://drive.google.com/uc?id={file_id}"

#         if not os.path.exists(pdf_file):
#             with st.spinner("⬇️ Downloading PDF from Google Drive..."):
#                 gdown.download(download_url, pdf_file, quiet=False)
#                 st.success("✅ PDF downloaded!")

#         # Progress bar
#         progress = st.progress(0, text="Starting PDF analysis...")
#         start_time = time.time()

#         def progress_callback(current, total):
#             if st.session_state.get("stop_analysis", False):
#                 raise Exception("⛔ Analysis stopped by user.")
#             pct = int((current / total) * 100)
#             progress.progress(pct, text=f"Analyzing pages... ({pct}%)")

#         try:
#             analyze_pdf(pdf_file, progress_callback=progress_callback)
#             end_time = time.time()
#             st.success(f"✅ Analysis Complete in {int(end_time - start_time)} seconds.")
#         except Exception as e:
#             st.error(f"❌ {str(e)}")

#         st.rerun()

# # --- Display Results ---
# csv_file_path = os.path.join("drive_outputs", f"{pdf_name}_gpt4o_summary.csv")
# pdf_file_path = f"{pdf_name}.pdf"

# if os.path.exists(csv_file_path):
#     df = pd.read_csv(csv_file_path)

#     # st.subheader("📘 PDF Summary")
#     # summary_text = df['pdf_summary'].iloc[0] if 'pdf_summary' in df.columns else "No summary found."
#     # st.markdown(summary_text)
#     # === TAB UI with Summary + Prompts ===
#     tab1, tab2 = st.tabs(["📘 PDF Summary", "🤯 Model-Breaking Prompts"])

#     with tab1:
#         st.subheader("📘 PDF Summary")
#         summary_text = df['pdf_summary'].iloc[0] if 'pdf_summary' in df.columns else "No summary found."
#         st.markdown(summary_text)

#     with tab2:
#         st.subheader("🤯 5 Model-Breaking Prompts")
#         if "prompts_suggestions" in df.columns and df["prompts_suggestions"].dropna().any():
#             prompt_text = df["prompts_suggestions"].dropna().iloc[0]
#             st.markdown(prompt_text)

#             st.download_button(
#                 label="📥 Download Prompts",
#                 data=prompt_text,
#                 file_name="model_breaking_prompts.txt",
#                 mime="text/plain"
#             )
#         else:
#             st.info("⚠️ No model-breaking prompts available in this report.")


#     if os.path.exists(pdf_file_path):
#         with open(pdf_file_path, "rb") as f:
#             st.download_button("📄 Download Original PDF", f.read(), file_name=pdf_file_path, mime="application/pdf")

#     st.subheader("📄 Page-wise Analysis")
#     page_numbers = df["page_no"].tolist()
#     selected_page = st.selectbox("Select a page number:", page_numbers)
#     selected_row = df[df["page_no"] == selected_page].iloc[0]
#     st.markdown(f"**Page {selected_page} Analysis:**")
#     st.markdown(selected_row["gpt4o_description"])

#     st.subheader("⬇️ Download CSV")
#     with open(csv_file_path, "rb") as f:
#         st.download_button("📊 Download Results CSV", f.read(), file_name=csv_file_path, mime="text/csv")


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

        countdown_placeholder = st.empty()
        start_time = time.time()

        def progress_callback(current, total):
            if st.session_state.get("stop_analysis", False):
                raise Exception("⛔ Analysis stopped by user.")
            elapsed = int(time.time() - start_time)
            pct = int((current / total) * 100)
            progress.progress(pct, text=f"Analyzing pages... ({pct}%)")
            countdown_placeholder.markdown(f"⏱️ Elapsed time: `{elapsed}` seconds")

        try:
            analyze_pdf(pdf_file, progress_callback=progress_callback)
            end_time = time.time()
            elapsed_total = int(end_time - start_time)
            st.success(f"✅ Analysis Complete in {elapsed_total} seconds.")
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
            prompt_text = df["prompts_suggestions"].dropna().iloc[0]
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
