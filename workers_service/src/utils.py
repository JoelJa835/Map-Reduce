import logging
import requests
from minio_utils import get_file, put_file
import os
import json
import uuid

MANAGER_SERVICE_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service.dena:8081")


def split_file(job_id, filename, num_chunks):
    try:
        # Pull file from Minio
        input_file = get_file(filename)
        

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

