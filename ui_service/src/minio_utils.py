# app/minio_utils.py
from minio import Minio
from minio.error import S3Error
import os

MINIO_ENDPOINT = os.getenv("MINIO_SERVICE_URL", "minio-service:9000")
MINIO_ACCESS_KEY = 'dena'
MINIO_SECRET_KEY = 'dena1234'
MINIO_BUCKET = 'map-reduce-input-files'

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # Set to True if using HTTPS
)

def create_minio_bucket():
    found = minio_client.bucket_exists(MINIO_BUCKET)
    if not found:
        minio_client.make_bucket(MINIO_BUCKET)
        print(f"Created bucket: {MINIO_BUCKET}")
    print('Bucket exists')

def check_file_existence(filename):
    try:
        minio_client.stat_object(MINIO_BUCKET, filename)
        return True
    except S3Error as e:
        if e.code == 'NoSuchKey':
            return False
        else:
            raise


