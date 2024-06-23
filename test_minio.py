from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = "83.212.78.127:30000"
ACCESS_KEY = "dena"
SECRET_KEY = "dena1234"
BUCKET_NAME = "chunk-bucket"

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

def list_files_in_bucket(bucket_name):
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False  # Set to True if using HTTPS
        )
        objects = minio_client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            print(obj.object_name)
    except S3Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example usage to list buckets and files in chunk-bucket
    print("Listing buckets:")
    list_buckets()

    print("\nListing files in bucket 'chunk-bucket':")
    list_files_in_bucket(BUCKET_NAME)
