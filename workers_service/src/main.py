from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement
import uuid
import json 
import collections

app = FastAPI()

# Cassandra configuration
CASSANDRA_KEYSPACE = "mapreduce"
CASSANDRA_TABLE = "intermediate_data"
FINAL_RESULT_TABLE = "final_results"

# Update with the correct Cassandra host and port
contact_points = ['127.0.0.1']
port = 9042

# Cluster initialization
cluster = Cluster(contact_points=contact_points, port=port)
session = cluster.connect()

# Ensure keyspace and tables exist
session.execute(f"""
CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }};
""")
# Table for intermediate results (Mapper results)
session.execute(f"""
CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (
    job_id UUID,
    key TEXT,
    value TEXT,
    unique_id UUID,
    PRIMARY KEY (job_id, key, unique_id)
);
""")


# Table for Reducer results
session.execute(f"""
CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{FINAL_RESULT_TABLE} (
    job_id uuid,
    key text,
    reduced_value int,
    PRIMARY KEY (job_id, key)
);
""")

class ShuffleSortRequest(BaseModel):
    job_id: uuid.UUID

class ReduceRequest(BaseModel):
    job_id: uuid.UUID
    key: str

@app.post("/map/")
async def map_data(job_id: uuid.UUID, file: UploadFile = File(...)):
    contents = await file.read()
    data = json.loads(contents.decode('utf-8'))
    
    batch = BatchStatement()
    
    for entry in data:
        text = entry.get("text", "")
        words = text.split()
        for word in words:
            normalized_word = word.strip().lower()
            unique_id = uuid.uuid4()  # Ensure uniqueness for each word entry
            batch.add(SimpleStatement(
                f"INSERT INTO {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (job_id, key, value, unique_id) VALUES (%s, %s, %s, %s)"
            ), (job_id, normalized_word, '1', unique_id))
    
    session.execute(batch)
    
    return {"status": "success", "message": "Data mapped and stored in Cassandra"}

@app.post("/shuffle-sort/")
async def shuffle_sort(shuffle_sort_request: ShuffleSortRequest):
    job_id = shuffle_sort_request.job_id

    # Logging the received job_id for debugging
    print(f"Received job_id: {job_id}")

    # Retrieve data grouped by key
    query = SimpleStatement(
        f"SELECT key, value FROM {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} WHERE job_id=%s"
    )
    result = session.execute(query, (job_id,))

    grouped_data = collections.defaultdict(list)
    for row in result:
        grouped_data[row.key].append(int(row.value))

    # Convert defaultdict to a regular dictionary for JSON serialization
    grouped_data = dict(grouped_data)

    return {"status": "success", "grouped_data": grouped_data}


@app.post("/reduce/")
async def reduce_data(reduce_request: ReduceRequest):
    job_id = reduce_request.job_id
    grouped_data = reduce_request.grouped_data

    # Sum the values for each key
    reduced_data = {}
    for key, values in grouped_data.items():
        total_count = sum(values)
        reduced_data[key] = total_count
        
        # Insert reduced value into final results table
        session.execute(
            f"INSERT INTO {CASSANDRA_KEYSPACE}.{FINAL_RESULT_TABLE} (job_id, key, reduced_value) VALUES (%s, %s, %s)",
            (job_id, key, total_count)
        )

    return {"status": "success", "reduced_data": reduced_data}



