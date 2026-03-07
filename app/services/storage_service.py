import uuid
from supabase import create_client, Client
from app.config.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from app.utils.logger import logger


BUCKET_NAME = "task-attachments"


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class StorageService:
    def __init__(self):
        self.client = get_supabase_client()
        self.bucket = BUCKET_NAME

    def upload_file(self, file_bytes: bytes, file_name: str, content_type: str, task_id: str) -> dict:
        """
        Upload a file to Supabase Storage under task-attachments/<task_id>/<unique_file_name>.

        Returns a dict with file_url, file_name, file_size, file_type, and a generated id.
        """
        try:
            unique_name = f"{uuid.uuid4()}_{file_name}"
            file_path = f"{task_id}/{unique_name}"

            self.client.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type},
            )

            # Build public URL
            file_url = (
                f"{SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{file_path}"
            )

            return {
                "id": str(uuid.uuid4()),
                "file_name": file_name,
                "file_url": file_url,
                "file_size": len(file_bytes),
                "file_type": content_type,
            }

        except Exception as e:
            logger.error(f"Error uploading file to Supabase Storage: {e}", exc_info=e)
            raise

    def delete_file(self, task_id: str, unique_file_name: str) -> bool:
        """
        Delete a file from Supabase Storage.

        Args:
            task_id: The task ID (used as folder name in storage).
            unique_file_name: Full file name including uuid prefix (e.g. 'uuid4_filename.pdf').

        Returns True if deleted successfully.
        """
        try:
            file_path = f"{task_id}/{unique_file_name}"
            self.client.storage.from_(self.bucket).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}", exc_info=e)
            raise
    
    def delete_folder(self, task_id: str) -> bool:
        """
        Delete entire folder for a task from Supabase Storage.
        Lists all files in folder then removes them all at once.
        """
        try:
            # List semua file dalam folder
            files = self.client.storage.from_(self.bucket).list(task_id)
            if not files:
                return True
            
            # Build path list
            paths = [f"{task_id}/{f['name']}" for f in files]
            
            # Remove semua sekaligus
            self.client.storage.from_(self.bucket).remove(paths)
            return True
        except Exception as e:
            logger.error(f"Error deleting folder: {e}", exc_info=e)
            raise