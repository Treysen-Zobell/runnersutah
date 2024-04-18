import io
from typing import TextIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload


class GoogleDrive:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            "runnersutah-website-420403-bdbb44c179d8.json"
        )
        scoped_credentials = creds.with_scopes(
            ["https://www.googleapis.com/auth/drive"]
        )
        self.service = build("drive", "v3", credentials=scoped_credentials)

    def list_files(self):
        try:
            results = (
                self.service.files()
                .list(pageSize=10, fields="nextPageToken, files(id, name)")
                .execute()
            )

            items = results.get("files", [])
            return items

        except HttpError as error:
            print(f"Failed to get file list from Google Drive: {error}")

    def upload_file(self, file: TextIO):
        file_metadata = {"name": file.name}
        media = MediaIoBaseUpload(file, mimetype="application/pdf", resumable=True)
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"Uploaded file with id {file['id']}")
        return file["id"]

    def download_file(self, file_id: str):
        try:
            request_file = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request_file)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_id}... {int(status.progress() * 100)}%")

            file_retrieved = file.getvalue()
            return file_retrieved

        except HttpError as error:
            print(f"Failed to download file from Google Drive: {error}")

    def delete_file(self, file_id: str):
        try:
            self.service.files().update(
                fileId=file_id, body={"trashed": True}
            ).execute()

        except HttpError as error:
            print(f"Failed to get file list from Google Drive: {error}")