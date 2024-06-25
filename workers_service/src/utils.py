import logging
import requests
from minio_utils import get_file, put_file
import os
import json
import uuid
from db_utils import insert_batch, insert_word, get_rows, insert_shuffled
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement
from collections import defaultdict
import re
from typing import List, Dict


MANAGER_SERVICE_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service.dena:8081")
INPUT_BUCKET_NAME = "map-reduce-input-files"
CHUCK_BUCKET_NAME = "chunk-bucket"
CASSANDRA_KEYSPACE = "admins"
MAP_TABLE = 'map_table'
SHUFFLE_TABLE = 'shuffle_table'
REDUCE_TABLE = 'reduce_table'

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



def map_file(job_id, filename, number):
    try:
        # Retrieve the chunk file
        input_file = get_file(filename, CHUCK_BUCKET_NAME)
        data = json.loads(input_file)
        word_count = defaultdict(int)

        
        
        for entry in data:
            text = entry.get("text", "")
            words = text.split()
            for word in words:
                sanitized_word = sanitize_word(word)
                if sanitized_word:
                    word_count[sanitized_word] += 1
        
        # Insert the results into Cassandra with associated job_id
        for word, count in word_count.items():
            insert_word(job_id, word, count, number)

        # batch = BatchStatement()


        # for entry in data:
        #     text = entry.get("text", "")
        #     words = text.split()
        #     for word in words:
        #         normalized_word = word.strip().lower()
        #         unique_id = uuid.uuid4()  # Ensure uniqueness for each word entry
        #         # Convert job_id to UUID explicitly
        #         batch.add(SimpleStatement(
        #             f"INSERT INTO {CASSANDRA_KEYSPACE}.{MAP_TABLE} (job_id, key, value, unique_id) VALUES (%s, %s, %s, %s)"
        #         ), (uuid.UUID(str(job_id)), normalized_word, '1', unique_id))


        # insert_batch(batch)

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


def shuffle_in_database(job_id, reducers):

    try:

        rows = get_rows(job_id)
        key_value_pairs = defaultdict(list)

        for row in rows:
            key_value_pairs[row.key].append(row.value)


        sorted_key_value_pairs = sorted(key_value_pairs.items(), key=lambda x: x[0])

        # Split data among reducers
        num_pairs = len(sorted_key_value_pairs)
        chunk_size = (num_pairs + reducers - 1) // reducers  # Ensure we cover all elements
        

        for i in range(reducers):
            start_index = i * chunk_size
            end_index = min(start_index + chunk_size, num_pairs)
            for key, values in sorted_key_value_pairs[start_index:end_index]:
                insert_shuffled(job_id, i, key, values)



        # Notify manager of completion
        prefix = f'job-{job_id}'
        response = requests.post(f"{MANAGER_SERVICE_URL}/shuffle_sort_complete", json={
            "job_id": str(job_id),  # Ensure job_id is sent as string
            "prefix": prefix, 
        })

        if response.status_code != 200:
            logging.error("Failed to notify manager of completion")
        else:
            print('Manager notified.')



    except Exception as e:
        logging.error(f"Failed to suffle and sort file: {e}")



def sanitize_word(word: str) -> str:
    # Remove non-alphanumeric characters and convert to lowercase
    sanitized_word = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
    return sanitized_word



