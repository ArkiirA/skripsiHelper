import os
from pathlib import Path
from typing import Optional
from datetime import timedelta
from google.cloud import storage

from skripsi_helper.core.config import settings

LOCAL_STORAGE_DIR = Path("storage/pdfs")


def get_gcs_client() -> Optional[storage.Client]:
    """Return GCS client or None if credentials not configured."""
    try:
        if settings.GCS_CREDENTIALS_PATH and os.path.exists(settings.GCS_CREDENTIALS_PATH):
            return storage.Client.from_service_account_json(settings.GCS_CREDENTIALS_PATH)
        return storage.Client()
    except Exception:
        return None


def store_pdf_file(file_bytes: bytes, filename: str, project_id: int) -> str:
    """Store PDF in GCS (or local storage fallback). Return storage path."""
    destination_blob = f"projects/{project_id}/pdfs/{filename}"
    client = get_gcs_client()

    if client:
        try:
            bucket = client.bucket(settings.GCS_BUCKET_NAME)
            blob = bucket.blob(destination_blob)
            blob.upload_from_string(file_bytes, content_type="application/pdf")
            return f"gs://{settings.GCS_BUCKET_NAME}/{destination_blob}"
        except Exception:
            pass

    # Local fallback for dev/testing
    LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    local_path = LOCAL_STORAGE_DIR / f"{project_id}_{filename}"
    local_path.write_bytes(file_bytes)
    return str(local_path)


def get_pdf_download_url(gcs_or_local_path: str) -> str:
    """Generate signed URL or direct path for download."""
    if gcs_or_local_path.startswith("gs://"):
        client = get_gcs_client()
        if client:
            try:
                parts = gcs_or_local_path.replace("gs://", "").split("/", 1)
                bucket = client.bucket(parts[0])
                blob = bucket.blob(parts[1])
                return blob.generate_signed_url(expiration=timedelta(hours=1))
            except Exception:
                pass

    return f"/api/v1/citations/download-file?path={gcs_or_local_path}"
