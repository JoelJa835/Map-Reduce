from minio import Minio
from minio.error import S3Error
import os

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


def get_chunk_names(job_id):
    '''
    Retrieves chunk names from bucket
    '''
    try:
        # List objects in the bucket with a prefix matching job_id
        chunk_names = []
        prefix = f'job-{job_id}/'
        objects = minio_client.list_objects(MINIO_BUCKET, prefix=prefix)
        for obj in objects:
            chunk_names.append(obj.object_name)
        return chunk_names
    except S3Error as e:
        print(f"Error occurred while retrieving chunk names: {e}")
        traceback.print_exc()
        return []



def delete_chunk(chunk_name):
    '''
    Deletes a chunk from the bucket
    '''
    try:
        minio_client.remove_object(MINIO_BUCKET, chunk_name)
        print(f"Chunk {chunk_name} deleted successfully.")
    except S3Error as e:
        print(f"Error occurred while deleting chunk: {e}")
        traceback.print_exc()