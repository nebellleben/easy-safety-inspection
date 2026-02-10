"""S3 storage service."""
import os
from datetime import timedelta
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


class StorageService:
    """S3-compatible storage service."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        region: str | None = None,
        use_ssl: bool | None = None,
    ):
        """Initialize storage service."""
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.access_key = access_key or settings.S3_ACCESS_KEY
        self.secret_key = secret_key or settings.S3_SECRET_KEY
        self.bucket = bucket or settings.S3_BUCKET
        self.region = region or settings.S3_REGION
        self.use_ssl = use_ssl if use_ssl is not None else settings.S3_USE_SSL

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name=self.region,
            use_ssl=self.use_ssl,
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create if not."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket)
                except ClientError as create_error:
                    # Handle bucket creation error (might already exist)
                    pass
            else:
                raise

    def generate_key(self, filename: str, prefix: str = "photos") -> str:
        """Generate a unique S3 key for a file."""
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid4()}{ext}"
        return f"{prefix}/{unique_filename}"

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        prefix: str = "photos",
    ) -> tuple[str, int]:
        """
        Upload a file to S3.

        Returns:
            Tuple of (s3_key, file_size)
        """
        s3_key = self.generate_key(filename, prefix)
        file_size = len(file_data)

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=file_data,
            ContentType=content_type,
        )

        return s3_key, file_size

    def upload_fileobj(
        self,
        fileobj,
        filename: str,
        content_type: str,
        prefix: str = "photos",
    ) -> tuple[str, int]:
        """
        Upload a file-like object to S3.

        Returns:
            Tuple of (s3_key, file_size)
        """
        s3_key = self.generate_key(filename, prefix)

        # Read file to get size
        fileobj.seek(0, os.SEEK_END)
        file_size = fileobj.tell()
        fileobj.seek(0)

        self.s3_client.upload_fileobj(
            fileobj,
            self.bucket,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )

        return s3_key, file_size

    def get_presigned_url(
        self, s3_key: str, expires_in: int = 3600
    ) -> str:
        """Generate a presigned URL for downloading a file."""
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": s3_key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False

    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Get a URL for the file."""
        # If using public endpoint, could return direct URL
        # For now, always use presigned URLs
        return self.get_presigned_url(s3_key, expires_in)


# Global storage service instance
storage_service = StorageService()
