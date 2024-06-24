import logging
import requests
from minio_utils import get_file, put_file
import os
import json
import uuid
from db_utils import create_table_if_not_exists, insert_batch
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement

MANAGER_SERVICE_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service.dena:8081")
INPUT_BUCKET_NAME = "map-reduce-input-files"
CHUCK_BUCKET_NAME = "chunk-bucket"
CASSANDRA_KEYSPACE = "admins"
CASSANDRA_TABLE = "intermediate_data"

def split_file(job_id, filename, num_chunks):
    try:
        # Pull file from Minio
        input_file = get_file(filename, INPUT_BUCKET_NAME)
        

        # Perform splitting
        data = json.loads(input_file)

        chunk_size = len(data) // num_chunks
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        if len(chunks) > num_chunks:
            last_chunk = chunks.pop()
            chunks[-1].extend(last_chunk)

        chunk_file_names = []
        base_name, ext = os.path.splitext(filename)

        # Store each chunk in the bucket with job-specific prefix
        prefix = f'job-{job_id}'
        for i, chunk in enumerate(chunks):
            chunk_name = f'{prefix}/chunk-{i}'
            put_file(chunk_name, json.dumps(chunk))  # Example: Convert chunk to JSON and store
            chunk_file_names.append(chunk_name)

        # Notify manager of completion
        response = requests.post(f"{MANAGER_SERVICE_URL}/split_complete", json={
            "job_id": job_id,
            "prefix": prefix,
            "num_chunks": len(chunks)
        })

        if response.status_code != 200:
            logging.error("Failed to notify manager of completion")
        else:
            print('Manager notified.')
        

    except Exception as e:
        logging.error(f"Failed to split file: {e}")



def map_file(job_id, filename):
    try:
        print(f"Job ID type: {type(job_id)}")
        print(f"Job ID type: {uuid.UUID(str(job_id))}")
        # Retrieve the chunk file
        input_file = get_file(filename, CHUCK_BUCKET_NAME)
        data = json.loads(input_file)

        create_table_if_not_exists()

        batch = BatchStatement()


        for entry in data:
            text = entry.get("text", "")
            words = text.split()
            for word in words:
                normalized_word = word.strip().lower()
                unique_id = uuid.uuid4()  # Ensure uniqueness for each word entry
                # Convert job_id to UUID explicitly
                batch.add(SimpleStatement(
                    f"INSERT INTO {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (job_id, key, value, unique_id) VALUES (%s, %s, %s, %s)"
                ), (uuid.UUID(str(job_id)), normalized_word, '1', unique_id))


        insert_batch(batch)

        # Notify manager of completion
        prefix = f'job-{job_id}'
        response = requests.post(f"{MANAGER_SERVICE_URL}/map_complete", json={
            "job_id": str(job_id),  # Ensure job_id is sent as string
            "prefix": prefix,
            "chunk_name": filename  
        })

        if response.status_code != 200:
            logging.error("Failed to notify manager of completion")
        else:
            print('Manager notified.')

    except Exception as e:
        logging.error(f"Failed to map file: {e}")
