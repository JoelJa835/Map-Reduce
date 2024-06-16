from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = "83.212.78.127:30000"
ACCESS_KEY = "dena"
SECRET_KEY = "dena1234"

def list_buckets():
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False  # Set to True if using HTTPS
        )
        buckets = minio_client.list_buckets()
        for bucket in buckets:
            print(bucket.name)
    except S3Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_buckets()
