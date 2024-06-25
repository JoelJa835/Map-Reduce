from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from cassandra.cluster import Cluster
# from cassandra.query import BatchStatement, SimpleStatement
import uuid
from uuid import UUID
from uuid import uuid4
from collections import defaultdict
from typing import List, Dict
import re

app = FastAPI()

# Initialize keyspace and tables
KEYSPACE = "mapreduce"
MAP_TABLE = "map_table"
SHUFFLE_TABLE = "shuffle_table"
REDUCE_TABLE = "reduce_table"

# Update with the correct Cassandra host and port
contact_points = ['127.0.0.1']
port = 9042

# Cluster initialization
cluster = Cluster(contact_points=contact_points, port=port)
session = cluster.connect()

# # Ensure keyspace and tables exist
# session.execute(f"""
# CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
# WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }};
# """)
# # Table for intermediate results (Mapper results)
# session.execute(f"""
# CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (
#     job_id UUID,
#     key TEXT,
#     value TEXT,
#     unique_id UUID,
#     PRIMARY KEY (job_id, key, unique_id)
# );
# """)


# # Table for Reducer results
# session.execute(f"""
# CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{FINAL_RESULT_TABLE} (
#     job_id uuid,
#     key text,
#     reduced_value int,
#     PRIMARY KEY (job_id, key)
# );
# """)

# class ShuffleSortRequest(BaseModel):
#     job_id: uuid.UUID

# class ReduceRequest(BaseModel):
#     job_id: uuid.UUID
#     key: str

def create_keyspace_and_tables(keyspace: str, map_table: str, shuffle_table: str, reduce_table: str):
    session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {keyspace}
    WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }}
    """)
    
    session.set_keyspace(keyspace)
    
    session.execute(f"""
    CREATE TABLE IF NOT EXISTS {MAP_TABLE} (
        job_id UUID,
        key TEXT,
        value INT,
        PRIMARY KEY (job_id, key)
    )
    """)

    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {SHUFFLE_TABLE} (
            job_id UUID,
            key TEXT,
            value INT,
            PRIMARY KEY (job_id, key)
        )
        """)

    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {REDUCE_TABLE} (
            job_id UUID,
            key TEXT,
            value INT,
            PRIMARY KEY (job_id, key)
        )
        """)


create_keyspace_and_tables(KEYSPACE, MAP_TABLE, SHUFFLE_TABLE, REDUCE_TABLE)

def sanitize_word(word: str) -> str:
    # Remove non-alphanumeric characters and convert to lowercase
    sanitized_word = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
    return sanitized_word

@app.post("/map/")
async def map_words(file: UploadFile = File(...)):
    job_id = uuid4()  # Generate a unique job_id for this mapping operation
    
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt files are accepted.")
    
    word_count = defaultdict(int)
    
    # Read and process the file
    contents = await file.read()
    text = contents.decode('utf-8')
    
    for word in text.split():
        sanitized_word = sanitize_word(word)
        if sanitized_word:
            word_count[sanitized_word] += 1
    
    # Insert the results into Cassandra with associated job_id
    for word, count in word_count.items():
        session.execute(
            f"""
            INSERT INTO {MAP_TABLE} (job_id, key, value) VALUES (%s, %s, %s)
            """,
            (job_id, word, count)
        )
    
    return {"message": "Mapping complete", "job_id": job_id}


@app.get("/shuffle_sort/")
async def shuffle_sort(job_id: uuid.UUID):
    rows = session.execute(f"SELECT * FROM {MAP_TABLE} WHERE job_id = %s", (job_id,))
    word_counts = defaultdict(int)
    
    for row in rows:
        word_counts[row.key] += row.value
    
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[0])
    
    # Store the sorted results into Cassandra
    session.execute(f"TRUNCATE {SHUFFLE_TABLE}")
    for word, count in sorted_word_counts:
        session.execute(
            f"""
            INSERT INTO {SHUFFLE_TABLE} (job_id, key, value) VALUES (%s, %s, %s)
            """,
            (job_id, word, count)
        )
    
    return sorted_word_counts

@app.get("/reduce/")
async def reduce(job_id: uuid.UUID):
    rows = session.execute(f"SELECT * FROM {SHUFFLE_TABLE} WHERE job_id = %s", (job_id,))
    word_counts = defaultdict(int)
    
    for row in rows:
        word_counts[row.key] += row.value
    
    reduced_word_counts = [{"key": word, "value": count} for word, count in word_counts.items()]
    
    # Store the reduced results into Cassandra
    session.execute(f"TRUNCATE {REDUCE_TABLE}")
    for item in reduced_word_counts:
        session.execute(
            f"""
            INSERT INTO {REDUCE_TABLE} (job_id, key, value) VALUES (%s, %s, %s)
            """,
            (job_id, item["key"], item["value"])
        )
    
    return reduced_word_counts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


















