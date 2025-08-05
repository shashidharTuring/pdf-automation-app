
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import streamlit as st
import json
import io
import os


def download_file_from_drive(file_id, dest_path):
    creds = service_account.Credentials.from_service_account_info(
        json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    )

    service = build("drive", "v3", credentials=creds)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()


def upload_file_to_drive(credentials, local_file_path, folder_id):
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": os.path.basename(local_file_path),
        "parents": [folder_id]
    }

    media = MediaFileUpload(local_file_path, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return uploaded["id"]
