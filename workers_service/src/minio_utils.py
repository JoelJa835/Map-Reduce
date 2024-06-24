from minio import Minio
from minio.error import S3Error
import os
import traceback
import io

MINIO_ENDPOINT = os.getenv("MINIO_SERVICE_URL", "minio-service:9000")
MINIO_ACCESS_KEY = 'dena'
MINIO_SECRET_KEY = 'dena1234'
MINIO_BUCKET = 'chunk-bucket'

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # Set to True if using HTTPS
)


def get_file(filename, bucket_name):
    try:
        response = minio_client.get_object(bucket_name, filename)
        file_content = response.read().decode('utf-8')  # Assuming the content is UTF-8 encoded JSON
        return file_content
    except Exception as e:
        logging.error(f"Failed to retrieve file {filename} from Minio: {e}")
        raise




def put_file(chunk_name, chunk):
    try:
        # Check if bucket exists, create if not
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)

        # Upload file to MinIO
        bytes_data = chunk.encode('utf-8')

        minio_client.put_object(MINIO_BUCKET, chunk_name, io.BytesIO(bytes_data), len(chunk))

        print(f"File '{chunk_name}' uploaded successfully to bucket '{MINIO_BUCKET}'.")

    except Exception as e:
        print(f"An error occurred while uploading file '{chunk_name}' to bucket '{MINIO_BUCKET}':")
        print(traceback.format_exc())  # Print full traceback for debugging
        print(f"Error details: {e}")

