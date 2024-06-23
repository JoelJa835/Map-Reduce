from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = "83.212.78.127:30000"
ACCESS_KEY = "dena"
SECRET_KEY = "dena1234"
BUCKET_NAME = "chunk-bucket"

def empty_bucket(bucket_name):
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False  # Set to True if using HTTPS
        )

        # List all objects in the bucket
        objects = minio_client.list_objects(bucket_name, recursive=True)
        
        # Remove each object one by one
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
            print(f"Removed object: {obj.object_name}")

        print(f"Bucket '{bucket_name}' emptied successfully.")
        
    except S3Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Call empty_bucket function to empty 'chunk-bucket'
    empty_bucket(BUCKET_NAME)
