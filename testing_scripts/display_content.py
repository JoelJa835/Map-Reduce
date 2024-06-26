
from minio import Minio
from minio.error import S3Error
import json

MINIO_ENDPOINT = "83.212.78.127:30000"
ACCESS_KEY = "dena"
SECRET_KEY = "dena1234"
BUCKET_NAME = "map-reduce-input-files"
CHUCK_BUCKET_NAME = 'chunk-bucket'
MINIO_OUTPUT_BUCKET = 'map-reduce-final-results'
BUCKET_NAME = "map-reduce-input-files"



def display_file_content(bucket_name, file_name):
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False  # Set to True if using HTTPS
        )
        
        # Get the object data
        response = minio_client.get_object(bucket_name, file_name)
        
        # Read the object data (assuming it's JSON data)
        data = response.data.decode('utf-8')
        json_data = json.loads(data)
        print(json.dumps(json_data, indent=4))
        
        # Close the response to release network resources
        response.close()
        response.release_conn()
        
    except S3Error as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Example usage to display the content of a JSON file
    # Replace "example-file.json" with the actual file name you want to display
    #display_file_content(MINIO_OUTPUT_BUCKET, "reduced_data_72998c1f-e70f-46a9-ac66-6c6f648403da.json")
    display_file_content(BUCKET_NAME, "word_stats.json")